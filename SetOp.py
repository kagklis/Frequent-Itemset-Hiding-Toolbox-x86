#-------------------------------------------------------------------------------
# Name:        SetOp.py
# Purpose:     Implements set-operation functions
# Author:      Vasileios Kagklis
# Created:     14/05/2014
# Copyright:   (c) Vasileios Kagklis
#-------------------------------------------------------------------------------
def minSet(S):
    temp = set()
    i=0
    while i<len(S)-1:
        j=i+1
        while j<len(S):
            if (S[j].issuperset(S[i])):
                temp.add(S[j])
            elif(S[i].issuperset(S[j])):
                temp.add(S[i])
            j += 1
        i += 1

    return(set(S)-temp)


def supersets(s_set,f_set):
    smax=set()
    for x in s_set:
        for y in f_set:
            if x.issubset(y):
                smax.add(y)
    return(smax)
