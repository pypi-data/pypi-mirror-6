from __future__ import absolute_import, with_statement

import inspect
import logging
import os
import re
import shutil
import tempfile
from collections import defaultdict
from contextlib import contextmanager

try:
    basestring
except NameError:
    basestring = str

log = logging.getLogger(__name__)


def eq(a, b, text=None):
    """Assert that `a == b` and raise a helpful error if not

    :param a: The first thing to compare.
    :param b: The second thing to compare.
    :param text: Optional text to include in the error if `a != b`.


    Usage:

        >>> eq(1, 1)
        >>> eq("long string of text", "long string of test")
        Traceback (most recent call last):
          ...
        AssertionError: not equal
        'long string of text'
        'long string of test'
        >>> eq("a", "b", "oops!")
        Traceback (most recent call last):
          ...
        AssertionError: oops! : 'a' != 'b'
    """
    if a != b:
        if callable(text):
            text = text()
        if len(repr(a)) > 20 or len(repr(b)) > 20:
            if text is None:
                text = "not equal"
            err = "%s\n%r\n%r" % (text, a, b)
        else:
            text = (str(text) + " : ") if text is not None else ""
            err = "%s%r != %r" % (text, a, b)
        raise AssertionError(err)

eq_ = eq # For compatibility with nose. Not sure why they do that.


class Config(object):
    """A configuration object whose members are accessible via key or attribute

    This is useful for configuring nose generator tests.

    Usage:

        >>> cfg = Config(value=1, other="a")
        >>> cfg.value
        1
        >>> cfg["value"]
        1
        >>> cfg
        (other='a', value=1)
        >>> cfg(xyz=3)
        (other='a', value=1, xyz=3)
        >>> assert cfg is not cfg()
        >>> eq(cfg(), cfg)
        >>> eq(cfg(xyz=3), cfg(xyz=4))
        Traceback (most recent call last):
          ...
        AssertionError: not equal
        (other='a', value=1, xyz=3)
        (other='a', value=1, xyz=4)
    """
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)
    def __iter__(self):
        return iter(self.__dict__.items())
    def __call__(self, **kw):
        return Config(self.__dict__, **kw)
    def __contains__(self, name):
        return name in self.__dict__
    def __getitem__(self, name):
        return self.__dict__[name]
    def _get(self, name, default=None):
        return getattr(self, name, default)
    def __eq__(self, other):
        return (issubclass(type(other), type(self))
            and self.__dict__ == other.__dict__)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __len__(self):
        return len(self.__dict__)
    def __repr__(self):
        val = ", ".join("%s=%r" % kv for kv in sorted(self.__dict__.items()))
        return "(%s)" % val


@contextmanager
def replattr(*args, **kw):
    """Temporarly replace attribute(s)

    A context manager that temporarily replaces attributes (or values
    when in dict mode) on an object or objects. All attributes (or
    values) are replaced with their original values when the context
    manager exits.

    Usage:

        >>> obj = Config(attrname="abc")
        >>> with replattr(obj, "attrname", "val"):
        ...     # do stuff with obj. obj.attrname is val
        ...     eq(obj.attrname, "val")
        ...
        >>> eq(obj.attrname, "abc")

        >>> foo = Config(attr_a=1)
        >>> bar = Config(attr_b=2)
        >>> with replattr(
        ...         (foo, "attr_a", "a"),
        ...         (bar, "attr_b", "b"),
        ...     ):
        ...     eq(foo.attr_a, "a")
        ...     eq(bar.attr_b, "b")
        ...
        >>> eq(foo.attr_a, 1)
        >>> eq(bar.attr_b, 2)

        >>> mapping = {"key": "value"}
        >>> with replattr(mapping, "key", 1, dict=True):
        ...     eq(mapping["key"], 1)
        ...
        >>> eq(mapping["key"], "value")

        >>> def fake_exists(arg): return arg
        >>> with replattr(os.path, "exists", fake_exists, sigcheck=False):
        ...     eq(os.path.exists("foo"), "foo")
        ...
        >>> eq(os.path.exists("foo"), False)
    """
    sigcheck = kw.pop('sigcheck', True)
    dict_replace = kw.pop('dict', False)
    if kw:
        raise ValueError('unrecognized keyword arguments: %s' % ', '.join(kw))
    if len(args) == 3 and isinstance(args[1], basestring):
        args = [args]
    errors = []
    temps = []
    for obj, attr, value in args:
        try:
            temp = obj[attr] if dict_replace else getattr(obj, attr)
            if sigcheck and (inspect.isfunction(temp) or inspect.ismethod(temp)):
                as0 = inspect.getargspec(temp)
                as1 = inspect.getargspec(value)
                if as0 != as1:
                    errors.append("%s%s != %s%s" % (
                        temp.__name__, inspect.formatargspec(*as0),
                        value.__name__, inspect.formatargspec(*as1),
                    ))
            temps.append(temp)
            if dict_replace:
                obj[attr] = value
            else:
                setattr(obj, attr, value)
        except Exception as ex:
            rtype = 'key' if dict_replace else 'attribute'
            log.error("cannot replace %s: %s", rtype, attr, exc_info=True)
            errors.append(str(ex))
    try:
        yield
    finally:
        for (obj, attr, value), temp in zip(args, temps):
            if dict_replace:
                obj[attr] = temp
                if obj[attr] is not temp:
                    errors.append("%r is not %r" % (obj[attr], temp))
            else:
                setattr(obj, attr, temp)
                if getattr(obj, attr) is not temp:
                    errors.append("%r is not %r" % (getattr(obj, attr), temp))
    assert not errors, "\n".join(errors)


def assert_raises(exception, *args, **kw):
    """Assert that an exception is raised

    :param exception: An exception or tuple of exceptions. Must be
    specified as a positional argument.
    :param function: Optional function that should raise an exception.
    Must be specified as a positional argument.
    :param *args: Optional function arguments (only if `function`
    parameter is given).
    :param **kwargs: Optional function keyword arguments (only if
    `function` parameter is given).
    :param msg: Optional exception message verifier. Must be passed as
    a keyword argument to the context manager. May be one of the
    following:
    
        - A string matching the exception message exactly.
        - A compiled `re` object matching the raised exception using
          `msg.search(str(exc))`.
        - An exception instance, which must equal the raised exception.
        - A callable that is called with the raised exception as its
          single argument.

    If any of the above do not match the raised exception or raise an
    exception themselves, then the assertion will fail.


    Usage:

        >>> # functional form
        >>> assert_raises(ValueError, int, "value")

        >>> # context manager
        >>> with assert_raises(ValueError):
        ...     int("value")
        ...
    """
    if not args:
        msg = kw.pop('msg', None)
        if kw:
            raise AssertionError('invalid kwargs: %r' % (kwargs,))
        @contextmanager
        def raises():
            if exception is None:
                yield
                return
            try:
                yield
                raise AssertionError('%s not raised' % (exception,))
            except exception as err:
                if isinstance(msg, basestring):
                    eq_(str(err), msg)
                elif isinstance(msg, BaseException):
                    eq_(err, msg)
                elif hasattr(msg, 'search'):
                    assert msg.search(str(err)), \
                        '%r does not match %r' % (msg.pattern, str(err))
                elif msg is not None:
                    msg(err)
            except Exception as err:
                log.error("unexpected error", exc_info=True)
                raise AssertionError(
                    "%s != %s" % (type(err).__name__, exception.__name__))
        return raises()
    else:
        with assert_raises(exception):
            args[0](*args[1:], **kw)


class CaptureLogging(object):
    """Capture logging output

    Usage:

        In module being tested
        >>> log = logging.getLogger(__name__)

        In test
        >>> import testil as mod
        >>> with CaptureLogging(mod) as log:
        ...     # do stuff that logs stuff
        ...     mod.log.info("message")
        ...     eq(log.data, {"info": ["message"]})
    """

    def __init__(self, module, log_attribute="log"):
        self.log = getattr(module, log_attribute)
        self.module = module
        self.data = defaultdict(list)

    def __getattr__(self, name):
        def log(message, *args, **kw):
            getattr(self.log, name)(message, *args, **kw)
            exc_info = kw.pop("exc_info", None)
            assert not kw, "unrecognized keyword args: %s" % (kw,)
            if args:
                message = message % args
            if exc_info is not None:
                message += "\nexc_info = %r" % (exc_info,)
            self.data[name].append(message)
        log.__name__ = name
        return log

    def __enter__(self):
        self.context = replattr(self.module, "log", self)
        self.context.__enter__()
        return self

    def __exit__(self, *args):
        self.context.__exit__(*args)


class Regex(object):
    """A regular expression object that can be used to match strings

    Usage:

        >>> ob = object()
        >>> rx = Regex("^<object .+>$")
        >>> eq(repr(ob), rx)
        >>> eq("<object>", rx)
        Traceback (most recent call last):
          ...
        AssertionError: not equal
        '<object>'
        Regex('^<object .+>$')
    """

    def __init__(self, expression, *args, **kw):
        self.repr = kw.pop("repr", None)
        self.expr = re.compile(expression, *args, **kw)
        self.expression = expression

    def __repr__(self):
        if self.repr is not None:
            return self.repr
        return "Regex(%r)" % (self.expression,)

    def __str__(self):
        return self.expression

    def __eq__(self, other):
        return self.expr.search(other)

    def __ne__(self, other):
        return not self.__eq__(other)


@contextmanager
def tempdir(*args, **kw):
    """Context manager that creates a temporary directory

    The directory and all of its contents are removed on exit unless a
    keyword argument `delete=False` is given. All other arguments and
    keyword arguments are passed to `tempfile.mkdtemp`.

    Usage:

        >>> from os.path import exists, isdir, join
        >>>
        >>> with tempdir() as tmp:
        ...     foo = join(tmp, "foo.txt")
        ...     with open(foo, mode="w") as f:
        ...         x = f.write("data")
        ...     with open(foo) as f:
        ...         eq(f.read(), "data")
        ...     bar = join(tmp, "bar")
        ...     os.mkdir(bar)
        ...     assert isdir(bar), bar
        ...
        >>> assert not exists(foo), foo
        >>> assert not exists(bar), bar
        >>> assert not exists(tmp), tmp
    """
    delete = kw.pop("delete", True)
    path = tempfile.mkdtemp(*args, **kw)
    try:
        yield path
    finally:
        if delete and os.path.exists(path):
            shutil.rmtree(path)


def unittest_print_first_failures_last():
    """monkeypatch unittest to print errors in reverse order
    which is more convenient for viewing in the console
    """
    import unittest
    old_printErrorList = unittest._TextTestResult.printErrorList
    def printErrorList(self, flavor, errors):
        return old_printErrorList(self, flavor, reversed(errors))
    unittest._TextTestResult.printErrorList = printErrorList


def patch_nose_tools():
    """Patch nose.tools

    Functions patched:

        nose.tools.eq_
        nose.tools.assert_raises

    Additionally the standard `pdb.set_trace` is patched to work in
    tests being run by nose.
    """
    import nose.tools
    nose.tools.eq_ = eq
    nose.tools.assert_raises = assert_raises

    import pdb
    import sys
    def set_trace():
        """nose-compatible trace function

        uses default stdout, which is not consumed by nose
        """
        pdb.Pdb(stdout=sys.__stdout__).set_trace(sys._getframe().f_back)
    pdb.set_trace = set_trace


def test_testil():
    # nose test generator
    import testil
    from doctest import DocTestFinder, DocTestRunner

    def run(test):
        result = runner.run(test)
        assert not result.failed, (
            "%s of %s examples failed while testing %s"
            % (result.failed, len(test.examples), test.name))

    # Find, parse, and run all tests in this module.
    finder = DocTestFinder()
    runner = DocTestRunner()
    for test in finder.find(testil, "testil"):
        yield run, test


if __name__ == "__main__":
    import doctest
    assert doctest.testmod()
