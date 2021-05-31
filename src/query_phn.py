import openfst_python as fst
import sys
import math
import pdb

class analyzer:
    def __init__(self, lattice, refiner, isyms_fname):

        self.lattice = fst.Fst.read(lattice)
        self.refiner = fst.Fst.read(refiner)
        self.input_syms = fst.SymbolTable.read_text(isyms_fname)
        self.code = {}
        for ltr, c in self.input_syms:
            self.code[c]=ltr

    def make_query(self, cns, lemma):

        cns = cns.split(";")
        q = cns + ["<sigma>"] + lemma + ["</s>"]
        f = fst.Fst("log")
        f.set_input_symbols(self.input_syms)
        f.set_output_symbols(self.input_syms)
        s0 = f.add_state()
        f.set_start(s0)
        old = s0
        for j in range(len(q)):
            new = f.add_state()
            f.add_arc(old, fst.Arc(self.code[q[j]], self.code[q[j]], fst.Weight(f.weight_type(), 2.0), new))
            old = new
        f.set_final(old)
        return f

    def generate_inflections(self,q, lemma):
        
        paths = fst.compose(q, self.lattice)
        two_state = fst.compose(paths, self.refiner)
        output = two_state.project(project_output=True)
        output.rmepsilon()
        output = fst.determinize(output)
        output.minimize()
        # read fst out
        dist = []
        labels = []
        state = output.start()
        for arc in output.arcs(state):
            label = self.input_syms.find(arc.ilabel)
            pr = float(arc.weight)
            dist.append(math.e**(-pr))
            labels.append(label)
        sum_value = sum(dist)
        norm_dist = [prob/sum_value for prob in dist]
        relabels = []
        inf_d = {}
        #for label in labels:
        for label, dist in zip(labels, norm_dist):
            delete, insert = label.split("_")
            l = len(delete)
            label = "".join(lemma[:-l])+insert
            relabels.append(label)
            inf_d[label]=dist
        return inf_d
        #return str(sorted(zip(relabels, norm_dist), key=lambda x:x[1], reverse=True))

if __name__ == "__main__":
    analyser = analyzer(sys.argv[1], sys.argv[2], sys.argv[3])
    q_file = sys.argv[4]
    outfile = sys.argv[5]
    outf = open(outfile,"w")
    for line in open(q_file,"r").readlines():
        line = line.strip()
        lemma, cns, test_inf = line.split("\t")
        lemma = lemma.split()
        test_inf = test_inf.split()
        test_inf = "".join(test_inf)
        query = analyser.make_query(cns,lemma)
        print(query)
        try:
            inflections = analyser.generate_inflections(query, lemma)
            print(test_inf,inflections)
            if test_inf in inflections:
                outf.write("".join(lemma)+"\t"+test_inf+"\t"+cns.replace(";", "")+"\t"+str(inflections[test_inf])+"\n")
            #outf.write(cns+" "+"".join(lemma)+" "+inflections+"\n")
            else:
                outf.write("".join(lemma)+"\t"+test_inf+"\t"+cns.replace(";", "")+"\t"+"0\n")
        except:
            outf.write("".join(lemma)+"\t"+test_inf+"\t"+cns.replace(";", "")+"\t"+"0\n")
            #outf.write(cns+" "+"".join(lemma)+" "+"\n")
    outf.close()
