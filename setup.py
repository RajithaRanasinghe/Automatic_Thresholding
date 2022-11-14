import sys
import cx_Freeze
from cx_Freeze import setup, Executable
from scipy.sparse.csgraph import _validation



packages = ['scipy']
executables = [cx_Freeze.Executable('AutomaticThresholding.py', base='Win32GUI')]

'''include the file of the package from python/anaconda installation '''
#include_files = ['C:\\ProgramData\\Continuum\\Anaconda\\Lib\\site-packages\\scipy']

cx_Freeze.setup(
    name = 'Test1',
    #options = {'AutomaticThresholding': {'packages':packages, 'include_files':include_files}},
    #options = {'AutomaticThresholding': {'packages':packages}},
    options = {"build_exe": {"include_msvcr": True, "packages": ["scipy", "matplotlib"], "zip_include_packages": "*", "zip_exclude_packages": ""}},
    version = '0.2',
    description = 'Automatic Thresholding',
    executables = executables
    )