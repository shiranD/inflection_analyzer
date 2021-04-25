import sys

# get fname argumment of dev/train/test

def create_symbol_sets(dev_fname, letters_fname, isyms_fname):

    # make dict
    symbol_dict = {}

    # add special symbols
    symbol_dict['<epsilon>']=0
    symbol_dict['<sigma>']=1
    symbol_dict['</s>']=2
    
    i = 2
    for i, k in enumerate(open(letters_fname,"r").readlines()):
        symbol_dict[k]=i+1
    
    # add prior condition
    symbol_dict['V']=40
    symbol_dict['FUT']=41
    symbol_dict['1']=42
    symbol_dict['SG']=43
    
    # add all possible inflections (inflection is considered here as the letter sequence that diverges from the lemma)
    i=100
    for line in open(dev_fname,'r').readlines(): # all possilbe inflections are added, regardless of the prior (applying the prior an make for a more effecifent computation)
        constraints, lemma, inflection = line.split()
        # comparing strings
        idx = 0
        for j, (lm, flc) in enumerate(zip(lemma, inflection)):
            if lm !=flc:
                idx = j
                break
        if inflection[idx:] not in symbol_dict:
            symbol_dict[inflection[idx:]]= i
            i+=1
    
    # create isyms file
    f = open(isyms_fname, "w")
    for k, v in symbol_dict.items():
        f.write(k+"\t"+str(v)+"\n")
    f.close()

if __name__ == "__main__":
    create_symbol_sets(sys.argv[1], sys.argv[2], sys.argv[3])
