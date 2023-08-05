import numpy
from numpy import dot

from numba.vectorize import guvectorize

def evaluate_source( texp, s ):

    res = dot( texp, s )

    return res

from numba.vectorize import GUVectorize
evaluate = GUVectorize( evaluate_source,  )


coeffs = numpy.zeros((3,4))
N =10
sv0 = numpy.zeros( (4, N) )

evaluate(coeffs, sv0) 
