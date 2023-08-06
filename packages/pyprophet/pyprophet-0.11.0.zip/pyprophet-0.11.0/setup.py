from setuptools import setup, find_packages
from distutils.extension import Extension


import pyprophet
import numpy

version = pyprophet.__version__

ext_modules = [Extension("pyprophet._optimized", ["pyprophet/_optimized.c"])]

setup(name='pyprophet',
      version="%d.%d.%d" % version,
      author="Uwe Schmitt",
      author_email="rocksportrocker@gmail.com",
      description="""Python reimplementation of mProphet peak scoring.

      The windows binary egg installer requieres numpy 1.8. and does
      not work with prior versions. This is indidcated by a ValueError
      indicating a buffer dtype mismatch exception when you run
      pyprophet.
      """,
      license="BSD",
      url="http://github.com/uweschmitt/pyprophet",
      packages=find_packages(exclude=['ez_setup',
                                      'examples', 'tests']),
      include_package_data=True,
      include_dirs = [numpy.get_include()],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Chemistry',
      ],
      zip_safe=False,
      install_requires=[
          "numpy >= 1.7.1",
          "pandas == 0.12",   # 0.13.0 does not work yet
          "scipy >= 0.9.0",
          "numexpr >= 2.1",
          "scikit-learn >= 0.13",
      ],
      test_suite="nose.collector",
      tests_require="nose",
      entry_points={
          'console_scripts': [
              "pyprophet=pyprophet.main:main",
              ]
      },
      ext_modules=ext_modules,
      )
