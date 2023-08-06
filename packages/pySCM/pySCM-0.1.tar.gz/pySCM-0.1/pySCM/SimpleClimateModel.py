import matplotlib.pyplot as plt
import numpy as np
import string
import sys
import math

#-------------------------------------------------------------------------------
# These are our global variables
#-------------------------------------------------------------------------------
baseCO2 = 278.305
baseCH4 = 700.0
baseN2O = 270.0

# Sulfate forcing factors
# Direct and indirect RF factors on next line in units of (w/m^2)/TgS
aerDirectFac = -0.002265226
aerIndirectFac = -0.013558119

#-------------------------------------------------------------------------------
# define functions
#-------------------------------------------------------------------------------

class SCMError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
     
class emissionRec:
    def __init__(self):
        self.CO2 = float('NaN')
        self.CH4 = float('NaN')
        self.SOx = float('NaN')
        self.N2O = float('NaN')
     
class SimpleClimateModel:
    '''
    This is an example of using a doc string for documentation
    '''
    def __init__(self, Filename):
        self._contents = self._ReadParameters(Filename)
        self.emissions = self._ReadEmissions(self.GetParameter('File of emissions data'))
    
    def runModel(self):
        ''' 
        This function does.. 
        '''
        simYears =  int(self.GetParameter('Years to evaluate response functions'))
        oceanMLDepth = float(self.GetParameter('Ocean mixed layer depth [in meters]'))
        self._CO2Concs = CO2EmissionsToConcs(self.emissions, simYears, oceanMLDepth)
        self._CH4Concs = CH4EmssionstoConcs(self.emissions)
        self._N2OConcs = N2OEmssionstoConcs(self.emissions)
        self._RadForcing = CalcRadForcing(self.emissions, self._CO2Concs, self._CH4Concs, self._N2OConcs)

        self._temperatureChange = CalculateTemperatureChange(simYears, self._RadForcing)
        self._seaLevelChange = CalculateSeaLevelChange(simYears, self._temperatureChange)
        
    def saveOutput(self):        
        # write to file if required
        Filename = self.GetParameter('Write CH4 concentrations to file')
        if (Filename != None) and (Filename != ""):
            self.writeCO2ConcsToFile(self._CH4Concs, Filename)
        
        # plot CH4 concentations
        switch = self.GetParameter('Plot CH4 concentrations to file')
        if (switch != None) and (switch != ""):
            self.plotConcs('CH4', self._CH4Concs, switch)
            
        # write to file if required
        Filename = self.GetParameter('Write N20 concentrations to file')
        if (Filename != None) and (Filename != ""):
            self.writeCO2ConcsToFile(self._N2OConcs, Filename)
        
        # plot N2O concentations
        switch = self.GetParameter('Plot N2O concentrations to file')
        if (switch != None) and (switch != ""):
            self.plotConcs('N2O', self._N2OConcs, switch)
        
        # write to file if required
        Filename = self.GetParameter('Write CO2 concentrations to file')
        if (Filename != None) and (Filename != ""):
            self.writeCO2ConcsToFile(self._CO2Concs, Filename)
        
        # plot CO2 concentations
        switch = self.GetParameter('Plot CO2 concentrations to file')
        if (switch != None) and (switch != ""):
            self.plotConcs('CO2', self._CO2Concs, switch)

    
    def _ReadParameters(self, Filename):
        reader = open(Filename,'r')
        
        self._parameters = dict()
        for line in reader:
            pos = line.find('=')
            if (pos > 1):
                tag = line[0:pos]
                value = line[pos+1:].strip()
                self._parameters[tag] = value
        reader.close()
        
    
    def GetParameter(self, Tag):
        try:
            result = self._parameters[Tag]
        except KeyError:
            result = None
            
        return result
    
    def _ReadEmissions(self, Filename):
        startYr = int(self.GetParameter('Start year'))
        endYr = int(self.GetParameter('End year'))
        returnval = []
        for i in range(endYr-startYr+1):
            returnval.append(emissionRec())
    
        # read data
        table =np.loadtxt(self.GetParameter('File of emissions data'), skiprows=3)
    
        for col in range(1,table.shape[1]):
            data = np.zeros((len(returnval)))
            data.fill(float('NaN'))
            for row in range(len(table)):
                index = int(table[row][0] - startYr)
                data[index] = table[row][col]
    
            # now you should have all data for one species
            # interpolate missing values
    
            ind = np.where(np.isnan(data))[0]
            x = np.arange(0,len(returnval))
    
            xp_hold = np.where(~np.isnan(data))[0]
            xp = np.zeros(len(xp_hold)+1)
            xp[1:len(xp)] = xp_hold[0:len(xp_hold)]
    
            fp_hold = data[np.where(~np.isnan(data))[0]]
            fp = np.zeros(len(fp_hold)+1)
            fp[1:len(fp)] = fp_hold[0:len(fp_hold)]
    
            interpolVal = np.interp(x, xp, fp)
            #plt.plot(interpolVal,x)
            #plt.show()
            for index in range(len(interpolVal)):
                if col == 1:
                    returnval[index].CO2 = interpolVal[index]
                elif col == 2:
                    returnval[index].CH4 = interpolVal[index]
                elif col == 3:
                    returnval[index].N2O = interpolVal[index]
                elif col == 4:
                    returnval[index].SOx = interpolVal[index]
    
        return returnval
    
    #-------------------------------------------------------------------------------
    # Plot and print output
    #-------------------------------------------------------------------------------
    
    def writeCO2ConcsToFile(self, CO2Concs, Filename):
    
        startYr = int(self.GetParameter('Start year'))
        writer = open(Filename, 'w')
        for i in range(len(CO2Concs)):
            writer.write(str(startYr+i)+"    "+str(CO2Concs[i]+baseCO2)+"\n")
        writer.close()
    
    def plotConcs(self,species, concs, outputFile):
        startYr = int(self.GetParameter('Start year'))
        endYr = int(self.GetParameter('End year'))
        x = np.arange(startYr,endYr+1)
         
        if species == 'CO2':
            concs2plot = concs+baseCO2
        elif species == 'CH4':
            concs2plot = concs+baseCH4
        elif species == 'N2O':
            concs2plot = concs+baseN2O    
         
        fig = plt.figure(1)
        plt.plot(x,concs2plot)
        # title and axes labels
        fig.suptitle(species + ' concentrations', fontsize=20)
        plt.xlabel('Year', fontsize=18)
        plt.ylabel(species + ' concentration [ppm]', fontsize=18)
        # axes limits
        plt.xlim([startYr,endYr])
        plt.ylim([np.min(concs2plot), np.max(concs2plot)])
        # save figure to file
        plt.savefig(outputFile)
        
        
def GenerateOceanResponseFunction(numYears, OceanMLDepth):
    '''
    :param numYears: The number of years to simulate.
    :type name: int.
    :param OceanMLDepth: Ocean mixed layer depth [in meters].
    :type OceanMLDepth: float.
    :returns:  numpy.array -- the return code.
    '''
    # The following value taken from Joos et al., 1996, pg 400.}
    OceanArea = 3.62E14
    gCperMole = 12.0113     # Molar mass of carbon.
    SeaWaterDens = 1.0265E3 # Sea water density in kg/m^3.
    #OceanMLDepth = float(_GetParameter('Ocean mixed layer depth [in meters]'))

    returnVal = np.zeros(numYears)

    for yr in range(numYears):
        if yr < 2.0:
            value = 0.12935 + 0.21898*np.exp(-yr/0.034569) + 0.17003*np.exp(-yr/0.26936) + 0.24071*np.exp(-yr/0.96083) + 0.24093*np.exp(-yr/4.9792)
        else:
            value = 0.022936 + 0.24278*np.exp(-yr/1.2679) + 0.13963*np.exp(-yr/5.2528) + 0.089318*np.exp(-yr/18.601) + 0.037820*np.exp(-yr/68.736) + 0.035549*np.exp(-yr/232.30);
        returnVal[yr] = value * (1E21*PgCperppm/gCperMole)/(SeaWaterDens*OceanMLDepth*OceanArea)

    return returnVal

def GenerateBiosphereResponseFunction(numYears):
    returnVal = np.zeros(numYears)
    for yr in range(numYears):
        returnVal[yr] = 0.7021*np.exp(-0.35*yr) + 0.01341*np.exp(-yr/20.0) - 0.7185*np.exp(-0.4583*yr)+0.002932*np.exp(-0.01*yr);

    x = np.arange(numYears)
    #plt.plot(x,returnVal)
    #plt.show()
    return returnVal

def DeltaSeaWaterCO2FromOceanDIC(SurfaceOceanDIC):
    TC = 18.1716 # Effective Ocean temperature for carbonate chemistry in deg C.
    A1 = (1.5568-1.3993E-2*TC);
    A2 = (7.4706-0.20207*TC)*1E-3;
    A3 = -(1.2748-0.12015*TC)*1E-5;
    A4 = (2.4491-0.12639*TC)*1E-7;
    A5 = -(1.5468-0.15326*TC)*1E-10;
    returnVal = SurfaceOceanDIC*(A1+SurfaceOceanDIC*(A2+SurfaceOceanDIC*(A3+SurfaceOceanDIC*(A4+SurfaceOceanDIC*A5))));
    return returnVal

def CO2EmissionsToConcs(emissions, years, OceanMLDepth):
    """ 
    """
    # XAtmosBio is the amount of CO2 returned to the atmosphere as a result
    # of decay of the enhanced plant growth resulting from higher CO2.
    XAtmosBio = 0.0
    AirSeaGasExchangeCoeff = 0.1042  # kg m^-2 year^-1
    BiosphereNPP_0 = 60.0            # GtC/year.
    # 0.287 balances LUC emission of 1.1 PgC/yr in 1980s (Joos et al, 1996)}
    # 0.380  balances LUC emission of 1.6 PgC/yr in 1980s (IPCC 1994)}
    CO2FertFactor = 0.287
    CO2ppm_0 = 278.305
    atmosCO2 = np.zeros(len(emissions))
    atmosBioFlux = np.zeros(len(emissions))
    surfaceOceanDIC = np.zeros(len(emissions))
    seaWaterPCO2 = np.zeros(len(emissions))
    atmosSeaFlux = np.zeros(len(emissions))

    oceanResponse = GenerateOceanResponseFunction(years, OceanMLDepth)
    bioResponse = GenerateBiosphereResponseFunction(years)

    for yrInd in range(len(emissions)-1):
        if (yrInd > 0):
            seaWaterPCO2[yrInd] = DeltaSeaWaterCO2FromOceanDIC(surfaceOceanDIC[yrInd])

        atmosSeaFlux[yrInd] = AirSeaGasExchangeCoeff*(atmosCO2[yrInd]-seaWaterPCO2[yrInd])
        delta = BiosphereNPP_0*CO2FertFactor*np.log(1.0+(atmosCO2[yrInd]/CO2ppm_0))/PgCperppm-XAtmosBio
        XAtmosBio += delta
        atmosBioFlux[yrInd] += XAtmosBio
        # Accumulate committments of these fluxes to all future
        # times for SurfaceOceanDIC and AtmosBioFlux.
        for j in range(yrInd+1,len(surfaceOceanDIC)):
            Hold = surfaceOceanDIC[j]
            Hold = Hold + atmosSeaFlux[yrInd] * oceanResponse[j-yrInd];
            surfaceOceanDIC[j] = Hold

        for j in range(yrInd+1,len(atmosBioFlux)):
            atmosBioFlux[j] = atmosBioFlux[j] - XAtmosBio * bioResponse[j-yrInd]

        atmosCO2[yrInd+1] = atmosCO2[yrInd]+(emissions[yrInd].CO2/PgCperppm)-atmosSeaFlux[yrInd]-atmosBioFlux[yrInd]
    return atmosCO2

def CH4EmssionstoConcs(emissions):
    TauCH4 = 10.0
    LamCH4 = 1.0/TauCH4
    ScaleCH4 = 2.78

    Result = np.zeros(len(emissions))
    decay = np.exp(-LamCH4)
    accum = (1.0-decay)/(LamCH4*ScaleCH4)
    for i in range(1,len(emissions)):
        Result[i] = Result[i-1] * decay + emissions[i-1].CH4 * accum

    return Result

def N2OEmssionstoConcs(emissions):
    tauN2O = 114.0
    lamN2O = 1.0/tauN2O
    scaleN2O = 4.8

    Result = np.zeros(len(emissions))
    decay = np.exp(-lamN2O)
    accum = (1.0-decay)/(lamN2O*scaleN2O)
    for i in range(1,len(emissions)):
        Result[i] = Result[i-1] * decay + emissions[i-1].N2O * accum

    return Result

def CalcRadForcing(emissions, CO2Concs, CH4Concs, N2OConcs):
    radForcingCO2 = np.zeros(len(emissions))
    radForcingCH4 = np.zeros(len(emissions))
    radForcingN2O = np.zeros(len(emissions))
    radForcingSOx = np.zeros(len(emissions))
    totalRadForcing = np.zeros(len(emissions))

    # total CO2 radiative forcing
    radForcingCO2 = ([5.35 * np.log(1 + (CO2Concs[i]/baseCO2)) for i in range(len(emissions))])

    # total CH4 radiative forcing
    for i in range(len(emissions)):
        fnow = 0.47 * np.log(1 + 2.01e-5 * (((baseCH4 + CH4Concs[i]) * baseN2O)**0.75) + 5.31e-15 * (baseCH4 + CH4Concs[i]) * (((baseCH4 + CH4Concs[i])*baseN2O)**1.52))
        fthen = 0.47 * np.log(1 + 2.01e-5 * ((baseCH4 * baseN2O)**0.75) + 5.31e-15 * baseCH4 * ((baseCH4 * baseN2O)**1.52))
        radForcingCH4[i] = 0.036 * (math.sqrt(baseCH4 + CH4Concs[i]) - math.sqrt(baseCH4)) - (fnow - fthen)

    # total N2O radiative forcing
    for i in range(len(emissions)):
        fnow = 0.47 * np.log(1 + 2.01e-5 * ((baseCH4 * (baseN2O + N2OConcs[i]))**0.75) + 5.31e-15 * baseCH4 * ((baseCH4 * (baseN2O + N2OConcs[i]))**1.52))
        fthen = 0.47 * np.log(1 + 2.01e-5 * ((baseCH4 * baseN2O)**0.75) + 5.31e-15 * baseCH4 * ((baseCH4 * baseN2O)**1.52))
        radForcingN2O[i] = 0.12 * (math.sqrt(baseN2O + N2OConcs[i]) - math.sqrt(baseN2O)) - (fnow - fthen)

    # total SOx radiative forcing
    radForcingSOx = ([(aerDirectFac + aerIndirectFac) * emissions[i].SOx for i in range(len(emissions))])

    totalRadForcing = radForcingCO2 + radForcingCH4 + radForcingN2O + radForcingSOx
    return totalRadForcing

def GenerateTempResponseFunction(numYrs):
    result = ([(0.59557/8.4007)*np.exp(-i/8.4007)+(0.40443/409.54)*np.exp(-i/409.54) for i in range(numYrs)])

    return result

def GenerateSeaLevelResponseFunction(numYrs):
    result = ([(0.96677/1700.2)*np.exp(-i/1700.2)+(0.03323/33.788)*np.exp(-i/33.788) for i in range(numYrs)])

    return result


def CalculateTemperatureChange(years, radForcing):
    ClimateSensitivity = 1.1; #(4.114/3.74)
    result = np.zeros(len(radForcing))

    tempResFunc = GenerateTempResponseFunction(years)

    for i in range(len(radForcing)):
        for j in range(i, len(radForcing)):
            result[j] = result[j] + radForcing[i] * tempResFunc[j-i]

    result = result * ClimateSensitivity

    return result

def CalculateSeaLevelChange(years, tempChange):
    result = np.zeros(len(tempChange))

    seaLevelResFunc = GenerateSeaLevelResponseFunction(years)

    for i in range(len(tempChange)):
        for j in range(i, len(tempChange)):
            result[j] = result[j] + tempChange[i] * seaLevelResFunc[j-i]

    return result
