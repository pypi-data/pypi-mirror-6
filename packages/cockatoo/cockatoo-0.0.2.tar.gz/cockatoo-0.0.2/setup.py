from setuptools import setup, find_packages

VERSION = '0.0.2'

setup(
    name='cockatoo',
    description='cockatoo - A similarity metric for macromolecular crystallization conditions',
    long_description='cockatoo - A similarity metric for macromolecular crystallization conditions',
    author='Andrew E. Bruno',
    url='https://github.com/ubccr/cockatoo',
    license='GNU General Public License v3 (GPLv3)',
    author_email='aebruno2@buffalo.edu',
    version=VERSION,
    include_package_data=True,
    packages=find_packages(exclude=['tests*']),
    package_data={'cockatoo': ['data/*.csv', 'data/*.json']},
    scripts=['bin/cockatoo'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
     ]
)
