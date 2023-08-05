from setuptools import setup
from gravipy import __version__


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='GraviPy',
      version=__version__,
      description='Tensor Calculus Package for General Relativity',
      long_description=readme(),
      url='',
      author='Wojciech Czaja and contributors',
      author_email='wojciech.czaja@gmail.com',
      maintainer='Wojciech Czaja and contributors',
      maintainer_email='wojciech.czaja@gmail.com',
      license='BSD',
      packages=['gravipy'],
      include_package_data=True,
      install_requires=["sympy >= 0.7.3"],
      platforms='any',
      zip_safe=False,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ])
