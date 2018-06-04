#-------------------------------------------------------------------------------
# Name:        Coeff_Max_Accuracy.py
# Purpose:     Implements FIH algorithm found in "Coefficient-Based Exact Approach for Frequent Itemset Hiding" by Leloglu et al.
# Author:      Vasileios Kagklis
# Created:     03/04/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from time import clock
import cplex
from cplex import SparsePair
from math import ceil
import myiolib
import cbma_ext
from SetOp import *

###################################################

def Coeff_Max_Accuracy_main(fname1, fname2, fname3, sup, mod_name):
   
    change_raw_data = 0    
    lines, tid = myiolib.readDataset(fname3)
    abs_supp = int(ceil(sup*lines))
    F = myiolib.readLargeData(fname1)  
    
    S = minSet(myiolib.readSensitiveSet(fname2))
    SS = supersets(S, F)
    
    sens_ind = []
    for i in xrange(lines):        
        for itemset in S:
            if itemset.issubset(tid[i]):
                sens_ind.append(i)
                break
    start_time = clock()

    N = len(sens_ind)
    coeffs, rem = cbma_ext.calculateCoeffs(tid, sup, sens_ind, S, sorted(F, key = len))
    
    cpx = cplex.Cplex()
    cpx.set_results_stream(None)
    cpx.objective.set_sense(cpx.objective.sense.minimize)
    cpx.variables.add(obj = coeffs, lb =(0,)*N,
                      ub=(1,)*N, types=(cpx.variables.type.binary,)*N)

    del coeffs
    k = 0
    for itemset in S:
        ind = []
        cur_supp = 0
        for i in xrange(N):
            if itemset.issubset(tid[sens_ind[i]]):
                ind.append(i)
                cur_supp += 1
        cpx.linear_constraints.add(lin_expr = [SparsePair(ind = ind, val=(1,)*len(ind))],
            senses=["G"], rhs=[cur_supp - abs_supp + 1], names=["c"+str(k)])
        k+=1

    cpx.solve()
    solution = map(int, cpx.solution.get_values())
    
    for i in cbma_ext.get_indices(solution, 1):
        tid[sens_ind[i]] = tid[sens_ind[i]] - rem[i]
        change_raw_data += len(rem[i])
        
    cpx = None

    exec_time = clock()-start_time
    
    ######----create out files-----######
    out_file = open(mod_name+'_results.txt', 'w')
    for i in xrange(lines):
        k = ' '.join(sorted(tid[i]))
        print(k, file = out_file)
    
    out_file.close()
    tid = None
    F = None

    return("Not Applicable", change_raw_data, exec_time)

