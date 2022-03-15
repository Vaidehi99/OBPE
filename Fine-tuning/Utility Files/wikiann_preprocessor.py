import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--infile", default=None, type=str, required=True, help="path of input file to preprocess")
parser.add_argument("--outfile", default=None, type=str, required=True,help="output file path")
args = parser.parse_args()

lines=open(args.infile,'r').readlines()
outfile=open(args.outfile,'w')

for line in lines:
	if(len(line.split(' '))==0):
		outfile.write('\n')
	else:
		outfile.write(line.split(' ')[0]+'\t'+line.split(' ')[-1])
			
