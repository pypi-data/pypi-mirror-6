from __future__ import print_function, division, absolute_import


def test():
    import numba.unittest_support as unittest
    loader = unittest.TestLoader()
    startdir = "numba.tests"
    suite = loader.discover(startdir)

    runner = unittest.TextTestRunner(descriptions=True, verbosity=2,
                                     buffer=True)
    result = runner.run(suite)
    return result.wasSuccessful()


def multitest():
    """
    Run tests in multiple processes.
    """
    import numba.unittest_support as unittest
    import multiprocessing as mp
    loader = unittest.TestLoader()
    startdir = "numba.tests"
    suites = loader.discover(startdir)

    pool = mp.Pool(processes=mp.cpu_count())
    results = pool.map(_multiruntest, suites)
    return all(results)


def _multiruntest(suite):
    import numba.unittest_support as unittest
    runner = unittest.TextTestRunner(descriptions=False, verbosity=0,
                                     buffer=True)
    result = runner.run(suite)
    return result.wasSuccessful()
