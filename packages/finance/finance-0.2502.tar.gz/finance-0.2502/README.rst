##########################
finance - long description
##########################

The purpose of this project is to deliver ease of use python code for financial
risk calculations.
This code is not unconsious reproduction of textbook material.

It's about developing `abstract data types <http://en.wikipedia.org/wiki/Abstract_data_type>`_ as objects to ease financial calculations and code 
development.

At this point the code is by no means optimized for speed.

Financial and mathematical concepts are developed on the PythonHacks homepage.

* `To see more <http://www.bruunisejs.dk/PythonHacks/rstFiles/300%20Thoughts%20on%20finance.html>`_

=====================================
Part 1 - Simple time dependent assets
=====================================

Time is generic like a period such as eg 1 month and non-generic like a specific date.
In part both types are implemented with a heavy use of operator overload.

This means that questions like: How many days are there between a date 2009-12-27
and 3 months ahead can be calculated like:

>>> from finance import bankdate
>>> t1 = bankdate('2009-12-27')
>>> print t1 + '3m'
2010-03-27
>>> print t1 + '3m' - t1
90

* `To see more on bankdate <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.bankdate>`_
* `To see more on timeperiods <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.timeperiod>`_

Further a vector-like structure handling future payments - a dateflow - is 
implemented as a class.

Through method overload it is easy to build even very complex cashflows (= dateflow)

* `To see more on dateflows <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.dateflow>`_

Generators of standard dateflows is also a part of the package.

* `To see more on daterange <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.daterange>`_
* `To see more on daterangeiter <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.daterangeiter>`_ 
* `To see more on standarddateflowgenerator <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.standarddateflowgenerator>`_ 

Before any calculations on a dateflow can be made dates has to be converted into
times. For this the class datetotime is created.

* `To see more on datetotime <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.datetotime>`_

Finally simpel calculations like present value and different sorts of duration 
can be made though the class timeflow

* `To see more on timeflow <http://www.bruunisejs.dk/PythonHacks/rstFiles/200%20PythonHacks.html#finance.timeflow>`_

How to install
--------------

Just run setup.py install command. Or in windows use the windows installer.

Documentation, etc
------------------

Visit my `homepage <http://www.bruunisejs.dk/PythonHacks/>`_ to see more on how 
to use and the research behind the code. It's a blog like place on finance, math 
and scientific computing.

==================
Changes in 0.2502:
==================

There were still some problems with ultimo dates which now should be solved. 
Thank you to Johan Uys for bringing it to my attention.

==================
Changes in 0.2501:
==================

Problems with generating ultimo dates has been solved. Thank you to Ankush Sahai 
for bringing it to my attention.

================
Changes in 0.25:
================

Code has been rewritten to isolate strickt mathematical strucktures like e.g. DecimalVector in separate packages.
There have been slight modifications to yieldcurves.

================
Changes in 0.20:
================

Now discount curves based on benchmark zero bonds where the rates are continous forward rates.
It is possible to get standard yieldcalculations done like:

    Instantiate:

    >>> import finance
    >>> ns = finance.yieldcurves.NelsonSiegel(0.061, -0.01, -0.0241, 0.275)
    
    See the settings: 

    >>> ns
    Nelson Siegel (level=0.061, slope=-0.01, curvature=-0.0241, scale=0.275)
    
    Get the discountfactors at times 1, 2, 5, 10:

    >>> times = [1, 2, 5, 10]
    >>> ns(times)
    DecimalVector([0.9517121708497056177816078083, 0.9072377300179418172521412527, 0.7844132592062346545344544940, 0.6008958407659500402742872859])
    
    Get the zero coupon rate at time 5 and 7

    >>> r5, r7 = ns.zero_coupon_rate([5, 7])
    >>> r5, r7
    (Decimal('0.049762403554685553400657196'), Decimal('0.050625188777310061599365592'))
    
    Get the forward rate between time 5 and 7

    >>> f5_7 = ns.discrete_forward_rate(5, 7)
    >>> f5_7
    Decimal('0.052785255470657667493924028')

As shown above yieldcurves are made using the DecimalVector concept. Especially 
all outputs will be Decimal or DecimalVector.

For now there are 3 different yield curve types:

* The Nelson Siegel
* The natural cubic spline
* The financial cubic spline

This way the finance package covers a large part of yieldcurves in use.
Since it is easy to add more yieldcurves due to the design more will come.

Yieldcurves are of course integrated into the timeflow. **So now it is possible 
to do most fixed income calculations**.

**A tutorial on fixed income calculations in the finance package is on its way**.

Risk calculations based on linearily decomposable discountcurves is postponed 
intil later.

=================
Changes in 0.121:
=================

The code is rewritten according to recommedations from using 
`pylint <http://www.logilab.org/857>`_

================
Changes in 0.12:
================

* Timeflows are no longer based on numpy and scipy. In relation to financial 
  calculations numpy and scipy turned out to be not so profitable. The base is 
  now the datatype Decimal. This way all results are understandable without 
  knowledge of the puzles of numerical precision

================
Changes in 0.11:
================

Thanks to Nick Leaton for inspiring comments.

* Date rolling is moved to the bankdate class
* Time period is added the unit w(eek)
* Generators will handle date rolling
* Timeflows are now based on numpy and scipy

######################
Planned added contents
######################

The planned development so far is:

Planned added content of version 0.3:    
    Currencies, implementing Markowitz etc                             

Planned added content of version 0.4:
    Optionality though (binomial) trees
    
Planned added content of version 0.5:
    Bootstrapping from timeflows to get a base of benchmark zero bonds
    
Planned added content of version 0.6:
    Concept of portfolios, eg structured products                      

