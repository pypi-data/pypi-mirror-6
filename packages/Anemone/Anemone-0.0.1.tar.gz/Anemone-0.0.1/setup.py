from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name = 'Anemone',
    packages = ['anemone'],
    version = '0.0.1',
    description = 'Monitor long running analyses by remote plotting of selected variables',
    long_description = long_description,
    author = 'Tormod Landet',
    url = 'https://bitbucket.org/trlandet/anemone',
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires = ['wxPython', 'pyzmq', 'matplotlib']
)

