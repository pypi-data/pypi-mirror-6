#!/usr/bin/python

from distutils.core import setup

with open('long_description.rst') as file:
    long_description = file.read()
    
setup(
    name='finance',
    version='0.2502',
    author='Niels Henrik Bruun',
    author_email='niels.henrik.bruun@gmail.com',
    url='http://www.bruunisejs.dk/PythonHacks/',
    download_url = "http://pypi.python.org/pypi/finance",
    description='finance - Financial Risk Calculations. Optimized for ease of use through class construction and operator overload',
    long_description=long_description,
    package_dir={'finance': 'finance', 
                 'decimalpy': 'decimalpy',
                 'mathematical_meta_code': 'mathematical_meta_code'
                 },
    packages=['finance', 'decimalpy', 'mathematical_meta_code'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Topic :: Office/Business',
        'Topic :: Education',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Utilities'
        ],
    platforms=["Operating System :: OS Independent"],
    licence='http://www.opensource.org/licenses/PythonSoftFoundation.php'
    )
