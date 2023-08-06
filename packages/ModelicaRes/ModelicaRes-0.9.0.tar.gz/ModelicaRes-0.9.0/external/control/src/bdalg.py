"""bdalg.py

This file contains some standard block diagram algebra.

Routines in this module:

series
parallel
negate
feedback

"""

"""Copyright (c) 2010 by California Institute of Technology
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the California Institute of Technology nor
   the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior
   written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CALTECH
OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.

Author: Richard M. Murray
Date: 24 May 09
Revised: Kevin K. Chen, Dec 10

$Id: bdalg.py 226 2012-11-03 22:51:28Z murrayrm $

"""

import scipy as sp
import control.xferfcn as tf
import control.statesp as ss

def series(sys1, sys2):
    """Return the series connection sys2 * sys1 for --> sys1 --> sys2 -->.

    Parameters
    ----------
    sys1: scalar, StateSpace, or TransferFunction
    sys2: scalar, StateSpace, or TransferFunction

    Returns
    -------
    out: scalar, StateSpace, or TransferFunction

    Raises
    ------
    ValueError
        if `sys2.inputs` does not equal `sys1.outputs`
        if `sys1.dt` is not compatible with `sys2.dt`

    See Also
    --------
    parallel
    feedback

    Notes
    -----
    This function is a wrapper for the __mul__ function in the StateSpace and
    TransferFunction classes.  The output type is usually the type of `sys2`.
    If `sys2` is a scalar, then the output type is the type of `sys1`.

    If both systems have a defined timebase (dt = 0 for continuous time,
    dt > 0 for discrete time), then the timebase for both systems must
    match.  If only one of the system has a timebase, the return
    timebase will be set to match it.

    Examples
    --------
    >>> sys3 = series(sys1, sys2) # Same as sys3 = sys2 * sys1.

    """
    
    return sys2 * sys1

def parallel(sys1, sys2):
    """
    Return the parallel connection sys1 + sys2.

    Parameters
    ----------
    sys1: scalar, StateSpace, or TransferFunction
    sys2: scalar, StateSpace, or TransferFunction

    Returns
    -------
    out: scalar, StateSpace, or TransferFunction

    Raises
    ------
    ValueError
        if `sys1` and `sys2` do not have the same numbers of inputs and outputs
            
    See Also
    --------
    series
    feedback
    
    Notes
    -----
    This function is a wrapper for the __add__ function in the
    StateSpace and TransferFunction classes.  The output type is usually
    the type of `sys1`.  If `sys1` is a scalar, then the output type is
    the type of `sys2`.

    If both systems have a defined timebase (dt = 0 for continuous time,
    dt > 0 for discrete time), then the timebase for both systems must
    match.  If only one of the system has a timebase, the return
    timebase will be set to match it.

    Examples
    --------
    >>> sys3 = parallel(sys1, sys2) # Same as sys3 = sys1 + sys2.

    """
    
    return sys1 + sys2

def negate(sys):
    """
    Return the negative of a system.

    Parameters
    ----------
    sys: StateSpace or TransferFunction

    Returns
    -------
    out: StateSpace or TransferFunction

    Notes
    -----
    This function is a wrapper for the __neg__ function in the StateSpace and
    TransferFunction classes.  The output type is the same as the input type.

    If both systems have a defined timebase (dt = 0 for continuous time,
    dt > 0 for discrete time), then the timebase for both systems must
    match.  If only one of the system has a timebase, the return
    timebase will be set to match it.

    Examples
    --------
    >>> sys2 = negate(sys1) # Same as sys2 = -sys1.

    """
    
    return -sys;

def feedback(sys1, sys2, sign=-1):
    """
    Feedback interconnection between two I/O systems.

    Parameters
    ----------
    sys1: scalar, StateSpace, or TransferFunction
        The primary plant.
    sys2: scalar, StateSpace, or TransferFunction
        The feedback plant (often a feedback controller).
    sign: scalar
        The sign of feedback.  `sign` = -1 indicates negative feedback, and
        `sign` = 1 indicates positive feedback.  `sign` is an optional
        argument; it assumes a value of -1 if not specified.

    Returns
    -------
    out: StateSpace or TransferFunction

    Raises
    ------
    ValueError
        if `sys1` does not have as many inputs as `sys2` has outputs, or if
        `sys2` does not have as many inputs as `sys1` has outputs
    NotImplementedError
        if an attempt is made to perform a feedback on a MIMO TransferFunction
        object

    See Also
    --------
    series
    parallel

    Notes
    -----
    This function is a wrapper for the feedback function in the StateSpace and
    TransferFunction classes.  It calls TransferFunction.feedback if `sys1` is a
    TransferFunction object, and StateSpace.feedback if `sys1` is a StateSpace
    object.  If `sys1` is a scalar, then it is converted to `sys2`'s type, and
    the corresponding feedback function is used.  If `sys1` and `sys2` are both
    scalars, then TransferFunction.feedback is used.
  
    """

    # Check for correct input types.
    if not isinstance(sys1, (int, float, complex, tf.TransferFunction,
        ss.StateSpace)):
        raise TypeError("sys1 must be a TransferFunction or StateSpace object, \
or a scalar.")
    if not isinstance(sys2, (int, float, complex, tf.TransferFunction,
        ss.StateSpace)):
        raise TypeError("sys2 must be a TransferFunction or StateSpace object, \
or a scalar.")

    # If sys1 is a scalar, convert it to the appropriate LTI type so that we can
    # its feedback member function.
    if isinstance(sys1, (int, float, complex)):
        if isinstance(sys2, tf.TransferFunction):
            sys1 = tf._convertToTransferFunction(sys1)
        elif isinstance(sys2, ss.StateSpace):
            sys1 = ss._convertToStateSpace(sys1)
        else: # sys2 is a scalar.
            sys1 = tf._convertToTransferFunction(sys1)
            sys2 = tf._convertToTransferFunction(sys2)

    return sys1.feedback(sys2, sign)
