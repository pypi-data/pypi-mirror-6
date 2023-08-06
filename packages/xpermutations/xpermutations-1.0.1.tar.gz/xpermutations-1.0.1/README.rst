===============
 xpermutations 
===============


Introduction
------------

This package is made from the `xpermutations recipe`_
submitted to ActiveState by Ulrich Hoffman.

The documentation provided therein follows and is assumed
to be under the Creative Commons Attribution 3.0 license.

Install with pip or easy_install::

   sudo pip install xpermutations


Recipe Documentation (Ulrich Hoffman)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Permutations and combinations are often required in algorithms
that do a complete search of the solution space. They are
typically rather large so it's best not to compute them
entirely but better to lazily generate them. This recipe
uses Python 2.2 generators to create appropriate generator
objects, that can be use for example as ranges in for loops.

This recipe provides both combinations and permutations and lazily
generates them. You can do arbitrary calculations on the
permutation/combination items not just print them.

If you require the complete list of permutations, just use the
built-in list() operator. Note that the resulting list can be huge.

All x-generators defined here yield sequences with elements from the
original sequence. Their difference is in which elements they take:

*xpermutations()* takes all elements from the sequence, order matters.

*xcombinations()* takes n distinct elements from the sequence,
order matters.

*xuniqueCombinations()* takes n distinct elements from the sequence,
order is irrelevant.

*xselections()* takes n elements (not necessarily distinct) from the
sequence, order matters.

Note that 'distinct' means "different elements in the orginal
sequence" and not "different value", i.e.::

     >>> list(xuniqueCombinations('aabb', 2))
     [['a', 'a'], ['a', 'b'], ['a', 'b'], ['a', 'b'], ['a', 'b'], ['b', 'b']]

Compare the latter to::

     >>> all_different = list(set('aabb'))
     >>> list(xuniqueCombinations(all_different, 2))
     [['a', 'b']]

If your sequence has only items with unique values, you won't
notice the difference (no pun intended).

Caveats
~~~~~~~

Set theoreticians may take issue with the nomenclature.


Home Page & Repository
----------------------

Home Page: https://pypi.python.org/pypi/xpermutations/

Repository: https://github.com/jcstroud/xpermutations/


Examples
--------

xcombinations()
~~~~~~~~~~~~~~~

    >>> " ".join("".join(x) for x in xcombinations("1234", 2))
    '12 13 14 21 23 24 31 32 34 41 42 43'

xuniqueCombinations()
~~~~~~~~~~~~~~~~~~~~~

    >>> " ".join("".join(x) for x in xuniqueCombinations("1234", 2))
    '12 13 14 23 24 34'

xselections()
~~~~~~~~~~~~~

    >>> " ".join("".join(x) for x in xselections("1234", 2))
    '11 12 13 14 21 22 23 24 31 32 33 34 41 42 43 44'

xpermutations()
~~~~~~~~~~~~~~~

    >>> " ".join("".join(x) for x in xpermutations("123"))
    '123 132 213 231 312 321'


.. _`xpermutations recipe`: http://code.activestate.com/recipes/190465-generator-for-permutations-combinations-selections/

