#-------------------------------------------------------------------------------
# Name:        Tool.py
# Purpose:     Implements GUI
# Author:      Vasileios Kagklis
# Created:     12/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
from __future__ import division, print_function
from Tkinter import *
import ttk
from tkMessageBox import *
from tkFileDialog import askopenfilename
from tkSimpleDialog import askstring
from tkFileDialog import asksaveasfilename
from time import clock
from glob import glob
import Apriori
import Compare
import os
os.system
from numpy import linspace
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from math import ceil, floor
from fim import apriori
from multiprocessing import Process, Pipe
from datetime import datetime
import gc
from myiolib import *
from SetOp import *

def display_error(code):
    if code ==  1:
        errmsg = "Please select a Data Mining Algorithm"
        showerror('Selection Error', errmsg)
    elif code ==  2:
        errmsg = "Please select a Data Transaction File"
        showerror('Selection Error', errmsg)
    elif code ==  3:
        errmsg = "Please select a Sensitive File"
        showerror('Selection Error', errmsg)
    elif code ==  4:
        errmsg = "An Error has occured! Please try with another data set"
        showerror('Data Set Error', errmsg)
    elif code ==  5:
        errmsg = "An Error has occured! Please try with another data set or sensitive set or support"
        showerror('Data Set Error', errmsg)
    elif code ==  6:
        errmsg = "No path for dataset file specified"
        showerror('Specification File Error', errmsg)
    elif code ==  7:
        errmsg = "No path for sensitive itemsets' file specified"
        showerror('Specification File Error', errmsg)
    elif code ==  8:
        errmsg = "The third line of the file (support)  has to be a float number"
        showerror('Specification File Error', errmsg)
    elif code ==  9:
        errmsg = "Please check the format of your specification file"
        showerror('Specification File Error', errmsg)
    elif code ==  10:
        errmsg = "Support threshold must be a float number"
        showerror('Support Value Error', errmsg)
    elif code ==  11:
        errmsg = "Please type the Support Threshold"
        showerror('Support Missing Value Error', errmsg)
    elif code ==  12:
        errmsg = "Oops! Out of memory! Try with a smaller dataset!"
        showerror('Memory Error', errmsg)

def display_first(_text):
    global text
    text.insert('1.0', _text)

def display_text(_file):
    global text
    text.delete('1.0', END)
    text.insert('1.0', open(_file, 'r').read())

def get_TID_file_Name():
    global f_tid_name
    f_tid_name = None
    f_tid_name = askopenfilename()
    label6.config(text = f_tid_name.split("/")[-1])

def get_Sens_file_Name():
    global f_sens_name
    f_sens_name = None
    f_sens_name = askopenfilename()
    label7.config(text = f_sens_name.split("/")[-1])

def onOpen():
    filename  = askopenfilename()
    if filename:
        text.delete('1.0', END)
        text.insert('1.0', open(filename, 'r+').read())

def onSave():
    filename = asksaveasfilename()
    if filename:
        open(filename, 'w').write(text.get('1.0', END+'-1c'))

def On_Help():
    pop_up_help = Toplevel(root)
    pop_up_help.title('Help')
    H_text = Text(pop_up_help, width = 60, height = 40, relief = SUNKEN)
    H_text.pack(side = LEFT)
    Sbar = Scrollbar(pop_up_help)
    Sbar.config(command = H_text.yview)
    H_text.config(yscrollcommand = Sbar.set)
    Sbar.pack(side = RIGHT, fill = Y)
    text_help = open('Help.txt', 'r').read()
    H_text.insert('1.0', text_help)
    
def onPaste(): # add clipboard text
    try:
        text = selection_get(selection = 'CLIPBOARD')
        text.insert(INSERT, text)
    except TclError:
        pass    

def myPlot():
    plot_options = ['Number of Sensitive Itemsets - Changes in raw data',
                     'Number of Sensitive Itemsets - Side Effects',
                     'Number of Sensitive Itemsets - CPU time (sec)',
                     'Number of Sensitive Itemsets - Information Loss (%)','Support - Changes in raw data',
                     'Support - Side Effects',
                     'Support - CPU time (sec)',
                     'Support - Information Loss (%)']

    if plotOpt.get() == plot_options[0]:
        onSheet4()
    elif plotOpt.get() == plot_options[1]:
        onSheet5()
    elif plotOpt.get() == plot_options[2]:
        onSheet6()
    elif plotOpt.get() == plot_options[3]:
        onSheet7()
    elif plotOpt.get() == plot_options[4]:
        onSheet1()
    elif plotOpt.get() == plot_options[5]:
        onSheet2()
    elif plotOpt.get() == plot_options[6]:
        onSheet3()
    elif plotOpt.get() == plot_options[7]:
        onSheet8()
    
def mySave():
    d = datetime.now()
    canvas.figure.savefig('image_'+str(d.year)+str(d.month)+str(d.day)+
                          str(d.hour)+str(d.minute)+str(d.second)+'.png',
                          format='png', dpi=300)

def myClear():
    f.clf()
    f.clear()
    canvas.figure = f
    canvas.draw()
    
def destr():
    global support
    global text
    global crd;global s_ef;global t;global inls
    global Crd;global S_ef;global T;global Inls
    global f_tid_name
    global f_sens_name
    global bP;global bS;global bC;global plotDL
    crd = 0;s_ef = 0;t = 0;inls = 0
    Crd = 0;S_ef = 0;T = 0;Inls = 0
    f_tid_name = None
    f_sens_name = None
    label6.config(text = '')
    label7.config(text = '')
    
    support.delete(0, END)
    text.delete('1.0', END)
    display_first('\n\tResults will be dispalyed here...')
    f.clf()
    f.clear()
    canvas.figure = f
    canvas.draw()

    plotOpt.set(None)
    plotDL.set_menu('None')
    bP.configure(state = DISABLED)
    bS.configure(state = DISABLED)
    bC.configure(state = DISABLED)
    gc.collect()
    
    
def onPress(i):
    states[i] = not states[i]


def countTrues(p):
    counter = 0
    for item in p:
        if item:
            counter +=  1
    return(counter)

def convert2frozen_m(f):
    result = []
    for itemset in f:
        result.append(frozenset(itemset[0]))
    return(result)

def aprioriWorker(data_fname, sup, conn, flag=True):
    try:
        if flag:
            Apriori.Apriori_main(data_fname, sup)
            conn.send(0)
            conn.close()
            return
        else:
            conn.send(Apriori.Apriori_main(data_fname, sup)[1])
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


############ Features for plots ###############

# MARKERS
global markers
markers = [(4,0,0), (4,0,45), (3,0,0), (3,0,180) ,(5,1,0), (0,3,0), (4,1,0), (8,1,0), (3,0,90), (3,0,270), (5,0,0)]


# COLORS
global colors
colors = ['#E31A1C', '#D55E00', '#E69F00', '#F0E442', '#33A02C', '#56B4E9', '#0072B2', '#CC79A7', '#000000']

###############################################
def _Go():
    global support;global text
    global f_tid_name;global f_sens_name
    global crd;global s_ef;global t;global inls
    global plotDL;global bP;global bS;global bC;global plotOpt
    crd = 0;s_ef = 0;t = 0;inls = 0 
    
    sel_dat_min_alg = alg_1.get()
    SUP = support.get()
    
    if (sel_dat_min_alg == 'None'):
        display_error(1)
        return
            
    if (f_tid_name == None or f_tid_name == ''):
        display_error(2)
        return

    #---------------------------------------------------------------
    #-------- Apriori/E-Clat & No Hiding Algorithm Selected --------
    #---------------------------------------------------------------   
    if not(any(states)):

        if (SUP != '' and not(":" in SUP)):
            try:
                sup = float(support.get())
            except ValueError:
                display_error(10)
                return
        else:
            display_error(11)
            return
        
        if sel_dat_min_alg == 'Apriori':
            parent, child = Pipe()
            p = Process(target=aprioriWorker, args=(f_tid_name, sup, child,))
            p.start()
            p.join()
            response = parent.recv()
            parent.close()
            
            if response == -1:
                display_error(12)
                return
            elif type(response) == type(tuple):
                print(response)
                return
            
            p = None
            display_text('Apriori_visible.txt')
            gc.collect()
        

    plotOpt.set(None)
    plotDL.set_menu('None')
    bP.configure(state = DISABLED)
    bS.configure(state = DISABLED)
    bC.configure(state = DISABLED)

    #---------------------------------------------------------------
    #------ Apriori/E-Clat & Only 1 Hiding Algorithm Selected ------
    #---------------------------------------------------------------   
    if countTrues(states) ==  1:
        
        if (f_sens_name == None or f_sens_name == ''):
            display_error(3)
            return

        if (SUP != '' and not(":" in SUP)):
            try:
                sup = float(support.get())
            except ValueError:
                display_error(10)
                return
        else:
            display_error(11)
            return

        CPU_time = 0
        if sel_dat_min_alg ==  'Apriori':
            filename = os.getcwd()+'\\Apriori_results.txt'
            parent, child = Pipe()
            p = Process(target=aprioriWorker, args=(f_tid_name, sup, child, False,))
            p.start()
            response = parent.recv()
            parent.close()
            p.join()
            p = None
            parent = None
            child = None
            if response == -1:
                display_error(12)
                return
            elif type(response) == type(tuple):
                print(response)
                return
        
                
        CPU_time = response
        parent, child = Pipe()
        option = states.index(True)
        
        p = Process(target=functionWorker, args=(fNames[option], filename, f_sens_name, f_tid_name, sup, child,))
        p.start()
        response = parent.recv()
        
        parent.close()
        p.join()


        if response == -1:
            display_error(12)
            return
        elif type(response) == type(tuple):
            print(response)
            return

        #print(response)
        rev_t, crd, t = response
            
        p = None
        parent = None
        child = None
        gc.collect()
        
        if sel_dat_min_alg ==  'Apriori':
            parent, child = Pipe()
            p = Process(target=metricWorker, args=(filename, fNames[option]+"_results.txt", f_sens_name, sup, child,))
            p.start()
            response= parent.recv()
            #print(response)
            se, inls = response
            parent.close()
            p.join()
            p = None
            parent = None
            child = None
            gc.collect()
            if se < 0:
                display_error(4)
                return
            else:
                with open(fNames[option]+"_visible.txt", "w") as vis:
                    print('',file=vis)
                    print(fNames[option]+' Results\n------------------------------\n', file=vis)
                    if fNames[option] == 'OPHA':
                        print('Apriori Time: '+str(round(rev_t,4))+' sec', file=vis)
                        print('Border Revision Time: 0 sec', file=vis)
                        print('Hiding Alg. Time: '+str(round(t,4)),file=vis)
                        print('Total Execution Time: '+str(round(t,4)), file=vis)
                    else:
                        print('Apriori Time: '+str(round(CPU_time,4)), file=vis)
                        if type(rev_t) == str:
                            print('Border Revision Time: '+rev_t, file=vis)
                            print('Hiding Alg. Time: '+str(round(t,4)),file=vis)
                            print('Total Execution Time: '+str(round(CPU_time+t,4)), file=vis)
                        else:
                            print('Border Revision Time: '+str(round(rev_t,4))+' sec', file=vis)
                            print('Hiding Alg. Time: '+str(round(t,4)),file=vis)
                            print('Total Execution Time: '+str(round(CPU_time+rev_t+t,4)), file=vis)
                    print('Changes in Raw Data: '+str(crd), file=vis)
                    print('Side Effects: '+str(se),file=vis)
                    print('Frequency Information Loss: '+str(inls),file=vis)
                    #print('Rev. Pos. Border Inf. Loss: '+str(Bd_rate),file=vis)

                display_text(fNames[option]+"_visible.txt")
             
    #---------------------------------------------------------------
    #------------ Multiple Algorithms & Specified Support ----------
    #---------------------------------------------------------------
    if countTrues(states) > 1:
        if (f_sens_name == None or f_sens_name == ''):
            display_error(3)
            return
 
        if SUP != '' and not(":" in SUP):

            try:
                sup = float(support.get())
            except ValueError:
                display_error(10)
                return

            response = Compare.Comp_main_true(
                    f_tid_name, sup, f_sens_name, states, fNames, Algorithms)


            if response == -1:
                display_error(12)
                return
            elif type(response) == type(tuple) and len(response) == 2:
                print(response)
                return
            
            s_ef, crd, t, inls = response
            response = None
            gc.collect()
            
            for x in s_ef:
                for y in x.values():
                    for z in y:
                        if z<0:
                            display_error(5)
                            error = True
                            break
           
            display_text('Comparison_results_Graphs4_5_6.txt')

            plot_options = ['None','Number of Sensitive Itemsets - Changes in raw data',
                     'Number of Sensitive Itemsets - Side Effects',
                     'Number of Sensitive Itemsets - CPU time (sec)',
                     'Number of Sensitive Itemsets - Information Loss (%)']
            plotDL.set_menu(*plot_options)
            bP.configure(state = NORMAL)
            bS.configure(state = NORMAL)
            bC.configure(state = NORMAL)

        elif SUP !=  '' and ":" in SUP:
            
            response = Compare.Comp_main_false(f_tid_name, f_sens_name, states, SUP, fNames, Algorithms)

            if response == -1:
                display_error(12)
                return
            elif type(response) == type(tuple) and len(response) == 2:
                print(response)
                return
            
            S_ef, Crd, T, Inls = response
            response = None
            gc.collect()
            
            for x in S_ef:
                for y in x.values():
                    for z in y:
                        if z<0:
                            display_error(5)
                            return
            display_text('Comparison_results_Graphs1_2_3.txt')
            plot_options = ['None','Support - Changes in raw data',
                     'Support - Side Effects',
                     'Support - CPU time (sec)',
                     'Support - Information Loss (%)']
            plotDL.set_menu(*plot_options)
            bP.configure(state = NORMAL)
            bS.configure(state = NORMAL)
            bC.configure(state = NORMAL)
            bP.configure(state = NORMAL)
            bS.configure(state = NORMAL)
            bC.configure(state = NORMAL)
        else:
            display_error(11)
            return


def create_graphs_1_2_4_5(data, ax):
    global states
    global support
    step = 0
    if ":" in support.get():
        step = float(support.get().split(":")[-1])
        
    line_points_x = []
    line_points_y = []
    local_flag = True
    MX = 0
    MY = 0
    def_size = 8
    for i in xrange(len(states)):
        line_points_x.append([])
        line_points_y.append([])
    for i in xrange(len(states)):
        
        if states[i]:
            if local_flag:
                mX = data[i].keys()[0]
                mY = k = sum(data[i][mX])/len(data[i][mX])
                local_flag = False
            for j in sorted(data[i].keys()):
                k = sum(data[i][j])/len(data[i][j])
                line_points_x[i].append(j)
                line_points_y[i].append(k)
                
                if mX > j:
                    mX = j

                if MX < j:
                    MX = j

                if mY > k:
                    mY = k

                if MY < k:
                    MY = k

            if not(line_points_x[i] ==  [] or line_points_y[i] ==  []):
                ax.plot(line_points_x[i], line_points_y[i], marker = markers[i], color = colors[i], label = str(Algorithms[i]), lod = True, clip_on = False, markersize = def_size)
                ax.legend(prop = {'size':9})
                def_size -=  0.33

    
    
    if step != 0:
        ax.set_xlim(0, MX+2*step)
    else:
        ax.set_xlim(0, MX+(mX/2))
    
    
    ax.set_ylim(0, MY+(mY/2))

    ax.grid()
    canvas.figure = f
    canvas.draw()


def onSheet1():
    global Crd
    f.clf()
    ax = f.add_subplot(111)
    ax.set_xlabel("Support")
    ax.set_ylabel("Changes in Raw Data")
    colormap = plt.cm.gist_ncar
    f.gca().set_color_cycle([colormap(i) for i in linspace(0, 0.9, countTrues(states))])
    create_graphs_1_2_4_5(Crd, ax)
    
def onSheet2():
    global S_ef
    f.clf()
    ax = f.add_subplot(111)
    ax.set_xlabel("Support")
    ax.set_ylabel("Side Effects")
    colormap = plt.cm.gist_ncar
    f.gca().set_color_cycle([colormap(i) for i in linspace(0, 0.9, countTrues(states))])
    create_graphs_1_2_4_5(S_ef, ax)
    
    
def onSheet3():
    global T
    f.clf()
    ax = f.add_subplot(111)
    ax.set_xlabel("Support")
    ax.set_ylabel("CPU Time (sec)")
    colormap = plt.cm.gist_ncar
    f.gca().set_color_cycle([colormap(i) for i in linspace(0, 0.9, countTrues(states))])
    create_graphs_1_2_4_5(T, ax)
    
def onSheet4():
    global crd
    f.clf()
    ax = f.add_subplot(111)
    ax.set_ylabel("Changes in Raw Data")
    ax.set_xlabel("Number of Sensitive Itemsets")
    create_graphs_1_2_4_5(crd, ax)
      
    
def onSheet5():
    global s_ef
    f.clf()
    ax = f.add_subplot(111)
    ax.set_ylabel("Side Effects")
    ax.set_xlabel("Number of Sensitive Itemsets")
    create_graphs_1_2_4_5(s_ef, ax)
    
def onSheet6():
    global t
    f.clf()
    ax = f.add_subplot(111)
    #ax.set_xlabel("Length of Sensitive Itemset(s)")
    ax.set_ylabel("CPU Time (sec)")
    ax.set_xlabel("Number of Sensitive Itemsets")
    
    colormap = plt.cm.gist_ncar
    f.gca().set_color_cycle([colormap(i) for i in linspace(0, 0.9, countTrues(states))])
    create_graphs_1_2_4_5(t, ax)
    

def onSheet7():
    global inls
    f.clf()
    ax = f.add_subplot(111)
    ax.set_ylabel("Information Loss (%)")
    ax.set_xlabel("Number of Sensitive Itemsets")
    
    colormap = plt.cm.gist_ncar
    f.gca().set_color_cycle([colormap(i) for i in linspace(0, 0.9, countTrues(states))])
    create_graphs_1_2_4_5(inls, ax)
    

def onSheet8():
    global Inls
    f.clf()
    ax = f.add_subplot(111)
    ax.set_xlabel("Support")
    ax.set_ylabel("Information Loss (%)")
    colormap = plt.cm.gist_ncar
    f.gca().set_color_cycle([colormap(i) for i in linspace(0, 0.9, countTrues(states))])
    create_graphs_1_2_4_5(Inls, ax)

if __name__== '__main__':
    root = Tk()
    root.geometry('1200x700')
    root.title('Frequent Itemset Hiding Toolbox')
    root.config(bg = '#1F78B4')

    ####============== Left Side (Options) ==============####
    global text
    global Algorithms
    global states
    global fNames

    frame_style = ttk.Style()
    frame_style.configure("M.TFrame", background = '#1F78B4')

    inp_btn = ttk.Style()
    inp_btn.configure("In.TLabel", background = 'lightblue', font = ('arial', 10, 'italic'))

    inp_lab = ttk.Style()
    inp_lab.configure("In.TLabel", background = 'lightblue', font = ('arial', 8, 'italic'))

    frame_1 = ttk.Frame(root, style = "M.TFrame")
    frame_1.pack(side = LEFT)

    subframe_style = ttk.Style()
    subframe_style.configure("SM.TFrame", background = 'lightblue')

    sub_frame_1 = ttk.Frame(frame_1, style = "SM.TFrame")
    sub_frame_1.pack(side = LEFT, expand = YES, fill = X, padx = 10)

    labelfont = ('times', 10, 'bold')

    label_style = ttk.Style()
    label_style.configure("TLabel", background = 'lightblue', font = labelfont)

    label1 = ttk.Label(sub_frame_1, text = 'Select Data Mining Algorithm:')
    label1.pack(side = TOP, pady = 5)


    alg_1 = StringVar()
    alg_1.set(None)
    global opt1
    options = ['None', 'Apriori']
    opt1 = ttk.OptionMenu(sub_frame_1, alg_1, 'Apriori')#'None',*options)
    opt1.pack(side = TOP)

    label2 = ttk.Label(sub_frame_1, text = 'Read TIDs from File...')
    label2.pack(side = TOP, pady = 5)

    f_tid_name = None

    ttk.Button(sub_frame_1, 
           text = 'Select file', 
           command = lambda:get_TID_file_Name(), 
           style = 'In.TButton').pack(side = TOP)

    label6 = ttk.Label(sub_frame_1, text = f_tid_name, style = "In.TLabel")
    label6.pack(side = TOP)

    label4 = ttk.Label(sub_frame_1, text = 'Read Sensitive Set from File...')
    label4.pack(side = TOP, pady = 5)

    ttk.Button(sub_frame_1, 
           text = 'Select file', 
           command = lambda:get_Sens_file_Name(), 
           style = 'In.TButton').pack(side = TOP)

    f_sens_name = None

    label7 = ttk.Label(sub_frame_1, text = f_sens_name, style = "In.TLabel")
    label7.pack(side = TOP)

    label5 = ttk.Label(sub_frame_1, text = "Enter Support (e.g. 0.1, 0.2, ..):")
    label5.pack(side = TOP, pady = 5)

    support = DoubleVar()
    support = ttk.Entry(sub_frame_1)
    support.pack(side = TOP)


    label3 = ttk.Label(sub_frame_1, text = "")
    label3.pack(side = TOP)

    label3 = ttk.Label(sub_frame_1, text = "Select Hiding Algorithm:")
    label3.pack(side = TOP)

    #################### Implementing New Extendable Interface #########################
    Algorithms = ['Max-Min 1', 'Max-Min 2','WBA','Max-Accuracy', 'BBMax-Accuracy', 'Coeff. Max-Accuracy', 'Heuristic Coeff.']
    fNames = ['Max_Min_1', 'Max_Min_2', 'WBA', 'Max_Accuracy', 'BBMax_Accuracy', 'Coeff_Max_Accuracy', 'Heuristic_Coeff']

    ext_path = os.getcwd()+"\\Extensions"
    Extend = []

    for extension in glob(ext_path+"\*.py"):
        directory, module_name = os.path.split(extension)
        module_name = os.path.splitext(module_name)[0]
        Extend.append(module_name)
        
    Algorithms += Extend
    fNames += Extend

    numA = len(Algorithms)
    checkButtons = [0]*numA
    states = [False]*numA

    #colormap = plt.cm.gist_ncar
    #colors = [colormap(i) for i in linspace(0, 0.5, len(states))]
    #print(colors)

    sub_frame_1_2 = Frame(sub_frame_1)
    sub_frame_1_2.pack(pady = 5)
    sub_frame_1_2.config(bg = 'lightblue')

    chk_btn_style = ttk.Style()
    chk_btn_style.configure("TCheckbutton", background = 'lightblue', font = labelfont)
    for i in xrange(numA):    
        checkButtons[i] = ttk.Checkbutton(sub_frame_1_2, text = Algorithms[i], onvalue = 1, offvalue = 0, command = (lambda var = i:onPress(var)))
        checkButtons[i].invoke()
        checkButtons[i].invoke()
        checkButtons[i].pack(side = TOP, anchor = W, padx = 25)

    #####################################################################################

    mid_btn = ttk.Style()
    mid_btn.configure("SS.TButton", background = '#1F78B4', font = ('arial', 10, 'italic'))

    go_style = ttk.Style()
    go_style.configure("Go.TButton", foreground = '#1F78B4', font = ('arial', 12, 'bold'))

    help_style = ttk.Style()
    help_style.configure("Help.TButton", foreground = '#27AE60', font = ('arial', 12, 'italic'))

    reset_style = ttk.Style()
    reset_style.configure("Reset.TButton", foreground = '#E31A1C', font = ('arial', 12, 'italic'))

    Help = ttk.Button(sub_frame_1, text = "HELP", style = "Help.TButton", command = On_Help)
    Help.pack(padx = 20, pady = 5, side = BOTTOM)

    clear = ttk.Button(sub_frame_1, text = "RESET", style = "Reset.TButton", command  = destr)
    clear.pack(padx = 20, pady = 5, side = BOTTOM)

    go = ttk.Button(sub_frame_1, text = "GO", style = "Go.TButton", command = _Go)
    go.pack(padx = 20, pady = 5, side = BOTTOM)



    ####============== Menu Bar ==============####
    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1


    def Load():
        global f_tid_name
        global f_sens_name
        
        spec = askopenfilename()
        if file_len(spec) ==  3:
            fload = open(spec, 'rU')
            fields = fload.readlines()
            fload.close()
            f_tid_name = fields[0].strip('\n')
            try:
                float(f_tid_name)
            except Exception:
                label6.config(text = f_tid_name)
            else:
                display_error(6)
                return(False)

            
            f_sens_name = fields[1].strip('\n')
            try:
                float(f_sens_name)
            except Exception:
                label7.config(text = f_sens_name)
            else:
                display_error(7)
                return(False)
            
            if fields[2] ==  ' ':
                support.insert(0, '')
            else:
                try:
                    test = float(fields[2])
                except Exception:
                    display_error(8)
                    support.insert(0, '')
                else:
                    support.delete(0, len(support.get()))
                    support.insert(0, fields[2].strip('\n'))
           
            return(True)    
        else:
            display_error(9)
            return(False)
                        
    def About():
        errmsg = "Frequent Itemset Hiding Toolbox\nCopyright Vasileios Kagklis, 2015"
        showinfo('About', errmsg)
        
    def Give(dp, mySup, sens_fname):
        global f_tid_name
        global f_sens_name
        f_tid_name = dp
        label6.config(text = dp.split("\\")[-1])
        f_sens_name = sens_fname
        label7.config(text = sens_fname.split("\\")[-1])
        support.delete(0, END)
        support.insert(0, mySup)

    def Update(menumbar):
        menubar.delete(0, END)
        Mount(menubar)
        helpmenu = Menu(menubar, tearoff = 0)
        helpmenu.add_command(label = "Help", command = On_Help)
        helpmenu.add_command(label = "About...", command = About)
        menubar.add_cascade(label = "Help", menu = helpmenu)

    def Mount(menubar):
        path = os.getcwd()+"\Datasets"
        datasets = Menu(menubar, tearoff = 0)
        dataset_menu = None
        sup_menu = None
        for folder in glob(path+"\*"):                  # Folders with ds name
            dataset = folder.split("\\")
            dataset = dataset[len(dataset)-1]
            dpath = folder
            
            if len(glob(dpath+"\\*.csv")) >= 1:
                dpath += "\\"+dataset+".csv"
            elif len(glob(dpath+"\\*.ssv")) >= 1:
                dpath += "\\"+dataset+".ssv"
            else:
                dpath += "\\"+dataset+"."+glob(dpath+"\\"+dataset+".*")[0].split("\\")[-1].split(".")[-1]
                
            dataset_menu = Menu(datasets, tearoff = 0)
            for subfolder in glob(folder+"\*"):         # Subfolders with support
                mySup = subfolder.split("\\")
                mySup = mySup[len(mySup)-1]
                #print(subfolder)
                try:
                    float(mySup)
                    sup_menu = Menu(dataset_menu, tearoff = 0)
                    for ssf in glob(subfolder+"\*"):              # Subsubfolders with Ss
                        sens_fname = ssf.split("\\")
                        sens_fname = sens_fname[len(sens_fname)-1]
                        #print(ssf)
                        sup_menu.add_command(label = sens_fname, command = lambda dpath = dpath, mySup = mySup, ssf = ssf:Give(dpath, mySup, ssf))
                    dataset_menu.add_cascade(label = str(mySup), menu = sup_menu)
                except:
                    continue
            
            datasets.add_cascade(label = str(dataset), menu = dataset_menu)

        datasets.add_cascade(label = "Update Datasets", command = lambda menubar = menubar:Update(menubar))
        menubar.add_cascade(label = "Datasets", menu = datasets)

    menubar = Menu(root)
    Mount(menubar)

    helpmenu = Menu(menubar, tearoff = 0)
    helpmenu.add_command(label = "Help", command = On_Help)
    helpmenu.add_command(label = "About...", command = About)
    menubar.add_cascade(label = "Help", menu = helpmenu)
    root.config(menu = menubar)



    ####============== Middle strip (Text Editor) ==============####
    frame_2 = Frame(root)
    frame_2.pack(side = LEFT, expand = YES, fill = X, padx = 20)
    frame_2.config(bg = '#1F78B4')

    sub_frame_3 = Frame(frame_2)
    sub_frame_3.pack(side = TOP)
    sub_frame_3.config(bg = '#1F78B4')

    ##=======   Text editor     =======##
    sbar = Scrollbar(sub_frame_3)
    text = Text(sub_frame_3, width = 42, height = 30, relief = SUNKEN)
    sbar.config(command = text.yview)
    text.config(yscrollcommand = sbar.set)
    sbar.pack(side = RIGHT, fill = Y)
    text.pack(side = RIGHT, expand = YES, fill = BOTH)
    text.config(bg = '#ffffcc', fg = 'black', font = ('times', 10, 'bold'))
    display_first('\n\tResults will be displayed here...')

    global sub_frame_6
    sub_frame_6 = Frame(frame_2)
    sub_frame_6.pack(side = BOTTOM, pady = 5)
    sub_frame_6.config(bg = '#1F78B4')

    ##=======   Text editors' buttons   =======##
    B1 = ttk.Button(sub_frame_6, text = 'Open', command = onOpen, style = "SS.TButton")
    B1.pack(side = LEFT, padx = 5)
    B2 = ttk.Button(sub_frame_6, text = 'Save', command = onSave, style = "SS.TButton")
    B2.pack(side = LEFT, padx = 5)
    B3 = ttk.Button(sub_frame_6, text = 'Find', style = "SS.TButton")
    B3.pack(side = LEFT, padx = 5)



    ####============== Right Side (matplot area) ==============####
    frame_3 = Frame(root)
    frame_3.pack(side = LEFT, expand = YES, fill = X, padx = 20)
    frame_3.config(bg = '#1F78B4')
    sub_frame_4 = Frame(frame_3)
    sub_frame_4.pack(side = TOP)

    ##=======   f for figures    =======##
    global f
    f = Figure(figsize = (7.5, 7.5), dpi = 85, facecolor = 'white')

    ##=======   Main canvas    =======##
    global canvas
    canvas = FigureCanvasTkAgg(f, master = sub_frame_4)
    canvas.show()
    canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)


    ##=======   Subframe with droplist + plot, save, clear  =======##
    sub_frame_5 = Frame(frame_3)
    sub_frame_5.pack(side = BOTTOM, pady = 5)
    sub_frame_5.config(bg = '#1F78B4')

    ##=======   Droplist + figure buttons   =======##
    global plotDL;global bP;global bS;global bC;global plotOpt
    plotOpt = StringVar()
    plotOpt.set(None)

    plotDL = ttk.OptionMenu(sub_frame_5, plotOpt)
    plotDL.pack(side = LEFT, padx=4)
    bP = ttk.Button(sub_frame_5, text = 'Plot', command = myPlot)
    bP.pack(side = LEFT, padx = 4)
    bP.configure(state = DISABLED)
    bS = ttk.Button(sub_frame_5, text = 'Save', command = mySave)
    bS.pack(side = LEFT, padx = 4)
    bS.configure(state = DISABLED)
    bC = ttk.Button(sub_frame_5, text = 'Clear', command = myClear)
    bC.pack(side = LEFT, padx = 4)
    bC.configure(state = DISABLED)



    ####==============   Ask before quitting     ==============####
    def ask_quit():
        if askokcancel("Quit", "Do you really want to quit?"):
            root.withdraw()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", ask_quit)
    root.mainloop()

