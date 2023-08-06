import numpy as np

import time

from socket import timeout

from pysmac.smacrunner import SMACRunner
from pysmac.smacremote import SMACRemote


def check_param_dimensions(x0, xmin, xmax):
    assert(x0.shape == xmin.shape), "shape of x0 and xmin don't agree"
    assert(x0.shape == xmax.shape), "shape of x0 and xmax don't agree"
    return True

def format_params(x0, xmin, xmax, nptype):
    x0 = np.asarray(x0, dtype=nptype)
    xmin = np.asarray(xmin, dtype=nptype)
    xmax = np.asarray(xmax, dtype=nptype)
    return x0, xmin, xmax

def check_categorical_params(params):
    assert isinstance(params, dict), "Categorical parameters must be a dict of lists."
    for key, value in params.iteritems():
        assert isinstance(value, list), "Categorical parameters must be a dict of lists."

def fmin(objective,
         x0=[], xmin=[], xmax=[],
         x0_int=[], xmin_int=[], xmax_int=[],
         x_categorical={},
         max_evaluations=100, seed=1, **args):
    """
        min_x f(x) s.t. xmin < x < xmax

        objective: The objective function that should be optimized.
                   Designed for objective functions that are:
                   costly to calculate + don't have a derivative available.
        x0: initial guess
        xmin: minimum values 
        xmax: maximum values
        x0_int: initial guess of integer params
        xmin_int: minimum values of integer params
        xmax_int: maximum values of integer params
        x_categorical: dictionary of categorical parameters
        max_evaluations: the maximum number of evaluations to execute
        seed: the seed that SMAC is initialized with
        args: extra parameters to pass to the objective function

        returns: best parameters found
    """
    x0, xmin, xmax = format_params(x0, xmin, xmax, np.float)
    check_param_dimensions(x0, xmin, xmax)

    x0_int, xmin_int, xmax_int = format_params(x0_int, xmin_int, xmax_int, np.int)
    check_param_dimensions(x0_int, xmin_int, xmax_int)

    check_categorical_params(x_categorical)

    smacremote = SMACRemote()

    smacrunner = SMACRunner(x0, xmin, xmax,
                            x0_int, xmin_int, xmax_int,
                            x_categorical,
                            smacremote.port, max_evaluations, seed)

    while not smacrunner.is_finished():
        try:
            params = smacremote.get_next_parameters()
        except timeout:
            #Timeout, check if the runner is finished
            continue

        start = time.clock()
        assert all([param not in args.keys() for param in params.keys()]), "Naming collision between parameters and custom arguments"
        function_args = {}
        function_args.update(params)
        function_args.update(args)
        performance = objective(**function_args)
        assert performance is not None, ("objective function did not return "
            "a result for parameters %s" % str(function_args))
        print "Performance: %f, with parameters: " % performance, params
        runtime = time.clock() - start

        smacremote.report_performance(performance, runtime)

    return smacrunner.get_best_parameters()


