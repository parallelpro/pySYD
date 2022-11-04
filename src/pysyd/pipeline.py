import numpy as np
import pandas as pd
import multiprocessing as mp









# Package mode
from . import utils
from . import plots
from .target import Target


def check(args):
    """
    
    This is intended to be a way to check a target before running it by plotting the
    times series data and/or power spectrum. This works in the most basic way  but has
    not been tested otherwise
    
    Parameters
        args : argparse.Namespace
            the command line arguments
    
    .. important::
        has not been extensively tested

    
    """
    star = load(args)
    plots.check_data(star)


def fun(args):
    """Get logo output
    
    Parameters
        args : argparse.Namespace
            the command line arguments
    
    """
    utils.get_output(fun=True)


def load(args):
    """
    
    Module to load in all relevant information and dictionaries
    required to run the pipeline
    
    .. note::
        this does *not* load in a target or target data, this is purely
        information that is required to run any ``pySYD`` mode successfully
        (with the exception of ``pysyd.pipeline.setup``)

    Parameters
        args : argparse.Namespace
            the command line arguments
        star : object, optional
            pretty sure this is only used from jupyter notebook
        verbose : bool, optional
            again, this is only used if not using command line
        command : str, optional
            which of the 5 ``pysyd.pipeline`` modes to execute from the notebook

    Returns
        single : target.Target
            current data available for the provided target

    Deprecated
        single : target.Target
            current data available for the provided target

    """
    if args.data:
        if args.stars is None:
            print('\nTrying to check data but no target provided.\nPlease provide a star via --star and try again.')
            return
        else:
            assert len(args.stars) == 1, "No more than one star can be checked at a time."
        if args.verbose:
            print('\n\nChecking data for target %s:'%args.stars[0])
    # Load in data for a given star
    params = utils.Parameters(args=args)
    # Add target stars
    params.add_targets(stars=args.stars)
    # Load target data
    star = Target(args.stars[0], params)
    return star


def parallel(args):
    """
    
    Run ``pySYD`` in parallel for a large number of stars

    Parameters
        args : argparse.Namespace
            the command line arguments

    Methods
        pipe

    .. seealso:: :mod:`pysyd.pipeline.run`
    
    """
    # Load relevant pySYD parameters
    params = utils.Parameters(args=args)
    if args.stars is None:
        try:
            args.stars = params.load_starlist()
        except utils.InputError as error:
            print(error.msg)
            return
    # Add target stars
    params.add_targets(stars=args.stars)
    # Creates the separate, asyncrhonous (nthread) processes
    pool = mp.Pool(args.n_threads)
    result_objects = [pool.apply_async(pipe, args=(group, params)) for group in params.params['groups']]
    results = [r.get() for r in result_objects]
    pool.close()
    pool.join()               # postpones execution of the next line until all processes finish
    # Concatenates output into two files
    utils.scrape_output(params)


def pipe(group, params, progress=False):
    """

    This function is called by both :mod:`pysyd.pipeline.run` and :mod:`pysyd.pipeline.parallel`
    to initialize the pipeline for a `'group'` of stars

    Parameters
        group : List[str]
            list of stars to be processed as a group
        args : argparse.Namespace
            the command line arguments

    """
    # Iterate through and run stars in a given star 'group'
    for name in group:
        star = Target(name, params)
        if star.load_data():
            star.process_star()


def plot(args):
    """
    
    Module to load in all relevant information and dictionaries
    required to run the pipeline
    
    .. note::
        this does *not* load in a target or target data, this is purely
        information that is required to run any ``pySYD`` mode successfully
        (with the exception of ``pysyd.pipeline.setup``)

    Parameters
        args : argparse.Namespace
            the command line arguments


    """
    if args.compare:
        plots.create_comparison_plot(show=args.show, save=args.save, overwrite=args.overwrite,)
    if args.results:
        if args.stars is None:
            raise utils.InputError("\nPlease provide a star to plot results for\n")
        else:
            assert len(args.stars) == 1, "No more than one star can be checked at a time."
        if args.verbose:
            print('\n\nPlotting results for target %s:'%args.stars[0])


def run(args):
    """
    
    Main function to initiate the pySYD pipeline (consecutively, not
    in parallel)

    Parameters
        args : argparse.Namespace
            the command line arguments

    Methods
        pipe

    .. seealso:: :mod:`pysyd.pipeline.parallel`


    """
    # Load default pySYD parameters
    params = utils.Parameters(args=args)
    if args.stars is None:
        try:
            args.stars = params.load_starlist()
        except utils.InputError as error:
            print(error.msg)
            return
    # Update with CL options
    params.add_targets(stars=args.stars)
    # Run single batch of stars
    pipe(args.stars, params)
    # Concatenates output into two files
    utils.scrape_output(params)


def setup(args):
    """
    
    Running this after installation will create the appropriate directories in the current working
    directory as well as download example data and files to test your pySYD installation

    Parameters
        args : argparse.Namespace
            the command line arguments
        note : str, optional
            suppressed (optional) verbose output
        raw : str
            path to download "raw" package data and examples from the ``pySYD`` source directory


    """
    utils.setup_dirs(args)