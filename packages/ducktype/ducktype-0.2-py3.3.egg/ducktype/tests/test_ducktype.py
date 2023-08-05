# -*- coding: utf8 -*-
from unittest import TestCase
from mock import Mock
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
    attr1 = False
    def method1(self, arg, kwarg):
        return arg

class C(object):
    attr1 = None

    def method1(self, **kwargs):
        return kwargs

    def method2(self, arg1, arg2=None):
        return None

class D(object):
    attr1 = False
    method1 = None
    method2 = None


class DuckTypeTest(TestCase):
    def setUp(self):
        self.bird = Mock()

    def test_an_object_ducktype_another_when_its_methods_have_at_least_same_number_of_args(self):
        self.assertTrue(isducktype(A, C))
        self.assertTrue(isducktype(A(), C))
        self.assertTrue(isducktype(A, C()))
        self.assertTrue(isducktype(A(), C()))

    def test_an_object_ducktype_another_when_it_has_at_least_same_public_members_names(self):
        self.assertTrue(isducktype(A, B))
        self.assertTrue(isducktype(A(), B))
        self.assertTrue(isducktype(A, B()))
        self.assertTrue(isducktype(A(), B()))

    def test_an_object_dont_ducktype_another_when_its_methods_are_just_attr(self):
        self.assertFalse(isducktype(A, D))
        self.assertFalse(isducktype(D, A))

    def test_a_routine_ducktype_another_when_it_has_same_number_of_args(self):
        func_a = lambda a1, a2=None: None
        func_b = lambda b1: None
        func_c = lambda c1, c2: None

        self.assertFalse(isducktype(func_b, func_c))
        self.assertFalse(isducktype(func_c, func_b))
        self.assertTrue(isducktype(func_b, func_a))
        self.assertTrue(isducktype(func_a, func_b))
        self.assertTrue(isducktype(func_c, func_a))
        self.assertTrue(isducktype(func_a, func_c))

    def test_when_a_routine_as_varargs_or_keywords_its_always_a_duck_type(self):
        func_a = lambda *a1: None
        func_b = lambda **b1: None
        func_c = lambda *c1, **c2: None
        func_d = lambda d1, d2, d3: None

        self.assertTrue(isducktype(func_a, func_d))
        self.assertTrue(isducktype(func_b, func_d))
        self.assertTrue(isducktype(func_c, func_d))

    def test_it_calls_ducktypecheck_if_object_got_it(self):
        duck, typecheck = self.a_duck_with_type_check(True)
        isducktype(self.bird, duck)

        typecheck.assert_called_once_with(self.bird)

    def test_if_cls_is_tuple_test_until_one_is_true(self):
        duck1, typecheck1 = self.a_duck_with_type_check(False)
        duck2, typecheck2 = self.a_duck_with_type_check(True)
        duck3, typecheck3 = self.a_duck_with_type_check(True)
        isducktype(self.bird, (duck1, duck2, duck3))

        typecheck1.assert_called_once_with(self.bird)
        typecheck2.assert_called_once_with(self.bird)
        self.assertFalse(typecheck3.called)

    def a_duck_with_type_check(self, returns=True):
        duck = Mock()
        typecheck = Mock(return_value=returns)
        duck.attach_mock(typecheck, '__ducktypecheck__')
        return duck, typecheck
