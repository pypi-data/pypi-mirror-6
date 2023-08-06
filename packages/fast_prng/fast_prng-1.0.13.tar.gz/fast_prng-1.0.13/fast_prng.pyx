#cython: cdivision=True
#cython: overflowcheck=False
#cython: wraparound=False

from numpy cimport *
import numpy as np

#cdef extern from "fast_prng/exponential.h":

cdef extern from "fast_prng/normal.h":
	void exponential_setup()
	double c_exponential "exponential"()
	double c_uniform "uniform_double_PRN"()
	void normal_setup()
	double c_normal "normal"()

exponential_setup()
normal_setup()

def exponential(double scale=1.0, size=None):
	"""exponential(scale=1.0, size=None)

Exponential distribution.

Its probability density function is

.. math:: f(x; \frac{1}{\beta}) = \frac{1}{\beta} \exp(-\frac{x}{\beta}),

for ``x > 0`` and 0 elsewhere. :math:`\beta` is the scale parameter,
which is the inverse of the rate parameter :math:`\lambda = 1/\beta`.
The rate parameter is an alternative, widely used parameterization
of the exponential distribution.

Parameters
----------
scale : float
    The scale parameter, :math:`\beta = 1/\lambda`.
size : tuple of ints
    Number of samples to draw.  The output is shaped
    according to `size`.

See https://bitbucket.org/cdmcfarland/fast_prng for further details.
"""
	if not size:
		return scale*c_exponential()
	
	cdef long total_size = np.multiply.reduce(size)
	cdef ndarray[dtype=double, ndim=1] output = np.empty(total_size, order='C')
	cdef double *element = &(output[0]), *end = &(output[0]) + total_size
	
	if scale != 1.0:
		while element < end:
			element[0] = scale*c_exponential()
			element += 1
	else:
		while element < end:
			element[0] = c_exponential()
			element += 1
	return output.reshape(size)

def normal(double loc=0.0, double scale=1.0, size=None):
	"""normal(loc=0.0, scale=1.0, size=None)

Draw random samples from a normal (Gaussian) distribution.

The probability density function:

		p(x) = 1/sqrt(2*pi*sigma**2)*exp( -(x - loc)**2/(2*sigma^2) ),

	where mu = loc, scale = sigma, and sqrt/pi/exp are defined in numpy. 

Parameters
----------
loc : float
    Mean ("centre") of the distribution.
scale : float
    Standard deviation (spread or "width") of the distribution.
size : tuple of ints
    Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
    ``m * n * k`` samples are drawn.

see https://bitbucket.org/cdmcfarland/fast_prng for further details. 
"""
	if not size:
		return loc + scale*c_normal()

	cdef long total_size = np.multiply.reduce(size) 
	cdef ndarray[dtype=double, ndim=1] output = np.empty(total_size, order='C')
	cdef double *element = &(output[0]), *end = &(output[0]) + total_size

	if scale != 1.0:
		if loc != 0:
			while element < end:
				element[0] = scale*c_normal() + loc
				element += 1
		else:
			while element < end:
				element[0] = scale*c_normal()
				element += 1
	else:
		if loc != 0:
			while element < end:
				element[0] = c_normal() + loc
				element += 1
		else:
			while element < end:
				element[0] = c_normal()
				element += 1
	return output.reshape(size)

def random_sample(size=None):
	"""random_sample(size=None)

Return random floats in the half-open interval [0.0, 1.0).

Results are from the "continuous uniform" distribution.

Parameters
----------
size : tuple of ints
    Output shape. Defines the shape of the outputed array. If e.g. 
	``(m, n, k)``, then ``m * n * k`` samples are drawn."""

	if not size:
		return c_uniform()
	
	cdef long total_size = np.multiply.reduce(size)
	cdef ndarray[dtype=double, ndim=1] output = np.empty(total_size, order='C')
	cdef double *element = &(output[0]), *end = &(output[0]) + total_size

	while element < end:
		element[0] = c_uniform()
		element += 1

	return output.reshape(size)
