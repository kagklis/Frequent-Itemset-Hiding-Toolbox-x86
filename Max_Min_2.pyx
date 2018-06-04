#-------------------------------------------------------------------------------
# Name:        Max_Min_2.pyx
# Purpose:     Implements the FIH algorithm found in "A maxmin approach for hiding frequent itemsets" by Moustakides et al.
# Author:      Vasileios Kagklis
# Created:     17/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from time import clock
from fim import apriori
import myiolib
from SetOp import *
from libc.math cimport pow, ceil

cdef initMax_Min_2():
    pass

cdef double my_round(double x, unsigned int digits):
    cdef double fac = pow(10, digits)
    return round(x*fac)/fac;

cdef class viClass:
    cdef public char* item
    cdef public frozenset itemset

   
cdef viClass vi(char* item, frozenset itemset):
    cdef viClass instance = viClass.__new__(viClass)
    instance.item = item
    instance.itemset = itemset
    return instance


cdef tuple max_min_2_2(list m_m_s, frozenset chosen, list tid):
    cdef int i, j
    cdef int k1, k2
    cdef set tent_vict_item = set()
    cdef set Li = set()
    cdef set Lu = set()
    cdef set L = set()
    cdef list v_i_l =  []
    cdef viClass x
    
    for x in m_m_s:
        tent_vict_item.add(x.item)
        v_i_l.append(x.itemset)

    ######----FIRST CASE SCENARIO-----######
    if len(tent_vict_item)==1:
        Vic_it = frozenset([list(tent_vict_item)[-1]])
        for i in xrange(len(tid)):
            if chosen <= tid[i]:
                Li.add(i)
            for itemset in v_i_l:
                if itemset <= tid[i]:
                    Lu.add(i)
        
        L = Li-Lu
        
        if not(L):
            return((Vic_it, Li,))
        else:
            return((Vic_it, L,))
    
    ######----SECOND CASE SCENARIO-----######
    else:
        for i in xrange(len(tid)):
            if chosen <= tid[i]:
                Li.add(i)

        for itemset in v_i_l:
            Lu = set()
            for j in xrange(len(tid)):
                if itemset <= tid[j]:
                    Lu.add(j)
            L = Li-Lu
            
            if L:
                return((frozenset([x.item]), L,))

        #Second Case does not apply
        Lu1 = set()
        Lu2 = set()
        for i in xrange(len(v_i_l)):
            for j in xrange(i+1, len(v_i_l)):
                if v_i_l[i] != v_i_l[j]:
                    for t,line in enumerate(tid):
                        if set(v_i_l[i]).issubset(line):
                            Lu1.add(t)
                        if set(v_i_l[j]).issubset(line):
                            Lu2.add(t)
                    L=(Lu1&Li)-(Lu2&Li)
                    if L!=set():
                        return((frozenset([x.item]),L,))
                    else:
                        return((frozenset([x.item]),Lu1&Li,))
                else:
                    return((frozenset([x.item]), Li,))

cdef frozenset remove_victim(char* vict, frozenset ch, list tid):
    cdef int i
    cdef frozenset temp
    for i in xrange(len(tid)):
        if ch <= tid[i]:
            temp = frozenset(tid[i])
            tid[i].discard(vict)
            return(temp)


cdef list max_min_2_1(frozenset chosen, list Rev_pos_bord, dict freq_frozen):

    cdef double min_value
    cdef double max_value = 0.0
    
    cdef dict affinity = {}
    cdef list max_min_set = []
    
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
        return([list(chosen)[0]])

    max_value = my_round(max_value,10)
    
    for item in affinity:
        for itemset in affinity[item]:
            if my_round(freq_frozen[itemset],10) == max_value:
                max_min_set.append(vi(item,itemset))
                
    return(max_min_set)

###################################################

cdef list convert2frozen_m(list f):
    cdef list result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)

###################################################

def Max_Min_2_main(fname1, fname2, fname3, double sup, mod_name):

    cdef int change_raw_data = 0
    cdef int lines
    cdef int abs_supp

    cdef tid, Rev_Fd, Rev_pos_bord
    cdef set SS
    cdef dict F = {}
    cdef dict S = {}

    cdef frozenset tid_vict, chosen, itemset

    victim = None
    
    lines, tid = myiolib.readDataset(fname3)
    F = myiolib.readLargeData(fname1)
    abs_supp = int(ceil(sup*lines-0.5))
    s_min = minSet(myiolib.readSensitiveSet(fname2))
    for itemset in s_min:
        if itemset in F:
            S[itemset] =  int(ceil(F[itemset]*lines-0.5))

    start_time = clock()
    SS = supersets(s_min, F)
    Rev_Fd = list(set(F)-SS)

    # Calculate the revised positive border
    Rev_pos_bord = convert2frozen_m(apriori(Rev_Fd, target = 'm', supp = float(0.0)))
    rev_t = clock()-start_time
    
    start_time = clock()
    while s_min:
        chosen = min(S, key=lambda x:(S[x],-len(x), list(x)))
        while S[chosen]  >= abs_supp:

            max_min_set = max_min_2_1(chosen, Rev_pos_bord, F)
            tid_vict = frozenset()
            victim, L_of_vict = max_min_2_2(max_min_set, chosen, tid)
            ii = min(L_of_vict)
            tid_vict = frozenset(tid[ii])
            tid[ii].discard(list(victim)[0])
           
            change_raw_data += 1
           
            if victim:
                for itemset in S:
                    if (itemset <= tid_vict) and (victim <= itemset):
                        S[itemset] = S[itemset]-1
                        F[itemset] = F[itemset]-(1.0/lines)

                for itemset in Rev_pos_bord:
                    if (itemset <= tid_vict) and (victim <= itemset):
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
