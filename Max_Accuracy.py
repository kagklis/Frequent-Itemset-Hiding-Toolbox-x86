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
# Name:        Max_Accuracy.py
# Purpose:     Implements FIH algorithm found in "Maximizing accuracy of shared databases when concealing sensitive patterns" by Menon et al.
# Author:      Vasileios Kagklis
# Created:     20/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from time import clock
import cplex
from cplex import SparsePair
from math import ceil
from random import randrange
from myiolib import *
from SetOp import *

###################################################

def get_indices(lst, item):
    for i, x in enumerate(lst):
        if x == item:
            yield i

###################################################

def Max_Accuracy_main(fname1, fname2, fname3, sup, mod_name):
    change_raw_data = 0
    
    lines,tid = readDataset(fname3)
    abs_supp = ceil(sup*lines-0.5)

    S = minSet(readSensitiveSet(fname2))

    sens_ind = []
    for i in xrange(lines):        
        for itemset in S:
            if itemset.issubset(tid[i]):
                sens_ind.append(i)
                break

    N = len(sens_ind)
  
    start_time = clock()
    cpx = cplex.Cplex()
    cpx.set_results_stream(None)
    cpx.objective.set_sense(cpx.objective.sense.minimize)
    cpx.variables.add(obj = (1,)*N, lb =(0,)*N, ub=(1,)*N,
                      types=(cpx.variables.type.integer,)*N)

    for itemset in S:
        ind = []
        cur_supp = 0
        for i in xrange(N):
            if itemset.issubset(tid[sens_ind[i]]):
                ind.append(i)
                cur_supp += 1
        cpx.linear_constraints.add(lin_expr = [SparsePair(ind = ind, val=(1,)*len(ind))],
            senses=["G"], rhs=[cur_supp - abs_supp + 1])
    cpx.parameters.mip.pool.relgap.set(0)
    cpx.solve()
	
    for i in get_indices(map(int, cpx.solution.get_values()), 1):
        
        temp_set = set()
        for itemset in S:
            if itemset.issubset(tid[sens_ind[i]]):
                temp_set.add(itemset)

        while len(temp_set) > 0:
            item_dic = {}
            for itemset in temp_set:
                for item in itemset:
                    if item not in item_dic:
                        item_dic[item] = 0

                    item_dic[item] += 1
            max_val = 0
            for item, freq in item_dic.items():
                if max_val < freq:
                    max_val = freq
                    element = frozenset([item])

            if item_dic.values().count(max_val) > 1:
                candidates = [frozenset([item])  for item, freq in item_dic.items() if freq==max_val]
                element = candidates[randrange(0, len(candidates))]

            tid[sens_ind[i]] = tid[sens_ind[i]] - element
            change_raw_data += 1
            for itemset in temp_set:
                if element.issubset(itemset):
                    temp_set = temp_set - set([itemset])
    
    exec_time=clock()-start_time
    cpx = None

    ######----create out files-----######
    out_file = open(mod_name+'_results.txt', 'w')
    for i in xrange(lines):
        k = ' '.join(sorted(tid[i]))
        print(k, file = out_file)

    
    out_file.close()
    tid = None
    
    return("Not Applicable", change_raw_data, exec_time)

