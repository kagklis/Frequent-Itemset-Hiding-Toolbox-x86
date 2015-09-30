#-------------------------------------------------------------------------------
# Name:        hcba_ext.pyx
# Purpose:     Implements calculation of coefficients for "An Integer Linear Programming Scheme to Sanitize Sensitive Frequent Itemsets" by Kagklis et al.
# Author:      Vasileios Kagklis
# Created:     20/03/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from random import randrange
from math import log

def calculateCoeffs(list tid, double sup, list sens_ind, s_min, dict freq_frozen, list Rev_Fd_frozen):
    cdef list coeffs
    cdef list rem
    cdef int i
    cdef double summing = 0.0
    cdef double endangered = 0.0
    cdef double pricing = 0.0
    cdef double maxx
    cdef double minn
    cdef dict item_dic
    cdef set temp_set
    cdef set der

    cdef frozenset element
    cdef frozenset itemset
    
    coeffs = [0]*len(tid)
    rem = [frozenset()]*len(sens_ind)
    
    for i in xrange(len(sens_ind)):
        temp_set = set()
        for itemset in s_min:
            if (itemset <= tid[sens_ind[i]]):
                temp_set.add(itemset)
                
        maxx = 0
        minn = 1
        max_el = None
        min_el = None
        summing = 0.0
        endangered = 0.0
        pricing = 0.0
        while len(temp_set) > 0:
            item_dic = {}
            for itemset in temp_set:
                for item in itemset:
                    if item not in item_dic:
                        item_dic[item] = 0
                    item_dic[item] += 1
            max_val = 0
            for item in item_dic:
                if max_val < item_dic[item]:
                    max_val = item_dic[item]
                    element = frozenset([item])

            if item_dic.values().count(max_val) > 1:
                    
                candidates = [frozenset([item]) for item in item_dic if item_dic[item]==max_val]
                c_weights = {}
                for item in candidates:
                    if not(c_weights.has_key(item)):
                        c_weights[item] = 0
                    for itemset in Rev_Fd_frozen:
                        if item <= itemset and itemset <=tid[sens_ind[i]]:
                            c_weights[item] +=1
                    
                
                min_val = min(c_weights.values())
                if(c_weights.values().count(min_val)==1):                    
                    element = min(c_weights, key = c_weights.get)
                else:
                    candidates = [item for item, val in c_weights.items() if val==min_val]
                    max_val = 0
                    for item in candidates:
                        if item in freq_frozen and freq_frozen[item] > max_val:
                            max_val = freq_frozen[item]
                            element = item

                    if freq_frozen.values().count(max_val) > 1:
                        candidates = [candidates[j] for j in xrange(len(candidates)) if freq_frozen[candidates[j]] == max_val]
                        element = candidates[randrange(0, len(candidates))]
            #print("Transaction #",i," eliminate: ", element)
            for itemset in s_min:
                if freq_frozen[itemset] > maxx and element <= itemset:
                    maxx = freq_frozen[itemset]

            if maxx!=1:
                thr = (maxx-sup)
            else:
                thr = maxx/2.0        
                    
            rem[i] = rem[i]|element
            for itemset in Rev_Fd_frozen:
                if itemset not in temp_set and len(tid[sens_ind[i]]) < len(itemset):
                    break
                if (element <= itemset) and (itemset <= tid[sens_ind[i]]) and (itemset not in temp_set):
                    summing += 1.0
                    if freq_frozen[itemset]-thr < sup:
                        endangered += 1
                        pricing = pricing + (1.0-freq_frozen[itemset])

            der = set()
            for itemset in temp_set:
                if (element <= itemset):
                    der.add(itemset)
            temp_set -= der
        #print(summing," ",endangered," ",pricing)
        coeffs[i] = endangered*log(len(tid), 2) + pricing + (1.0*summing)

    return(coeffs, rem)

def get_indices(list lst, int item):
    cdef int i
    for i in range((len(lst)-1),-1,-1):
        if lst[i] == item:
            yield i


def get_1itemsets(list transaction):
    cdef set itemSet = set()
    cdef set record
    for record in transaction:
        for item in record:
            if item != '':
                itemSet.add(item)
    return itemSet
