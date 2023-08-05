from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules=[Extension('_write',['_write.pyx'])]

setup(
    name='write csv',
    cmdclass={'build_ext':build_ext},
    ext_modules=ext_modules
)