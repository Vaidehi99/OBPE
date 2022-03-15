# OBPE
This repository contains the source code of the following ACL 2022 paper: [Overlap-based Vocabulary Generation Improves Cross-lingual Transfer Among Related Languages](https://arxiv.org/abs/2203.01976). It is divided into 5 sections:
- [Setup](#setup)
- [Creating OBPE tokenizer](#creating-obpe-tokenizer)
- [Pretraining with MLM](#pretraining-with-mlm)
- [Fine-Tuning on Downstream Tasks](#fine-tuning-on-downstream-tasks)
- [Miscellaneous](#miscellaneous)


## Setup
First, create the conda environment from [obpe_env.yml](https://github.com/Vaidehi99/OBPE/blob/main/obpe_env.yml) file using:
```shell
conda env create -f obpe_env.yml
conda activate obpe_env
```
After that, setup **indic-trans** library using the instructions from [this](https://github.com/libindic/indic-trans) repository.<br>
Also note that the pretraining has been done using Google Cloud TPUs so some of the code will be TPU-specific.

## Creating OBPE tokenizer
To create OBPE tokenizer, run the follwoing three scripts sequentially

```shell
python3 get_vocab.py\
  --mono_files ./l1_monolingual_data.txt ./l2_monolingual_data.txt\ 
  --output_files vocabs/l1.pkl vocabs/l2.pkl
```
```shell
python3 tokenizer.py\ 
  --vocab_files vocabs/l1.pkl vocabs/l2.pkl\
  --use_vocab\
  --output_dir models/l1_l2_p_-3\
  --vocab_size 30000\
  --model bpe\
  --eow_suffix "</w>"\ 
  --n_HRL 1\
  --max_tok\
  --alpha 0.5\ 
  --overlap mean\
  --p -3
```
OR
```shell
python3 tokenizer.py\ 
  --vocab_files vocabs/l1.pkl vocabs/l2.pkl\
  --use_vocab\
  --output_dir models/l1_l2_min\
  --vocab_size 30000\
  --model bpe\
  --eow_suffix "</w>"\
  --n_HRL 1\
  --max_tok\
  --alpha 0.5\
  --overlap min 
```
```shell
python3 generate_json_from_model.py\
  --vocab models/l1_l2_min/vocab.json\
  --merges models/l1_l2_min/merges.txt\
  --model bpe\
  --outfile tokenizers/l1_l2_min_tokenizer.json
```
Use this json file as input to create_pretraining_data_ENS_with_diff_tokenizer.py while creating MLM pretraining data

## Pretraining with MLM
We need to create 2 new conda environments for Pretraining with BERT. We will make use of some code from [Google BERT Repo](https://github.com/google-research/bert) along with our code. Pretraining BERT has 2 components:
1. Preprocessing: <br>
(a) The current BERT Preprocessig code needs to run in Tensorflow v2. Create a new conda environment and set it up as follows:
```shell
conda env create --name bert_preprocessing
conda activate bert_preprocessing
conda install tensorflow==2.3.0

```
(b) Run the following command from the directory "BERT Pretraining and Preprocessing/Preprocessing Code" to create the preprocessing code. Refer to the [Google BERT Repo](https://github.com/google-research/bert) for other information.

```shell
python3 create_pretraining_data_ENS_with_diff_tokenizer.py\
  --input_file=./monolingual_data.txt\
  --output_file=/tmp/tf_examples.tfrecord\
  --json_vocab_file=$BERT_BASE_DIR/tokenizer.json
  --do_lower_case=False\
  --max_seq_length=128\
  --max_predictions_per_seq=20\
  --do_whole_word_mask=False\
  --masked_lm_prob=0.15\
  --random_seed=12345\
  --dupe_factor=2

2. Pre-training:<br>
(a) The BERT Pretraining code used needs to run in Tensorflow v1 (same as the original Google BERT). Create a new conda environment and set it up as follows:
```shell
conda env create --name bert_pretraining
conda activate bert_pretraining
conda install -c conda-forge tensorflow==1.14

```
(b) Clone the Original [Google BERT Repo](https://github.com/google-research/bert) and replace the create_pretraining_data.py with our "BERT Pretraining and Preprocessing/Pretraining Diff Files/run_pretraining_without_NSP.py". Note that to run the pretraining on TPUs, the init_checkpoint, input_file and output_dir need to be on a Google Cloud Bucket.
Run the following command for pretraining:

```shell
python run_pretraining_without_NSP.py\
  --input_file=/tmp/tf_examples.tfrecord\
  --output_dir=/tmp/pretraining_output\
  --do_train=True\
  --do_eval=True\
  --bert_config_file=$BERT_CONFIG_DIR/bert_config.json\
  --init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt\
  --train_batch_size=32\
  --max_seq_length=128\
  --max_predictions_per_seq=20\
  --num_train_steps=20\
  --num_warmup_steps=10\
  --learning_rate=2e-5\
  --save_checkpoint_steps=10\
  --iterations_per_loop=5\
  --use_tpu=True\
  --tpu_name=node-1\
  --tpu_zone=zone-1\
  --num_tpu_cores=8 
```

## Fine-Tuning on Downstream Tasks
We fine tune of 4 different tasks. The dataset procurement, data cleaning and fine-tuning steps are as follows:

### Named Entity Recognition :
The dataset is obtained from XTREME Dataset(for en and hi) and WikiAnn NER (for pa, gu, bn, or, as). For preprocessing the WikiAnn NER dataset files, use  "Fine Tuning/Utility Files/wikiann_preprocessor.py" as follows:
```shell
python3 wikiann_preprocessor.py --infile language/language-train.txt --outfile language/train-language.tsv
```
Use the "Fine Tuning/NER_Fine_Tuning.ipynb" for NER evaluation.<br><br> 

POS Tagging and Text Classification : The datasets for POS Tagging and Text Classification has been obtained from (Indian Language Technology Proliferation and Deployment Centre)[http://tdil-dc.in/]. <br><br>
### Part of Speech Tagging :
Preprocess the data using the preprocessing files from "Fine Tuning/Utility Files/POS/". The "file to language mapping" has been included in "Fine Tuning/Utility Files/POS/Language to File Mapping.txt". Then combine the files using "Fine Tuning/Utility Files/POS/files_combiner.py" to create the train-test splits.
```shell
python3 pos_preprocessor.py --input_folder Language_Raw_Files/ --output_folder Language_POS_Data/
python3 files_combiner.py   --input_folder Language_POS/ --output_folder datasets/ --l_code_actual language_code_as_per_ISO_639 --l_code_in_raw_data language_code_as_per_tdil_dataset
```
We use the [BIS Tagset](https://www.aclweb.org/anthology/W12-5012.pdf) as the POS tags. The Indian Languages are already tagged with the BIS Tagset whereas the English Dataset is labelled with Penn Tagset. To convert the Penn to BIS, use "Fine Tuning/Utility Files/convert_penn_to_bis.py" to run the following command on the directory containing preprocessed POS dataset files tagged with Penn Tagset:
```shell
python3 convert_penn_to_bis.py --input_folder English_POS_Penn/ --output_folder English_POS_BIS/
```
Use the "Fine Tuning/POS_Fine_Tuning.ipynb" for POS evaluation.<br> 

### Text Classification<br>
Preprocess the data using the preprocessing files from "Fine Tuning/Utility Files/Text Classification/". The "file to language mapping" has been included in "Fine Tuning/Utility Files/Doc Classification/Language to File Mapping.txt".

```shell
python3 doc_classification_preprocessor_for_chunked.py --input_folder Language_Raw_Files/ --output_folder Language_Doc_Classification_Data --l_code_actual language_code_as_per_ISO_639 --l_code_in_raw_data language_code_as_per_tdil_dataset --train_files_taken train_files_taken.txt --test_files_taken test_files_taken.txt --valid_files_taken val_files_taken.txt 
```
Use the "Fine Tuning/Text_Classification_Fine_Tuning.ipynb" for Doc Classification evaluation.<br> 
<br>

### XNLI<br>
Use the "Fine Tuning/XNLI_Fine_Tuning.ipynb" for Doc Classification evaluation.<br> 
<br>

## Miscellaneous
### transliterate_monolingual.py
Used for transliterating monolingual data to another languages's script. To use, run:
```shell
python3 transliterate_monolingual.py\
    --mono path_to_monolingual_data\
    --outfile path_to_output_transliterated_data\
    --l1 source_lang\
    --l2 target_lang
```
`--mono` : Path to the monolingual (text) data<br>
`--outfile` : Path to output transliterated (text) file<br>
`--l1` : Code for source language
`--l2` : Code for target language

# Paper

If you use the code in this repo, please cite our paper `\cite{patil2022overlap}`.
```
@article{patil2022overlap,
  title={Overlap-based Vocabulary Generation Improves Cross-lingual Transfer Among Related Languages},
  author={Patil, Vaidehi and Talukdar, Partha and Sarawagi, Sunita},
  journal={arXiv preprint arXiv:2203.01976},
  year={2022}
}
```
