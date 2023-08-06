Documentation for the Code
**************************

Introduction

Constants
#########

Set all the constants used for running the simple climate model. 

+ Carbon dioxide (CO2), methane (CH4), and nitrous oxide (N2O) concentrations at their pre-industrial level (1750 values).

	baseCO2 = 278.305
 
	baseCH4 = 700.0

	baseN2O = 270.0
+ CO2 emissions are reported in Peta grams of carbon (PgC) where 1 PgC = 10^15 g carbon
	PgCperppm is the conversion factor for PgC to ppm of CO2.

	PgCperppm = 2.123

+ estimates of direct (aerDirectFac) and indirect (aerIndirectFac) aerosol radiative forcing factors in units of (W/m^2)/TgS 

	aerDirectFac = -0.002265226

	aerIndirectFac = -0.013558119

Description of the class
------------------------

.. automodule:: pySCM.SimpleClimateModel
   :members:

