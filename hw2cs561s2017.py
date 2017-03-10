import os, sys, itertools
from copy import copy 
import time
start_time = time.time()

inputFilePath = os.path.dirname(os.path.realpath(__file__)) + "/SampleTestCases/input16.txt"
outputFilePath = os.path.dirname(os.path.realpath(__file__)) + "/SampleTestCases/output.txt"

def formatDict(d):
    result = []
    for k,v in d.iteritems():
        if v:
            val = k.split('_')
            result.append([int(val[0]),int(val[1])])
    return result

def symbl(l):
    if l[0] == '~':
        return l[1:]
    return l

def nt(l):
    if l[0] == '~':
        return l[1:]
    return "~"+l

def remove(item, seq):
    if isinstance(seq, str):
        return seq.replace(item, '')
    else:
        return [x for x in seq if x != item]

def extend(d, var, val):
    dd = d.copy()
    dd[var] = val
    return dd

def evaluateClause(clause,model):
    flag = False
    for c in clause:
        if c not in model and nt(c) not in model:
            flag = True
        elif symbl(c) in model and model[symbl(c)] == (c[0] != '~'):
            return True
    if flag:
        return None
    return False

def dpll(clauses, symbols, model):
    unknown_clauses = []
    for c in clauses:
        val = evaluateClause(c, model)
        if val is False: return False
        if val is not True: unknown_clauses.append(c)
    if not unknown_clauses: return model
    P, value = findPureSymbol(symbols, unknown_clauses)
    if P: return dpll(clauses, remove(P, symbols), extend(model, P, value))
    P, value = findUnitClause(clauses, model)
    if P: return dpll(clauses, remove(P, symbols), extend(model, P, value))
    
    P, symbols = symbols[0], symbols[1:]
    
    return (dpll(clauses, symbols, extend(model, P, True)) or
            dpll(clauses, symbols, extend(model, P, False)))

def findPureSymbol(symbols, clauses):
    for s in symbols:
        found_pos, found_neg = False, False
        for c in clauses:
            if not found_pos and s in c: found_pos = True
            if not found_neg and nt(s) in c: found_neg = True
        if found_pos != found_neg: return s, found_pos
    return None, None

def findUnitClause(clauses, model):
    for clause in clauses:
        nm = 0
        for l in clause:
            sym = symbl(l)
            if sym in model and model[sym] == (l[0] != '~'):
                return None, None
            if sym not in model:
                nm += 1
                P, value = sym, (l[0] != '~')
        if nm == 1:
            return P, value
    return None, None


def readInput(fileName):
    clauses = set()
    literals = set()
    with open(fileName,'r') as f:
        lines = f.readlines()
        lineCount = len(lines)
        firstLine = lines[0].strip().split(' ')
        nGuest,nTable = int(firstLine[0]),int(firstLine[1]) #m,n
        if nGuest == 0 or nTable == 0:
            return (None,None)
        
        # Case 1a - Guest g should be seated on at least 1 table
        for g in range(1,nGuest + 1):
            guest = str(g)
            clause = [guest + "_1"]
            for t in range(2,nTable + 1):
                clause.append(guest + "_" + str(t))
                literals.add(guest + "_" + str(t))
            clauses.add(tuple(sorted(clause)))
            
        # Case 1b - Guest g should be seated on at most 1 table
        for g in range(1,nGuest+1):
            guest = "~" + str(g)
            for ti in range(1,nTable+1):
                for tj in range(ti+1,nTable+1):
                    tup = (guest + "_" + str(ti), guest + "_" + str(tj))
                    literals.add(str(g) + "_" + str(ti))
                    literals.add(str(g) + "_" + str(tj))
                    clauses.add(tuple(sorted(tup)))

        frnd,enmy = set(),set()
        for k in range(1,lineCount):
            line = lines[k].strip().split(' ')
            i,j,rel = int(line[0]),int(line[1]),line[2]
            if rel == "F":
                frnd.add((i,j))
            elif rel == "E":
                enmy.add((i,j))

        # Case 2 - Friends
        for t in range(1,nTable+1):        
            for f in frnd:
                guest = str(f[0]) + "_" + str(t)
                friend = str(f[1]) + "_" + str(t)
                literals.add(guest)
                literals.add(friend)
                tup1,tup2 = (nt(guest),friend),(nt(friend),guest)
                clauses.add(tuple(sorted(tup1)))
                clauses.add(tuple(sorted(tup2)))

        # Case 3 - Enemies
        for t in range(1,nTable+1):        
            for e in enmy:
                guest = str(e[0]) + "_" + str(t)
                enemy = str(e[1]) + "_" + str(t)
                literals.add(guest)
                literals.add(enemy)
                tup = (nt(guest),nt(enemy))
                clauses.add(tuple(sorted(tup)))
                
    return (clauses,literals)


kb,symb = readInput(inputFilePath)

if kb:
    res = dpll(kb, list(symb), {})
else:
    res = False

with open(outputFilePath,'w') as f:
    if not res:
        print 'no'
        f.write('no\n')
    else:
        print 'yes'
        f.write('yes\n')
        asgn = formatDict(res)
        for a in sorted(asgn):
            print a[0],a[1]
            f.write(str(a[0]) + ' ' + str(a[1]) + '\n')

print("--- %s seconds ---" % (time.time() - start_time))
