'''
The MIT License (MIT)

Copyright (c) 2016 kagklis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#-------------------------------------------------------------------------------
# Name:        WBA.pyx
# Purpose:     Implements the FIH algorithm found in "Hiding sensitive frequent itemsets by a border-based approach" by Sun and Yu.
# Author:      Vasileios Kagklis
# Created:     18/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from time import clock
from fim import apriori
import myiolib
from SetOp import *
from math import ceil

cdef initWBA():
    pass

cdef class s_setClass:
   cdef public list i_set
   cdef public int len_i_set
   cdef public double sup

   
cdef s_setClass s_set(list i_set, int len_i_set, double sup):
   cdef s_setClass instance = s_setClass.__new__(s_setClass)
   instance.i_set = i_set
   instance.len_i_set = len_i_set
   instance.sup = sup
   return instance

###################################################

def get_indices(list lst, item):
    cdef int i
    for i in range((len(lst)-1),-1,-1):
        if lst[i] == item:
            yield i

###################################################

cdef list convert2frozen_m(list f):
    cdef list result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)

###################################################

cdef float w(int supB, int supBa, int sigma, int el):
    if supBa >= sigma + 1:
        return (float(supB - supBa + 1)/float(supB - sigma))
    elif 0 <= supBa and supBa <= sigma:
        return float(el + sigma - supBa)
    
###################################################

def WBA_main(fname1, fname2, fname3, double sup, mod_name):

    cdef int change_raw_data = 0
    cdef int lines, el, abs_supp, Q=0

    cdef tid, Rev_Fd, Rev_pos_bord
    cdef set SS
    cdef dict F = {}
    cdef dict S = {}
    cdef dict C = {}
    cdef dict B

    cdef frozenset tid_vict, chosen
    
    lines, TID = myiolib.readDataset(fname3)
    F = myiolib.readLargeData(fname1)
    
    s_min = minSet(myiolib.readSensitiveSet(fname2))

    for itemset in F:
        F[itemset] = ceil(F[itemset]*lines - 0.5)
        
    for itemset in s_min:
        if itemset in F:
            S[itemset] = F[itemset]

    start_time = clock()
    SS = supersets(s_min, F)
    Rev_Fd = list(set(F) -SS)
    # Calculate the revised positive border
    Rev_pos_bord = convert2frozen_m(apriori(Rev_Fd, target = 'm', supp = float(0.0)))
    rev_t = clock()-start_time

    abs_supp = ceil(sup*lines - 0.5)
    
    start_time = clock()

   
    el = 2*len(Rev_pos_bord)
    B = {}
    for I_S in Rev_pos_bord:
        if I_S not in B:
            B[I_S] = {"w":0, "d":0}
            B[I_S]["d"] = 0
            B[I_S]["w"] = w(F[I_S], F[I_S]-B[I_S]["d"], abs_supp, el)
            
    for itemset in sorted(S, key=lambda x:(-len(x), S[x])):
        
        C = {}
        for i in xrange(len(TID)):
            if itemset <= TID[i]:
                for item in itemset:
                    C[(i,item)] = 0

        while S[itemset] >= abs_supp:

            for T, u in C:
                C[(T,u)] = 0
                for Bj in B:
                    if (Bj & itemset) and (Bj <= TID[T]) and (u in Bj):
                        C[(T,u)] += B[Bj]["w"]
        
            rem = min(C, key=lambda x: C[x])
            Q = len(TID[rem[0]])
            
            for item in [item for item in C if item[0] == rem[0]]:
                del C[item]

            for I_S in B:
                if (I_S & itemset) and (I_S <= TID[rem[0]]) and (rem[1] in I_S):
                    B[I_S]["d"] += 1
                    B[I_S]["w"] = w(F[I_S], F[I_S]-B[I_S]["d"], abs_supp, el)

            for it in S:
                if it <= TID[rem[0]] and rem[1] in it:
                    S[it] -= 1
            
            TID[rem[0]].discard(rem[1])
            if not(Q == len(TID[rem[0]])):
                change_raw_data += 1
            
        
    exec_time = clock()-start_time
    
    ######----create out files-----######
    out_file = open(mod_name+'_results.txt', 'w')
    for i in xrange(lines):
        k = ' '.join(sorted(TID[i]))
        print(k, file = out_file)
    
    
    out_file.close()
    TID = None
    F = None
    Rev_Fd = None
    B = None
     
    return(rev_t,change_raw_data,exec_time)
