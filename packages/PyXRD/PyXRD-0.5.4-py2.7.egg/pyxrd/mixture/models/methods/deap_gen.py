# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from itertools import izip, imap
from math import log
from multiprocessing.pool import AsyncResult

import numpy as np
import scipy

from deap import creator, base, cma, tools

# TODO integrate this in a single class somewhere...
try:
    from scoop import futures as pool
    from scoop._types import Result as ScoopResult
except ImportError:
    logger.warning("Could not import SCOOP, falling back to multiprocessing pool!")
    ScoopResult = object # make sure we don't get errors...
    from pyxrd.data.settings import POOL as pool

from .refine_run import RefineRun
from .deap_utils import pyxrd_array, evaluate

# Default settings:
NGEN = 100
STAGN_NGEN = 10
STAGN_TOL = 0.5

# Needs to be shared for multiprocessing to work properly
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

def submit_async_call(func, *args):
    """ Utility that passes function calls either to SCOOP (if it's available)
    or down to a multiprocessing call."""
    if hasattr(pool, "submit"): # SCOOP
        result = pool.submit(func, args)
    elif hasattr(pool, "apply_async"): # Regular multiprocessing pool
        result = pool.apply_async(func, args)
    else: # No parallelization:
        result = func(*args)
    return result

def fetch_async_result(result):
    """ Utility that parses the result object returned by submit_async_call"""
    if isinstance(result, AsyncResult): # Multiprocessing pool result object
        return result.get()
    elif isinstance(result, ScoopResult): # SCOOP result object
        return result.result()
    else:
        return result

def do_async_evaluation(population, toolbox):
    """ Utility that combines a submit and fetch cycle in a single
    function call"""
    results = []
    for ind in toolbox.generate():
        result = submit_async_call(toolbox.evaluate, ind)
        population.append(ind)
        results.append(result)
    for ind, result in izip(population, results):
        ind.fitness.values = fetch_async_result(result)
    del results

def eaGenerateUpdateStagn(toolbox, ngen, halloffame=None, stats=None,
                     verbose=__debug__, stagn_ngen=STAGN_NGEN, stagn_tol=STAGN_TOL, context=None):
    """This is algorithm implements the ask-tell model proposed in 
    [Colette2010]_, where ask is called `generate` and tell is called `update`.
    
    Modified (Mathijs Dumon) so it checks for stagnation.
    
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :param stagn_gens: The number of generations to check for stagnation
    :param stagn_tol: The maximum tolerance for the last `stagn_gens` best fitnesses.
    :param context: PyXRD refinement context object

    :returns: The final population.
    
    The toolbox should contain a reference to the generate and the update method 
    of the chosen strategy.

    .. [Colette2010] Collette, Y., N. Hansen, G. Pujol, D. Salazar Aponte and
       R. Le Riche (2010). On Object-Oriented Programming of Optimizers -
       Examples in Scilab. In P. Breitkopf and R. F. Coelho, eds.:
       Multidisciplinary Design Optimization in Computational Mechanics,
       Wiley, pp. 527-565;

    """

    column_names = ["gen", "evals"]
    if stats is not None:
        column_names += stats.functions.keys()
    if verbose:
        logger = tools.EvolutionLogger(column_names)
        logger.logHeader()

    best_fitnesses = []
    for gen in xrange(ngen):
        context.status_message = "Creating generation #%d" % (gen + 1)
        # Generate a new population:
        population = []
        do_async_evaluation(population, toolbox)
        if halloffame is not None:
            halloffame.update(population)

        context.status_message = "Updating strategy"
        # Update the strategy with the evaluated individuals
        toolbox.update(population)
        if stats is not None:
            stats.update(population)
        best = population[0]
        pop_size = len(population)
        context.update(best, best.fitness.values[0])

        best_fitnesses.append(best.fitness.values)
        if len(best_fitnesses) > (stagn_ngen + 1):
            del best_fitnesses[0]

        if context is not None:
            context.record_state_data([
                ("gen", gen),
                ("pop", pop_size),
                ("min", float(stats.min[-1][-1][-1])),
                ("avg", float(stats.avg[-1][-1][-1])),
                ("max", float(stats.max[-1][-1][-1])),
                ("std", float(stats.std[-1][-1][-1])),
            ] + [ ("par%d" % i, float(val)) for i, val in enumerate(best)])

        if verbose:
            logger.logGeneration(evals=pop_size, gen=gen, stats=stats)

        context.status_message = "Checking for stagnation"
        if gen >= stagn_ngen: # 10

            yvals = stats.std[-1][-1][-(stagn_ngen - 1):]
            xvals = range(len(yvals))
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xvals, yvals) #@UnusedVariable
            stagnation = bool(p_value >= 0.95)

            stagnation = True
            last_fitn = np.array(best_fitnesses[-1])
            for fitn in best_fitnesses[-(stagn_ngen - 1):]:
                fitn = np.array(fitn)
                if np.any(np.abs(fitn - last_fitn) > stagn_tol): # 0.01
                    stagnation = False
                    break
            if stagnation:
                break

    return population

class CustomStrategy(cma.StrategyOnePlusLambda):

    def __init__(self, centroid, sigma, **kwargs):
        if not "lambda_" in kwargs:
            kwargs["lambda_"] = int(50 + min(3 * log(len(centroid)), 150)) #@UndefinedVariable
        super(CustomStrategy, self).__init__(centroid, sigma, ** kwargs)

    def generate(self, ind_init):
        """Generate a population from the current strategy using the 
        centroid individual as parent.
        
        :param ind_init: A function object that is able to initialize an
                         individual from a list.
        :returns: an iterator yielding the generated individuals.
        """
        arz = np.random.standard_normal((self.lambda_, self.dim)) #@UndefinedVariable
        if hasattr(self, "BD"):
            arz = np.array(self.centroid) + self.sigma * np.dot(arz, self.BD.T) #@UndefinedVariable
        else:
            arz = np.array(self.parent) + self.sigma * np.dot(arz, self.A.T) #@UndefinedVariable

        for arr in arz:
            yield ind_init(arr)



class RefineCMAESRun(RefineRun):
    """
        The DEAP CMA-ES algorithm implementation with added stagnation thresholds
    """
    name = "CMA-ES refinement"
    description = "This algorithm uses the CMA-ES refinement strategy as implemented by DEAP"

    options = [
        ('Maximum # of generations', 'ngen', int, NGEN, [1, 10000]),
        ('Minimum # of generations', 'stagn_ngen', int, STAGN_NGEN, [1, 10000]),
        ('Fitness stagnation tolerance', 'stagn_tol', float, STAGN_TOL, [0., 100.]),
    ]

    def run(self, context, ngen=NGEN, stagn_ngen=STAGN_NGEN, stagn_tol=STAGN_TOL, **kwargs):

        logger.info("Setting up the DEAP CMA-ES refinement algorithm")

        N = len(context.ref_props)

        # Individual generation:
        bounds = np.array(context.ranges)
        creator.create(
            "Individual", pyxrd_array,
            fitness=creator.FitnessMin, # @UndefinedVariable
            context=context,
            min_bounds=bounds[:, 0].copy(),
            max_bounds=bounds[:, 1].copy(),
        )

        # Makes sure individuals stay in-bound:
        def create_individual(lst):
            arr = np.array(lst).clip(bounds[:, 0], bounds[:, 1])
            return creator.Individual(arr) # @UndefinedVariable

        # Toolbox setup:
        toolbox = base.Toolbox()
        toolbox.register("evaluate", evaluate)

        # Setup strategy:
        method = "1plusCMA"
        if method == "1plusCMA":
            centroid = create_individual(context.initial_solution)
            sigma = np.array(abs(bounds[:, 0] - bounds[:, 1]) / 20.0)
        else:
            centroid = context.initial_solution
            sigma = max(abs(bounds[:, 0] - bounds[:, 1]) / 20.0)

        strategy = CustomStrategy(centroid=centroid, sigma=sigma)

        # Create Generation 0:
        logger.info("Creating generation #0:")
        context.status_message = "Creating generation #0"

        logger.info("\t evaluating uniformly distributed solutions...")
        # Pre-feed the strategy with a normal distributed population over the entire domain:
        solutions = np.random.normal(size=(strategy.lambda_, N))
        solutions = (solutions - solutions.min()) / (solutions.max() - solutions.min()) # stretch to [0-1] interval
        solutions = bounds[:, 0] + solutions * (bounds[:, 1] - bounds[:, 0])
        toolbox.register("generate", imap, create_individual, solutions)
        population = []
        do_async_evaluation(population, toolbox)

        logger.info("\t updating population...")
        strategy.update(population)
        del population
        logger.info("\t Done.")

        # Register the correct functions:
        toolbox.register("update", strategy.update)
        toolbox.register("generate", strategy.generate, create_individual)

        # Hall of fame:
        logger.info("Creating hall-off-fame and statistics")
        halloffame = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", tools.mean)
        stats.register("std", tools.std)
        stats.register("min", min)
        stats.register("max", max)

        # Get this show on the road:
        if pool is not None:
            toolbox.register("map", lambda f, i: pool.map(f, i, 10))

        logger.info("Running the CMA-ES algorithm...")
        context.status = "running"
        context.status_message = "Running CMA-ES algorithm ..."
        final = eaGenerateUpdateStagn(
            toolbox,
            ngen=ngen,
            stats=stats,
            halloffame=halloffame,
            context=context,
            stagn_ngen=STAGN_NGEN,
            stagn_tol=STAGN_TOL
        )

        context.status_message = "CMA-ES converged ..."
        context.status = "finished"

    pass # end of class
