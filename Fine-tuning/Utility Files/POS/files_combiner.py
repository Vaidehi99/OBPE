import argparse
import sys
import os 


parser = argparse.ArgumentParser()
parser.add_argument("--input_folder", default=None, type=str, required=True, help="path to the input_folder")
parser.add_argument("--output_folder", default=None, type=str, required=True,help="path to the output_folder")
parser.add_argument("--l_code_actual", default=None, type=str, required=True,help="language code")
parser.add_argument("--l_code_in_raw_data", default=None, type=str, required=True,help="language code")
args = parser.parse_args()


try:
    os.makedirs(args.output_folder,exist_ok=True)
except:
    print('error while creating outdir',args.output_folder)
out_dir=args.output_folder+'/'+args.l_code_actual

try:
    os.makedirs(out_dir,exist_ok=True)
except:
    print('error while creating outdir',out_dir)

train_out=open(out_dir+'/'+'train-'+args.l_code_actual+'.tsv','w')

for file_name in open('train_files_taken.txt','r').readlines():
	f=open(args.input_folder+'/'+args.l_code_in_raw_data+'_'+file_name[:-1]+'.tsv')
	a=f.readlines()
	for line in a:
		train_out.write(line)
train_out.close()
test_out=open(out_dir+'/'+'test-'+args.l_code_actual+'.tsv','w')

for file_name in open('test_files_taken.txt','r').readlines():
	f=open(args.input_folder+'/'+args.l_code_in_raw_data+'_'+file_name[:-1]+'.tsv')
	a=f.readlines()
	for line in a:
		test_out.write(line)
test_out.close()
