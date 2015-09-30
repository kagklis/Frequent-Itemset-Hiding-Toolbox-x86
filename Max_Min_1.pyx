#-------------------------------------------------------------------------------
# Name:        Max_Min_1.pyx
# Purpose:     Implements the FIH algorithm found in "A maxmin approach for hiding frequent itemsets" by Moustakides et al.
# Author:      Vasileios Kagklis
# Created:     16/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from time import clock
from fim import apriori
import myiolib
from SetOp import *
from libc.math cimport pow, ceil

cdef initMax_Min_1():
    pass

cdef double my_round(double x, unsigned int digits):
    cdef double fac = pow(10, digits)
    return round(x*fac)/fac;

cdef max_min(list chosen, list Rev_pos_bord, dict freq_frozen):

    cdef double max_value = 0.0
    cdef double min_value
    
    cdef dict affinity = {}
    
    for item in chosen:
        min_value = my_round(min([freq_frozen[itemset] for itemset in Rev_pos_bord if (item in itemset)]+[2]),10)
        if min_value < 1.5:
            for itemset in Rev_pos_bord:
                if (item in itemset) and my_round(freq_frozen[itemset],10) == min_value:
                    if item not in affinity:
                        affinity[item] = []
                    affinity[item].append(itemset)
                    if freq_frozen[itemset] > max_value:
                        max_value = freq_frozen[itemset]
                    
    if not(affinity):
        return(list(chosen)[0])
   
    victim = None
    max_value = my_round(max_value,10)
    for item in affinity:
        for itemset in affinity[item]:
            if my_round(freq_frozen[itemset],10) == max_value:
                victim = item
                break
        if victim:
            break
    
    return(victim)

###############################################

cdef frozenset remove_victim(char* vict, frozenset ch, list tid):
    cdef int i
    cdef frozenset temp
    for i in xrange(len(tid)):
        if ch <= tid[i]:
            temp = frozenset(tid[i])
            tid[i].discard(vict)
            return(temp)

###################################################

cdef list convert2frozen_m(list f):
    cdef list result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)

###############################################

def Max_Min_1_main(fname1, fname2, fname3, double sup, mod_name):

    cdef int change_raw_data = 0
    cdef int lines
    cdef int abs_supp
    cdef tid, Rev_Fd, Rev_pos_bord
    cdef set SS
    cdef dict F = {}
    cdef dict S = {}

    cdef frozenset tid_vict, chosen
    
    lines, tid = myiolib.readDataset(fname3)
    F = myiolib.readLargeData(fname1)
    abs_supp = int(ceil(sup*lines-0.5))
    s_min = minSet(myiolib.readSensitiveSet(fname2))
    for itemset in s_min:
        if itemset in F:
            S[itemset] =  int(ceil(F[itemset]*lines-0.5))


    start_time = clock()
    SS = supersets(s_min, F.keys())
    Rev_Fd = list(set(F) - SS)
    # Calculate the revised positive border
    Rev_pos_bord = convert2frozen_m(apriori(Rev_Fd, target = 'm', supp = float(0.0)))
    rev_t = clock()-start_time

    start_time = clock()
    
    while s_min:
        chosen = min(S, key=lambda x:(S[x],-len(x), list(x)))
        while S[chosen] >= abs_supp:
            victim = max_min(list(chosen), Rev_pos_bord, F)
            if victim:
                tid_vict = remove_victim(victim, chosen, tid)
                if tid_vict:
                    change_raw_data = change_raw_data+1

                for itemset in S:
                    if (itemset <= tid_vict) and (victim in itemset):
                        S[itemset] = S[itemset]-1
                        F[itemset] = F[itemset]-(1.0/lines)

                for itemset in Rev_pos_bord:
                    if (itemset <= tid_vict) and (victim in itemset):
                        F[itemset] = F[itemset]-(1.0/lines)

        s_min -= set([chosen])
        del S[chosen]

    
    exec_time = clock()-start_time
    
    ######----create out files-----######
    out_file = open(mod_name+'_results.txt', 'w')
    for i in xrange(lines):
        k = ' '.join(sorted(tid[i]))
        print(k, file = out_file)
    
    
    out_file.close()
    tid = None
    F = None
    Rev_Fd = None  
    return(rev_t,change_raw_data,exec_time)
