# BSD 3-Clause License
#
# Copyright (c) 2019-2020, Gabriel S. Gerlero
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Find roots of scalar functions."""

from __future__ import division, absolute_import, print_function

__version__ = '1.0.1-dev0'

import itertools


class Result(object):
    """
    Result from a succesful call to a function in this module.

    Attributes
    ----------
    root : float or None
        Estimated root location. `None` if it is not known.
    f_root : float or None
        Value of `f` evaluated at `root`. `None` if `root` is `None`.
    bracket : sequence of two floats or None
        Interval that brackets the root. `None` if it is not known.
    f_bracket : sequence of two floats or None
        Values of `f` at the endpoints of `bracket. `None` if `f_bracket` is
        `None`.
    iterations : int
        Number of iterations performed by the algorithm.
    function_calls : int
        Number of calls to `f`.
    """

    def __init__(self, root=None, f_root=None, bracket=None, f_bracket=None,
                 iterations=0, function_calls=0):
        self.root = root
        self.f_root = f_root
        self.bracket = bracket
        self.f_bracket = f_bracket
        self.iterations = iterations
        self.function_calls = function_calls


class IterationLimitReached(RuntimeError):
    """
    Exception raised when a function in this module does not finish within the
    specified maximum number of iterations.

    Attributes
    ----------
    interval : sequence of two floats
        Working interval at the time the iteration limit was reached.
    f_interval : sequence of two floats
        Values of the `f` at the endpoints of `interval`.
    function_calls : int
        Number of calls to `f`.
    """
    def __init__(self, message, interval, f_interval, function_calls):

        super(RuntimeError, self).__init__(message)

        self.interval = interval
        self.f_interval = f_interval
        self.function_calls = function_calls


def bracket_root(f, interval, growth_factor=2, maxiter=100,
                 f_interval=(None, None), ftol=None):
    """
    Find an interval that brackets a root of a function by searching in one
    direction.

    Starting from an interval, it moves and expands the interval in the
    direction of the second endpoint until the interval brackets a root of the
    given function.

    Parameters
    ----------
    f : callable
        Continuous scalar function.
    interval : sequence of two floats
        Starting interval. Must have non-equal endpoints. It is not necessary
        that ``interval[0] < interval[1]``.
    growth_factor : float, optional
        How much to grow the length of the interval in each iteration.
    maxiter : int or None, optional
        Maximum number of iterations. Must be nonnegative. An
        :exc:`IterationLimitReached` exception will be raised if the bracket is
        not found within the specified number of iterations. If `None`,
        there is no maximum number of iterations.
    f_interval : sequence of two of {None, float}, optional
        Values of `f` at the endpoints of the interval, if known (use `None` if
        a value is not known). For every known value, one fewer call to `f`
        will be required.
    ftol : None or float
        An optional absolute tolerance for the value of `f` at a root. If
        given, the algorithm will immediately return any root it happens to
        discover in its execution.

    Returns
    -------
    result : Result
        Normally contains a bracket and no root. However, if `ftol` is not
        `None` and a root is found, it will contain that root; in this case,
        the result will also include a bracket only if one was found at the
        same time as the root.

    See also
    --------
    bisect

    Notes
    -----
    If `ftol` is not `None` and both endpoints of the starting interval qualify
    as roots, the one where the absolute value of `f` is lower is chosen as the
    root.
    """
    if ftol is not None and ftol < 0:
        raise ValueError("ftol cannot be negative")

    if maxiter is not None and maxiter < 0:
        raise ValueError("maxiter cannot be negative")

    a, b = interval

    if a == b:
        raise ValueError("interval must have different endpoints")

    f_a, f_b = f_interval

    function_calls = 0

    # Evaluate at endpoints if necessary
    if f_a is None:
        f_a = f(a)
        function_calls += 1

    if f_b is None:
        f_b = f(b)
        function_calls += 1

    # Test for a root at the first endpoint (the second endpoint will be
    # checked inside the main loop)
    if ftol is not None and abs(f_a) <= ftol and abs(f_a) <= abs(f_b):
        if f_a*f_b < 0:
            return Result(root=a,
                          f_root=f_a,
                          bracket=(a,b),
                          f_bracket=(f_a, f_b),
                          iterations=0,
                          function_calls=function_calls)

        return Result(root=a,
                      f_root=f_a,
                      iterations=0,
                      function_calls=function_calls)

    # Test and move the interval until it brackets a root
    for iteration in itertools.count(start=0):

        if f_a*f_b < 0:
            if ftol is not None and abs(f_b) <= ftol:
                return Result(root=b,
                              f_root=f_b,
                              bracket=(a,b),
                              f_bracket=(f_a, f_b),
                              iterations=iteration,
                              function_calls=function_calls)

            return Result(bracket=(a,b),
                          f_bracket=(f_a, f_b),
                          iterations=iteration,
                          function_calls=function_calls)

        if ftol is not None and abs(f_b) <= ftol:
            return Result(root=b,
                          f_root=f_b,
                          iterations=0,
                          function_calls=function_calls)

        if maxiter is not None and iteration >= maxiter:
            raise IterationLimitReached("failed to converge after {} "
                                        "iterations".format(maxiter),
                                        interval=(a,b),
                                        f_interval=(f_a, f_b),
                                        function_calls=function_calls)

        a, b = b, b + (growth_factor+1)*(b-a)
        f_a, f_b = f_b, f(b)
        function_calls += 1


class NotABracketError(ValueError):
    """
    Exception raised by :func:`bisect` when the interval passed as `bracket`
    does not actually contain a root.

    Attributes
    ----------
    f_interval : sequence of two floats
        Values of the `f` at the endpoints of the interval that is not a
        bracket.
    function_calls : int
        Number of calls to `f`.
    """
    def __init__(self, message, f_interval, function_calls):

        super(ValueError, self).__init__(message)

        self.f_interval = f_interval
        self.function_calls = function_calls


def bisect(f, bracket, ftol=1e-12, maxiter=100, f_bracket=(None, None)):
    """
    Find root of a function within a bracket using the bisection method.

    The function must have opposite signs at the endpoints of the bracket.

    Compared to SciPy's :func:`scipy.optimize.bisect` and
    :func:`scipy.optimize.root_scalar` functions, this function tests for a
    root by looking only at the residual (i.e., the value of `f`).

    Parameters
    ----------
    f : callable
        Continuous scalar function.
    bracket: sequence of two floats
        An interval bracketing a root. `f` must have different signs at the two
        endpoints, or a :exc:`NotABracketError` will be raised. It is not
        necessary that ``bracket[0] < bracket[1]``.
    ftol : float, optional
        Absolute tolerance for the value of `f` at the root. Must be
        nonnegative.
    maxiter : int or None, optional
        Maximum number of iterations. Must be nonnegative. An
        :exc:`IterationLimitReached` exception will be raised if the specified
        tolerance is not achieved within this number of iterations. If `None`,
        there is no maximum number of iterations.
    f_bracket : sequence of two of {None, float}, optional
        Values of `f` at the endpoints of `bracket`, if known (use `None` if a
        value is not known). For every known value, one fewer call to `f` will
        be required.

    Returns
    -------
    result : Result
        Contains the root and the final bracket.

    See also
    --------
    bracket_root : Can find a bracket when one is not known.

    Notes
    -----
    The function starts by testing the endpoints of the bracket. If a root is
    found at one of the endpoints of a valid bracket, no bisection iterations
    are performed and the root is immediately returned. If both endpoints
    qualify as roots, the one where the absolute value of `f` is lower is
    returned.
    """

    if ftol < 0:
        raise ValueError("ftol cannot be negative")

    if maxiter is not None and maxiter < 0:
        raise ValueError("maxiter cannot be negative")

    a, b = bracket
    f_a, f_b = f_bracket

    function_calls = 0

    # Evaluate at endpoints if necessary
    if f_a is None:
        f_a = f(a)
        function_calls += 1

    if f_b is None:
        f_b = f(b)
        function_calls += 1

    # Check that the bracket is valid
    if f_a*f_b > 0:
        raise NotABracketError("f must have different signs at the bracket "
                               "endpoints",
                               f_interval=(f_a, f_b),
                               function_calls=function_calls)

    # Test the endpoints themselves for a root
    if abs(f_a) <= ftol or abs(f_b) <= ftol:
        if abs(f_a) <= abs(f_b):
            root, f_root = a, f_a
        else:
            root, f_root = b, f_b

        return Result(root=root,
                      f_root=f_root,
                      bracket=(a,b),
                      f_bracket=(f_a, f_b),
                      iterations=0,
                      function_calls=function_calls)

    # Perform the actual bisection
    for iteration in itertools.count(start=1):

        if maxiter is not None and iteration > maxiter:
            raise IterationLimitReached("failed to converge after {} "
                                        "iterations".format(maxiter),
                                        interval=(a,b),
                                        f_interval=(f_a, f_b),
                                        function_calls=function_calls)

        m = (a + b)/2
        f_m = f(m)
        function_calls += 1

        if f_m*f_a > 0:
            a, f_a = m, f_m
        else:
            b, f_b = m, f_m

        if abs(f_m) <= ftol:
            return Result(root=m,
                          f_root=f_m,
                          bracket=(a,b),
                          f_bracket=(f_a, f_b),
                          iterations=iteration,
                          function_calls=function_calls)
