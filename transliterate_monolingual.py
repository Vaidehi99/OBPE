from indictrans import Transliterator
import argparse
from tqdm import tqdm

def transliterate(monofile,outfile, l1, l2):
    trn = Transliterator(source=l1,target=l2,build_lookup=True)
    with open(monofile) as f:
        lines = f.readlines()
    with open(outfile,'w') as w:
        for line in tqdm(lines):
            t13n = trn.transform(line)
            assert(len(t13n.split(" ")) == len(line.split(" ")))
            if not t13n.endswith('\n'):
                t13n = t13n+'\n'
            w.write(t13n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mono',type=str,help='Path to monolingual data')
    parser.add_argument('--outfile',type=str,help='Path to output file')
    parser.add_argument('--l1',type=str,help='Source Language')
    parser.add_argument('--l2',type=str,help='Target Language')
    args = parser.parse_args()
    transliterate(args.mono,args.outfile,args.l1,args.l2)
