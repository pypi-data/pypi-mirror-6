"""
The acscte module contains a function `acscte` that calls the ACSCTE executable.
Use this function to facilitate batch runs of ACSCTE, or for the TEAL interface.

.. warning:: Only use with WFC full-frame images.

Examples
--------

In Python without TEAL:

>>> from acstools import acscte
>>> acscte.acscte('*blv_tmp.fits')

In Python with TEAL:

>>> from stsci.tools import teal
>>> from acstools import acscte
>>> teal.teal('acscte')

In Pyraf::

    --> import acstools
    --> epar acscte

"""
# STDLIB
import os.path
import subprocess

# STSCI
from stsci.tools import parseinput
try:
    from stsci.tools import teal
except:
    teal = None


__taskname__ = "acscte"
__version__ = "1.0"
__vdate__ = "13-Aug-2013"


def acscte(input, exec_path='', time_stamps=False, verbose=False, quiet=False,
           single_core=False):
    """
    Run the acscte.e executable as from the shell.

    Expect input to be ``*_blv_tmp.fits``.
    Output is automatically named ``*_blc_tmp.fits``.

    .. note:: Calibration flags are controlled by primary header.

    .. warning:: Only use with WFC full-frame images.

    Parameters
    ----------
    input : str or list of str
        Input filenames in one of these formats:

            * a single filename ('j1234567q_blv_tmp.fits')
            * a Python list of filenames
            * a partial filename with wildcards ('\*blv_tmp.fits')
            * filename of an ASN table ('j12345670_asn.fits')
            * an at-file (``@input``)

    exec_path : str, optional
        The complete path to ACSCTE executable.
        If not given, run ACSCTE given by 'acscte.e'.

    time_stamps : bool, optional
        Set to True to turn on the printing of time stamps.

    verbose : bool, optional
        Set to True for verbose output.

    quiet : bool, optional
        Set to True for quiet output.

    single_core : bool, optional
        CTE correction in ACSCTE will by default try to use all available
        CPUs on your computer. Set this to True to force the use of just
        one CPU.

    """
    if exec_path:
        if not os.path.exists(exec_path):
            raise OSError('Executable not found: ' + exec_path)
        call_list = [exec_path]
    else:
        call_list = ['acscte.e']

    # Parse input to get list of filenames to process.
    # acscte.e only takes 'file1,file2,...'
    infiles, dummy_out = parseinput.parseinput(input)
    call_list.append(','.join(infiles))

    if time_stamps:
        call_list.append('-t')

    if verbose:
        call_list.append('-v')

    if quiet:
        call_list.append('-q')

    if single_core:
        call_list.append('-1')

    subprocess.call(call_list)


def getHelpAsString():
    """
    Returns documentation on the `acscte` function. Required by TEAL.

    """
    return acscte.__doc__


def run(configobj=None):
    """
    TEAL interface for the `acscte` function.

    """
    acscte(configobj['input'],
           exec_path=configobj['exec_path'],
           time_stamps=configobj['time_stamps'],
           verbose=configobj['verbose'],
           quiet=configobj['quiet'],
           single_core=configobj['single_core']
           )
