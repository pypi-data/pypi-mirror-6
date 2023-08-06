# -*- encoding: utf-8 -*-
'''Implementation of the Needleman-Wunsch algorithm based on a code
snippet found at
http://www.dzone.com/snippets/needleman-wunsch-back-track.  The
following description is taken from that page (accessed 2013-03-21):

The Needleman-Wunsch algorithm performs a global alignment of two
sequences (of length n and m) For a given similarity matrix s
(containing the penalties for character match-mismatch) and a LINEAR
gap penalty the algorithm is guaranteed to find the alignment with
highest score (in O(nm) time).  The algorithm is outlined through
comments to the source.
'''
try:
    import numpy as np
except ImportError:
    np = None

from sys import *
from collections import deque

class Gap(object):
    def __eq__(self, other):
        return (isinstance(other, Gap))

    def __repr__(self):
        return '<Gap>'

def demo_penalty(left, right):
    if Gap() in (left, right):
        return -1.
    if left == right:
        return 1.
    return -1.

def needle(seq1, seq2, penalty_func):
    rows=len(seq1)+1
    cols=len(seq2)+1

    if np is None:
        #use a list if we have to
        a=[]
        for i in range(rows):
            a+=[[0.]*cols]
    else:
        #use fast numerical arrays if we can
        a=np.zeros((rows,cols),float)
        
        
    for i in range(rows):
        a[i][0] = 0
    for j in range(cols):
        a[0][j] = 0
    for i in range(1,rows):
        for j in range(1,cols):
            # Dynamic programing -- aka. divide and conquer:
            # Since gap penalties are linear in gap size
            # the score of an alignment of length l only depends on the   
            # the l-th characters in the alignment (match - mismatch - gap)
            # and the score of the one shorter (l-1) alignment,
            # i.e. we can calculate how to extend an arbritary alignment
            # soley based on the previous score value.  
            choice1 = a[i-1][j-1] + penalty_func(seq1[i-1], seq2[j-1])
            choice2 = a[i-1][j] + penalty_func(seq1[i-1], Gap())
            choice3 = a[i][j-1] + penalty_func(Gap(), seq2[j-1])
            a[i][j] = max(choice1, choice2, choice3)

				
    aseq1 = []
    aseq2 = []
    #We reconstruct the alignment into aseq1 and aseq2, 
    i = len(seq1)
    j = len(seq2)
    while i>0 and j>0:
    #     if i%10==0:
    #         stderr.write('.')

    #by performing a traceback of how the matrix was filled out above,
    #i.e. we find a shortest path from a[n,m] to a[0,0]
        score = a[i][j]
        score_diag = a[i-1][j-1]
        score_up = a[i][j-1]
        score_left = a[i-1][j]
        if score == score_diag + penalty_func(seq1[i-1],  seq2[j-1]):
            aseq1.append(seq1[i-1])
            aseq2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif score == score_left + penalty_func(seq1[i-1], Gap()):
            aseq1.append(seq1[i-1])
            aseq2.append(Gap())
            i -= 1
        elif score == score_up + penalty_func(Gap(), seq2[j-1]):
            aseq1.append(Gap())
            aseq2.append(seq2[j-1])
            j -= 1
        else:
            #should never get here.
            i=0
            j=0
            aseq1='ERROR';aseq2='ERROR';seq1='ERROR';seq2='ERROR'

    while i>0:
        #If we hit j==0 before i==0 we keep going in i.
        aseq1.append(seq1[i-1])
        aseq2.append(Gap())
        i -= 1		

    while j>0:
        #If we hit i==0 before i==0 we keep going in j. 
        aseq1.append(Gap())
        aseq2.append(seq2[j-1])
        j -= 1

    aseq1.reverse()
    aseq2.reverse()
    return a, aseq1, aseq2

#To reconstruct all alignments is somewhat tedious..
def make_graph(seq1, seq2, a, penalty_func):
#the simplest way is to make a graph of the possible constructions of the values in a 
    rows, cols = getattr(a, 'shape', (len(a), len(a[0])))
    graph={}
    for i in range(1,rows)[::-1]:
        graph[(i,0)] = [(i-1,0)]
        graph[(0,i)] = [(0,i-1)]
        for j in range(1,cols)[::-1]:
            graph[(i,j)]=deque()
            score = a[i][j]
            score_diag = a[i-1][j-1]
            score_up = a[i][j-1]
            score_left = a[i-1][j]
            if score == score_diag + penalty_func(seq1[i-1], seq2[j-1]):
                graph[(i,j)].append((i-1,j-1))
            if score == score_left + penalty_func(seq1[i-1], Gap()):
                graph[(i,j)].append((i-1,j))
            if score == score_up + penalty_func(Gap(), seq2[j-1]):
                graph[(i,j)].append((i,j-1))
    return graph

def find_all_paths(graph, start, end, path=[]):
#and then to recursively find all paths 
#from bottom right to top left..
    path = path + [start]
#    print start
    if start == end:
        yield path
    if start in graph:
        for node in graph[start]:
            if node not in path:
                for newpath in find_all_paths(graph, node, end, path):
                    yield newpath

def backtrack(seq1, seq2, a, penalty_func):
    #################################################
    #################################################
    ##              Full backtrack                 ##
    #################################################

    rows, cols = getattr(a, 'shape', (len(a), len(a[0])))
    graph=make_graph(seq1, seq2, a, penalty_func)
    tracks=find_all_paths(graph,(rows-1,cols-1),(0,0))

    for track in tracks:
        baseq1 = deque()
        baseq2 = deque()
        last_step=(rows-1,cols-1)
        for step in track[1:]:
            i,j=last_step
            if i==step[0]:
                baseq1.append(Gap())
                baseq2.append(seq2[j-1])
            elif j==step[1]:
                baseq1.append(seq1[i-1])
                baseq2.append(Gap())
            else:
                baseq1.append(seq1[i-1])
                baseq2.append(seq2[j-1])

            last_step=step

        yield list(reversed(baseq1)), list(reversed(baseq2))

def main():
    seq1='GAGACCGCCATGGCGACCCTGGAAAAGCTGATGAAGGCCCT'
    seq2='AGACCCAATGCGACCCTGAAAAAGCTGATGAAGGCCTTTTT'

    # Both sequences are similar to the human protein huntingtin. 
    # Spurious expanded trinucleotide (CGA) repeats in this protein 
    # cause it to aggregate in neurons leading to Huntington's disease. 

    # The Needleman-Wunsch algorithm performs a global alignment of
    # two sequences (of length n and m). For a given similarity matrix
    # s (containing the penalties for character match-mismatch) and a
    # LINEAR gap penalty the algorithm is guaranteed to find the
    # alignment with highest score (in O(nm) time).  The algorithm is
    # outlined through comments to the source.

    a, aseq1, aseq2 = needle(seq1, seq2, demo_penalty)
    return backtrack(seq1, seq2, a, demo_penalty)

if __name__ == '__main__':
    main()
