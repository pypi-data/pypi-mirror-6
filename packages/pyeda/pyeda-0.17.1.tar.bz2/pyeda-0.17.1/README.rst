Python Electronic Design Automation
===================================

PyEDA is a Python library for electronic design automation.

`Read the docs! <http://pyeda.rtfd.org>`_

.. image:: https://travis-ci.org/cjdrake/pyeda.png?branch=master
   :target: https://travis-ci.org/cjdrake/pyeda

Features
--------

* Symbolic Boolean algebra with a selection of function representations:

  * Logic expressions
  * Truth tables, with three output states (0, 1, "don't care")
  * Reduced, ordered binary decision diagrams (ROBDDs)
  * Fast, disjunctive/conjunctive normal form logic expressions

* SAT solvers:

  * Backtracking
  * DPLL
  * `PicoSAT <http://fmv.jku.at/picosat>`_

* Formal equivalence
* Multi-dimensional bit vectors
* DIMACS CNF/SAT parsers
* Logic expression parser

Download
--------

Bleeding edge code::

    $ git clone git://github.com/cjdrake/pyeda.git

For release tarballs and zipfiles,
visit PyEDA's page at the
`Cheese Shop <https://pypi.python.org/pypi/pyeda>`_.

Installation
------------

Latest released version using
`setuptools <http://pythonhosted.org/setuptools>`_::

    $ easy_install pyeda

Latest release version using
`pip <http://www.pip-installer.org/en/latest>`_::

    $ pip install pyeda

Installation from the repository::

    $ python setup.py install

Getting Started With Logic Expressions
--------------------------------------

Invoke your favorite Python terminal,
and invoke an interactive ``pyeda`` session::

    >>> from pyeda.inter import *

Create some Boolean expression variables::

    >>> a, b, c, d = map(exprvar, "abcd")

Construct Boolean functions using overloaded Python operators:
``-`` (NOT), ``+`` (OR), ``*`` (AND), ``>>`` (IMPLIES)::

    >>> f0 = -a * b + c * -d
    >>> f1 = a >> b
    >>> f2 = -a * b + a * -b
    >>> f3 = -a * -b + a * b
    >>> f4 = -a * -b * -c + a * b * c
    >>> f5 = a * b + -a * c

Construct Boolean functions using standard function syntax::

    >>> f10 = Or(And(Not(a), b), And(c, Not(d)))
    >>> f11 = Implies(a, b)
    >>> f12 = Xor(a, b)
    >>> f13 = Xnor(a, b)
    >>> f14 = Equal(a, b, c)
    >>> f15 = ITE(a, b, c)

Construct Boolean functions using higher order operators::

    >>> f20 = Nor(a, b, c)
    >>> f21 = Nand(a, b, c)
    >>> f22 = OneHot(a, b, c)
    >>> f23 = OneHot0(a, b, c)

Investigate a function's properties::

    >>> f0.support
    frozenset([a, b, c, d])
    >>> f0.inputs
    (a, b, c, d)
    >>> f0.top
    a
    >>> f0.degree
    4
    >>> f0.cardinality
    16
    >>> f0.depth
    2

Factor complex expressions into only OR/AND and literals::

    >>> f11.factor()
    a' + b
    >>> f12.factor()
    a' * b + a * b'
    >>> f13.factor()
    a' * b' + a * b
    >>> f14.factor()
    a' * b' * c' + a * b * c
    >>> f15.factor()
    a * b + a' * c

Restrict a function's input variables to fixed values,
and perform function composition::

    >>> f0.restrict({a: 0, c: 1})
    b + d'
    >>> f0.compose({a: c, b: -d})
    c' * d' + c * d'

Test function formal equivalence::

    >>> f2.equivalent(f12)
    True
    >>> f4.equivalent(f14)
    True

Investigate Boolean identities::

    # Law of double complement
    >>> --a
    a

    # Idempotent laws
    >>> a + a
    a
    >>> a * a
    a

    # Identity laws
    >>> a + 0
    a
    >>> a * 1
    a

    # Dominance laws
    >>> a + 1
    1
    >>> a * 0
    0

    # Commutative laws
    >>> (a + b).equivalent(b + a)
    True
    >>> (a * b).equivalent(b * a)
    True

    # Associative laws
    >>> a + (b + c)
    a + b + c
    >>> a * (b * c)
    a * b * c

    # Distributive laws
    >>> (a + (b * c)).to_cnf()
    (a + b) * (a + c)
    >>> (a * (b + c)).to_dnf()
    a * b + a * c

    # De Morgan's laws
    >>> Not(a + b).factor()
    a' * b'
    >>> Not(a * b).factor()
    a' + b'

    # Absorption laws
    >>> (a + (a * b)).absorb()
    a
    >>> (a * (a + b)).absorb()
    a

Perform Shannon expansions::

    >>> a.expand(b)
    a * b' + a * b
    >>> (a * b).expand([c, d])
    a * b * c' * d' + a * b * c' * d + a * b * c * d' + a * b * c * d

Convert a nested expression to disjunctive normal form::

    >>> f = a * (b + (c * d))
    >>> f.depth
    3
    >>> g = f.to_dnf()
    >>> g
    a * b + a * c * d
    >>> g.depth
    2
    >>> f.equivalent(g)
    True

Convert between disjunctive and conjunctive normal forms::

    >>> f = -a * -b * c + -a * b * -c + a * -b * -c + a * b * c
    >>> g = f.to_cnf()
    >>> h = g.to_dnf()
    >>> g
    (a + b + c) * (a + b' + c') * (a' + b + c') * (a' + b' + c)
    >>> h
    a' * b' * c + a' * b * c' + a * b' * c' + a * b * c

Getting Started With Multi-Dimensional Bit Vectors
--------------------------------------------------

Create some four-bit vectors, and use slice operators::

    >>> A = bitvec('A', 4)
    >>> B = bitvec('B', 4)
    >>> A
    [A[0], A[1], A[2], A[3]]
    >>> A[2:]
    [A[2], A[3]]
    >>> A[-3:-1]
    [A[1], A[2]]

Perform bitwise operations using Python overloaded operators:
``~`` (NOT), ``|`` (OR), ``&`` (AND), ``^`` (XOR)::

    >>> ~A
    [A[0]', A[1]', A[2]', A[3]']
    >>> A | B
    [A[0] + B[0], A[1] + B[1], A[2] + B[2], A[3] + B[3]]
    >>> A & B
    [A[0] * B[0], A[1] * B[1], A[2] * B[2], A[3] * B[3]]
    >>> A ^ B
    [Xor(A[0], B[0]), Xor(A[1], B[1]), Xor(A[2], B[2]), Xor(A[3], B[3])]

Reduce bit vectors using unary OR, AND, XOR::

    >>> A.uor()
    A[0] + A[1] + A[2] + A[3]
    >>> A.uand()
    A[0] * A[1] * A[2] * A[3]
    >>> A.uxor()
    Xor(A[0], A[1], A[2], A[3])

Create and test functions that implement non-trivial logic such as arithmetic::

    >>> from pyeda.logic.addition import *
    >>> S, C = ripple_carry_add(A, B)
    # Note "1110" is LSB first. This says: "7 + 1 = 8".
    >>> S.vrestrict({A: "1110", B: "1000"}).to_uint()
    8

Other Function Representations
------------------------------

Consult the `documentation <http://pyeda.rtfd.org>`_ for information on
normal form expressions, truth tables, and binary decision diagrams.
Each function representation has different trade-offs,
so always use the right one for the job.

Execute Unit Test Suite
-----------------------

If you have `Nose <http://nose.readthedocs.org/en/latest>`_ installed,
run the unit test suite with the following command::

    $ make test

If you have `Coverage <https://pypi.python.org/pypi/coverage>`_ installed,
generate a coverage report (including HTML) with the following command::

    $ make cover

Perform Static Lint Checks
--------------------------

If you have `Pylint <http://www.logilab.org/857>`_ installed,
perform static lint checks with the following command::

    $ make lint

Build the Documentation
-----------------------

If you have `Sphinx <http://sphinx-doc.org>`_ installed,
build the HTML documentation with the following command::

    $ make html

Python Versions Supported
-------------------------

PyEDA is developed using Python 3.2+.
It is **NOT** compatible with Python 2.7.

Contact the Authors
-------------------

* Chris Drake (cjdrake AT gmail DOT com), http://cjdrake.blogspot.com
