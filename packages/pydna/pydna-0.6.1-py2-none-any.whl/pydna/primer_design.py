#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 by Björn Johansson.  All rights reserved.
# This code is part of the Python-dna distribution and governed by its
# license.  Please see the LICENSE.txt file that should have been included
# as part of this package.

'''
This module contain functions for primer design.

'''
from operator import itemgetter
from Bio.SeqUtils import GC
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from pydna.amplify import Anneal, tmbresluc, basictm, tmstaluc98, tmbreslauer86


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
                    
    '''This function can design primers for PCR amplification of a given sequence. 
    This function accepts a Dseqrecord object containing the template sequence and 
    returns a tuple cntaining two ::mod`Bio.SeqRecord.SeqRecord` objects describing 
    the primers.
    
    Primer tails can optionally be given in the form of strings.
    
    An predesigned primer can be given, either the forward or reverse primers. In this 
    case this function tries to design a primer with a Tm to match the given primer. 
        

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

    primerc : float, optional 
        Concentration of each primer in nM, set to 1000.0 nM by default 
    
    saltc  : float, optional
        Salt concentration (monovalet cations) :mod:`tmbresluc` set to 50.0 mM by default

    formula : function
        formula used for tm calculation
        this is the name of a function.
        built in options are:
        
        1. :func:`pydna.amplify.tmbresluc` (default)
        2. :func:`pydna.amplify.basictm`
        3. :func:`pydna.amplify.tmstaluc98` 
        4. :func:`pydna.amplify.tmbreslauer86`
        
        These functions are imported from the :mod:`pydna.amplify` module, but can be 
        substituted for some other custom made function.

    Returns
    -------
    fp, rp : tuple
        fp is a :mod:Bio.SeqRecord object describing the forward primer
        rp is a :mod:Bio.SeqRecord object describing the reverse primer

        
    
    Examples
    --------
    
    >>> import pydna
    >>> t=pydna.Dseqrecord("atgactgctaacccttccttggtgttgaacaagatcgacgacatttcgttcgaaacttacgatg")
    >>> t
    Dseqrecord(-64)
    >>> pf,pr = pydna.cloning_primers(t)
    >>> pf
    SeqRecord(seq=Seq('atgactgctaacccttc', Alphabet()), id='pfw64', name='pfw64', description='pfw64', dbxrefs=[])
    >>> pr
    SeqRecord(seq=Seq('catcgtaagtttcgaac', Alphabet()), id='prv64', name='prv64', description='prv64', dbxrefs=[])
    >>> pcr_prod = pydna.pcr(pf, pr, t)
    >>> pcr_prod
    Amplicon(64)
    >>>               
    >>> print pcr_prod.figure()
    5atgactgctaacccttc...gttcgaaacttacgatg3
                         ||||||||||||||||| tm 42.4 (dbd) 52.9
                        3caagctttgaatgctac5
    5atgactgctaacccttc3
     ||||||||||||||||| tm 44.5 (dbd) 54.0
    3tactgacgattgggaag...caagctttgaatgctac5
    >>> pf,pr = pydna.cloning_primers(t, fp_tail="GGATCC", rp_tail="GAATTC")
    >>> pf
    SeqRecord(seq=Seq('GGATCCatgactgctaacccttc', Alphabet()), id='pfw64', name='pfw64', description='pfw64', dbxrefs=[])
    >>> pr
    SeqRecord(seq=Seq('GAATTCcatcgtaagtttcgaac', Alphabet()), id='prv64', name='prv64', description='prv64', dbxrefs=[])
    >>> pcr_prod = pydna.pcr(pf, pr, t)
    >>> print pcr_prod.figure()
          5atgactgctaacccttc...gttcgaaacttacgatg3
                               ||||||||||||||||| tm 42.4 (dbd) 52.9
                              3caagctttgaatgctacCTTAAG5
    5GGATCCatgactgctaacccttc3
           ||||||||||||||||| tm 44.5 (dbd) 54.0
          3tactgacgattgggaag...caagctttgaatgctac5
    >>> print pcr_prod.seq
    GGATCCatgactgctaacccttccttggtgttgaacaagatcgacgacatttcgttcgaaacttacgatgGAATTC
    >>>
    >>> from Bio.Seq import Seq
    >>> from Bio.SeqRecord import SeqRecord
    >>> pf = SeqRecord(Seq("atgactgctaacccttccttggtgttg"))
    >>> pf,pr = pydna.cloning_primers(t, fp = pf, fp_tail="GGATCC", rp_tail="GAATTC")
    >>> pf
    SeqRecord(seq=Seq('GGATCCatgactgctaacccttccttggtgttg', Alphabet()), id='pfw64', name='pfw64', description='pfw64', dbxrefs=[])
    >>> pr
    SeqRecord(seq=Seq('GAATTCcatcgtaagtttcgaacgaaatgtcgtc', Alphabet()), id='prv64', name='prv64', description='prv64', dbxrefs=[])
    >>> ampl = pydna.pcr(pf,pr,t)
    >>> print ampl.figure()
          5atgactgctaacccttccttggtgttg...gacgacatttcgttcgaaacttacgatg3
                                         |||||||||||||||||||||||||||| tm 57.5 (dbd) 72.2
                                        3ctgctgtaaagcaagctttgaatgctacCTTAAG5
    5GGATCCatgactgctaacccttccttggtgttg3
           ||||||||||||||||||||||||||| tm 59.0 (dbd) 72.3
          3tactgacgattgggaaggaaccacaac...ctgctgtaaagcaagctttgaatgctac5
    >>> 


    '''

    if fp and not rp:
        fp = SeqRecord(Seq(fp_tail)) + fp
        p  = Anneal([fp], template).fwd_primers.pop()
        fp = SeqRecord(p.footprint)
        fp_tail = SeqRecord(p.tail)
        rp = SeqRecord(Seq(str(template[-(maxlength*3-len(rp_tail)):].reverse_complement().seq)))
        target_tm = formula(fp.seq.tostring().upper(), primerc=primerc, saltc=saltc)
    elif not fp and rp:
        rp = SeqRecord(Seq(rp_tail)) + rp
        p =  Anneal([rp], template).rev_primers.pop()
        rp = SeqRecord(p.footprint)
        rp_tail = SeqRecord(p.tail)
        fp = SeqRecord(Seq(str(template[:maxlength*3-len(fp_tail)].seq)))
        target_tm = formula(rp.seq.tostring().upper(), primerc=primerc, saltc=saltc)
    elif not fp and not rp:        
        fp = SeqRecord(Seq(str(template[:maxlength].seq)))
        rp = SeqRecord(Seq(str(template[-maxlength:].reverse_complement().seq)))     
    else:
        raise Exception("Specify one or none of the primers, not both.")

    lowtm, hightm = sorted( [( formula(fp.seq.tostring(), primerc, saltc), fp, "f" ),
                             ( formula(rp.seq.tostring(), primerc, saltc), rp, "r" ) ] ) 
    
    while lowtm[0] > target_tm and len(lowtm[1])>minlength:
        shorter = lowtm[1][:-1]
        tm      = formula(shorter.seq.tostring().upper(), primerc=primerc, saltc=saltc)
        lowtm   = (tm, shorter, lowtm[2])
        
    while hightm[0] > lowtm[0] + 2.0 and len(hightm[1])>minlength:
        shorter = hightm[1][:-1]
        tm = formula(shorter.seq.tostring().upper(), primerc = primerc, saltc = saltc)
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
                     minlength  = 16,
                     maxlength  = 29,
                     tot_length = 40,
                     target_tm  = 55.0, 
                     primerc    = 1000.0,
                     saltc      = 50.0,
                     formula    = tmbresluc ):
    '''This function return primer pairs that are useful for fusion of DNA sequences given in template.
    Given two sequences that we wish to fuse (a and b) to form fragment c.  

    ::
    
       _________ a _________           __________ b ________
      /                     \\         /                     \\
      agcctatcatcttggtctctgca   <-->  TTTATATCGCATGACTCTTCTTT
      |||||||||||||||||||||||         |||||||||||||||||||||||
      tcggatagtagaaccagagacgt   <-->  AAATATAGCGTACTGAGAAGAAA
     
     
           agcctatcatcttggtctctgcaTTTATATCGCATGACTCTTCTTT
           ||||||||||||||||||||||||||||||||||||||||||||||
           tcggatagtagaaccagagacgtAAATATAGCGTACTGAGAAGAAA  
           \\___________________ c ______________________/
                      
    
    We can design tailed primers to fuse a and b by fusion PCR, Gibson assembly or 
    in-vivo homologous recombination. The basic requirements for the primers for 
    the three techniques are the same.
    
    
    Design tailed primers incorporating a part of the next or previous fragment to be assembled.  
    
    ::
    

      agcctatcatcttggtctctgca     
      |||||||||||||||||||||||     
                      gagacgtAAATATA
                                  
      |||||||||||||||||||||||     
      tcggatagtagaaccagagacgt
      
           
                             TTTATATCGCATGACTCTTCTTT
                             |||||||||||||||||||||||
                             
                      ctctgcaTTTATAT
                             |||||||||||||||||||||||
                             AAATATAGCGTACTGAGAAGAAA
     
    PCR products with flanking sequences are formed in the PCR process.
    
    ::
     
      agcctatcatcttggtctctgcaTTTATAT     
      ||||||||||||||||||||||||||||||     
      tcggatagtagaaccagagacgtAAATATA
                      \\____________/
                      
                         identical 
                         sequences
                       ____________        
                      /            \\        
                      ctctgcaTTTATATCGCATGACTCTTCTTT
                      ||||||||||||||||||||||||||||||
                      gagacgtAAATATAGCGTACTGAGAAGAAA
    
    The fragments can be fused by any of the techniques mentioned earlier.
       
    ::
     
      agcctatcatcttggtctctgcaTTTATATCGCATGACTCTTCTTT
      ||||||||||||||||||||||||||||||||||||||||||||||
      tcggatagtagaaccagagacgtAAATATAGCGTACTGAGAAGAAA  

    
                        

    Parameters
    ----------

    templates : list of Dseqrecord
        list Dseqrecord object for which fusion primers should be constructed.
        
    minlength : int, optional
        Minimum length of the annealing part of the primer.
    
    maxlength : int, optional
        Maximum length (including tail) for designed primers.
        
    tot_length : int, optional
        Maximum total length of a the primers
        
    target_tm : float, optional
        target tm for the primers        

    primerc : float, optional 
        Concentration of each primer in nM, set to 1000.0 nM by default 
    
    saltc  : float, optional
        Salt concentration (monovalet cations) :mod:`tmbresluc` set to 50.0 mM by default

    formula : function
        formula used for tm calculation
        this is the name of a function.
        built in options are:
        
        1. :func:`pydna.amplify.tmbresluc` (default)
        2. :func:`pydna.amplify.basictm`
        3. :func:`pydna.amplify.tmstaluc98` 
        4. :func:`pydna.amplify.tmbreslauer86`
        
        These functions are imported from the :mod:`pydna.amplify` module, but can be 
        substituted for some other custom made function.

    Returns
    -------
    primer_pairs : list of tuples of :mod:`Bio.Seqrecord` objects
    
        ::
    
          [(forward_primer_1, reverse_primer_1),
           (forward_primer_2, reverse_primer_2), ...]
        
    
    Examples
    --------
    
    >>> import pydna
    >>> a=pydna.Dseqrecord("atgactgctaacccttccttggtgttgaacaagatcgacgacatttcgttcgaaacttacgatg")
    >>> b=pydna.Dseqrecord("ccaaacccaccaggtaccttatgtaagtacttcaagtcgccagaagacttcttggtcaagttgcc")
    >>> c=pydna.Dseqrecord("tgtactggtgctgaaccttgtatcaagttgggtgttgacgccattgccccaggtggtcgtttcgtt")
    >>> primer_pairs = pydna.assembly_primers([a,b,c])
    >>> p=[]                                      
    >>> for t, (f,r) in zip([a,b,c], primer_pairs): p.append(pydna.pcr(f,r,t))  
    >>> p
    [Amplicon(87), Amplicon(110), Amplicon(90)]
    >>> assemblyobj = pydna.Assembly(p)     
    >>> assemblyobj
    Assembly object:
    Sequences........................: 87, 110, 90
    Sequences with shared homologies.: No analyzed sequences
    Homology limit (bp)..............: 25
    Number of overlaps...............: No overlaps
    Nodes in graph...................: No graph
    Assembly protocol................: No protocol
    Circular products................: No circular products
    Linear products..................: No linear products
    >>>    
    >>> assemblyobj.assemble_gibson_linear()
    '5 linear products were formed with the following sizes (bp): 195, 155, 150, 47, 45'
    >>> assemblyobj.linear_products
    [Dseqrecord(-195), Dseqrecord(-155), Dseqrecord(-150), Dseqrecord(-47), Dseqrecord(-45)]
    >>> assemblyobj.linear_products[0].seguid()
    '1eNv3d/1PqDPP8qJZIVoA45Www8'
    >>> (a+b+c).seguid()
    '1eNv3d/1PqDPP8qJZIVoA45Www8'
    >>> pydna.eq(a+b+c, assemblyobj.linear_products[0])
    True
    >>>
    >>> print assemblyobj.linear_products[0].small_fig()
    87bp_PCR_prod|47
                  \\/
                  /\\
                  47|110bp_PCR_prod|45
                                    \\/
                                    /\\
                                    45|90bp_PCR_prod
    >>>                                

    '''


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
    import doctest
    doctest.testmod()

    
    
    
