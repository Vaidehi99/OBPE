import tempfile
from multiprocessing import Pool, cpu_count
import sys,os
import tqdm
from tqdm import tqdm
import warnings
from collections import Counter
import pickle
from tokenizers.pre_tokenizers import BertPreTokenizer
import argparse

def get_vocabulary(fobj, pre_tokenizer, num_workers=1):
    """Read text and return dictionary that encodes vocabulary
    """
    vocab = Counter()
    num_lines = 0

    if num_workers == 1 or fobj.name == '<stdin>':
        if num_workers > 1:
            warnings.warn("In parallel mode, the input cannot be STDIN. Using 1 processor instead.")
        for i, line in tqdm(enumerate(fobj)):
            num_lines += 1
            for word,_ in pre_tokenizer.pre_tokenize_str(line):
                if word:
                    vocab[word] += 1

    elif num_workers > 1:
        with open(fobj.name, encoding="utf8") as f:
            size = os.fstat(f.fileno()).st_size
            chunk_size = int(size / num_workers)
            offsets = [0 for _ in range(num_workers + 1)]
            for i in range(1, num_workers):
                f.seek(chunk_size * i)
                pos = f.tell()
                while True:
                    try:
                        line = f.readline()
                        break
                    except UnicodeDecodeError:
                        pos -= 1
                        f.seek(pos)
                offsets[i] = f.tell()
                assert 0 <= offsets[i] < 1e20, "Bad new line separator, e.g. '\\r'"

        vocab_files = []
        pool = Pool(processes=num_workers)
        for i in range(num_workers):
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.close()
            vocab_files.append(tmp)
            pool.apply_async(_get_vocabulary, (fobj.name, tmp.name, pre_tokenizer, offsets[i], offsets[i + 1]))
        pool.close()
        pool.join()
        import pickle
        for i in range(num_workers):
            with open(vocab_files[i].name, 'rb') as f:
                tmp_vocab,tmp_num_lines = pickle.load(f)
                vocab += tmp_vocab
                num_lines += tmp_num_lines
            os.remove(vocab_files[i].name)
    else:
        raise ValueError('`num_workers` is expected to be a positive number, but got {}.'.format(num_workers))
    return vocab,num_lines

def _get_vocabulary(infile, outfile, pre_tokenizer, begin, end):
    import pickle
    vocab = Counter()
    num_lines = 0
    with open(infile, encoding="utf8") as f:
        f.seek(begin)
        line = f.readline()
        while line:
            pos = f.tell()
            assert 0 <= pos < 1e20, "Bad new line separator, e.g. '\\r'"
            if end > 0 and pos > end:
                break
            num_lines+=1
            for word,_ in pre_tokenizer.pre_tokenize_str(line):
                if word:
                    vocab[word] += 1
            line = f.readline()
    with open(outfile, 'wb') as f:
        pickle.dump([vocab,num_lines], f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mono_files',type=str,nargs='+',help='Path to monolingual text files')
    parser.add_argument('--output_files',type=str,nargs='+',help='Path to output vocabulary files')
    parser.add_argument('--num_workers',type=int,default=1,help='Number of workers for building vocabulary from mono data')
    args = parser.parse_args()
    pre_tokenizer = BertPreTokenizer()
    for i,(filename,outfile) in enumerate(zip(args.mono_files,args.output_files)):
        os.makedirs(os.path.dirname(outfile),exist_ok=True)
        print("Building vocabulary for file",filename)
        with open(filename,'r') as f:
            vocab,num_lines = get_vocabulary(f,pre_tokenizer,args.num_workers)
        with open(outfile,'wb') as w:
            pickle.dump([vocab,num_lines],w)
