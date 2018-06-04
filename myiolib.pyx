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
