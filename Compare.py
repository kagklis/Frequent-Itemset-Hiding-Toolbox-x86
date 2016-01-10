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
# Name:        Compare.py
# Purpose:     Runs multiple selected algorithms
# Author:      Vasileios Kagklis
# Created:     12/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
import Apriori
from time import clock
from multiprocessing import Process, Pipe
import gc
import os,sys
from fim import apriori
from myiolib import *
from SetOp import *

def convert2frozen_m(f):
    result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)  

def aprioriWorker(data_fname, sup, out_fname, conn):
    try:
        conn.send(Apriori.Apriori_main(data_fname, sup, out_fname)[1])
        conn.close()
        return
    except MemoryError:
        conn.send(-1)
        conn.close()
        return
    except Exception as e:
        conn.send((-1,e.message,))
        conn.close()
        return

def functionWorker(mod_name, freq_fname, sens_fname, data_fname, sup, conn):
    try:
        sys.path.insert(0, os.getcwd())
        module = __import__(mod_name)
        conn.send(getattr(module, mod_name+"_main")(freq_fname, sens_fname, data_fname, sup, mod_name))
        conn.close()
        gc.collect()
        return
    except MemoryError:
        conn.send(-1)
        conn.close()
        return
    except Exception as e:
        conn.send((-1,e.message,))
        conn.close()
        return

def metricWorker(fname, sanitized, sens, sup, conn):
    Apriori_results_init = readLargeData(fname)
    S = minSet(readSensitiveSet(sens))
    SS = supersets(S, Apriori_results_init.keys())
    
    r_fd = list(set(Apriori_results_init) - SS)
    Apriori_results = Apriori.Apriori_main(sanitized, sup)[0]

    side_effects = len(r_fd)-len(Apriori_results)
    
    if side_effects<0:
        conn.send((side_effects,0,))
        conn.close()
        return
    else:
##        a1 = 0.
##        a2 = 0.
##        for itemset in convert2frozen_m(apriori(r_fd, target='m', supp = float(0.0))):
##            a1 += 1.0
##            for itemset2 in convert2frozen_m(apriori(Apriori_results.keys(), target='m', supp = float(0.0))):
##                if itemset == itemset2:
##                    a2 += 1.0
##                    
##        Bd_rate = abs(round(float((a1-a2)/a1),2))
        
        SumAll = 0
        AbsDif = 0.0
        for itemset in r_fd:
            SumAll +=  Apriori_results_init[itemset]
            if itemset in Apriori_results:
                AbsDif +=  float(abs(Apriori_results_init[itemset] - Apriori_results[itemset]))
            else:
                AbsDif +=  float(Apriori_results_init[itemset])
                
        if SumAll == 0:
            inls =  round(float(AbsDif), 3)
        else:
            inls =  round(float(AbsDif/SumAll), 3)

        conn.send((side_effects, inls,))
        conn.close()
        return

###############################################

def read_sens_data_file(sens_name):
    sens=[]
    SENS=[]
    delimiter = ' '
    file_iter = open(sens_name, 'rU')
    if sens_name.split('\\')[-1].split(".")[-1] == "csv" or sens_name.split('/')[-1].split(".")[-1] == "csv":
        delimiter = ','
        
    for line in file_iter:
        line = line.strip()
        line=line.split(';')
        for x in line:
            y=(x.split(delimiter))
            y.sort()
            sens.append(y)
        SENS.append(sens)
        sens=[]
    file_iter.close()
    return(SENS)

##############-----main-----###############
def Compare(Original_DB, support, Sens_f, selection, fNames):

    time = ['']*len(selection)
    s_ef = [0]*len(selection)
    ch_raw_dat = [0]*len(selection)
    fil = [0]*len(selection)
    rev_t = ['']*len(selection)
    CPU_time = 0
    
    if any(selection):
        out_fname = os.getcwd()+'\\Apriori_init.txt'
        parent, child = Pipe()
        p = Process(target=aprioriWorker, args=(Original_DB, support, out_fname, child,))
        p.start()
        response = parent.recv()
        parent.close()
        p.join()
        p = None
        parent = None
        child = None
        if response == -1:
            return(response)
        elif type(response) == type(tuple):
            return(response)

        CPU_time = response
    
    for index in [i for i in xrange(len(selection)) if selection[i]]:
        parent, child = Pipe()
        
        p = Process(target=functionWorker, args=(fNames[index], out_fname, Sens_f, Original_DB, support, child,))
        p.start()
        response = parent.recv()
        parent.close()
        p.join()
        if response == -1:
            return(response)
        elif type(response) == type(tuple) and len(response) == 2:
            return((response[0], fNames[index]))

        print(response)
        rev_t[index], ch_raw_dat[index], time[index] = response
       
        parent, child = Pipe()
        p = Process(target=metricWorker, args=(out_fname, fNames[index]+"_results.txt", Sens_f, support, child,))
        p.start()
        s_ef[index], fil[index]= parent.recv()
        parent.close()
        p.join()
        p = None
        parent = None
        child = None
        gc.collect()
    
    return(s_ef, ch_raw_dat, time, rev_t, fil, CPU_time)
           

###############################################

def Comp_main_false(Original_DB, Sens_f, selection, sigma, fNames, algos):
    OUT_FILE=open('Comparison_results_Graphs1_2_3.txt','w')
    S_F=read_sens_data_file(Sens_f)
    side_effects = []
    change_raw = []
    time_cpu = []
    inf_loss = []
    
    for i in range(len(selection)):
        side_effects.append({})
        change_raw.append({})
        time_cpu.append({})
        inf_loss.append({})
    
    for table in S_F:
        OUT_FILE_2=open('List_to_file.txt','w')
        for sub_table in table:
            k=''
            for set_ in sub_table:
                k=k+set_+' '
            x=(list(k)).sort()
            print(k,file=OUT_FILE_2)
        OUT_FILE_2.close()
        (SUPPORT,LIMIT,STEP) = sigma.split(":")
        SUPPORT = float(SUPPORT)
        LIMIT = float(LIMIT)
        STEP = float(STEP)
        while SUPPORT<=LIMIT:
            
            response=Compare(Original_DB, SUPPORT, 'List_to_file.txt', selection, fNames)

            if response == -1:
                return(response)
            elif type(response) == type(tuple) and len(response)==2:
                return(response)
            
            n,c,t,rv,fil,m_time=response
            response = None
            
            for i in range(len(selection)):
                if selection[i]:
                    #####    Side Effects   ######
                    if SUPPORT in side_effects[i]:
                        side_effects[i][SUPPORT].append(n[i])
                    else:
                        side_effects[i][SUPPORT] = [n[i]]

                    #####   Change Raw Data  #####
                    if SUPPORT in change_raw[i]:
                        change_raw[i][SUPPORT].append(c[i])
                    else:
                        change_raw[i][SUPPORT] = [c[i]]
                
                    #####   CPU Time        #####
                    if SUPPORT in time_cpu[i]:
                       time_cpu[i][SUPPORT].append(round(t[i]+m_time,4))
                    else:
                       time_cpu[i][SUPPORT] = [round(t[i]+m_time,4)]

                    if SUPPORT in inf_loss[i]:
                        inf_loss[i][SUPPORT].append(fil[i])
                    else:
                        inf_loss[i][SUPPORT] = [fil[i]]

            print('For support:',SUPPORT,'and Sensitive Itemset',tuple(table),file=OUT_FILE)
            for i in range(len(selection)):
                if(selection[i] and c[i]>=0):
                    print('',file=OUT_FILE)
                    if fNames[i] == "OPHA":
                        print('Data Min. Alg. Time: ',rv[i],' sec',file=OUT_FILE)
                        print('Border Revision Time: 0 sec',file=OUT_FILE)
                        print(algos[i],'CPU Time: ',round(t[i],4),' sec',file=OUT_FILE)
                        print('Total CPU Time: ', round(rv[i] + t[i],4),' sec', file=OUT_FILE)
                    else:
                        print("Data Min. Alg. Time: ",round(m_time,4),' sec',file=OUT_FILE)
                        if type(rv[i]) == str:
                            print("Border Revision Time: ",rv[i],file=OUT_FILE)
                            print(algos[i],'CPU Time: ',round(t[i],4),' sec',file=OUT_FILE)
                            print('Total CPU Time: ', round(t[i] + m_time,4), file=OUT_FILE)
                        else:
                            print("Border Revision Time: ",round(rv[i],4),' sec',file=OUT_FILE)
                            print(algos[i],'CPU Time: ',round(t[i],4),' sec',file=OUT_FILE)
                            print('Total CPU Time: ', round(t[i] + rv[i] + m_time,4), file=OUT_FILE)
                    print(algos[i],'Change in Raw Data: ',c[i],file=OUT_FILE)
                    print(algos[i],'Side Effects: ',n[i],file=OUT_FILE)
                    print(algos[i],'Frequency Information Loss: ',fil[i],file=OUT_FILE)
                    #print(algos[i],'Rev. Pos. Border Inf. Loss: ',bdr[i],file=OUT_FILE)
            print('=================================',file=OUT_FILE)
            print('\n',file=OUT_FILE)
            SUPPORT=SUPPORT+STEP
            #print('SUPPORT=',SUPPORT)
    OUT_FILE.close()
    gc.collect()
    return(side_effects , change_raw, time_cpu, inf_loss)

###############################################

def Comp_main_true(Original_DB, support, Sens_f, selection, fNames, algos):
    S_F=read_sens_data_file(Sens_f)
    #print(S_F)
    OUT_FILE=open('Comparison_results_Graphs4_5_6.txt','w')

    
    side_effects = []
    change_raw = []
    time_cpu = []
    inf_loss = []
    
    for i in range(len(selection)):
        side_effects.append({})
        change_raw.append({})
        time_cpu.append({})
        inf_loss.append({})

    num_itemsets = 0
    length_total = 0
    for table in S_F:
        length=0
        num=0
        for sub_table in table:
            length += len(sub_table)
            num += 1
        
        length_total = length
        num_itemsets = num
        OUT_FILE_2=open('List_to_file.txt','w')
        for sub_table in table:
            k=''
            for set_ in sub_table:
                k=k+set_+' '
            x=(list(k)).sort()
            print(k,file=OUT_FILE_2)
            #print('k=',k)
        OUT_FILE_2.close()
        response=Compare(Original_DB, support, 'List_to_file.txt', selection, fNames)

        if response == -1:
            return(response)
        elif type(response) == type(tuple) and len(response)==2:
            return(response)
        
        n,c,t,rv,fil,m_time=response
        response = None

        for i in range(len(selection)):
            if selection[i]:
                #####   Side Effects    #####
                if num_itemsets in side_effects[i]:
                    side_effects[i][num_itemsets].append(n[i])
                else:
                    side_effects[i][num_itemsets]=[n[i]]
                    
                #####   Change Raw Data #####
                    
                if num_itemsets in change_raw[i]:
                    change_raw[i][num_itemsets].append(c[i])
                else:
                    change_raw[i][num_itemsets]=[c[i]]
                
                #####   CPU Time        #####
                                 
                if num_itemsets in time_cpu[i]:
                    time_cpu[i][num_itemsets].append(round(t[i]+m_time,4))
                else:
                    time_cpu[i][num_itemsets]=[round(t[i]+m_time,4)]

                if num_itemsets in inf_loss[i]:
                    inf_loss[i][num_itemsets].append(fil[i])
                else:
                    inf_loss[i][num_itemsets] = [fil[i]]
                
        
        print('For Itemset:', tuple(table), 'Lenght=', length_total,
              file=OUT_FILE)
        for i in range(len(selection)):
            if(selection[i] and c[i]>=0):
                print('', file=OUT_FILE)
                if fNames[i] == "OPHA":
                    print('Data Min. Alg. Time: ',rv[i],' sec',file=OUT_FILE)
                    print('Border Revision Time: 0 sec',file=OUT_FILE)
                    print(algos[i],'CPU Time: ',round(t[i],4),' sec',file=OUT_FILE)
                    print('Total CPU Time: ', round(rv[i] + t[i],4),' sec', file=OUT_FILE)
                else:
                    print("Data Min. Alg. Time: ",round(m_time,4),' sec',file=OUT_FILE)
                    if type(rv[i]) == str:
                        print("Border Revision Time: ",rv[i],file=OUT_FILE)
                        print(algos[i],'CPU Time: ',round(t[i],4),' sec',file=OUT_FILE)
                        print('Total CPU Time: ', round(t[i] + m_time,4), file=OUT_FILE)
                    else:
                        print("Border Revision Time: ",round(rv[i],4),' sec',file=OUT_FILE)
                        print(algos[i],'CPU Time: ',round(t[i],4),' sec',file=OUT_FILE)
                        print('Total CPU Time: ', round(t[i] + rv[i] + m_time,4), file=OUT_FILE)
                print(algos[i],'Change in Raw Data: ',c[i],file=OUT_FILE)
                print(algos[i],'Side Effects: ',n[i],file=OUT_FILE)
                print(algos[i],'Frequency Information Loss: ',fil[i],file=OUT_FILE)
                #print(algos[i],'Rev. Pos. Border Inf. Loss: ',bdr[i],file=OUT_FILE)
        print('=================================',file=OUT_FILE)
        print('\n',file=OUT_FILE)
    OUT_FILE.close()
    gc.collect()
    return(side_effects, change_raw, time_cpu, inf_loss)
