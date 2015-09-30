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

def BBMax_Accuracy_main(fname1, fname2, fname3, sup, m_time):
    global tid
    global lines
    change_raw_data = 0
    
    lines,tid = readDataset(fname3)
    abs_supp = ceil(sup*lines-0.5)

    F = readLargeData(fname1)
    
    S = minSet(readSensitiveSet(fname2))
    SS = supersets(S, F.keys())
    
    Rev_Fd = list(set(F) - SS)
    start_time = clock()   
    
    Rev_pos_bord = convert2frozen_m(apriori(Rev_Fd, target = 'm', supp = float(0.0), conf=100))
    
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
##        print(ind)
##        print(itemset)
##        print("GreaterEq than ",cur_supp - abs_supp + 1)
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
##        print(ind)
##        print(itemset)
##        print("LessEq than ",cur_supp - abs_supp)
        cpx.linear_constraints.add(lin_expr = [SparsePair(ind = ind, val=(1,)*(len(ind)-1)+(-1,))],
            senses=["L"], rhs=[cur_supp - abs_supp])

    cpx.parameters.mip.pool.relgap.set(0)
##    cpx.parameters.preprocessing.presolve.set(cpx.parameters.preprocessing.presolve.values.off)
##    cpx.populate_solution_pool()
    cpx.solve()
    if any([i for i in map(int, cpx.solution.get_values())[lines:(lines+len(Rev_pos_bord))]]):
        print("System would be infeasible!!")

    
    print("Number of solutions: ", cpx.solution.pool.get_num())
    
##    print(map(int, cpx.solution.get_values()))
##    print("Objective: ", cpx.solution.get_objective_value())
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
    
    exec_time=((clock()-start_time))
    total_time = exec_time + m_time,"sec"
    exec_time = exec_time,"sec"
    cpx = None

    ######----create out files-----######
    out_file = open('BBMax_Accuracy_results.txt', 'w')
    out_file2 = open('BBMax_Accuracy_visible.txt','w')
    print('Border-Based Max-Accuracy Results\n---------------\n',file = out_file2)
    print('\nThe Sanitized DB is:\n',file = out_file2)
    for i in xrange(lines):
        k = ' '.join(sorted(tid[i]))
        z = '{'+ k + '}'
        print(k, file = out_file)
        print(z, file = out_file2)
    
    out_file.close()
        
    print(file = out_file2)
    m_time = m_time, "sec"
    print('changes in raw data:', change_raw_data, file = out_file2)
    print('data min. alg. time = ', m_time, file = out_file2)
    print('hiding alg. time = ', exec_time, file = out_file2)
    print('total execution time = ', total_time, file = out_file2)
    out_file2.close()
    
    return(tid, change_raw_data, Rev_Fd)


##########-----------main-----------###############
if __name__=='__main__':
##    f_name1 = raw_input('Enter the frequent set file name:')
##    f_name2 = raw_input('Enter the sensitive set file name:')
##    f_name3 = raw_input('Enter the original TID file name:')
##    support = raw_input('Enter the support value:')
    f_name1 = "Apriori_results.txt"
    f_name2 = "5x5_1.txt"
    f_name3 = "Mushroom.dat"
    support = "0.4"
    supp = round(float(support),2)
    results, c_raw_data, len_of_fd = BBMax_Accuracy_main(
        f_name1, f_name2, f_name3, supp, 0)
