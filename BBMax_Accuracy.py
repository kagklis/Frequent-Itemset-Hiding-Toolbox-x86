#-------------------------------------------------------------------------------
# Name:        BBMax_Accuracy.py
# Purpose:     Implements FIH algorithm found in "A Transversal Hypergraph Approach for the Frequent Itemset Hiding Problem" by Stavropoulos et al.
# Author:      Vasileios Kagklis
# Created:     11/09/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from time import clock
import cplex
from cplex import SparsePair
from math import ceil
from fim import apriori
from random import randrange
from myiolib import *
from SetOp import *

###################################################

def convert2frozen_m(f):
    result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)

###################################################

def get_indices(lst, item):
    for i, x in enumerate(lst):
        if x == item:
            yield i

###################################################

def BBMax_Accuracy_main(fname1, fname2, fname3, sup, mod_name):

    change_raw_data = 0
    
    lines,tid = readDataset(fname3)
    abs_supp = ceil(sup*lines-0.5)

    F = readLargeData(fname1)
    
    S = minSet(readSensitiveSet(fname2))
    

    start_time = clock()
    SS = supersets(S, F.keys())
    Rev_Fd = list(set(F) - SS)
    Rev_pos_bord = convert2frozen_m(apriori(Rev_Fd, target = 'm', supp = float(0.0), conf=100))
    rev_t = clock()-start_time

    with open("positive_border.dat", "w") as f:
        for itemset in Rev_pos_bord:
            f.write(' '.join(list(itemset))+"\n")

    start_time = clock()  
    sens_ind = []
    for i in xrange(lines):
        flag = True
        for itemset in S:
            if itemset.issubset(tid[i]):
                sens_ind.append(i)
                flag = False
                break

        if flag:
            for itemset in Rev_pos_bord:
                if itemset.issubset(tid[i]):
                    sens_ind.append(i)
                    break

    
    sens_ind = list(set(sens_ind))
    N = len(sens_ind)
    
    cpx = cplex.Cplex()
    cpx.set_results_stream(None)
    cpx.objective.set_sense(cpx.objective.sense.minimize)
    cpx.variables.add(obj = (1,)*N + (lines,)*len(Rev_pos_bord), lb =(0,)*(N+len(Rev_pos_bord)),
                      ub=(1,)*N+(cplex.infinity,)*len(Rev_pos_bord),
                      types=(cpx.variables.type.integer,)*(N+len(Rev_pos_bord)))

    for itemset in S:
        ind = []
        cur_supp = 0
        for i in xrange(N):
            if itemset.issubset(tid[sens_ind[i]]):
                ind.append(i)
                cur_supp += 1

        cpx.linear_constraints.add(lin_expr = [SparsePair(ind = ind, val=(1,)*len(ind))],
            senses=["G"], rhs=[cur_supp - abs_supp + 1])


    rpb_c = 0       
    for itemset in Rev_pos_bord:
        ind = []
        cur_supp = 0
        for i in range(N):
            if itemset.issubset(tid[sens_ind[i]]):
                ind.append(i)
                cur_supp += 1

        
        ind.append(N+rpb_c)
        rpb_c += 1
        cpx.linear_constraints.add(lin_expr = [SparsePair(ind = ind, val=(1,)*(len(ind)-1)+(-1,))],
            senses=["L"], rhs=[cur_supp - abs_supp])

    cpx.parameters.mip.pool.relgap.set(0)
    cpx.solve()
    with open("Logfile.dat", "a") as log:
        log.write("Dataset: "+fname3+" No. Sens.:"+str(len(S))+" Relaxed Constraints: "+
                      str(sum(i > 0 for i in map(int, cpx.solution.get_values())[N:])) +
                  "/"+str(len(Rev_pos_bord))+"\n"
                  )
        if any([i for i in map(int, cpx.solution.get_values())[N:]]):
            log.write("System would be infeasible!!\n")
    print(Rev_pos_bord)
    print(map(int, cpx.solution.get_values()))
    for i in get_indices(map(int, cpx.solution.get_values())[0:N], 1):        
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
    
    cpx = None
    F = None
    Rev_Fd = None
    exec_time = clock()-start_time
    
    ######----create out files-----######
    out_file = open(mod_name+'_results.txt', 'w')
    for i in xrange(lines):
        k = ' '.join(sorted(tid[i]))
        print(k, file = out_file)
    
    out_file.close()
    tid = None
       
    return(rev_t, change_raw_data, exec_time)
