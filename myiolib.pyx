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
# Name:        myiolib.pyx
# Purpose:     Implements functions to read data
# Author:      Vasileios Kagklis
# Created:     12/12/2013
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
def readDataset(TID_name):
    
    cdef:
        list TID=[]
        int line_count=0

    delimiter = ' '
    if TID_name.split('\\')[-1].split(".")[-1] == "csv" or TID_name.split('/')[-1].split(".")[-1] == "csv":
        delimiter = ','

    with open(TID_name, 'rU') as file_iter:
        for line in file_iter:
            line_count=line_count+1
            TID.append(set(line.strip().split(delimiter)))
        
    return(line_count,TID)

def readSensitiveSet(file_name):

    cdef list S = []
    
    delimiter = ' '    
    if file_name.split('\\')[-1].split(".")[-1] == "csv" or file_name.split('/')[-1].split(".")[-1] == "csv":
        delimiter = ','

    with open(file_name, 'rU') as file_iter:
        for line in file_iter:
            S.append(frozenset(line.strip().split(delimiter)))
        
    return(S)


def readLargeData(file_name):
    cdef dict F = {}
    cdef list record = []

    delimiter = ' '
    if file_name.split('\\')[-1].split(".")[-1] == "csv" or file_name.split('/')[-1].split(".")[-1] == "csv":
        delimiter = ','
        
    with open(file_name, 'rU') as file_iter:
        for line in file_iter:
            line = line.split(delimiter)
            F[frozenset(line[0:-1])] = float(line[-1])

    return(F)
