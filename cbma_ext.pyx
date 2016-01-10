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
# Name:        cbma_ext.pyx
# Purpose:     Implements calculation of coefficients for "Coefficient-Based Exact Approach for Frequent Itemset Hiding" by Leloglu et al.
# Author:      Vasileios Kagklis
# Created:     03/04/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from random import randrange

def calculateCoeffs(list tid, double sup, list sens_ind, set sens_set, list F):
    cdef int N = len(sens_ind)
    cdef list coeffs
    cdef list rem
    cdef set der
    cdef set temp_set

    cdef int summing
    cdef double max_val
    cdef double freq
    
    cdef frozenset element
    cdef frozenset itemset
    
    coeffs = [0]*N
    rem = [frozenset()]*N
    for i in xrange(N):
        temp_set = set()
        for itemset in sens_set:
            if (itemset <= tid[sens_ind[i]]):
                temp_set.add(itemset)
        
        summing = 0
        while len(temp_set) > 0:
            item_dic = {}
            for itemset in temp_set:
                for item in itemset:
                    if item not in item_dic:
                        item_dic[item] = 0

                    item_dic[item] += 1
            max_val = 0.0
            for item in item_dic:
                if max_val < item_dic[item]:
                    max_val = item_dic[item]
                    element = frozenset([item])

                if item_dic.values().count(max_val) > 1:
                    candidates = [frozenset([item]) for item in item_dic if item_dic[item]==max_val]
                    element = candidates[randrange(0, len(candidates))]

            rem[i] = rem[i]|element
            for itemset in F:
                if itemset not in temp_set and len(tid[sens_ind[i]]) < len(itemset):
                    break
                if (element <= itemset) and (itemset <= tid[sens_ind[i]]) and (itemset not in temp_set):
                    summing += 1

            der = set()
            for itemset in temp_set:
                if (element <= itemset):
                    der.add(itemset)

            temp_set -= der
        coeffs[i] = summing

    return(coeffs, rem)


def get_indices(list lst, int item):
    cdef int i
    for i in range((len(lst)-1),-1,-1):
        if lst[i] == item:
            yield i
