# coding: utf8
'''
Name: mzsudoku

mzsudoku.run('207006100000...', options) # 81 characters
-- or --
Use mzsudoku.py as script

(r) option partially from
http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/

help(mzsudoku.run) or see run() code for details
''' 

import sys
import itertools

sudoku = ""   # last state

finished = False
failure = False

def same_row(i,j): return (i/9 == j/9)
def same_col(i,j): return (i-j) % 9 == 0
def same_block(i,j): return (i/27 == j/27 and i%9/3 == j%9/3)

def fill(number, row, col):
    '''will set number to the given position and then continue .run()
    works for suspended solution: mzsudoku.sudoku must exist 
    in mzsudoku.sudoku must be '0' on the given position
    row,col - 1..9
    '''
    if sudoku:
        pos = 9*(row-1)+col-1
        number = str(number)[-1:]
        if not number in '123456789':
            print 'digit 1..9 required as first parameter'
            return
        global sudoku
        if sudoku[pos]=='0':
            sudoku = sudoku[:pos] + number + sudoku[pos+1:]
            print sudoku 
        else:
            print "not '0' on required position"
    else:
        print "not suspended; run .run() first"

def run(setting, options='tnr'):
    '''setting: 81-characters string (or more with spaces; spaces will be removed),
              0 for unknown numbers
    options:
     (t) show table (w/wo possibilities [see K]
     (n) find n-combinations
     (r) find result(r)
    in addition to tnr, options can contain:
     (k) show unknown-possibilities and definitely known numbers (tk)
     (K) definitely known numbers only (tK)
        ((t) without k/K will show unknown-possibilities only)
     (a) apply known new numbers after pressing Enter (anything else will quit)
     (A) apply known new numbers and cycle again
    '''
    
    global sudoku
    setting = setting or sudoku
    setting = setting.replace(' ', '') 
    if len(setting)!=81:
        print 'string with 81 positions required (0 for unknown digits)'
        return
    
    marked_by_N = {}
    while True:
        hidden_singles = []
        marked = p(setting, marked_by_N)    # mark possibilities
        n(marked, options, hidden_singles, marked_by_N)
                                            # localize hidden n-combinations
        if finished:
            print
            print "FINISHED."
            break
        if failure:
            print
            print "FAILURE IN SETTING."
            break
        if not 'a' in options.lower():
            break
        setting2 = apply_known(setting, marked, hidden_singles)
        if setting==setting2:
            print ("Cannot find algorithmical solution. "
                      "Try set something with .fill() method.")
            break
        if user_break(options):
            break
        setting = setting2
    sudoku = setting
    if '0' in sudoku:
        print "suspended; use .fill(digit, row, col) and/or .run('', options)"
    print sudoku
    if 'r' in options and '0' in sudoku:
        #http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/
        r(setting)   # solve based on recursive algorithmus from link above

def user_break(options):
    if 'A' in options:
        print "\n==== next iteration ====\n"
        return False
    return raw_input(
             "press Enter for next iteration (something else + enter to stop)") 

def p(a, marked_by_N):
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
            if marked_by_N:
                set_by_N = marked_by_N.get(i)
                if set_by_N:
                    excluded_numbers = excluded_numbers.union(set_by_N)  
            marked.append(excluded_numbers)
            finished = False
        else:
            marked.append(a[i])
    return marked

def n(marked, options, hidden_singles, marked_by_N):
    '''print where n-sets are inside possibilities'''

    def pp(marked, options):
        '''print marked possibilities'''

        def psub(subln, row, marked, options):

            def ppvertsep():
                print '|',
            
            def pplinesep():
                print

            def ppskip():
                print ' ',
            
            def pppossible(subnum):
                print subnum, 
            
            def ppfixed(symbol, options):
                if 'K' in options:
                    print '  %s  ' % symbol,
                elif 'k' in options:
                    print ' = %s ' % symbol,
                else:
                    ppspace()
            
            def ppspace():
                print 5*' ',
    
            show_poss = not 'K' in options
            for cl in xrange(36):
                subcl = cl%4
                if subcl:
                    pos = 9*row + cl/4
                    if isinstance(marked[pos], set):
                        subnum = str(3*(subln-1) + subcl)
                        if not show_poss or subnum in marked[pos]:
                            ppskip()
                        else:
                            pppossible(subnum) 
                    elif subcl==1:
                        if subln==2:
                            ppfixed(marked[pos], options)
                        else:
                            ppspace()
                else:
                    ppvertsep()
            ppvertsep()
            pplinesep()
        
        def ppl():
            print 9*'+-------' + '+'
                       
        if 't' in options:
            for ln in xrange(36):
                row = ln/4
                subln = ln%4 
                if subln:
                    psub(subln, row, marked, options)
                else:
                    ppl()
            ppl()

    print_result = 'n' in options
    used_groups = 0
    hidden_groups = []
    while True:
        pp(marked, options)           # print possibilities as table
        to_print = []
        for ln in xrange(9):
            block_pos = []
            block = []
            excluded = []
            for cl in xrange(9):
                pos = 9*ln + cl
                if isinstance(marked[pos], set):
                    block.append(marked[pos])
                    block_pos.append(pos)
                else:
                    excluded.append(marked[pos])
            solveN('ln%s'%(ln+1), block, excluded, used_groups, hidden_groups, 
                  block_pos, hidden_singles, to_print, marked, print_result)
        for cl in xrange(9):
            block_pos = []
            block = []
            excluded = []
            for ln in xrange(9):
                pos = 9*ln + cl
                if isinstance(marked[pos], set):
                    block.append(marked[pos])
                    block_pos.append(pos)
                else:
                    excluded.append(marked[pos])
            solveN('cl%s'%(cl+1), block, excluded, used_groups, hidden_groups,         
                  block_pos, hidden_singles, to_print, marked, print_result)         
        for bl in xrange(9):
            block_pos = []
            hor = bl/3
            vert = bl%3 
            block = []
            excluded = []
            for ln in xrange(3*hor, 3*(hor+1)):
                for cl in xrange(3*vert, 3*(vert+1)):
                    pos = 9*ln + cl
                    if isinstance(marked[pos], set):
                        block.append(marked[pos])
                        block_pos.append(pos)
                    else:
                        excluded.append(marked[pos])
            solveN('bl%s'%(bl+1), block, excluded, used_groups, hidden_groups,
                  block_pos, hidden_singles, to_print, marked, print_result)         
        if print_result and to_print:      
            print "hidden n-combinations"
            print ("[as naked <=> where / digits / field position "
                            "(unknown fields counted)]:")
            for line in to_print:
                for item in line:
                    print item,
                print
        naked_count = naked_singles(marked)
        print "naked singles  : ", naked_count 
        print "hidden singles : ", len(hidden_singles) 
        if hidden_singles or naked_count or used_groups>=len(hidden_groups):
            break
        # we have (more) hidden_groups and it is necessary to use them
        # (symbol, candidate, where, lenN, block_pos, included, cnt_naked)
        if not used_groups:
            hidden_groups.sort(key=lambda item:item[6]) # cnt_naked
            print "no easy solution - can try apply N-groups"
        while used_groups<len(hidden_groups): 
            hidden_group = hidden_groups[used_groups]                    
            removed = set()
            for where1 in hidden_group[2]:      # hidden_group[2] === where
                pos = hidden_group[4][where1-1] # hidden_group[4] === block_pos 
                for number in hidden_group[5]:  # hidden_group[5] === included
                    if not number in hidden_group[1] and not number in marked[pos]:
                                                # hidden_group[1] === candidate 
                        removed.add(number)
                        marked[pos].add(number)
                        if not marked_by_N.has_key(pos):
                            marked_by_N[pos] = set()
                        marked_by_N[pos].add(number)
            used_groups += 1
            if removed:
                if print_result:
                    print hidden_group[0], hidden_group[1], hidden_group[2], 'removed:', removed
                        # symbol, candidate, where
                break
            # if nothing changed, apply next N-group (if any)
        if user_break(options):
            used_groups = 0  # don't write about help of N-groups 
            break
    if used_groups:
        if used_groups>=len(hidden_groups):
            print "seems, no help received from N-groups"
        else:
            print "seems, N-groups helped us to continue" 

def naked_singles(marked):
    cnt = 0
    for fld in marked:
        if len(fld)==8:
            cnt += 1
    return cnt

def solveN(symbol, block, excluded, used_groups, hidden_groups,
          block_pos, hidden_singles, to_print, marked, print_result):
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
                print_append = [symbol, candidate, where]
                cnt_naked = len(block)-len(where) # visible as naked N-th                 
                if len(where)==1:
                    to_append = (candidate, block_pos[where[0]-1])
                    if not to_append in hidden_singles: 
                        hidden_singles.append(to_append)
                elif not used_groups:
                    hidden_groups.append((symbol, candidate, where,
                                lenN, block_pos, included, cnt_naked))
                if len(where)<lenN:
                    failure = True
                    print_append.insert(0, 13*' ')
                    print_append.append(
                                'WARNING: in %s fields only' % len(where))
                else:
                    print_append.insert(0, 'naked %s  <=> ' % cnt_naked)
                to_print.append(print_append)

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

def apply_known(setting, marked, hidden_singles):
    # apply naked singles
    setting2 = ''
    for i, fld in enumerate(marked):
        if len(fld)==8:
            for number in '123456789':
                if not number in fld:
                    setting2 += number
                    break
            continue   # setting2 enlarged already
        setting2 += setting[i]

    # apply hidden singles (obtained from n())
    for candidate, pos in hidden_singles:
        if setting2[pos]=='0':
            setting2 = setting2[:pos] + candidate[0] + setting2[pos+1:]    

    return setting2

if __name__ == '__main__':
    if len(sys.argv)>=2 and len(sys.argv[1]) == 81:
        run(sys.argv[1], len(sys.argv)>=3 and sys.argv[2] or 'tnr')
    else:
        print 'Usage: python sudoku.py puzzle'
        print '''  where puzzle is an 81 character string 
               representing the puzzle read left-to-right,
               top-to-bottom, and 0 is a blank'''