"""
PyWENO non-uniform reconstruction code generation routines

Original code written by Matthew Emmett as part of PyWENO.
Edited by Ben Thompson.

To generate a new fortran module for weno reconstruction of order k, run:

create_fncs(k)
"""

import os
import subprocess
import sympy
from sympy.utilities.codegen import codegen
from sympy.core.cache import clear_cache
from pyweno.nonuniform import smoothness_fnc_name, coeffs_fnc_name

from pyweno.symbolic import polynomial_interpolator
from pyweno.symbolic import primitive_polynomial_interpolator


def coeffs(k, d):
    # build arrays of cell boundaries and cell averages
    xs = [sympy.var('x%d' % j) for j in range(k + 1)]
    fs = [sympy.var('f%d' % j) for j in range(k)]

    x = sympy.var('x')

    # compute reconstruction coefficients for each left shift r
    # Interpolate the polynomial
    poly = primitive_polynomial_interpolator(xs, fs).diff(x, d + 1)
    for j in range(k):
        print("Coefficient: %d %d" % (d, j))
        args = xs[:]
        args.append(x)
        fnc = poly.copy()
        # Subs in 1.0 and 0.0 to simulate getting a coefficient
        for i in range(k):
            if i == j:
                fnc = fnc.subs(fs[i], 1.0)
            else:
                fnc = fnc.subs(fs[i], 0.0)
        # Zero center to mitigate floating point error
        # DONT SIMPLIFY AFTER THIS
        for var in xs:
            fnc = fnc.subs(var, var - xs[0])
        fnc_name = coeffs_fnc_name(k, d, j)
        save_fnc(k, fnc, fnc_name, args)


def smoothness_coefficient(r, i, j, k, xs, ys, b1, b2, fnc):
    """
    Computes a single coefficient function
    in the Jiang-Shu smoothness coefficient
    """
    args = [xs[m] for m in range(0, k + 1)]
    # I suspect that I could carefully redesign this so that
    # b1 and b2 would be drawn from the xs array
    args.append(b1)
    args.append(b2)
    for u in range(k):
        for v in range(u, k):
            if (u == i and v == j) or (v == i and u == j):
                continue
            fnc = fnc.subs(ys[u] * ys[v], 0.0)
    fnc = fnc.subs(ys[i] * ys[j], 1.0)
    # Zero center to mitigate floating point error
    # DONT SIMPLIFY AFTER THIS
    for var in xs:
        fnc = fnc.subs(var, var - xs[0])
    fnc = fnc.subs(b1, b1 - xs[0])
    fnc = fnc.subs(b2, b2 - xs[0])
    fnc_name = smoothness_fnc_name(k, r, i, j)
    save_fnc(k, fnc, fnc_name, args)


def smoothness(k):
    """
    Compute the Jiang-Shu smoothness coefficient functions and output them in a form ready
    to be compiled to fortran.
    """

    # the integration variable (represents position within the cell)
    x = sympy.var('x')

    # build array of cell boundaries and cell averages (sympy vars x[i])
    xs = []
    for j in range(k + 1):
        xs.append(sympy.var('x%d' % j))
    # and build the array of cell averages
    ys = []
    for j in range(k):
        ys.append(sympy.var('y%d' % j))

    # The upper and lower boundaries of the cell, used as the integration
    # bounds.
    b1 = sympy.var('b1')
    b2 = sympy.var('b2')

    # Interpolate the polynomial
    p = primitive_polynomial_interpolator(xs, ys)
    p = p.as_poly(x)
    p = p.diff(x)

    ppp = []
    for r in range(0, k):
        # The smoothness is measured as the sum of L^2 norms of derivatives
        s = 0
        for j in range(1, k):
            pp = (p.diff((0, j))) ** 2
            pp = pp.integrate(x)
            pp = (b2 - b1) ** (2 * j - 1) * (
                pp.subs(x, b2) - pp.subs(x, b1))
            s = s + pp
        # We have to do .simplify().expand() in order to get the proper
        # symbolic coefficients
        ppp.append(s)

    # Saves functions and arguments in a form ready to be compiled to fortran
    # expressions that can be called from the live code.
    for r in range(0, k):
        for i in range(0, k):
            for j in range(0, k):
                print("Smoothness Coefficient: %d %d %d" % (r, i, j))
                fnc = ppp[r].copy()
                smoothness_coefficient(
                    r, i, j, k, xs, ys, b1, b2, fnc)


def save_fnc(k, fnc, fnc_name, args):
    # Build the code using the sympy codegen module
    code = codegen((fnc_name, fnc), "F95", "autoweno",
                   argument_sequence=args)
    filename_prefix = get_filename_prefix(get_module_name(k))
    source_file = filename_prefix + '.f90'
    # Save it to the proper file.
    with open(source_file, 'a') as ff:
        ff.write(code[0][1])
    # Clear the sympy cache so that we don't completely fill up RAM.
    clear_cache()


def get_module_name(k):
    module_name = 'nonuniform_weno_' + str(k)
    return module_name


def get_filename_prefix(module_name):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, module_name)


def create_fncs(k, do_smoothness, max_derivative, force=False):
    """
    This function uses the sympy autowrap module to create fortran functions
    with f2py. It is massively faster at runtime than directly calling the
    sympy functions using subs. As a tradeoff, this takes a long time
    to generate the fortran functions (sympy can be slow!).

    Note: if the library already exists, this will do nothing. Delete the
    weno_k.so file to rebuild it.
    """
    module_name = get_module_name(k)
    filename_prefix = get_filename_prefix(module_name)
    source_file = filename_prefix + '.f90'

    # Check if the library already exists.
    if (not force) and os.path.exists(filename_prefix + '.so'):
        return

    # Delete the old source
    if os.path.exists(source_file):
        os.remove(source_file)

    # Build the new source
    if max_derivative == -1:
        max_derivative = k
    for d in range(0, max_derivative):
        coeffs(k, d)

    if do_smoothness is 1:
        smoothness(k)
    # Compile!
    subprocess.call('f2py -c ' + source_file + ' -m ' + module_name,
                    shell=True)
    # Test the module
    module = __import__(module_name)
    assert(module)


if __name__ == "__main__":
    import sys
    create_fncs(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
