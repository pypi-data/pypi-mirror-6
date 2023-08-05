# sudoku

## code: *mzsudoku.py*

In oposite to other sudoku modules this one gives to you a possibility solve step by step.
So instead of just see the result you can f.e. find all possibilities and then continue in manual work. 

usage: python mzsudoku.py 81-characters options

81-characters - 1..9 or 0 for unknown

options (any combination of p, n, r, a|A, = ; default is: pnr)
- p print possibilities as table
- n find hidden n-combinations
- r find solution and print result
- a apply known and run next cycle after pressing Enter
- A apply known and run next cycle immediately
- = show fixed numbers in p table (otherwise they are left blank)

r option: from http://freepythontips.wordpress.com/2013/09/01/sudoku-solver-in-python/

r option will return
- first result only if there are more solutions
- nothing if there is no solution

### example
python mzsudoku.py 020080700..... pnra=

means:
- write all (pnr),
- apply known and continue after Enter (a),
- show already fixed numbers (=)

TODO: at this time a|A can only set naked single numbers (from possibilities table);
  we need to implement more from
  - naked n-combinations (p section) - such numbers can be removed from other positions in line/column/block
  - hidden placing of single number (r section) - such number is sure
  
Info: There are puzzles, which cannot be solved by finding of naked/hidden n-combinations.
In such case (and in more cases while a|A doesn't implement all knowledge - see TODO) code will finish before solution.

Info: If a|A iterations will not lead to the solution, you can change the starting command
to use more knowledges (see TODO)
or to try some fork, f.e. if in '0' position you have possibilities (2,5)
you can try: '2'->'0' and later '5'->'0'.    


## text in czech language:

cz: Návod, jak úspěšně vyluštit jakékoli klasické Sudoku.

en: How to find solution for Sudoku game. Full description in czech language. 