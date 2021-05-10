import sys

# get fname argumment of dev/train/test

def create_symbol_sets(dev_fname, letters_fname, isyms_fname):

    # make dict
    symbol_dict = {}

    # add special symbols
    symbol_dict['<epsilon>']=0
    symbol_dict['<sigma>']=1
    symbol_dict['</s>']=2
    
    i = 3
    for m, k in enumerate(open(letters_fname,"r").readlines()):
        k = k.strip()
        symbol_dict[k]=i+m

    # add prior condition
    symbol_dict['V']=80
    symbol_dict['FUT']=81
    symbol_dict['PST']=82
    symbol_dict['PRS']=83
    symbol_dict['IND']=84
    symbol_dict['1']=85
    symbol_dict['2']=86
    symbol_dict['3']=87
    symbol_dict['SG']=88
    symbol_dict['PL']=89
    symbol_dict['SBJV']=90
    symbol_dict['IMP']=91
    symbol_dict['NFIN']=92
    symbol_dict['V.PTCP']=93

    # add all possible inflections (inflection is considered here as the letter sequence that diverges from the lemma)
    i=100
    for line in open(dev_fname,'r').readlines(): # all possilbe inflections are added, regardless of the prior (applying the prior an make for a more effecifent computation)
        line = line.strip()
        lemma, inflection, constraints = line.split("\t")[:-2]

        # comparing strings
        idx = 0
        lemma = lemma.split()
        inflection = inflection.split()
        for j, (lm, flc) in enumerate(zip(lemma, inflection)):
            if lm !=flc:
                idx = j
                break

        sym = "".join(lemma[idx:])+"_"+"".join(inflection[idx:])
        if sym not in symbol_dict:
            symbol_dict[sym]= i
            i+=1
    
    # create isyms file
    f = open(isyms_fname, "w")
    for k, v in symbol_dict.items():
        f.write(k+"\t"+str(v)+"\n")
    f.close()

if __name__ == "__main__":
    create_symbol_sets(sys.argv[1], sys.argv[2], sys.argv[3])
