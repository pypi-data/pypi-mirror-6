import numpy
from numpy import linspace, zeros, atleast_2d

steady_state( model )  # -> returns steady-state, using calibrated values as starting point

steady_state( model, e ) # -> sets exogenous values for shocks

steady_state( model, {'e_a':1, 'e':9}, {'k':[8,9])


def find_steady_state(model, e, force_values=None, get_jac=False):
    '''
    Finds the steady state corresponding to exogenous shocks :math:`e`.

    :param model: an "fg" model.
    :param e: a vector with the value for the exogenous shocks.
    :param force_values: (optional) a vector where finite values override the equilibrium conditions. For instance a vector :math:`[0,nan,nan]` would impose that the first state must be equal to 0, while the two next ones, will be determined by the model equations. This is useful, when the deterministic model has a unit root.
    :return: a list containing a vector for the steady-states and the corresponding steady controls.
    '''

    s0 = model.calibration['states']
    x0 = model.calibration['controls']
    p = model.calibration['parameters']
    z = numpy.concatenate([s0, x0])

    e = numpy.atleast_2d(e.ravel()).T

    if force_values is not None:
        inds =  numpy.where( numpy.isfinite( force_values ) )[0]
        vals = force_values[inds]

    def fobj(z):
        s = numpy.atleast_2d( z[:len(s0)] ).T
        x = numpy.atleast_2d( z[len(s0):] ).T
        S = model.functions['transition'](s,x,e,p)
        #    S[inds,0] = vals
        r = model.functions['arbitrage'](s,x,s,x,p)
        res = numpy.concatenate([S-s, r,  ])
        if force_values is not None:
            add = atleast_2d(S[inds,0]-vals).T
            res = numpy.concatenate([res, add])
        return res.ravel()
 
    if get_jac:
        from dolo.numeric.solver import MyJacobian
        jac = MyJacobian(fobj)( steady_state)
        return jac
        return res.flatten()

    from scipy.optimize import root
    sol = root(fobj, z, method='lm')
    steady_state = sol.x
    

    return [steady_state[:len(s0)], steady_state[len(s0):]]
