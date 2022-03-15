from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.models import WordPiece as wp
from tokenizers.pre_tokenizers import BertPreTokenizer
from tokenizers.decoders import BPEDecoder
from tokenizers.decoders import WordPiece as wpd
import argparse,os
import pickle
from tokenizers.models import Unigram
from tokenizers.decoders import Metaspace

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--vocab',type=str,help='Path to vocabulary file')
    parser.add_argument('--merges',type=str,help='Path to merges file')
    parser.add_argument('--model',type=str,help='Model Type',choices=['bpe','wordpiece','unigram'])
    parser.add_argument('--outfile',type=str,help='Path to the output json file')
    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.outfile),exist_ok=True)
    if args.model == 'bpe':
        model = BPE(args.vocab,args.merges,end_of_word_suffix='</w>')
        decoder = BPEDecoder()
        tokenizer = Tokenizer(model)
        tokenizer.add_special_tokens(['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]', '<S>', '<T>'])
        tokenizer.pre_tokenizer = BertPreTokenizer()
        tokenizer.decoder = decoder
        tokenizer.save(args.outfile,pretty=True)

    elif args.model == 'wordpiece':
        model = wp(args.vocab,'[UNK]')
        decoder = wpd()
        tokenizer = Tokenizer(model)
        tokenizer.add_special_tokens(['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]', '<S>', '<T>'])
        tokenizer.pre_tokenizer = BertPreTokenizer()
        tokenizer.decoder = decoder
        tokenizer.save(args.outfile,pretty=True)

    elif args.model == 'unigram':
        with open(args.vocab, 'rb') as f:
          vocab_merged = pickle.load(f)
        model = Unigram(vocab_merged, unk_id = 3)
        # when running spm_train use unk_id = 3 and also ensure that unk_id = 3 in merged_vocabs generated using merge_vocabs_modified_Unigram.py
        decoder = Metaspace()
        tokenizer = Tokenizer(model)
        tokenizer.add_special_tokens(['[CLS]', '[SEP]', '[MASK]', '<T>'])
        tokenizer.pre_tokenizer = BertPreTokenizer()
        tokenizer.decoder = decoder
        tokenizer.save(args.outfile,pretty=True)
