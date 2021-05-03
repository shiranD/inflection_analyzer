#!/bin/bash

set -x
set -e

dev_fname=rus.dev # make sure is correct
letter_fname=russian # make sure is found
isyms=symbols # will be created
query_file=query.txt # an example file is found
constraint=V_FUT_1_SG # set prior condition (V;FUT;1;SG)
lattice=${letter_fname}_${constraint}.fst # will be created
refiner=refiner.fst
model_outcome=predicted.txt

## create a symbol system
python src/create_syms.py $dev_fname $letter_fname $isyms


## create inflection convertion lattice
#python src/inflection_lattice.py $dev_fname $isyms $constraint $lattice $refiner

## query the lattice
#python src/query.py $lattice $refiner $isyms $query_file $model_outcome

