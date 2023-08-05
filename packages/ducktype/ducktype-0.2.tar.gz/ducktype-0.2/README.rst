********
Ducktype
********

.. image:: https://pypip.in/v/ducktype/badge.png
        :target: https://pypi.python.org/pypi/ducktype


Provides *isducktype*, a simple function to check ducktype.


Routine* 'A' is ducktype of 'B' when:
  - 'A' number of arguments is compatible with 'B' (names not checked)
  - OR A or B have varargs (*args) or keywords (**kwargs)

Arguments comparison between A and B is made within:
  - the number of required arguments to call A is between minimum and maximum number of B arguments
  - OR the number maximum of arguments to call A is between minimum and maximum number of B arguments

required arguments means all arguments without defaults

Object/Class 'A' is ducktype of 'B' when:
  - it has at least same public members names (public if they don't start by '_')
  - AND its methods are ducktypes of corresponding B methods.

If B has a method __ducktypecheck__, *isducktype* returns B.__ducktypecheck__(A)


Like *isinstance* or *issubclass*, *isducktype* second argument can be either an objet or a tuple of objects.


Routine* in the sense: a user defined or builtins, function, method, or lambda.

---------------------------------------------------------------------

**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none


=============
Installation
=============

Install it from pypi::

  pip install ducktype

or from sources::

  git clone git@github.com:apieum/ducktype.git
  cd ducktype
  python setup.py install

=====
Usage
=====

--------------------------------
Example 1 - comparing functions:
--------------------------------


.. code-block:: python

  from ducktype import isducktype

  func_a = lambda a1, a2, a3=None: None
  func_b = lambda *b1: None
  func_c = lambda **c2: None
  func_d = lambda d1, d2: None
  func_e = lambda e1: None
  func_f = lambda f1, f2, f3, f4: None

  assert isducktype(func_b, func_a)
  assert isducktype(func_c, func_a)
  assert isducktype(func_d, func_a)
  assert isducktype(func_a, func_e) is False
  assert isducktype(func_e, func_a) is False
  assert isducktype(func_f, func_a) is False

  # with a tuple (== Or)
  assert isducktype(func_e, (func_a, func_b))
  assert isducktype(func_e, (func_a, func_d)) is False

--------------------------------
Example 2 - comparing objects:
--------------------------------


.. code-block:: python


  from ducktype import isducktype

  class A(object):
    _protected = 'hidden'
    __private  = 'hidden'
    attr1 = None

    def method1(self, arg, kwargs=True):
      return kwargs

    def method2(self, arg):
      return arg

  class B(object):
    attr1 = None

    def method1(self, **kwargs):
      return kwargs

    def method2(self, arg1, arg2=None):
      return None

  class C(object):
    attr1 = False

    def method1(self, arg, kwarg):
      return arg

  class D(object):
    attr1 = False
    method1 = None
    method2 = None

  class E(object):
    def method1(self, **kwargs):
      return kwargs

    def method2(self, arg1, arg2=None):
      return None

  # it doesn't care if it's an instance or a class
  assert isducktype(A, B)
  assert isducktype(A(), B)
  assert isducktype(A, B())
  assert isducktype(A(), B())

  # You can call each A method as if it was C
  assert isducktype(A, C)
  # Reverse is not True
  assert isducktype(C, A) is False

  # Whereas D as same members as A, two are not functions
  assert isducktype(A, D) is False
  assert isducktype(D, A) is False

  # E need attribute "attr1" to ducktype A
  assert isducktype(A, E)
  assert isducktype(E, A) is False

--------------------------------
Example 3 - overriding default:
--------------------------------


.. code-block:: python


  from ducktype import isducktype

  class A(object):
    attr1 = None

  class B(object):
    attr1 = None
    attr2 = None

  class C(B):
    @classmethod
    def __ducktypecheck__(cls, maybe_duck):
      return hasattr(maybe_duck, 'attr1')

  class D(B):
    def __ducktypecheck__(self, maybe_duck):
      return hasattr(maybe_duck, 'attr1')

  # A must not ducktype B
  assert isducktype(A, B) is False

  # Returns A.__ducktypecheck__(C)
  assert isducktype(A, C)
  assert isducktype(A, D) is False
  assert isducktype(A, D())


===========
Development
===========

Any feedback or help is welcome.
You can contact me by mail: apieum [at] gmail [dot] com


Launch test::

  git clone git@github.com:apieum/ducktype.git
  cd ducktype
  nosetests --with-spec --spec-color ./




.. image:: https://secure.travis-ci.org/apieum/ducktype.png?branch=master
   :target: https://travis-ci.org/apieum/ducktype
