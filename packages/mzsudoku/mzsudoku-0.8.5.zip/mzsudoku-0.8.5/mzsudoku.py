# coding: utf8
'''
Name: mzsudoku
partially from http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/

Use mzsudoku.py as script
-- or --
mzsudoku.run('207006100000...') # 81 characters
or .run() subparts: .p(), .pp(), .n(), .r()
help(mzsudoku.run) or see run() code for details
''' 

import sys
import itertools

finished = False
failure = False

def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
def same_block(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

def run(setting, out='pnr'):
    '''setting 81-characters string, 0 for unknown numbers
    out: mark possibilities(p), find n-combinations(n), find result(r)
    in addition to pnr, out cat contain:
     = show definitely known numbers (otherwise show only unknown-possibilities)
     A apply known new numbers and cycle again
     a apply known new numbers after pressing Enter (anything else will quit)
    
    TODO: for a/A, ie. in apply_known, at this time naked singletons will apply
      only. We need to apply hidden combinations (obtained from n()) at least 
    '''
    while True:
        marked = p(setting)          # mark possibilities
        if 'p' in out:
            pp(marked, '=' in out)  # print possibilities as table
        if 'n' in out:
            n(marked)               # localize hidden n-combinations
        if 'r' in out:
            r(setting)           # solve based on original recursive algorithmus
        if finished:
            print
            print "FINISHED."
        if failure:
            print
            print "FAILURE IN SETTING."
        if not 'a' in out.lower():
            break
        setting2 = apply_known(setting, marked)
        if setting==setting2:
            break
        if 'a' in out and raw_input(): 
            break
        setting = setting2

def p(a):
    '''mark possibilities'''
    global finished
    finished = True
    marked = []
    for i in xrange(81):
        if a[i]=='0':
            excluded_numbers = set()
            for j in xrange(81):
                if a[j]!='0' and (
                          same_row(i,j) or same_col(i,j) or same_block(i,j)):
                    excluded_numbers.add(a[j])
            marked.append(excluded_numbers)
            finished = False
        else:
            marked.append(a[i])
    return marked

def n(marked):
    '''print where n-sets are inside possibilities'''
    first = True
    for ln in xrange(9):
        block = []
        excluded = []
        for cl in xrange(9):
            pos = 9*ln + cl
            if isinstance(marked[pos], set):
                block.append(marked[pos])
            else:
                excluded.append(marked[pos])
        first = solveN('ln%s'%(ln+1), block, excluded, first)         
    for cl in xrange(9):
        block = []
        excluded = []
        for ln in xrange(9):
            pos = 9*ln + cl
            if isinstance(marked[pos], set):
                block.append(marked[pos])
            else:
                excluded.append(marked[pos])
        first = solveN('cl%s'%(cl+1), block, excluded, first)         
    for bl in xrange(9):
        hor = bl/3
        vert = bl%3 
        block = []
        excluded = []
        for ln in xrange(3*hor, 3*(hor+1)):
            for cl in xrange(3*vert, 3*(vert+1)):
                pos = 9*ln + cl
                if isinstance(marked[pos], set):
                    block.append(marked[pos])
                else:
                    excluded.append(marked[pos])
        first = solveN('bl%s'%(bl+1), block, excluded, first)

def solveN(symbol, block, excluded, first):
    #print symbol, len(block), excluded
    global failure
    included = []
    for number in '123456789':
        if not number in excluded:
            included.append(number)
    for lenN in xrange(len(block)-1, 0, -1):
        for candidate in itertools.combinations(included, lenN):
            where = []
            for i, fld in enumerate(block):
                for number in candidate:
                    if number not in fld:
                        where.append(i+1)
                        break
                if len(where)>lenN:
                    break
            else:
                if first:
                    print "hidden n-combinations"
                    print ("[where / which numbers / field position "
                            "(from unknown only)]:")
                    first = False
                print symbol, candidate, where,
                if len(where)<lenN:
                    print 'WARNING: in %s fields only' % len(where)
                    failure = True
                else:
                    print
    return first  

def pp(marked, show_fixed=False):
    '''print marked possibilities'''
    for ln in xrange(36):
        row = ln/4
        subln = ln%4 
        if subln:
            psub(subln, row, marked, show_fixed)
        else:
            ppl()
    ppl()

def psub(subln, row, marked, show_fixed=False):
    for cl in xrange(36):
        subcl = cl%4
        if subcl:
            pos = 9*row + cl/4
            if isinstance(marked[pos], set):
                subnum = str(3*(subln-1) + subcl)
                if subnum in marked[pos]:
                    ppskip()
                else:
                    pppossible(subnum) 
            elif subcl==1:
                if subln==2:
                    ppfixed(marked[pos], show_fixed)
                else:
                    ppspace()
        else:
            ppvertsep()
    ppvertsep()
    pplinesep()

def ppl():
    print 9*'+-------' + '+'
               
def ppskip():
    print ' ',

def pppossible(subnum):
    print subnum, 

def ppvertsep():
    print '|',

def pplinesep():
    print

def ppfixed(symbol, show_fixed=False):
    if show_fixed:
        #print '* %s *' % symbol,
        #print ' _%s_ ' % symbol,
        print ' = %s ' % symbol,
    else:
        ppspace()

def ppspace():
    print 5*' ',

def r(a):
    '''find solution
    from http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/
    mz change: #mz'''
    i = a.find('0')
    if i == -1:
        print a
        return
  
    excluded_numbers = set()
    for j in xrange(81):
        #mz ++  a[j] and (....)  to avoid '0' in excluded_numbers  
        if a[j]!='0' and (
                      same_row(i,j) or same_col(i,j) or same_block(i,j)):
            excluded_numbers.add(a[j])
  
    for m in '123456789':
        if m not in excluded_numbers:
            r(a[:i]+m+a[i+1:])

def apply_known(setting, marked):
    setting2 = ''
    for i, fld in enumerate(marked):
        if len(fld)==8:
            for number in '123456789':
                if not number in fld:
                    setting2 += number
                    break
            continue   # setting2 enlarged already
        setting2 += setting[i]
    return setting2

if __name__ == '__main__':
    if len(sys.argv)>=2 and len(sys.argv[1]) == 81:
        run(sys.argv[1], len(sys.argv)>=3 and sys.argv[2] or 'pnr')
    else:
        print 'Usage: python sudoku.py puzzle'
        print '''  where puzzle is an 81 character string 
               representing the puzzle read left-to-right,
               top-to-bottom, and 0 is a blank'''