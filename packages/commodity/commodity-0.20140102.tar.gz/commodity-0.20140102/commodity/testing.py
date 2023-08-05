# -*- coding:utf-8; tab-width:4; mode:python -*-

import time
import types

import hamcrest
from hamcrest.core.matcher import Matcher as hamcrest_Matcher
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.string_description import StringDescription
from hamcrest.core.assert_that import _assert_bool

from .type_ import checked_type
from .deco import add_attr


def assert_that(arg1, arg2=None, arg3=''):
    if isinstance(arg2, hamcrest_Matcher):
        _assert_match(actual=arg1, matcher=arg2, reason=arg3)
    else:
        _assert_bool(assertion=arg1, reason=arg2)


def _assert_match(actual, matcher, reason):
    if not matcher.matches(actual):
        description = StringDescription()
        # print
        # print reason
        # print "-1 <%s>" % description.append_text(reason)
        # print matcher
        # print matcher.__class__
        # print dir(matcher)
        # print "-2 <%s>" % description.append_description_of(matcher)
        # print "-3 <%s>" % matcher.describe_mismatch(actual, description)
        # print

        description.append_text(reason)     \
            .append_text('\n  Expected: ') \
            .append_description_of(matcher) \
            .append_text('\n  But: ')
        matcher.describe_mismatch(actual, description)
        raise AssertionError(str(description))


@add_attr('default_delta', 1)
@add_attr('default_timeout', 5)
def wait_that(item, matcher, reason='', delta=None, timeout=None):
    '''
    Poll the given matcher each 'delta' secs until matches 'item' or
    'timeout' is reached. Default 'delta' and 'timeout' can be
    globally set with fucntion atributes:

    >>> wait_that.default_delta = 0.5
    >>> wait_that.defautl_timeout = 6
    '''

    delta = delta or wait_that.default_delta
    timeout = timeout or wait_that.default_timeout

    exc = None
    init = time.time()
    timeout_reached = False
    while 1:
        try:
            if time.time() - init > timeout:
                timeout_reached = True
                break

            _assert_match(item, matcher, reason)
            break

        except AssertionError as e:
            time.sleep(delta)
            exc = e

    if timeout_reached:
        msg = exc.args[0] + ' after {0} seconds'.format(timeout)
        exc.args = msg,
        raise exc


class Matcher(BaseMatcher):
    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text('it is not')


class __nothing__(object):
    pass


class call_with(BaseMatcher):
    '''
    >>> assert_that(abs, call_with(-2))
    >>> assert_that(abs, call_with(-2).returns(2))
    '''
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.expected = __nothing__
        self.actual = None
        self.exc = None

    def returns(self, expected=__nothing__):
        self.expected = expected
        return self

    def _matches(self, func):
        self._func = func
        try:
            self.actual = self._func(*self.args, **self.kargs)
        except Exception as e:
            self.exc = e
            return False

        self.exc = None
        if self.expected is __nothing__:
            return True

        return hamcrest.is_(self.expected).matches(self.actual)

    def describe_to(self, description):
        class_ = get_class_that_defined_method(self._func)
        classname = (str(class_.__name__) + '.') if class_ else ''

        description.append_text(
            "{0}{1}(*{2}, **{3}) should return '{4}'".format(
                classname, self._func.__name__, self.args, self.kargs, self.expected))

    def describe_mismatch(self, item, description):
        if self.exc is None:
            description.append_text("was '%s'" % self.actual)
        else:
            description.append_text("raises '%s'" % self.exc)


# http://stackoverflow.com/questions/961048/get-class-that-defined-method
def get_class_that_defined_method(method):
    method_name = method.__name__
    if not hasattr(method, '__self__'):
        return None

    if method.__self__:
        classes = [method.__self__.__class__]
    else:
        #unbound method
        classes = [method.im_class]

    while classes:
        c = classes.pop()
        if method_name in c.__dict__:
            return c

        classes = list(c.__bases__) + classes

    return None
