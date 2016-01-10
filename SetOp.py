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
