import pySCM

Filename = 'SimpleClimateModelParameterFile.txt'
PgCperppm = 2.123

try:
    scm = pySCM.SimpleClimateModel(Filename)
    scm.runModel()
    scm.saveOutput()
except SCMError as e:
    print('There was an error in thr program. The error message is: '+ e.value)
