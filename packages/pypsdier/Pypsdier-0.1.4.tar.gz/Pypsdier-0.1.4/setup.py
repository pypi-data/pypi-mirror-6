from distutils.core import setup

setup(
    name='Pypsdier',
    version='0.1.4',
    author='Sebastian Flores',
    author_email='sebastiandres@gmail.com',
    packages=['pypsdier', 'pypsdier/core', 'pypsdier/examples'],
    scripts=[],
    url='http://www.bitbucket.com/sebastiandres/pypsdier',
    license='BSD',
    description='Solver for general Reaction-Diffusion equations.',
    long_description=open('README.txt').read(),
)
