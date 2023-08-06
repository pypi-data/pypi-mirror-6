from distutils.core import setup

setup(
    name='BatchNotebook',
    version='0.0.3',
    packages=['batch_notebook'],
    license='BSD-new license',
    description='Tools for running an IPython notebook in batch mode.',
    long_description=open('README.rst').read(),
    author='John Bjorn Nelson',
    author_email='jbn@pathdependent.com',
    url='https://github.com/jbn/BatchNotebook',
    install_requires=[
        'ipython >= 1.1.0'
    ],
    scripts=['bin/run_ipython_script.py'],
)
