
def deterministic_solve_comp(model, start_s, T=10):

    # simulation is assumed to return to steady-state

    dr = approximate_controls(model, order=1,   )

    final_s = model.calibration['states'].copy()
    final_x = model.calibration['controls'].copy()
    start_x = dr( numpy.atleast_2d( start_s.ravel()).T ).flatten()

    final = numpy.concatenate( [final_s, final_x])
    start = numpy.concatenate( [start_s, start_x])

    print(final)
    print(start)

    n_s = len(final_s)
    n_x = len(final_x)

    initial_guess = numpy.concatenate( [start*(1-l) + final*l for l in linspace(0.0,1.0,T+1)] )

    initial_guess = initial_guess.reshape( (-1, n_s + n_x)).T
    N = initial_guess.shape[1]

    sh = initial_guess.shape
    from dolo.numeric.solver import MyJacobian

    fobj = lambda vec: det_residual(model, vec.reshape(sh), start_s, final_x).ravel()
    f = lambda x: [fobj(x), MyJacobian(fobj)(x)]

    upper_bound = initial_guess*0 + big_number
    lower_bound = initial_guess*0 - big_number
    upper_bound[n_s,:] = 0.12 # limit investment

    from dolo.numeric.ncpsolve import ncpsolve
    sol = ncpsolve(f, lower_bound.ravel(), upper_bound.ravel(), initial_guess.ravel())
    sol = sol.reshape(sh)

    res = f(sol.ravel())[0]

    # from dolo.numeric.solver import solver
    # sol = solver(f, initial_guess, lb=lower_bound, ub=upper_bound, method='lmmcp', verbose=True)

    print("YES")
    return sol




    initial_guess = numpy.row_stack( [initial_guess, numpy.zeros( (n_x, N) ), numpy.zeros( (n_x, N) )] )

    # initial_guess = initial_guess[n_s:-n_x]

    lower_bound = initial_guess*0
    lower_bound[:n_s+n_x,:] = -big_number
    lower_bound[:,-1] = -big_number

    upper_bound = lower_bound*0 + big_number

    print( sum( (upper_bound - initial_guess)<=0 ) )
    print( sum( (lower_bound - initial_guess)>0 ) )



    res = det_residual_comp(model, initial_guess, start_s, final_x)

    print(abs(res).max())

    sh = initial_guess.shape

    # fobj = lambda vec: det_residual_comp(model, vec, start_s, final_x)
    fobj = lambda vec: det_residual_comp(model, vec.reshape(sh), start_s, final_x).ravel()


    from dolo.numeric.solver import MyJacobian
    #
    dres = MyJacobian(fobj)(initial_guess.ravel())
    #
    # print(dres.shape)
    # print(numpy.linalg.matrix_rank(dres))

    f = lambda x: [fobj(x), MyJacobian(fobj)(x)]

    import time
    t = time.time()

    initial_guess = initial_guess.ravel()
    lower_bound = lower_bound.ravel()
    upper_bound = upper_bound.ravel()

    from dolo.numeric.ncpsolve import ncpsolve
    sol = ncpsolve( f, lower_bound, upper_bound, initial_guess, verbose=True)
    #
    # from dolo.numeric.solver import solver
    # sol = solver(fobj, initial_guess, lb=lower_bound, ub=upper_bound, serial_problem=False, method='lmmcp', verbose=True)

    print(sol.shape)

    s = time.time()
    print('Elapsed : {}'.format(s-t))

    return sol[:n_s+n_x,:]


def det_residual_comp(model, guess, start, final):

    n_s = len( model.symbols['states'] )
    n_x = len( model.symbols['controls'] )

    n_e = len( model.symbols['shocks'] )
    N = guess.shape[1]

    ee = zeros((n_e,1))

    p = model.calibration['parameters']

    f = model.functions['arbitrage']
    g = model.functions['transition']
    a = model.functions['auxiliary']

    [lb,ub] = model.x_bounds


    # guess = numpy.concatenate( [start, guess, final] )
    # guess = guess.reshape( (-1, n_s+n_x) ).T

    n_v = n_s + n_x

    v = guess[n_v:n_v+n_x,:-1]
    w = guess[n_v+n_x:,:-1]

    vec = guess[:n_v,:-1]
    vec_f = guess[:n_v,1:]

    s = vec[:n_s,:]
    x = vec[n_s:,:]
    S = vec_f[:n_s,:]
    X = vec_f[n_s:,:]

    y = a(s,x,p)
    Y = a(S,X,p)

    res_s = S - g(s,x,y,ee,p)
    res_x = ( f(s,x,y,S,X,Y,p) - v + w )

    lbv = lb(s,p)
    ubv = ub(s,p)

    lbv[numpy.isinf(lbv)] = -big_number
    ubv[numpy.isinf(ubv)] = big_number

    comp1 = x - lbv
    comp2 = ubv - x


    res = numpy.zeros( (n_s+n_x*3, N) )

    res[:n_s,1:] = res_s
    res[n_s:n_s+n_x,:-1] = res_x
    res[n_s+n_x:n_s+2*n_x,:-1] = comp1
    res[n_s+2*n_x:,:-1] = comp2


    res[:n_s,0] = vec[:n_s,0] - start_s                     # initial condition
    res[n_s:n_s+n_x,-1] = vec_f[n_s:n_s+n_x,-1] - final_x   # terminal condition

    res[n_s+n_x:n_s+2*n_x,-1] = guess[n_s+n_x:n_s+2*n_x,-1]
    res[n_s+2*n_x:,-1] = guess[n_s+2*n_x:,-1]

    return res
