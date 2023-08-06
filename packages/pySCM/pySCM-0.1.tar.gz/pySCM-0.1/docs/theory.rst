.. |H2O| replace:: H\ :sub:`2`\ O
.. |CO2| replace:: CO\ :sub:`2`
.. |CH4| replace:: CH\ :sub:`4`
.. |N2O| replace:: N\ :sub:`2`\ O

====================
 Theory
====================

This simple climate model tracks the causal chain from emissions of radiatively active gases, usually referred to as greenhouse gases (GHGs), to changes in their atmospheric concentrations, to changes in radiative forcing, to changes in global mean surface temperature and finally to changes in global mean sea-level. Each of these steps in described in a separate section below.

The model requires input time series of the three primary anthropogenic
GHGs viz. |CO2|, |CH4|, |N2O| and sulfate aerosol. That said, if the effects of any of these do not need to be accounted for in the simulation, they can be set to zero. The model is referred to as a ‘simple’ climate model to differentiate it from complex atmosphere ocean general circulation models (AOGCMs). AOGCMs are extremely computationally demanding, often requiring months of processing on massively parallel computers to complete a single climate simulation. AOGCMs therefore cannot be used for long or complex analyses e.g. those requiring multiple model runs for different scenarios based on different input data sets. Simple climate models have been used extensively in the IPCC assessment reports for the calculation of global warming potentials etc. They reproduce the essential behaviour of the far more complex AOGCMs by parameterizing key processes that are dealt with in detail by AOGCMs. The result is that simple climate models cannot reproduce the detailed spatial variability in climate change nor reproduce the detailed observed variability in climate change that AOGCMs do. Simple climate models are therefore used to model changes in global parameters such as changes in the global concentrations of GHGs, changes in global radiative forcing, changes in global mean surface temperature, and
changes in sea level.

--------------------
Prescribing GHG emissions in the model
--------------------

See code.rst for an example of headers

.. math::
   (a + b)^2 = a^2 + 2ab + b^2
