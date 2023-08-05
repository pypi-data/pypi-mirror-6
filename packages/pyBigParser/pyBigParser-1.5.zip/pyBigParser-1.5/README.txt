===========
pyBigParser
===========

pyBigParser provides classes for parsing long and complex math 
expresions. You might find it most useful for tasks involving 
evaluating from single functions to compounds functions.
Typical usage often looks like this::

    #!/usr/bin/env python
    
    from pybigparser import evaluator
    
    mybig = evaluator.bigFunction()
    mybig.setFunction("x**2+2*y")
    mybig.addSub("x", "24+6*c")
    mybig.addSub("y", "25 / d")
    mybig.addSub("c", "1")
    mybig.addSub("d", "4")
    
    mybig.evaluate()
    
    mybig.getSubValue("x")
    mybig.getSubValue("y")


Supported Functions
===================

 *  **cos**,  **sin**,  **abs**,  **log10**,  **log**,  **exp**, 
 *  **tan**,  **pi**,  **e**
 
Versions
========

 *  1.3 - It saves the values for each sub-function.
 *  1.5 - Fixed OverFlow Error with Exp function
 
Warnings
--------

 * The variables **e** and **pi** are reserved for the evaluator
 * Exceptions for iterative variables are not supported 