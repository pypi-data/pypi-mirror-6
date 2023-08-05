import unittest

import numpy as np

from dolo.numeric.ncpsolve import ncpsolve, smooth
import scipy.sparse


def josephy(x):
    #   Computes the function value F(x) of the NCP-example by Josephy.
    n=len(x)
    Fx=np.zeros(n)
    Fx[0]=3*x[0]**2+2*x[0]*x[1]+2*x[1]**2+x[2]+3*x[3]-6
    Fx[1]=2*x[0]**2+x[0]+x[1]**2+3*x[2]+2*x[3]-2
    Fx[2]=3*x[0]**2+x[0]*x[1]+2*x[1]**2+2*x[2]+3*x[3]-1
    Fx[3]=x[0]**2+3*x[1]**2+2*x[2]+3*x[3]-3;
    return Fx

def Djosephy(x):
    # Local Variables: x, DFx, n
    # Function calls: Djosephy, zeros, length
    #%
    #%   Computes the Jacobian DF(x) of the NCP-example by Josephy
    #%
    n = len(x)
    DFx = np.zeros( (n, n) )
    DFx[0,0] = 6.*x[0]+2.*x[1]
    DFx[0,1] = 2.*x[0]+4.*x[1]
    DFx[0,2] = 1.
    DFx[0,3] = 3.
    DFx[1,0] = 4.*x[0]+1.
    DFx[1,1] = 2.*x[1]
    DFx[1,2] = 3.
    DFx[1,3] = 2.
    DFx[2,0] = 6.*x[0]+x[1]
    DFx[2,1] = x[0]+4.*x[1]
    DFx[2,2] = 2.
    DFx[2,3] = 3.
    DFx[3,0] = 2.*x[0]
    DFx[3,1] = 6.*x[1]
    DFx[3,2] = 2.
    DFx[3,3] = 3.
    return scipy.sparse.csc_matrix(DFx)
    #from numpy import matrix
    #return matrix(DFx)

class SerialSolve(unittest.TestCase):

    def test_simple_solve(self):

        x0 = np.array([0.5,0.5,0.5,0.5])


        lb = np.array([0.0,0.6,0.0,0.0])
        ub = np.array([1.0,1.0,1.0,0.4])

        fval = np.array([ 0.5, 0.5, 0.1,0.5 ])

        jac = np.array([
            [1.0,0.2,0.1,0.0],
            [1.0,0.2,0.1,0.0],
            [0.0,1.0,0.2,0.0],
            [0.1,1.0,0.2,0.1]
        ])

        N = 10
        d = len(fval)

        from dolo.numeric.ncpsolve import ncpsolve


        fobj = lambda x: [josephy(x), Djosephy(x)]
        sol_lmmcp = ncpsolve(fobj, lb, ub, x0)
        print(sol_lmmcp)

        from dolo.numeric.solver import solver
        sol = solver(josephy, x0, lb=lb, ub=ub)
        print(sol)

if __name__ == '__main__':

    unittest.main()