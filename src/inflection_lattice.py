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

def create_lattice(dev_fname, isyms_fname, constraints, lattice_output):
    """
    Make a lattice that maps
    lemmas and constraints (or priors) to 
    an inflected version
    """
    
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
        _, _, cns, lemma, inflection = line.split("\t")
        if cns == constraints:
            # find idx that the strings diverge
            idx = 0
            for i, (lm, flc) in enumerate(zip(lemma, inflection)):
                if lm !=flc:
                    idx = i
                    break
            f, old= create_priors(cns, input_syms, input_syms, code)
            f.set_input_symbols(input_syms)
            f.set_output_symbols(input_syms)
            old = s0
            keep = old
            for j in range(idx,len(lemma)):            
                new = f.add_state()
                f.add_arc(old, fst.Arc(code[lemma[j]], code[lemma[j]], fst.Weight(f.weight_type(), 1.0), new))
                old = new
            new = f.add_state()
            # the residual of the lemma is mapped to the inflection residual (indirectly)
            f.add_arc(old, fst.Arc(code[s_fin], code[inflection[idx:]], fst.Weight(f.weight_type(), 1.0), new))
            f.set_final(new)
            f_big.union(f)
            f_big = fst.determinize(f_big.rmepsilon())

    # add <sigma> state in the <sigma place holder>
    for c, ltr in code.items():
        if int(ltr)>1 and int(ltr)<36: # (hard coded) symbols of Runssian + 2 more
            f_big.add_arc(keep, fst.Arc(code[c], code[c], fst.Weight(f.weight_type(), 1.0), keep)

    # save lattice
    f_big.write(lattice_output)

if __name__ == "__main__":
    create_lattices(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])