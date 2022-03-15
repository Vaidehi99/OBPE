import argparse
import sys
import os 


parser = argparse.ArgumentParser()
parser.add_argument("--input_folder", default=None, type=str, required=True, help="path to the input_folder")
parser.add_argument("--output_folder", default=None, type=str, required=True,help="path to the out_folder")
args = parser.parse_args()

files=os.listdir(args.input_folder)
try:
    os.makedirs(args.output_folder,exist_ok=True)
except:
    print('error while creating outdir',args.output_folder)

pos_tags_list=[t.split('\t')[0] for t in open('penn_to_bis_mapping.txt','r').readlines()[:-1]]
for file in files:
	f=args.input_folder+'/'+file
	f=open(f,'r')
	f.readline()
	a=f.readlines()
	outfile=open(args.output_folder+'/'+file[:-4]+'.tsv','w')
	count1=0
	count2=0
	for sent in a:
		ws=[]
		ts=[] 
		words=sent.split('\n')[0].split('\t')[-1].split(']]') 
		for wg in words[:-1]: 
			for w in wg.split('[[')[-1].split(' '):
				word=w.split('\n')[0].split("\\")[0].split('\t')[-1]
				tags=w.split('\n')[0].split("\\")[-1].split('_')
				t1=tags[0 % len(tags)] 
				t2=tags[1 %len(tags)]
				ws.append(word)
				ts.append(t1)
				if(t1 not in pos_tags_list):
					ws=[]
					ts=[]
					break
			if(ws==[]):
				break	
		if(ws==[]):
			count1+=1
			continue
		else:
			count2+=1
			for i in range(len(ws)):
				word=ws[i]
				t1=ts[i]
				outfile.write(word+'\t'+t1+'\n')
		outfile.write('\n')                                    
	f.close()
	outfile.close()
