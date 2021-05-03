import openfst_python as fst
import sys

def create_priors(priors, isym, osym, code):
    """This function creates a linear FST 
    and adds a <sigma> (joker) symbol at the
    end as a place holder"""

    priors = priors.split(";")

    # init a trasducer
    f = fst.Fst()
    f.set_input_symbols(isym)
    f.set_output_symbols(osym)
    s0 = f.add_state()
    f.set_start(s0)
    old = s0
    sig = "<sigma>"
    
    # adding priors
    for j in range(len(priors)):
        new = f.add_state()
        f.add_arc(old, fst.Arc(code[priors[j]], code[priors[j]], fst.Weight(f.weight_type(), 1.0), new))
        old = new
    new = f.add_state()

    # adding <sigma>
    f.add_arc(old, fst.Arc(code[sig], code[sig], fst.Weight(f.weight_type(), 1.0), new))
    f.add_arc(new, fst.Arc(code[sig], code[sig], fst.Weight(f.weight_type(), 1.0), new))
    return f,new

def build_lm(dev_fname, isyms_fname, constraints, lattice_output, refiner_fname):
    """
    Make a lattice that maps
    lemmas and constraints (or priors) to 
    an inflected version
    """
    # rewrite constraints
    constraints = constraints.replace("_",";")
    
    # read isyms
    input_syms = fst.SymbolTable.read_text(isyms_fname)
    s_fin = '</s>'
    code = {}
    for ltr, c in input_syms:
        code[c]=ltr

    # init the lattice
    f_big = fst.Fst()
    f_big.set_input_symbols(input_syms)
    f_big.set_output_symbols(input_syms)

    for line in open(dev_fname,'r').readlines():
        cns, lemma, inflection = line.split()[-3:]
        if cns == constraints:
            print(cns, lemma, inflection)
            # find idx that the strings diverge
            idx = 0
            for i, (lm, flc) in enumerate(zip(lemma, inflection)):
                if lm !=flc:
                    idx = i
                    break
            f, old= create_priors(cns, input_syms, input_syms, code)
            keep = old
            for j in range(idx,len(lemma)):            
                new = f.add_state()
                f.add_arc(old, fst.Arc(code[lemma[j]], code[lemma[j]], fst.Weight(f.weight_type(), 1.0), new))
                old = new
            new = f.add_state()
            # the residual of the lemma is mapped to the inflection residual (indirectly)
            sym = lemma[idx:]+"_"+inflection[idx:]
            print(lemma, inflection, sym)
            f.add_arc(old, fst.Arc(code[sym], code[s_fin], fst.Weight(f.weight_type(), 1.0), new))
            #f.add_arc(old, fst.Arc(code[inflection[idx:]], code[s_fin], fst.Weight(f.weight_type(), 1.0), new))
            #f.add_arc(old, fst.Arc(code[s_fin], code[inflection[idx:]], fst.Weight(f.weight_type(), 1.0), new))
            f.set_final(new)
            f_big.union(f)
            f_big = fst.determinize(f_big.rmepsilon())

    # add <sigma> state in the <sigma place holder>
    for c, ltr in code.items():
        if int(ltr)>1 and int(ltr)<36: # (hard coded) symbols of Runssian + 2 more
            f_big.add_arc(keep, fst.Arc(code[c], code[c], fst.Weight(f_big.weight_type(), 1.0), keep))

    f_big.invert()
    # save lattice
    f_big.write(lattice_output)

def build_refiner(isyms_fname, refiner_fname):
    """build refiner
    this fst would help extract the 
    last two states (one last arc)
    of the machine
    """

    # read isyms
    input_syms = fst.SymbolTable.read_text(isyms_fname)
    code = {}
    for ltr, c in input_syms:
        code[c]=ltr

    # build refiner
    refiner = fst.Fst()
    refiner.set_input_symbols(input_syms)
    refiner.set_output_symbols(input_syms)
    s0 = refiner.add_state()
    s1 = refiner.add_state()
    for c, ltr in code.items():
        if ltr == 0:
            continue
        if ltr < 100:
            refiner.add_arc(s0, fst.Arc(code[c], code["<epsilon>"], fst.Weight(refiner.weight_type(), 1.0), s0))
        refiner.add_arc(s0, fst.Arc(code[c], code[c], fst.Weight(refiner.weight_type(), 1.0), s1))
    refiner.set_start(s0)
    refiner.set_final(s1)

    # save refiner
    refiner.write(refiner_fname)

if __name__ == "__main__":
    build_lm(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    build_refiner(sys.argv[2], sys.argv[5])
