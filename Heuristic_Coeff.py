#-------------------------------------------------------------------------------
# Name:        Heuristic_Coeff.py
# Purpose:     Implements FIH algorithm found in "An Integer Linear Programming Scheme to Sanitize Sensitive Frequent Itemsets" by Kagklis et al.
# Author:      Vasileios Kagklis
# Created:     20/03/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import print_function
from time import clock
from math import ceil
import cplex
from cplex import SparsePair
from fim import apriori
import myiolib
import hcba_ext
from SetOp import *

###################################################

def findMin(S):
    result = []
    for i in xrange(len(S)):
        flag = True
        for j in xrange(len(S)):
            if i == j:
                continue
            if len(S[i]) >= len(S[j]) and S[i].issuperset(S[j]):
                flag = False
                break
            elif len(S[i]) < len(S[j]) and S[i].issubset(S[j]):
                flag = True
            elif len(S[i]) == len(S[j]):
                flag = True
                
        if flag:
            result.append(S[i])
    
    if len(result) == 0:
        return(S)
    else:
        return(result)

###################################################

def convert2frozen(rev_fd):
    result = []
    for itemset in rev_fd:
        for item in itemset:
            if isinstance(item, float):
                temp = itemset - frozenset([item])
        result.append(temp)
    return(result)

###################################################
def Heuristic_Coeff_main(fname1, fname2, fname3, sup, mod_name):

    change_raw_data = 0
    L = []
    solution = None
    k =0

    # Read dataset and identify discrete items
    lines, tid = myiolib.readDataset(fname3)
    I = hcba_ext.get_1itemsets(tid)

    # Calculate support count
    abs_supp = ceil(sup*lines-0.5)

    # Load F from file
    F = myiolib.readLargeData(fname1)

    # Load S from file
    S = minSet(myiolib.readSensitiveSet(fname2))

    # Calculate the revised F
    start_time = clock()
   
    SS = supersets(S, F)
    Rev_Fd = list(set(F)-SS)
    rev_t = clock() - start_time
    Rev_Fd.sort(key = len, reverse = True)

   
    
    # Calculate minimal set of S
    sens_ind =[]
    for i in xrange(lines):        
        for itemset in S:
            if itemset.issubset(tid[i]):
                sens_ind.append(i)
                break

    start_time = clock()  
    
    coeffs, rem = hcba_ext.calculateCoeffs(tid, sup, sens_ind, S, F, Rev_Fd)
    
    # The initial objective => Elastic filtering
    cpx = cplex.Cplex()
    cpx.set_results_stream(None)


    # Add obj. sense and columns
    cpx.objective.set_sense(cpx.objective.sense.minimize)
    cpx.variables.add(obj = coeffs, lb =[0]*len(coeffs),
                      ub=[1]*len(coeffs),
                      types=[cpx.variables.type.integer]*len(coeffs))

    # Build constraints for minimal S
    for itemset in S:
        ind = []
        cur_supp = 0
        for i in xrange(len(sens_ind)):
            if itemset.issubset(tid[sens_ind[i]]):
                ind.append(i)
                cur_supp += 1
        cpx.linear_constraints.add(lin_expr = [SparsePair(ind = ind, val=[1]*len(ind))],
            senses=["G"], rhs=[cur_supp - abs_supp + 1], names=["c"+str(k)])
        k+=1

    cpx.solve()
    solution = map(int, cpx.solution.get_values())
    
    # Apply sanitization
    for i in hcba_ext.get_indices(solution, 1):
        tid[sens_ind[i]] = tid[sens_ind[i]] - rem[i]
        change_raw_data += len(rem[i])

    coeffs = None
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
 
    return("Not Applicable", change_raw_data, rev_t+exec_time)
