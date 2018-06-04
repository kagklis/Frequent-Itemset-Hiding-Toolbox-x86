#-------------------------------------------------------------------------------
# Name:        Apriori.py
# Purpose:     Mining Frequent Itemsets
# Author:      Vasileios Kagklis
# Created:     10/02/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
import os
from time import clock
from fim import apriori
from myiolib import readDataset


def printResults(fname, sup, Time, F, out_fname):
    result_file=open(out_fname,'w')
    visible_file=open('Apriori_visible.txt','w')
    print('Apriori Execution',file=visible_file)
    print('=================',file=visible_file)
    print('Data Set from File:',fname,file=visible_file)
    print('Support= ',sup,file=visible_file)
    print('Frequent Itemsets ==> Support:',file=visible_file)
    print('',file=visible_file)
    print('Results:','\n',file=visible_file)
    data_line=''
    itemset_and_sup=''
    Vis_itemset_and_sup=''
    for itemset, support in F.items():
        ItemSet=list(itemset)
        ItemSet.sort()
        for item in ItemSet:
            data_line=data_line+item+' '
        itemset_and_sup=data_line+(str(support))
        Vis_itemset_and_sup=data_line+'==>'+(str(round(support,5)))
        print(itemset_and_sup,file=result_file)
        print(Vis_itemset_and_sup,file=visible_file)
        data_line=''
        itemset_and_sup=''
        Vis_itemset_and_sup=''
    print('Execution time= ',Time,file=visible_file)
    visible_file.close()
    result_file.close()
                     
    
def convert2dic(F, N):
    freq = {}
    for itemset in F:
        freq[frozenset(itemset[0])] = float(itemset[1][0]/N)
    return freq

def convert2frozen_m(f):
    result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)

def Apriori_main(data_fname, minSupport, out_fname='Apriori_results.txt'):
    lines,tid = readDataset(data_fname)
    t1=clock()
    temp_freq = apriori(tid, target='s', supp=float(minSupport*100), conf=100)
    CPU_time=clock()-t1    
    freq_items = convert2dic(temp_freq,lines)
    printResults(data_fname,minSupport,CPU_time,freq_items,out_fname)
    return(freq_items,CPU_time)
