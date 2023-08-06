import numba
import decimal
import numpy as np

@numba.jit(numba.int64(numba.cdecimal), nopython=True)
def foo(x):
    return x

@numba.jit(numba.datetime(units='D')(numba.datetime(units='D')), nopython=True)
def foo2(x):
    return x

#print foo2(np.datetime64('2014-01-01'))
print(foo(decimal.Decimal('123.456')))
