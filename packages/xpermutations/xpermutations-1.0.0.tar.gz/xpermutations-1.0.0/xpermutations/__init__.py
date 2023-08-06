"""
xpermutations.py

http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465

Generators for calculating a) the permutations of a sequence and
b) the combinations and selections of a number of elements from a
sequence. Uses Python 2.2 generators.

Similar solutions found also in comp.lang.python

Keywords: generator, combination, permutation, selection

See also: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/105962
See also: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66463
See also: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66465

This recipe provides both combinations and permutations and lazily
generates them. You can do arbitrary calculations on the
permutation/combination items not just print them.

If you require the complete list of permutations, just use the
built-in list() operator. Note that the resulting list can be huge.

All x-generators defined here yield sequences with elements from the
original sequence. Their difference is in which elements they take:

xpermutations takes all elements from the sequence, order matters.

xcombinations takes n distinct elements from the sequence,
order matters.

xuniqueCombinations takes n distinct elements from the sequence,
order is irrelevant.

xselections takes n elements (not necessarily distinct) from the
sequence, order matters.

Note that 'distinct' means "different elements in the orginal
sequence" and not "different value", i.e.

list(xuniqueCombinations('aabb',2)) is

[['a', 'a'], ['a', 'b'], ['a', 'b'], ['a', 'b'], ['a', 'b'], ['b', 'b']]

and not

[['a', 'b']].

If your sequence has only items with unique values, you won't
notice the difference (no pun intended).

Code in this file is by Ulrich Hoffmann
(Creative Commons Attribution 3.0 license).
"""

from _version import __version__

__all__ = ["xcombinations", "xuniqueCombinations",
           "xselections", "xpermutations"]


def xcombinations(items, n):
  """xcombinations takes n distinct elements from the sequence,
  order matters.
  """
  if n==0: yield []
  else:
    for i in xrange(len(items)):
      for cc in xcombinations(items[:i]+items[i+1:],n-1):
        yield [items[i]]+cc

def xuniqueCombinations(items, n):
  """xuniqueCombinations takes n distinct elements from the sequence,
  order is irrelevant.
  """
  if n==0: yield []
  else:
    for i in xrange(len(items)-n+1):
      for cc in xuniqueCombinations(items[i+1:],n-1):
        yield [items[i]]+cc

def xselections(items, n):
  """xselections takes n elements (not necessarily distinct) from the
  sequence, order matters.
  """
  if n==0: yield []
  else:
    for i in xrange(len(items)):
      for ss in xselections(items, n-1):
        yield [items[i]]+ss

def xpermutations(items):
  """xselections takes n elements (not necessarily distinct) from the
  sequence, order matters.
  """
  return xcombinations(items, len(items))

def test():
    print "Permutations of 'love'"
    for p in xpermutations(['l','o','v','e']): print ''.join(p)

    print
    print "Combinations of 2 letters from 'love'"
    for c in xcombinations(['l','o','v','e'],2): print ''.join(c)

    print
    print "Unique Combinations of 2 letters from 'love'"
    for uc in xuniqueCombinations(['l','o','v','e'],2): print ''.join(uc)

    print
    print "Selections of 2 letters from 'love'"
    for s in xselections(['l','o','v','e'],2): print ''.join(s)

    print
    print map(''.join, list(xpermutations('done')))
