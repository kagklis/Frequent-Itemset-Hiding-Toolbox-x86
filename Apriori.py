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

def Apriori_main(data_fname, minSupport, out_fname='Apriori_results.txt'):
    lines,tid = readDataset(data_fname)
    t1=clock()
    temp_freq = apriori(tid, target='s', supp=float(minSupport*100), conf=100)
    CPU_time=clock()-t1
    freq_items = convert2dic(temp_freq,lines)
    printResults(data_fname,minSupport,CPU_time,freq_items,out_fname)
    return(freq_items,CPU_time)
