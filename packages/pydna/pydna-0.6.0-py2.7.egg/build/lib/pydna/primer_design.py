#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import itemgetter

from Bio.SeqUtils import GC
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from pydna.amplify import tmbresluc, basictm, tmstaluc98, tmbreslauer86

def cloning_primers(template,
                    minlength=16,
                    maxlength=29,
                    fp=None,
                    rp=None,
                    fp_tail='',
                    rp_tail='',
                    target_tm=55.0, 
                    primerc = 1000.0,
                    saltc=50.0,
                    formula = tmbresluc ):
                    
    '''This function can design one or two primers for PCR amplification of a 
    given sequence. This function accepts a Dseqrecord object containing the 
    template sequence and returns a pydna amplicon object.
    
    The amplicon object contains the primers, a figure describing the how the 
    primers anneal and two suggested PCR programmes.
    

    Parameters
    ----------

    template : Dseqrecord
        a Dseqrecord object.
        
    minlength : int, optional
        Minimum length of the annealing part of the primer
    
    maxlength : int, optional
        Maximum length (including tail) for designed primers.
        
    fp, rp : SeqRecord, optional
        optional Biopython SeqRecord objects containing one primer each.

    fp_tail, rp_tail : string, optional
        optional tails to be added to the forwars or reverse primers
        
    target_tm : float, optional
        target tm for the primers        

    primerc, saltc  : float, optional
        limit is set to 25 by default.

    formula : string
        formula used for tm calculation
        this is the name of a function.
        built in options are:
        
        tmbresluc
        basictm
        tmstaluc98 
        tmbreslauer86
        
    These functions are imported from the pydna.amplify module, but can be 
    substituted for some other custom made function.

    Returns
    -------
    frecs, cp : tuple
        frecs are the same Dseqrecords as given as arguments, but with the
        regions of homology added to the features.

        cp is a list of Dseqrecords representing the circular products
        sorted by length (long -> short).

        '''

    if fp and not rp:
        fp = SeqRecord(Seq(fp_tail)) + fp
        p  = Anneal([fp], template).fwd_primers.pop()
        fp = SeqRecord(p.footprint)
        fp_tail = SeqRecord(p.tail.lower())
        rp = SeqRecord(Seq(str(template[-(maxlength*3-len(rp_tail)):].reverse_complement().seq)))
    elif not fp and rp:
        rp = SeqRecord(Seq(rp_tail)) + rp
        p =  Anneal([rp], template).rev_primers.pop()
        rp = SeqRecord(p.footprint)
        rp_tail = SeqRecord(p.tail.lower())
        fp = SeqRecord(Seq(str(template[:maxlength*3-len(fp_tail)].seq)))
    elif not fp and not rp:
        #fp = SeqRecord(Seq(str(template[:maxlength-len(fp_tail)].seq)))
        #rp = SeqRecord(Seq(str(template[-(maxlength-len(rp_tail)):].reverse_complement().seq)))
        
        fp = SeqRecord(Seq(str(template[:maxlength].seq)))
        rp = SeqRecord(Seq(str(template[-maxlength:].reverse_complement().seq)))     
        
    else:
        raise Exception("not both primers!")

    lowtm, hightm = sorted( [( formula(fp.seq.tostring(), primerc, saltc), fp, "f" ),
                             ( formula(rp.seq.tostring(), primerc, saltc), rp, "r" ) ] ) 
    
    while lowtm[0] > target_tm and len(lowtm[1])>minlength:
        shorter = lowtm[1][:-1]
        tm      = formula(shorter.seq.tostring(), primerc=primerc, saltc=saltc)
        lowtm   = (tm, shorter, lowtm[2])
        
    while hightm[0] > lowtm[0] + 2.0 and len(hightm[1])>minlength:
        shorter = hightm[1][:-1]
        tm = formula(shorter.seq.tostring(), primerc = primerc, saltc = saltc)
        hightm = (tm, shorter, hightm[2])

    fp, rp = sorted((lowtm, hightm), key=itemgetter(2))

    fp = fp_tail + fp[1]    
    rp = rp_tail + rp[1]

    fp.description = "pfw{}".format(len(template))
    rp.description = "prv{}".format(len(template))

    fp.name = fp.description[:15]
    rp.name = rp.description[:15]
    
    fp.id = fp.name
    rp.id = rp.name

    return fp, rp
    
def assembly_primers(templates,
                     minlength = 16,
                     maxlength = 29,
                     tot_length = 40,
                     target_tm = 55.0, 
                     primerc   = 1000.0,
                     saltc     = 50.0,
                     formula = tmbresluc ):

    if not hasattr(templates, '__iter__'):
        raise Exception("argument has to be iterable")  
    
    tails = [("", templates[1].seq[:tot_length].rc().tostring())]
    
    for i in range(1, len(templates)-1):
        tails.append(((templates[i-1].seq.tostring()[-tot_length:],
                       templates[i+1].seq[:tot_length].rc().tostring())))

    tails.append((templates[-2].seq.tostring()[-tot_length:], ""))
    
    primer_pairs = []
  
    for template, (fp_tail, rp_tail) in zip(templates, tails):
        fp, rp = cloning_primers(   template,
                                    minlength  = minlength,
                                    maxlength  = maxlength,
                                    fp_tail    = fp_tail,
                                    rp_tail    = rp_tail,
                                    target_tm  = target_tm, 
                                    primerc    = primerc,
                                    saltc      = saltc,
                                    formula    = formula)
        primer_pairs.append((fp[-tot_length:], rp[-tot_length:]))    
    return primer_pairs

if __name__=="__main__":
    
    from pydna import Dseqrecord
    from pydna_helper import ape

                                                                                                                                                                                                                                                                                                                                                                      
    templates = (Dseqrecord("atgactgctaacccttccttggtgttgaacaagatcgacgacatttcgttcgaaacttacgatgccccagaaatctctgaacctaccgatgtcctcgtccaggtcaagaaaaccggtatctgtggttccgacatccacttctacgcccatggtagaatcggtaacttcgttttgaccaagccaatggtcttgggtcacgaatccgccggtactgttgtccaggttggtaagggtgtcacctctcttaaggttggtgacaacgtcgctatcgaaccaggtattccatccagattctccgacgaatacaagagcggtcactacaacttgtgtcctcacatggccttcgccgctactcctaactccaaggaaggcgaa"),
                 Dseqrecord("ccaaacccaccaggtaccttatgtaagtacttcaagtcgccagaagacttcttggtcaagttgccagaccacgtcagcttggaactcggtgctcttgttgagccattgtctgttggtgtccacgcctccaagttgggttccgttgctttcggcgactacgttgccgtctttggtgctggtcctgttggtcttttggctgctgctgtcgccaagaccttcggtgctaagggtgtcatcgtcgttgacattttcgacaacaagttgaagatggccaaggacattggtgctgctactcacaccttcaactccaagaccggtggttctgaagaattgatcaaggctttcggtggtaacgtgccaaacgtcgttttggaa"),
                 Dseqrecord("tgtactggtgctgaaccttgtatcaagttgggtgttgacgccattgccccaggtggtcgtttcgttcaagttggtaacgctgctggtccagtcagcttcccaatcaccgttttcgccatgaaggaattgactttgttcggttctttcagatacggattcaacgactacaagactgctgttggaatctttgacactaactaccaaaacggtagagaaaatgctccaattgactttgaacaattgatcacccacagatacaagttcaaggacgctattgaagcctacgacttggtcagagccggtaagggtgctgtcaagtgtctcattgacggccctgagtaa"),)

    primer_pairs = assembly_primers(templates)
    
    from pydna import pcr
    
    p=[]

    for t, (f,r) in zip(templates, primer_pairs):       
        p.append(pcr(f,r,t))               
   
    from pydna import Assembly
    
    a=Assembly(p)
    
    print a.analyze_overlaps()
    
    print a.create_graph()
    
    print a.assemble_gibson_linear()
    
    print a.linear_products[0].seq.tostring().lower()=="atgactgctaacccttccttggtgttgaacaagatcgacgacatttcgttcgaaacttacgatgccccagaaatctctgaacctaccgatgtcctcgtccaggtcaagaaaaccggtatctgtggttccgacatccacttctacgcccatggtagaatcggtaacttcgttttgaccaagccaatggtcttgggtcacgaatccgccggtactgttgtccaggttggtaagggtgtcacctctcttaaggttggtgacaacgtcgctatcgaaccaggtattccatccagattctccgacgaatacaagagcggtcactacaacttgtgtcctcacatggccttcgccgctactcctaactccaaggaaggcgaaccaaacccaccaggtaccttatgtaagtacttcaagtcgccagaagacttcttggtcaagttgccagaccacgtcagcttggaactcggtgctcttgttgagccattgtctgttggtgtccacgcctccaagttgggttccgttgctttcggcgactacgttgccgtctttggtgctggtcctgttggtcttttggctgctgctgtcgccaagaccttcggtgctaagggtgtcatcgtcgttgacattttcgacaacaagttgaagatggccaaggacattggtgctgctactcacaccttcaactccaagaccggtggttctgaagaattgatcaaggctttcggtggtaacgtgccaaacgtcgttttggaatgtactggtgctgaaccttgtatcaagttgggtgttgacgccattgccccaggtggtcgtttcgttcaagttggtaacgctgctggtccagtcagcttcccaatcaccgttttcgccatgaaggaattgactttgttcggttctttcagatacggattcaacgactacaagactgctgttggaatctttgacactaactaccaaaacggtagagaaaatgctccaattgactttgaacaattgatcacccacagatacaagttcaaggacgctattgaagcctacgacttggtcagagccggtaagggtgctgtcaagtgtctcattgacggccctgagtaa"
    
    print a.linear_products[0].small_fig()







