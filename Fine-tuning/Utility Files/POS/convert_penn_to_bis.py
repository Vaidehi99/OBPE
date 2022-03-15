import argparse
import sys
import os 


parser = argparse.ArgumentParser()

parser.add_argument("--input_folder", default=None, type=str, required=True, help="path to the input_folder")
parser.add_argument("--output_folder", default=None, type=str, required=True,help="path to the out_folder")

args = parser.parse_args()

files=os.listdir(args.input_folder)
try:
    os.mkdir(args.output_folder)
except:
    print('error while creating outdir',args.output_folder)



mapping=open('penn_to_bis_mapping.txt','r').readlines()
fixed_mapping={}
fixed_mapping_count={}
fixed_mapping_count['unk']={}
count=0
for l in mapping:
	count+=1
	l=l[:-1]
	fixed_mapping[l.split('\t')[0]]=l.split('\t')[1]
	fixed_mapping_count[l.split('\t')[0]]=0
print("len(fixed_mapping)",len(fixed_mapping))
print(fixed_mapping)


special_mapping_list={}
dt={}
dt['QT']=[['some','every','both','all','another','a','an'],0]
dt['DM']=[['this','these','the'],0]
dt['PR']=[['those','that'],0]
dt['default']=[['QT'],{}]

pdt={}
pdt['QT']=[['all','half'],0]
pdt['DM']=[['such'],0]
pdt['default']=[['QT'],{}]

wdt={}
wdt['PR']=[['which','that'],0]
wdt['RP']=[['whatever'],0]
wdt['default']=[['PR'],{}]

wrb={}
wrb['PR']=[['how','when','where','wherever'],0]
wrb['RB']=[['whenever','why'],0]
wrb['default']=[['PR'],{}]

special_mapping_list['DT']=dt
special_mapping_list['PDT']=pdt
special_mapping_list['WDT']=wdt
special_mapping_list['WRB']=wrb



def get_mapping(tag,word):
	word=word.lower()
	if tag in fixed_mapping:
		fixed_mapping_count[tag]+=1
		return fixed_mapping[tag]
	elif tag in special_mapping_list:
		for key in special_mapping_list[tag]:
			if(word in special_mapping_list[tag][key][0]):
				# print(special_mapping_list[tag][key][1])
				special_mapping_list[tag][key][1]+=1
				return key
		if tag in special_mapping_list[tag]['default'][1]:
			# print(special_mapping_list[tag]['default'][1][tag])
			special_mapping_list[tag]['default'][1][word]+=1
		else:
			special_mapping_list[tag]['default'][1][word]=1		
		return special_mapping_list[tag]['default'][0][0]		
	else:
		if tag in fixed_mapping_count['unk']:
			fixed_mapping_count['unk']['tag']+=1
		else:
			fixed_mapping_count['unk']['tag']=1	
		return 'RD'	

files=os.listdir(args.input_folder)
try:
    os.mkdir(args.output_folder)
except:
    print('error while creating outdir',args.output_folder)


for file in files:
	f=args.input_folder+'/'+file
	f=open(f,'r')
	# f.readline()
	a=f.readlines()
	outfile=open(args.output_folder+'/'+file,'w')

	for line in a:
		if(line=='\n'):
			outfile.write('\n')
		else:
			line=line[:-1]
			word=line.split('\t')[0]
			tag=line.split('\t')[1]
			outfile.write(word+'\t'+get_mapping(tag,word)+'\n')
	outfile.close()
	f.close()

print("Easy mapping count")
for key in fixed_mapping_count:
	print(key,fixed_mapping_count[key]) 
# print(fixed_mapping_count)

print("\n\nSpecial Mapping\n")
for key in special_mapping_list:
	print(key,special_mapping_list[key]) 
