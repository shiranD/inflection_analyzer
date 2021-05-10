#!/bin/bash

set -x
set -e

lang=deu
dev_fname=${lang}.dev # make sure is correct
letter_fname=${lang} # make sure is found
isyms=${lang}_symbols # will be created
query_file=query.txt # an example file is found
constraint=V_IND_PST_2_SG # set prior condition (V;FUT;1;SG)
lattice=${letter_fname}_${constraint}.fst # will be created
refiner=refiner.fst
model_outcome=predicted.txt

## create a symbol system
#python src/create_phn_syms.py $dev_fname $letter_fname $isyms


## create inflection convertion lattice
#python src/inflection_phn_lattice.py $dev_fname $isyms $constraint $lattice $refiner

## query the lattice
python src/query_phn.py $lattice $refiner $isyms $query_file $model_outcome
