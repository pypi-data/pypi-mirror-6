"""
This library was designed to use L-moments to predict optimal parameters
for a number of distributions.  Distributions supported in this file are
listed below, with their distribution suffix:
    *Exponential (EXP)
    *Gamma (GAM)
    *Generalised Extreme Value (GEV)
    *Generalised Logistic (GLO)
    *Generalised Normal (GNO)
    *Generalised Pareto (GPA)
    *Gumbel (GUM)
    *Kappa (KAP)
    *Normal (NOR)
    *Pearson III (PE3)
    *Wakeby (WAK)
    *Weibull (WEI)

The primary function in this file is the samlmu(x,nmom) function, which takes
an input dataset x and  input of the number of moments to produce the log
moments of that dataset.

For Instance, given a list "Data", if 5 l-moments are needed, the function
would be called by lmoments.samlmu(Data,5)

In this file contains four different functions for using each distribution.
Each function can be called by the prefix FUN with the suffix DIS.

*PEL: (x,nmom):
      Parameter Estimates.  This takes the L-Moments calculated by samlmu()
      and predicts the parameter estimates for that function.
      
      EXAMPLE: Find Wakeby distribution that best fits dataset DATA:

          import lmoments
          para = lmoments.pelwak(lmoments.samlmu(DATA,5))

*QUA: (f,para)
      Quantile Estimates.  This takes the parameter estimates for a
      distribution, and a given Quantile value to calculate the quantile for the
      given function.

      EXAMPLE: Find the Upper Quantile (75%) of the Kappa distribution that
      best fits dataset DATA:

          import lmoments
          para = lmoments.pelkap(lmoments.samlmu(DATA,5))
          UQ = lmoments.quakap(0.75,para)

*LMR: (para,nmom):
      L-Moment Ratios.  This takes the parameter estimates for a distribution
      and calculates nmom L-Moment ratios.

      EXAMPLE: Find 4 lmoment ratios for the Gumbel distribution that
      best fits dataset DATA:

          import lmoments
          para = lmoments.pelgum(lmoments.samlmu(DATA,5))
          LMR = lmoments.lmrgum(para,4)

*CDF: (x,para):
      Cumulative Distribution Function.  This takes the parameter estimates
      for a distribution and calculates the quantile for a given value x.

      EXAMPLE: Find the quantile of the datapoint 6.4 for the Weibull
      Distribution that best fits the dataset DATA:

          import lmoments
          para = lmoments.pelwei(lmoments.samlmu(DATA,5))
          quantile = lmoments.cdfwei(6.4,para)


*PDF: (x,para):
      Probability Distribution Function.  This takes the parameter estimates
      for a distribution and calculates the p value for a given value x.

      EXAMPLE: Find the p-value of the datapoint 6.4 for the Weibull
      Distribution that best fits the dataset DATA:

          import lmoments
          para = lmoments.pelwei(lmoments.samlmu(DATA,5))
          quantile = lmoments.pdfwei(6.4,para)

*LMOM: (para):
      L-Moment Estimation from Parameters.  This function takes the input
      parameters for a given distribution, and attempt to calculate the
      L-Moments that would correspond to this distribution.

      EXAMPLE: Estimate the L-Moments of the Weibull Distribution that has
      parameters (2.5,1.5,0.5)

          import lmoments
          Lmoments = lmoments.lmomwei([2.5,1.5,0.5])

*NlogL: (data,dist,peldist):
      Calculates the Negative Log Likelihood for use in AIC/AICc/BIC calculations.
      Provide data, and distribution to calculate NlogL.  Can also provide curve
      fitting parameters, but if they aren't provided, then the function will
      generate them via pelxxx(samlmu(data)).  To specify the distribution, use the
      three letters typically assigned.

      EXAMPLE: Calculate the Negative Log Likelihood of a Gamma distribution
      fitted to Data.

          import lmoments
          NLL = lmoments.NlogL(data,"GAM")

      EXAMPLE:  Calculate the Negative Log Likelihood of a Gamma distribution
      with parameters [2.5,1.0] when fitted to Data.

          import lmoments
          NLL = lmoments.NlogL(data,"GAM",[2.5,1.0])

*AIC: (data,dist,*distfit):
      Calculate the Akaike Information Criterion (AIC) using the chosen dataset
      and distribution

      EXAMPLE:  Calculate the Akaike Information Criterion for the weibull
      distribution using the input dataset data:

          import lmoments
          Akaike = AIC(data,"WEI")

This file contains a Python implimentation of the lmoments.f library created by
J. R. M. HOSKING.                                                                                 

The base Fortran code is copyright of the IBM Corperation, and the licensing
information is shown below:

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
IBM software disclaimer

LMOMENTS: Fortran routines for use with the method of L-moments
Permission to use, copy, modify and distribute this software for any purpose
and without fee is hereby granted, provided that this copyright and permission
notice appear on all copies of the software. The name of the IBM Corporation
may not be used in any advertising or publicity pertaining to the use of the
software. IBM makes no warranty or representations about the suitability of the
software for any purpose. It is provided "AS IS" without any express or implied
warranty, including the implied warranties of merchantability, fitness for a
particular purpose and non-infringement. IBM shall not be liable for any direct,
indirect, _special or consequential damages resulting from the loss of use,
data or projects, whether in an action of contract or tort, arising out of or
in connection with the use or performance of this software.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Additional code from the R library "lmomco" has been converted into Python.
This library was developed by WILLIAM ASQUITH, and was released under the GPL-3
License. Copyright (C) 2012 WILLIAM ASQUITH

The Python translation was conducted by:
    Sam Gillespie
    Numerical Analyst
    C&R Consulting
    Townsville Australia
    September 2013

For more information, or to report bugs, contact:
    sam@candrconsulting.com.au

Licensing for Python Translation:
####################################################
    Copyright (C) 2014 Sam Gillespie

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.Version 0.1.0:
####################################################

Initial Release

Version 0.1.1:
Corrected Small Errors and Typos

Version 0.2.0:
Added Probability Density Functions (PDF)
Added Reverse Lmoment Estimation Functions (LMOM)
Added Negative Log Likelhood Function (NlogL)
Included Unit Tests
Implimented better version of PELWAK function
Support for lists as x inputs for all CDF functions
Bugfixes
Now licensed under the GPLv3



Yet to be Implimented Features:
Support for lists as inputs in all relevant functions
Additional Distributions
"""

import scipy as _sp
import scipy.special as _spsp
import scipy.stats as _spst
import math
import sys
################################################################
##L-MOMENT CALCULATION FUNCTION samlmu
################################################################
def comb(N,k,exact=1):
    if exact:
        if (k > N) or (N < 0) or (k < 0):
            return 0
        val = 1
        for j in xrange(min(k, N-k)):
            val = (val*(N-j))//(j+1)
        return val
    else:
        k,N = _sp.asarray(k), _sp.asarray(N)
        lgam = _spsp.gammaln
        cond = (k <= N) & (N >= 0) & (k >= 0)
        sv =_spsp.errprint(0)
        vals = _sp.exp(lgam(N+1) - lgam(N-k+1) - lgam(k+1))
        sv = _spsp.errprint(sv)
        return _sp.where(cond, vals, 0.0)


def samlmu(x,nmom=5):
    x = sorted(x)
    n = len(x)   
    ##Calculate first order
    ##Pretty efficient, no loops
    coefl1 = 1.0/comb(n,1)
    suml1 = sum(x)
    l1 = coefl1*suml1

    if nmom == 1:
        ret = l1
        return(ret)

    ##Calculate Second order

    #comb terms appear elsewhere, this will decrease calc time
    #for nmom > 2, and shouldn't decrease time for nmom == 2
    #comb1 = comb(i-1,1)
    #comb2 = comb(n-i,1)
    comb1 = []
    comb2 = []
    for i in range(1,n+1):
        comb1.append(comb(i-1,1))
        comb2.append(comb(n-i,1))
    
    coefl2 = 0.5 * 1.0/comb(n,2)
    xtrans = []
    for i in range(1,n+1):
        coeftemp = comb1[i-1]-comb2[i-1]
        xtrans.append(coeftemp*x[i-1])
    
    l2 = coefl2 * sum(xtrans)

    if nmom  ==2:
        ret = [l1,l2]
        return(ret)

    ##Calculate Third order
    #comb terms appear elsewhere, this will decrease calc time
    #for nmom > 2, and shouldn't decrease time for nmom == 2
    #comb3 = comb(i-1,2)
    #comb4 = comb(n-i,2)
    comb3 = []
    comb4 = []
    for i in range(1,n+1):
        comb3.append(comb(i-1,2))
        comb4.append(comb(n-i,2))
    
    coefl3 = 1.0/3 * 1.0/comb(n,3)
    xtrans = []
    for i in range(1,n+1):
        coeftemp = (comb3[i-1]-
                    2*comb1[i-1]*comb2[i-1] +
                    comb4[i-1])
        xtrans.append(coeftemp*x[i-1])

    l3 = coefl3 *sum(xtrans) /l2

    if nmom  ==3:
        ret = [l1,l2,l3]
        return(ret)

    ##Calculate Fourth order
    #comb5 = comb(i-1,3)
    #comb6 = comb(n-i,3)
    comb5 = []
    comb6 = []
    for i in range(1,n+1):
        comb5.append(comb(i-1,3))
        comb6.append(comb(n-i,3))
    
    coefl4 = 1.0/4 * 1.0/comb(n,4)
    xtrans = []
    for i in range(1,n+1):
        coeftemp = (comb5[i-1]-
                    3*comb3[i-1]*comb2[i-1] +
                    3*comb1[i-1]*comb4[i-1] -
                    comb6[i-1])
        xtrans.append(coeftemp*x[i-1])

    l4 = coefl4 *sum(xtrans)/l2

    if nmom  ==4:
        ret = [l1,l2,l3,l4]
        return(ret)

    ##Calculate Fifth order
    coefl5 = 1.0/5 * 1.0/comb(n,5)
    xtrans = []
    for i in range(1,n+1):
        coeftemp = (comb(i-1,4)-
                    4*comb5[i-1]*comb2[i-1] +
                    6*comb3[i-1]*comb4[i-1] -
                    4*comb1[i-1]*comb6[i-1] +
                    comb(n-i,4))
        xtrans.append(coeftemp*x[i-1])

    l5 = coefl5 *sum(xtrans)/l2

    if nmom ==5:
        ret = [l1,l2,l3,l4,l5]
        return(ret)

#######################################################
#CDF FUNCTIONS
#######################################################

def cdfexp(x,para):
    if type(x) != int and type(x) != float:
        x = _sp.array(x)
    
    U = para[0]
    A = para[1]
    if A <= 0:
        cdfexp = 0
        print("Parameters Invalid")
        return(cdfexp)
    else:
        Y = (x-U)/A
        if U <= 0:
            cdfexp = 0
            print("Parameters Invalid")
            return(cdfexp)
        else:
            cdfexp = 1-_sp.exp(-Y)
            if type(x) == int or type(x) == float:
                if cdfexp >= 0:
                    return(cdfexp)
                else:
                    return(0)
            else:
                for i in range(0,len(cdfexp)):
                    if cdfexp[i] < 0:
                        cdfexp[i] = 0

            return(cdfexp)
            
#############################################################
            
def cdfgam(x,para):

    CDFGAM=0
    Alpha=para[0]
    Beta=para[1]
    if Alpha <= 0 or Beta <= 0:
        print("Parameters Invalid")
        return
    if type(x) == int or type(x) == float:
        if x <= 0:
            print("x Parameter Invalid")
            return
    else:
        for i in x:
            if i <= 0:
                print("One X Parameter in list is Invalid")
                return
        x = _sp.array(x)
    CDFGAM = _spsp.gammainc(Alpha,x/Beta)
    return(CDFGAM)

#############################################################

def cdfgev(x,para):
    SMALL = 1e-15
    U=para[0]
    A=para[1]
    G=para[2]
    if A <= 0:
        print("Parameters Invalid")
        return

    if type(x) != int and type(x) != float:
        x = _sp.array(x)

        
    Y = (x-U)/A
    if G==0:
        CDFGEV = _sp.exp(-_sp.exp(-Y))
    else:
        Arg = 1-G*Y

        if type(x) == int or type(x) == float:
            if Arg > SMALL:
                Y = -_sp.log(Arg)/G
                CDFGEV = _sp.exp(-_sp.exp(-Y))
            elif G<0:
                CDFGEV = 0
            else:
                CDFGEV = 1
        else:
            CDFGEV = []
            for i in range(0,len(Y)):
                if Arg[i] > SMALL:
                    Y[i] = -_sp.log(Arg[i])/G
                    CDFGEV.append(_sp.exp(-_sp.exp(-Y[i])))
                elif G<0:
                    CDFGEV.append(0)
                else:
                    CDFGEV.append(1)

            CDFGEV = list(CDFGEV)

    return(CDFGEV)

#############################################################

def cdfglo(x,para):
    SMALL = 1e-15
    U=para[0]
    A=para[1]
    G=para[2]

    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    if A <= 0:
        print("Parameters Invalid")
        return
    Y = (x-U)/A
    if G==0:
        CDFGLO=1/(1+_sp.exp(-Y))
    else:
        Arg = 1-G*Y
        if type(x) == int or type(x) == float:
            if Arg > SMALL:
                Y = -_sp.log(Arg)/G
                CDFGLO=1/(1+_sp.exp(-Y))
            elif G<0:
                CDFGLO = 0
            else: 
                CDFGLO = 1
        else:
            CDFGLO = []
            for i in range(0,len(Y)):
                if Arg[i] > SMALL:
                    Y[i] = -_sp.log(Arg[i])/G
                    CDFGLO.append(1/(1+_sp.exp(-Y[i])))
                elif G<0:
                    CDFGLO = 0
                else:
                    CDFGLO = 1

            CDFGLO = list(CDFGLO)
            
    return(CDFGLO)

#############################################################

def cdfgno(x,para):
    SMALL = 1e-15
    U=para[0]
    A=para[1]
    G=para[2]
    
    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    if A <= 0:
        print("Parameters Invalid")
        return
    Y = (x-U)/A
    if G==0:
        CDFGNO = 0.5+0.5*_sp.erg(Y*1/_sp.sqrt(2))
    else:
        Arg = 1-G*Y
        if type(x) == int or type(x) == float:
            if Arg > SMALL:
                Y = -_sp.log(Arg)/G
                CDFGNO = 0.5+0.5*_spsp.erf(Y*1/_sp.sqrt(2))
            elif G<0:
                CDFGNO = 0
            else:
                CDFGNO = 1

        else:
            CDFGNO = []
            for i in range(0,len(Y)):
                if Arg[i] > SMALL:
                    Y[i] = -_sp.log(Arg[i])/G
                    CDFGNO.append(0.5+0.5*_spsp.erf(Y[i]*1/_sp.sqrt(2)))
                elif G<0:
                    CDFGNO.append(0)
                else:
                    CDFGNO.append(1)
            CDFGNO = list(CDFGNO)
    return(CDFGNO)

#############################################################

def cdfgpa(x,para):
    SMALL = 1e-15
    U=para[0]
    A=para[1]
    G=para[2]
    
    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    CDFGPA = 0
    if A <= 0:
        print("Parameters Invalid")
        return
    Y = (x-U)/A

    if type(x) == int or type(x) == float:
        if Y <= 0:
            print("Parameters Invalid")
            return
    else:
        for i in Y:
            if i <= 0:
                print("Parameters Invalid")
                return
    
    if G==0:
        CDFGPA=1-_sp.exp(-Y)
    else:
        Arg = 1-G*Y
        if type(x) == int or type(x) == float:
            if Arg > SMALL:
                Y = -_sp.log(Arg)/G
                CDFGPA=1-_sp.exp(-Y)
            else:
                CDFGPA = 1
        else:
            CDFGPA = []
            for i in range(0,len(Y)):
                if Arg[i] > SMALL:
                    Y[i] = -_sp.log(Arg[i])/G
                    CDFGPA.append(1-_sp.exp(-Y[i]))
                else:
                    CDFGPA.append(1)

            CDFGPA = list(CDFGPA)
    return(CDFGPA)

#############################################################

def cdfgum(x,para):
    U = para[0]
    A = para[1]

    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    if A <= 0:
        print("Parameters Invalid")
        return
    else:
        Y = (x-U)/A
        CDFGUM = _sp.exp(-_sp.exp(-Y))
        return(CDFGUM)

#############################################################
    
def cdfkap(x,para):
    para = map(float,para)
    if type(x) == int or type(x) == float:
        pass
    elif len(x) > 1:
        x = _sp.array(x)
        
    SMALL = 1e-15
    [U,A,G,H] = para
    if A <= 0:
        print("Invalid Parameters")
        return
    if type(x) == int or type(x) == float:
        Y = [(x-U)/A]
    else:
        Y = list((x-U)/A)
        
    CDFKAP = []
    for i in Y:
        if G != 0:
            ARG = 1-G*i
            if ARG < SMALL:
                if G < 0:
                    CDFKAP.append(0)
                    continue
                if G > 0:
                    CDFKAP.append(1)
                    continue    
            i = -_sp.log(ARG)/G

        i = _sp.exp(-i)
        if H == 0:
            CDFKAP.append(_sp.exp(-i))
        else:
            ARG = 1-H*i
            if ARG > SMALL:
                i = -_sp.log(ARG)/H
                CDFKAP.append(_sp.exp(-i))
                continue
            else:
                CDFKAP.append(0)
                continue
    if len(CDFKAP) == 1:
        CDFKAP = CDFKAP[0]
    return(CDFKAP)
#############################################################
        
def cdfnor(x,para):
    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    if para[1] < 0:
        print("Invalid Parameters")
    cdfnor = 0.5+0.5*_spsp.erf((x-para[0])/para[1]*1.0/_sp.sqrt(2))
    return(cdfnor)

#############################################################

def cdfpe3(x,para):
    SMALL = 1e-6
    
    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    CDFPE3 = 0
    if para[1]<= 0:
        print("Parameters Invalid")
        return
    else:
        Gamma = para[2]
        if abs(Gamma) <= SMALL:
            Z = (x-para[0])/para[1]
            
            if type(Z) == list:
                Z = _sp.array(Z)
                
            CDFPE3 = 0.5+0.5*_spsp.erf(Z*1/_sp.sqrt(2))
            return(CDFPE3)
        else:
            Alpha = 4/(Gamma**2)
            Z = 2*(x-para[0])/(para[1]*Gamma)+Alpha
            if type(x) == int or type(x) == float:
                if Z > 0:
                    CDFPE3 = _spsp.gammainc(Alpha,Z)
                if Gamma < 0:
                    CDFPE3 = 1-CDFPE3
                return(CDFPE3)
            else:
                CDFPE3 = []
                for i in Z:
                    if i > 0:
                        CDFPE3.append(_spsp.gammainc(Alpha,i))
                    if Gamma < 0:
                        CDFPE3[-1] = 1-CDFPE3[-1]
                return(CDFPE3)

        
#############################################################

##THIS IS REALLY INEFFICIENT, LOOK INTO OPTIMISING TO REDUCE
##FUNCTION CALL
def cdfwak(x,para):
    if type(x) == float or type(x) == int:
        return(cdfwak2(x,para))
    else:
        save = []
        for i in x:
            save.append(cdfwak2(i,para))
        return(save)
        
def cdfwak2(x,para):
    
    EPS = 1e-8
    MAXIT = 20
    ZINCMX =3
    ZMULT = 0.2
    UFL = -170
    XI = para[0]
    A = para[1]
    B = para[2]
    C = para[3]
    D = para[4]

    if B+D <= 0 and (B!=0 or C!=0 or D!= 0):
        print("Invalid Parameters")
        return
    if A == 0 and B!= 0:
        print("Invalid Parameters")
        return
    if C == 0 and D != 0:
        print("Invalid Parameters")
        return
    if C < 0 or A+C < 0:
        print("Invalid Parameters")
        return
    if A == 0 and C == 0:
        print("Invalid Parameters")
        return

    CDFWAK = 0
    if x <= XI:
        return(CDFWAK)

    #Test for _special cases
    if B == 0 and C == 0 and D == 0:
        
        Z = (x-XI)/A
        CDFWAK = 1
        if -Z >= UFL:
            CDFWAK = 1-_sp.exp(-Z)
        return(CDFWAK)
    
    if C == 0:
        CDFWAK = 1
        if x >= (XI+A/B):
            return(CDFWAK)
        Z = -_sp.log(1-(x-XI)*B/A)/B
        if -Z >= UFL:
            CDFWAK = 1-_sp.exp(-Z)
        return(CDFWAK)

    
    if A == 0:
        Z = _sp.log(1+(x-XI)*D/C)/D
        if -Z >= UFL:
            CDFWAK = 1-_sp.exp(-Z)
        return(CDFWAK)


    CDFWAK=1
    if D <0 and x >= (XI+A/B-C/D):
        return(CDFWAK)

    Z=0.7
    if x < quawak(0.1,para):
        Z = 0
    if x < quawak(0.99,para):
        pass
    else:
        if D < 0:
            Z = _sp.log((x-XI-A/B)*D/C+1)/D
        if D == 0:
            Z = (x-XI-A/B)/C
        if D > 0:
            Z = _sp.log((x-XI)*D/C+1)/D
            
    for IT in range(1,MAXIT+1):
        EB = 0
        BZ = -B*Z
        if BZ >= UFL:
            EB = _sp.exp(BZ)
        GB = Z
        
        if abs(B)>EPS:
            GB = (1-EB)/B
        ED = _sp.exp(D*Z)
        GD = -Z

        if abs(D)>EPS:
            GD = (1-ED)/D

        XEST =XI +A*GB-C*GD
        FUNC = x-XEST
        DERIV1 = A*EB+C*ED
        DERIV2 = -A*B*EB+C*D*ED
        TEMP = DERIV1+0.5*FUNC*DERIV2/DERIV1

        if TEMP <= 0:
            TEMP = DERIV1
        ZINC = FUNC/TEMP

        if ZINC > ZINCMX:
            ZINC = ZINCMX

        ZNEW = Z+ZINC

        if ZNEW <= 0:
            Z = Z*ZMULT
        else:
            Z = ZNEW
            if abs(ZINC) <= EPS:
                CDFWAK = 1
                if -Z >= UFL:
                    CDFWAK = 1-_sp.exp(-Z)
                return(CDFWAK)

#############################################################   
def cdfwei(x,para):
    U = para[0]
    A = para[1]
    G = para[2]
    if type(x) != int and type(x) != float:
        x = _sp.array(x)
        
    if len(para) < 3:
        print("Invalid number of parameters")
        return
    elif para[1] <= 0 or para[2] <= 0:
        print("Invalid Parameters")
        return
    else:
        cdfwei = 1-_sp.exp(-((x-para[0])/para[1])**para[2])
        return(cdfwei)
    
#############################################################
#LMR FUNCTIONS
#############################################################

def lmrexp(para,nmom):
    A=para[1]
    if A <= 0:
        print("Invalid Parameters")
        return
    if nmom > 20:
        print("Parameter nmom too large")
    xmom = []
    xmom.append(para[0]+A)
    if nmom == 1:
        return(xmom)

    xmom.append(0.5*A)
    if nmom ==2:
        return(xmom)

    for i in range(3,nmom+1):
        xmom.append(2/float(i*(i-1)))

    return(xmom)
    
#############################################################

def lmrgam(para,nmom):
    A0 = 0.32573501
    [A1,A2,A3] = [0.16869150, 0.078327243,-0.0029120539]
    [B1,B2] = [0.46697102, 0.24255406]
    C0 = 0.12260172
    [C1,C2,C3] = [0.053730130, 0.043384378, 0.011101277]
    [D1,D2]    = [0.18324466, 0.20166036]
    [E1,E2,E3] = [2.3807576, 1.5931792, 0.11618371]
    [F1,F2,F3] = [5.1533299, 7.1425260, 1.9745056]
    [G1,G2,G3] = [2.1235833, 4.1670213, 3.1925299]
    [H1,H2,H3] = [9.0551443, 26.649995, 26.193668]

    Alpha = para[0]
    Beta = para[1]
    if Alpha <= 0 or Beta <= 0:
        print("Invalid Parameters")
        return
    if nmom > 4:
        print("Parameter nmom too large")
        return
    
    xmom = []
    xmom.append(Alpha*Beta)
    if nmom == 1:
        return(xmom)

    xmom.append(Beta*1/_sp.sqrt(_sp.pi)*_sp.exp(_spsp.gammaln(Alpha+0.5)-_spsp.gammaln(Alpha)))
    if nmom == 2:
        return(xmom)

    if Alpha < 1:
        Z= Alpha
        xmom.append((((E3*Z+E2)*Z+E1)*Z+1)/(((F3*Z+F2)*Z+F1)*Z+1))
        if nmom == 3:
            return(xmom)
        xmom.append((((C3*Z+C2)*Z+C1)*Z+C0)/((D2*Z+D1)*Z+1))
        if nmom == 4:
            return(xmom)
    else:
        Z=1/Alpha
        xmom.append(_sp.sqrt(Z)*(((A3*Z+A2)*Z+A1)*Z+A0)/((B2*Z+B1)*Z+1))
        if nmom == 3:
            return(xmom)
        
        xmom.append((((C3*Z+C2)*Z+C1)*Z+C0)/((D2*Z+D1)*Z+1))
        if nmom == 4:
            return(xmom)

#############################################################

def lmrgev(para,nmom):

    ZMOM=[0.577215664901532861, 0.693147180559945309,
        0.169925001442312363,0.150374992788438185,
        0.558683500577583138e-1,0.581100239999710876e-1,
        0.276242584297309125e-1,0.305563766579053126e-1,
        0.164650282258328802e-1,0.187846624298170912e-1,
        0.109328215063027148e-1,0.126973126676329530e-1,
        0.778982818057231804e-2,0.914836179621999726e-2,
        0.583332389328363588e-2,0.690104287590348154e-2,
        0.453267970180679549e-2,0.538916811326595459e-2,
        0.362407767772368790e-2,0.432387608605538096e-2]
    SMALL = 1e-6
    U = para[0]
    A = para[1]
    G = para[2]
    if A<= 0 or G <= -1:
        print("Invalid Parameters")
        return
    if nmom > 20:
        print("Parameter nmom too large")
        return

    if abs(G)>SMALL:
        GAM = _sp.exp(_spsp.gammaln(1+G))
        xmom = [U+A*(1-GAM)/G]
        if nmom == 1:
            return(xmom)

        XX2 = 1-2**(-G)
        xmom.append(A*XX2*GAM/G)
        if nmom == 2:
            return(xmom)
 
        Z0=1
        for j in range(2,nmom):
            DJ=j+1
            BETA = (1-DJ**(-G))/XX2
            Z0 = Z0*(4*DJ-6)/DJ
            Z = Z0*3*(DJ-1)/(DJ+1)
            SUM = Z0*BETA-Z
            if j == 2:
                xmom.append(SUM)
            else:
                for i in range(1,j-1):
                    DI = i+1
                    Z = Z*(DI+DI+1)*(DJ-DI)/((DI+DI-1)*(DJ+DI))
                    SUM = SUM-Z*xmom[i+1]
                xmom.append(SUM)
        return(xmom)
    
    else:
        xmom = [U]
        if nmom == 1:
            return(xmom)

        xmom.append(A*ZMOM[1])
        if nmom == 2:
            return(xmom)

        for i in range(2,nmom):
            xmom.append(zmom[i-1])

        return(xmom)
  
#############################################################
    
def lmrglo(para,nmom):
    SMALL = 1e-4
    C1 = _sp.pi**2/6
    C2 = 7*_sp.pi**4/360


    Z = [[0],[0]]
    Z.append([1])
    Z.append([0.166666666666666667,  0.833333333333333333])
    Z.append([0.416666666666666667,  0.583333333333333333])
    Z.append([0.666666666666666667e-1,  0.583333333333333333,
              0.350000000000000000])
    Z.append([0.233333333333333333,  0.583333333333333333,
              0.183333333333333333])

    Z.append([0.357142857142857143e-1,  0.420833333333333333,
              0.458333333333333333,  0.851190476190476190e-1])

    Z.append([0.150992063492063492,  0.515625000000000000,
              0.297916666666666667,  0.354662698412698413e-1])

    Z.append([0.222222222222222222e-1,  0.318893298059964727,
              0.479976851851851852,  0.165509259259259259,
              0.133983686067019400e-1])

    Z.append([0.106507936507936508,  0.447663139329805996,
              0.360810185185185185,  0.803902116402116402e-1,
              0.462852733686067019e-2])

    Z.append([0.151515151515151515e-1,  0.251316137566137566,
              0.469695216049382716,  0.227650462962962963,
              0.347139550264550265e-1,  0.147271324354657688e-2])

    Z.append([0.795695045695045695e-1,  0.389765946502057613,
              0.392917309670781893,  0.123813106261022928,
              0.134998713991769547e-1,  0.434261597456041900e-3])

    Z.append([0.109890109890109890e-1,  0.204132996632996633,
              0.447736625514403292,  0.273053442827748383,
              0.591917438271604938e-1,  0.477687757201646091e-2,
              0.119302636663747775e-3])

    Z.append([0.619345205059490774e-1,  0.342031759392870504,
              0.407013705173427396,  0.162189192806752331,
              0.252492100235155791e-1,  0.155093427662872107e-2,
              0.306778208563922850e-4])

    Z.append([0.833333333333333333e-2,  0.169768364902293474,
              0.422191282868366202,  0.305427172894620811,
              0.840827939972285210e-1,  0.972435791446208113e-2,
              0.465280282988616322e-3,  0.741380670696146887e-5])

    Z.append([0.497166028416028416e-1,  0.302765838589871328,
              0.410473300089185506,  0.194839026503251764,
              0.386598063704648526e-1,  0.341399407642897226e-2,
              0.129741617371825705e-3,  0.168991182291033482e-5])
             
    Z.append([0.653594771241830065e-2,  0.143874847595085690,
              0.396432853710259464,  0.328084180720899471,
              0.107971393165194318,  0.159653369932077769e-1,
              0.110127737569143819e-2,  0.337982364582066963e-4,
              0.364490785333601627e-6])

    Z.append([0.408784570549276431e-1,  0.270244290725441519,
              0.407599524514551521,  0.222111426489320008,
              0.528463884629533398e-1,  0.598298239272872761e-2,
              0.328593965565898436e-3,  0.826179113422830354e-5,
              0.746033771150646605e-7])

    Z.append([0.526315789473684211e-2,  0.123817655753054913,
              0.371859291444794917,  0.343568747670189607,
              0.130198662812524058,  0.231474364899477023e-1,
              0.205192519479869981e-2,  0.912058258107571930e-4,
              0.190238611643414884e-5,  0.145280260697757497e-7])

    U = para[0]
    A = para[1]
    G = para[2]

    if A <= 0 or abs(G) >= 1:
        print("Invalid Parameters")
        return

    if nmom > 20:
        print("Parameter nmom too large")
        return
    GG = G*G
    ALAM1 = -G*(C1+GG*C2)
    ALAM2 = 1+GG*(C1+GG*C2)
    if abs(G) > SMALL:
        ALAM2=G*_sp.pi/_sp.sin(G*_sp.pi)
        ALAM1=(1-ALAM2)/G

    xmom = [U+A*ALAM1]
    if nmom == 1:
        return(xmom)
             
    xmom.append(A*ALAM2)
    if nmom == 2:
        return(xmom)

    for M in range(3,nmom+1):
        kmax = M/2
        SUMM=Z[M-1][kmax-1]
        for K in range(kmax-1,0,-1):
            SUMM = SUMM*GG+Z[M-1][K-1]
        if M != M/2*2:
            SUMM = -G*SUMM
        xmom.append(SUMM)

    return(xmom)

#############################################################

def lmrgno(para,nmom):

    ZMOM = [0,   0.564189583547756287, 0,   0.122601719540890947,
            0,   0.436611538950024944e-1,0, 0.218431360332508776e-1,
            0,   0.129635015801507746e-1,0, 0.852962124191705402e-2,
            0,   0.601389015179323333e-2,0, 0.445558258647650150e-2,
            0,   0.342643243578076985e-2,0, 0.271267963048139365e-2]


    RRT2 = 1/_sp.sqrt(2)
    RRTPI = 1/_sp.sqrt(_sp.pi)
    
    RANGE = 5
    EPS = 1e-8
    MAXIT = 10

    U = para[0]
    A = para[1]
    G = para[2]
    if A <= 0:
        print("Invalid Parameters")
        return
    if nmom > 20:
        print("Parameter nmom too large")
        return

    

    if abs(G)<=EPS:
        xmom = [U]
        if nmom == 1:
            return(xmom)

        xmom.append(A*ZMOM[1])
        if nmom == 2:
            return(xmom)

        for i in range(3,nmom+1):
            xmom.append(zmom[i-1])

        return(xmom)


    EGG = _sp.exp(0.5*G**2)
    ALAM1 = (1-EGG)/G
    xmom = [U+A*ALAM1]
    if nmom == 1:
        return(xmom)
    
    ALAM2=EGG*_spsp.erf(0.5*G)/G
    xmom.append(A*ALAM2)
    if nmom == 2:
        return(xmom)
  
    CC=-G*RRT2
    XMIN=CC-RANGE
    XMAX=CC+RANGE
    SUMM = [0]*nmom
    
    N=16
    XINC=(XMAX-XMIN)/N

    for i in range(1,N):
        X = XMIN+i*XINC
        E = _sp.exp(-((X-CC)**2))
        D = _spsp.erf(X)
        P1 = 1
        P = D
        for M in range(3,nmom+1):
            C1=M+M-3
            C2=M-2
            C3=M-1
            P2=P1
            P1=P
            P=(C1*D*P1-C2*P2)/C3
            SUMM[M-1] = SUMM[M-1]+E*P

    EST = []
    for i in SUMM:
        EST.append(i*XINC)


    for IT in range(1,MAXIT+1):
        ESTX = EST
        N=N*2
        XINC=(XMAX-XMIN)/N
        for i in range(1,N-1,2):
            X = XMIN+i*XINC
            E = _sp.exp(-((X-CC)**2))
            D = _spsp.erf(X)
            P1 = 1
            P = D
            for M in range(3,nmom+1):
                C1=M+M-3
                C2=M-2
                C3=M-1
                P2=P1
                P1=P
                P=(C1*D*P1-C2*P2)/C3
                SUMM[M-1] = SUMM[M-1]+E*P

        NOTCGD = 0
        for M in range(nmom,2,-1):
            EST[M-1] = SUMM[M-1]*XINC
            if abs(EST[M-1]-ESTX[M-1]) > EPS*abs(EST[M-1]):
                NOTCGD = M

        if NOTCGD == 0:
            CONST = -_sp.exp(CC**2)*RRTPI/(ALAM2*G)
            
            for M in range(3,nmom+1):
                xmom.append(CONST*EST[M-1])
            return(xmom)
        else:
            print("Did Not Converge")
            return
        
#############################################################
                
def lmrgpa(para,nmom):
    U = para[0]
    A = para[1]
    G = para[2]
    if A <=0 or G < -1:
        print("Invalid Parameters")
        return
    if nmom > 20:
        print("Parameter nmom too large")
        return

    Y = 1/(1+G)
    xmom = [U+A*Y]
    if nmom == 1:
        return(xmom)
    
    Y = Y/(2+G)
    xmom.append(A*Y)
    if nmom == 2:
        return(xmom)
    
    Y = 1
    for i in range(3,nmom+1):
        AM = i-2
        Y = Y*(AM-G)/(i+G)
        xmom.append(Y)
    return(xmom)

#############################################################

def lmrgum(para,nmom):
    ZMOM = [0.577215664901532861,  0.693147180559945309,
     0.169925001442312363,  0.150374992788438185,
     0.0558683500577583138,  0.0581100239999710876,
     0.0276242584297309125,  0.0305563766579053126,
     0.0164650282258328802,  0.0187846624298170912,
     0.0109328215063027148,  0.0126973126676329530,
     0.00778982818057231804,  0.00914836179621999726,
     0.00583332389328363588,  0.00690104287590348154,
     0.00453267970180679549,  0.00538916811326595459,
     0.00362407767772368790,  0.00432387608605538096]

    A = para[1]
    if A <=0:
        print("Invalid Parameters")
        return
    if nmom >20:
        print("Parameter nmom too large")
        return
    xmom = [para[0]+A*ZMOM[0]]
    if nmom == 1:
        return(xmom)
    xmom.append(A*ZMOM[1])
    if nmom == 2:
        return(xmom)

    for i in range(2,nmom):
        xmom.append(ZMOM[i])
    return(xmom)

#############################################################

def lmrkap(para,nmom):
    EU = 0.577215664901532861
    SMALL = 1e-8
    OFL = 170
    U = para[0]
    A = para[1]
    G = para[2]
    H = para[3]

    if A <= 0 or G <= -1: 
        print("Invalid Parameters")
        return
    if H < 0 and (G*H)<= -1:
        print("Invalid Parameters")
        return
    if nmom > 20:
        print("Parameter nmom too large")
        return

    DLGAM = _spsp.gammaln(1+G)
    ICASE = 1
    if H > 0:
        ICASE = 3
    elif abs(H) < SMALL:
        ICASE = 2
    elif G == 0:
        ICASE = ICASE+3

    if ICASE == 1:
        Beta = []
        for IR in range(1,nmom+1):
            ARG = DLGAM + _spsp.gammaln(-IR/H-G) - _spsp.gammaln(-IR/H)-G*_sp.log(-H)
            if abs(ARG) > OFL:
                print("Calculation of L-Moments Failed")
                return
            Beta.append(_sp.exp(ARG))


    elif ICASE == 2:
        Beta = []
        for IR in range(1,nmom+1):
            Beta.append(_sp.exp(DLGAM-G*_sp.log(IR))*(1-0.5*H*G*(1+G)/IR))

    elif ICASE == 3:
        Beta = []
        for IR in range(1,nmom+1):
            ARG = DLGAM+ _spsp.gammaln(1+IR/H)-_spsp.gammaln(1+G+IR/H)-G*_sp.log(H)
            if abs(ARG) > OFL:
                print("Calculation of L-Moments Failed")
                return
            Beta.append(_sp.exp(ARG))
            
    elif ICASE == 4:
        Beta = []
        for IR in range(1,nmom+1):
            Beta.append(EU+_sp.log(-H)+_spsp.psi(-IR/H))
            
    elif ICASE == 5:
        Beta = []
        for IR in range(1,nmom+1):
            Beta.append(EU+_sp.log(IR))

    elif ICASE == 6:
        Beta = []
        for IR in range(1,nmom+1):
            Beta.append(EU+_sp.log(H)+_spsp.psi(1+IR/H))

    if G == 0:
        xmom = [U+A*Beta[0]]
    else:
        xmom = [U+A*(1-Beta[0])/G]

    if nmom == 1:
        return(xmom)

    ALAM2 = Beta[1]-Beta[0]
    if G == 0:
        xmom.append(A*ALAM2)
    else:
        xmom.append(A*ALAM2/(-G))

    if nmom == 2:
        return(xmom)

    Z0 = 1
    for j in range(3,nmom+1):
        Z0 = Z0*(4.0*j-6)/j
        Z = 3*Z0*(j-1)/(j+1)
        SUMM = Z0*(Beta[j-1]-Beta[0])/ALAM2 - Z
        if j == 3:
            xmom.append(SUMM)
        else:
            for i in range(2,j-1):
                Z = Z*(i+i+1)*(j-i)/((i+i-1)*(j+i))
                SUMM = SUMM - Z*xmom[i]
            xmom.append(SUMM)
    return(xmom)

#############################################################

def lmrnor(para,nmom):

    ZMOM =[0, 0.564189583547756287, 0,   0.122601719540890947,
        0,  0.0436611538950024944, 0,   0.0218431360332508776,
        0,  0.0129635015801507746, 0,   0.00852962124191705402,
        0,  0.00601389015179323333, 0,   0.00445558258647650150,
        0,  0.00342643243578076985, 0,   0.00271267963048139365]

    if para[1] <= 0:
        print("Invalid Parameters")
        return
    if nmom > 20:
        print("Parameter nmom too large")
        return
    xmom = [para[0]]
    if nmom == 1:
        return(xmom)

    xmom.append(para[1]*ZMOM[1])
    if nmom == 2:
        return(xmom)

    for M in range(2,nmom):
        xmom.append(ZMOM[M])

    return(xmom)

#############################################################

def lmrpe3(para,nmom):
    SMALL = 1e-6
    CONST = 1/_sp.sqrt(_sp.pi)
    A0 = 0.32573501
    [A1,A2,A3] = [0.16869150, 0.078327243,-0.0029120539]
    [B1,B2] = [0.46697102,0.24255406]
    C0 = 0.12260172
    [C1,C2,C3] = 0.053730130, 0.043384378, 0.011101277
    [D1,D2] = [0.18324466, 0.20166036]
    [E1,E2,E3] = [2.3807576, 1.5931792, 0.11618371]
    [F1,F2,F3] = [5.1533299, 7.1425260, 1.9745056]
    [G1,G2,G3] = [2.1235833, 4.1670213, 3.1925299]
    [H1,H2,H3] = [9.0551443, 26.649995, 26.193668]

    SD = para[1]
    if SD <= 0:
        print("Invalid Parameters")
        return
    if nmom > 4:
        print("Parameter nmom too large")
        return

    xmom = [para[0]]
    if nmom == 1:
        return(xmom)

    Gamma = para[2]
    if abs(Gamma) < SMALL:
        xmom = [para[0]]
        if nmom == 1:
            return(xmom)

        xmom.append(CONST*Para[1])
        if nmom == 2:
            return(xmom)

        xmom.append(0)
        if nmom == 3:
            return(xmom)

        xmom.append(C0)
        return(xmom)
    else:
        Alpha = 4/(Gamma*Gamma)
        Beta = abs(0.5*SD*Gamma)
        ALAM2 = CONST*_sp.exp(_spsp.gammaln(Alpha+0.5)-_spsp.gammaln(Alpha))
        xmom.append(ALAM2*Beta)
        if nmom == 2:
            return(xmom)

        if Alpha < 1:
            Z = Alpha
            xmom.append((((E3*Z+E2)*Z+E1)*Z+1)/(((F3*Z+F2)*Z+F1)*Z+1))
            if Gamma<0:
                xmom[2] = -xmom[2]
            if nmom == 3:
                return(xmom)

            xmom.append((((G3*Z+G2)*Z+G1)*Z+1)/(((H3*Z+H2)*Z+H1)*Z+1))
            return(xmom)

        else:
            Z = 1.0/Alpha
            xmom.append(_sp.sqrt(Z)*(((A3*Z+A2)*Z+A1)*Z+A0)/((B2*Z+B1)*Z+1))
            if Gamma < 0:
                xmom[2] = -xmom[2]

            if nmom == 3:
                return(xmom)

            xmom.append((((C3*Z+C2)*Z+C1)*Z+C0)/((D2*Z+D1)*Z+1))
            return(xmom)


#############################################################

def lmrwak(para,nmom):
    [XI,A,B,C,D]=para
    fail = 0
    if D >= 1:
        fail = 1
    if (B+D)<= 0 and (B!= 0 or C != 0 or D!=0):
        fail = 1
    if A == 0 and B != 0:
        fail = 1
    if C == 0 and D != 0:
        fail = 1
    if C < 0:
        fail = 1
    if (A+C) < 0:
        fail = 1
    if A == 0 and C == 0:
        fail = 1
    if nmom >= 20:
        fail = 2

    if fail == 1:
        print("Invalid Parameters")
        return
    if fail == 2:
        print("Parameter nmom too large")
        return

    Y=A/(1+B)
    Z=C/(1-D)
    xmom = []
    xmom.append(XI+Y+Z)
    if nmom == 1:
        return
    
    Y=Y/(2+B)
    Z=Z/(2-D)
    ALAM2=Y+Z
    xmom.append(ALAM2)
    if nmom == 2:
        return

    for i in range(2,nmom):
        AM=i+1
        Y=Y*(AM-2-B)/(AM+B)
        Z=Z*(AM-2+D)/(AM-D)
        xmom.append((Y+Z)/ALAM2)

    return(xmom)

#############################################################
def lmrwei(para,nmom):
    if len(para) != 3:
        print("Invalid number of parameters")
        return
    if para[1] <= 0 or para[2] <= 0:
        print("Invalid Parameters")
        return
    
    xmom = lmrgev([0,para[1]/para[2],1/para[2]],nmom)
    xmom[0] = para[0]+para[1] - xmom[0]
    xmom[2] = -xmom[2]
    return(xmom)


#############################################################
###PEL FUNCTIONS
#############################################################


def pelexp(xmom):
    if xmom[1] <= 0:
        print("L-Moments Invalid")
        return
    else:
        para = [xmom[0]-2*xmom[1],2*xmom[1]]
        return(para)

#############################################################

def pelgam(xmom):
    A1 = -0.3080
    A2 = -0.05812
    A3 = 0.01765
    B1 = 0.7213
    B2 = -0.5947
    B3 = -2.1817
    B4 = 1.2113
    
    if xmom[0] <= xmom[1] or xmom[1]<= 0:
        print("L-Moments Invalid")
        return
    CV = xmom[1]/xmom[0]
    if CV >= 0.5:
        T = 1-CV
        ALPHA =T*(B1+T*B2)/(1+T*(B3+T*B4))
    else:
        T=_sp.pi*CV**2
        ALPHA=(1+A1*T)/(T*(1+T*(A2+T*A3)))
        
    para = [ALPHA,xmom[0]/ALPHA]
    return(para)

#############################################################

def pelgev(xmom):
    SMALL = 1e-5
    eps = 1e-6
    maxit = 20
    EU =0.57721566
    DL2 = _sp.log(2)
    DL3 = _sp.log(3)
    A0 =  0.28377530
    A1 = -1.21096399
    A2 = -2.50728214
    A3 = -1.13455566
    A4 = -0.07138022
    B1 =  2.06189696 
    B2 =  1.31912239 
    B3 =  0.25077104
    C1 =  1.59921491
    C2 = -0.48832213
    C3 =  0.01573152
    D1 = -0.64363929
    D2 =  0.08985247

    T3 = xmom[2]
    if xmom[1]<= 0 or abs(T3)>= 1:
        print("L-Moments Invalid")
        return
    if T3<= 0:
        G=(A0+T3*(A1+T3*(A2+T3*(A3+T3*A4))))/(1+T3*(B1+T3*(B2+T3*B3)))
        if T3>= -0.8:
            para3 = G
            GAM = _sp.exp(_sp.special.gammaln(1+G))
            para2=xmom[1]*G/(GAM*(1-2**(-G)))
            para1=xmom[0]-para2*(1-GAM)/G
            para = [para1,para2,para3]
            return(para)

        if T3 <= -0.97:
            G = 1-_sp.log(1+T3)/DL2
            
        T0=(T3+3)*0.5
        for IT in range(1,maxit):
            X2=2**(-G)
            X3=3**(-G)
            XX2=1-X2
            XX3=1-X3
            T=XX3/XX2
            DERIV=(XX2*X3*DL3-XX3*X2*DL2)/(XX2**2)
            GOLD=G
            G=G-(T-T0)/DERIV
            if abs(G-GOLD) <= eps*G:
                para3 = G
                GAM = _sp.exp(_sp.special.gammaln(1+G))
                para2=xmom[1]*G/(GAM*(1-2**(-G)))
                para1=xmom[0]-para2*(1-GAM)/G
                para = [para1,para2,para3]
                return(para)
            
        print("Iteration has not converged")

    Z=1-T3
    G=(-1+Z*(C1+Z*(C2+Z*C3)))/(1+Z*(D1+Z*D2))
    if abs(G)<SMALL:
        para2 = xmom[1]/DL2
        para1 = xmom[0]-EU*para2
        para = [para1,para2,0]
        return(para)
    else:
        para3 = G
        GAM = _sp.exp(_sp.special.gammaln(1+G))
        para2=xmom[1]*G/(GAM*(1-2**(-G)))
        para1=xmom[0]-para2*(1-GAM)/G
        para = [para1,para2,para3]
        return(para)
 
#############################################################

def pelglo(xmom):
    SMALL = 1e-6
    
    G=-xmom[2]
    if xmom[1]<= 0 or abs(G)>= 1:
        print("L-Moments Invalid")
        return

    if abs(G)<= SMALL:
        para = [xmom[0],xmom[1],0]
        return(para)

    GG = G*_sp.pi/_sp.sin(G*_sp.pi)
    A = xmom[1]/GG
    para1 = xmom[0]-A*(1-GG)/G
    para = [para1,A,G]
    return(para)

#############################################################

def pelgno(xmom):
    A0 =  0.20466534e+01
    A1 = -0.36544371e+01
    A2 =  0.18396733e+01
    A3 = -0.20360244e+00
    B1 = -0.20182173e+01
    B2 =  0.12420401e+01
    B3 = -0.21741801e+00
    SMALL = 1e-8

    T3=xmom[2]
    if xmom[1] <= 0 or abs(T3) >= 1:
        print("L-Moments Invalid")
        return
    if abs(T3)>= 0.95:
        para = [0,-1,0]
        return(para)

    if abs(T3)<= SMALL:
        para =[xmom[0],xmom[1]*_sp.sqrt(_sp.pi),0] 

    TT=T3**2
    G=-T3*(A0+TT*(A1+TT*(A2+TT*A3)))/(1+TT*(B1+TT*(B2+TT*B3)))
    E=_sp.exp(0.5*G**2)
    A=xmom[1]*G/(E*_sp.special.erf(0.5*G))
    U=xmom[0]+A*(E-1)/G
    para = [U,A,G]
    return(para)

#############################################################

def pelgpa(xmom):
    T3=xmom[2]
    if xmom[1]<= 0:
        print("L-Moments Invalid")
        return
    if abs(T3)>= 1:
        print("L-Moments Invalid")
        return

    G=(1-3*T3)/(1+T3)
    
    PARA3=G
    PARA2=(1+G)*(2+G)*xmom[1]
    PARA1=xmom[0]-PARA2/(1+G)
    para = [PARA1,PARA2,PARA3]
    return(para)

#############################################################

def pelgum(xmom):
    EU = 0.577215664901532861
    if xmom[1] <= 0:
        print("L-Moments Invalid")
        return
    else:
        para2 = xmom[1]/_sp.log(2)
        para1 = xmom[0]-EU*para2
        para = [para1, para2]
        return(para)

#############################################################

def pelkap(xmom):
    EPS = 1e-6
    MAXIT = 20
    MAXSR = 10
    HSTART = 1.001
    BIG = 10
    OFLEXP = 170
    OFLGAM = 53

    T3 = xmom[2]
    T4 = xmom[3]
    para = [0]*4
    if xmom[1] <= 0:
        print("L-Moments Invalid")
        return
    if abs(T3) >= 1 or abs(T4) >=  1:
        print("L-Moments Invalid")
        return

    if T4 <= (5*T3*T3-1)/4:
        print("L-Moments Invalid")
        return

    if T4 >= (5*T3*T3+1)/6:
        print("L-Moments Invalid")
        return

    G = (1-3*T3)/(1+T3)
    H = HSTART
    Z = G+H*0.725
    Xdist = BIG

    #Newton-Raphson Iteration
    for it in range(1,MAXIT+1):
        for i in range(1,MAXSR+1):
            if G > OFLGAM:
                print("Failed to converge")
                return
            if H > 0:
                U1 = _sp.exp(_spsp.gammaln(1/H)-_spsp.gammaln(1/H+1+G))
                U2 = _sp.exp(_spsp.gammaln(2/H)-_spsp.gammaln(2/H+1+G))
                U3 = _sp.exp(_spsp.gammaln(3/H)-_spsp.gammaln(3/H+1+G))
                U4 = _sp.exp(_spsp.gammaln(4/H)-_spsp.gammaln(4/H+1+G))
            else:
                U1 = _sp.exp(_spsp.gammaln(-1/H-G)-_spsp.gammaln(-1/H+1))
                U2 = _sp.exp(_spsp.gammaln(-2/H-G)-_spsp.gammaln(-2/H+1))
                U3 = _sp.exp(_spsp.gammaln(-3/H-G)-_spsp.gammaln(-3/H+1))
                U4 = _sp.exp(_spsp.gammaln(-4/H-G)-_spsp.gammaln(-4/H+1))

            ALAM2 =  U1-2*U2
            ALAM3 = -U1+6*U2-6*U3
            ALAM4 =  U1-12*U2+30*U3-20*U4
            if ALAM2 == 0:
                print("Failed to Converge")
                return
            TAU3 = ALAM3/ALAM2
            TAU4 = ALAM4/ALAM2
            E1 = TAU3-T3
            E2 = TAU4-T4

            DIST = max(abs(E1),abs(E2))
            if DIST < Xdist:
                Success = 1
                break
            else:
                DEL1 = 0.5*DEL1
                DEL2 = 0.5*DEL2
                G = XG-DEL1
                H = XH-DEL2
                
        if Success == 0:
            print("Failed to converge")
            return

        #Test for convergence
        if DIST < EPS:
            para[3]=H
            para[2]=G
            TEMP = _spsp.gammaln(1+G)
            if TEMP > OFLEXP:
                print("Failed to converge")
                return
            GAM = _sp.exp(TEMP)
            TEMP = (1+G)*_sp.log(abs(H))
            if  TEMP > OFLEXP:
                print("Failed to converge")
                return

            HH = _sp.exp(TEMP)
            para[1] = xmom[1]*G*HH/(ALAM2*GAM)
            para[0] = xmom[0]-para[1]/G*(1-GAM*U1/HH)
            return(para)
        else:
            XG=G
            XH=H
            XZ=Z
            Xdist=DIST
            RHH=1/(H**2)
            if H > 0:
                U1G=-U1*_spsp.psi(1/H+1+G)
                U2G=-U2*_spsp.psi(2/H+1+G)
                U3G=-U3*_spsp.psi(3/H+1+G)
                U4G=-U4*_spsp.psi(4/H+1+G)
                U1H=  RHH*(-U1G-U1*_spsp.psi(1/H))
                U2H=2*RHH*(-U2G-U2*_spsp.psi(2/H))
                U3H=3*RHH*(-U3G-U3*_spsp.psi(3/H))
                U4H=4*RHH*(-U4G-U4*_spsp.psi(4/H))
            else:
                U1G=-U1*_spsp.psi(-1/H-G)
                U2G=-U2*_spsp.psi(-2/H-G)
                U3G=-U3*_spsp.psi(-3/H-G)
                U4G=-U4*_spsp.psi(-4/H-G)
                U1H=  RHH*(-U1G-U1*_spsp.psi(-1/H+1))
                U2H=2*RHH*(-U2G-U2*_spsp.psi(-2/H+1))
                U3H=3*RHH*(-U3G-U3*_spsp.psi(-3/H+1))
                U4H=4*RHH*(-U4G-U4*_spsp.psi(-4/H+1))

            DL2G=U1G-2*U2G
            DL2H=U1H-2*U2H
            DL3G=-U1G+6*U2G-6*U3G
            DL3H=-U1H+6*U2H-6*U3H
            DL4G=U1G-12*U2G+30*U3G-20*U4G
            DL4H=U1H-12*U2H+30*U3H-20*U4H
            D11=(DL3G-TAU3*DL2G)/ALAM2
            D12=(DL3H-TAU3*DL2H)/ALAM2
            D21=(DL4G-TAU4*DL2G)/ALAM2
            D22=(DL4H-TAU4*DL2H)/ALAM2
            DET=D11*D22-D12*D21
            H11= D22/DET
            H12=-D12/DET
            H21=-D21/DET
            H22= D11/DET
            DEL1=E1*H11+E2*H12
            DEL2=E1*H21+E2*H22
            
##          TAKE NEXT N-R STEP
            G=XG-DEL1
            H=XH-DEL2
            Z=G+H*0.725

##          REDUCE STEP IF G AND H ARE OUTSIDE THE PARAMETER _spACE

            FACTOR=1
            if G <= -1:
                FACTOR = 0.8*(XG+1)/DEL1
            if H <= -1:
                FACTOR = min(FACTOR,0.8*(XH+1)/DEL2)
            if Z <= -1:
                FACTOR = min(FACTOR,0.8*(XZ+1)/(XZ-Z))
            if H <= 0 and G*H<= -1:
                FACTOR = min(FACTOR,0.8*(XG*XH+1)/(XG*XH-G*H))

            if FACTOR == 1:
                pass
            else:
                DEL1 = DEL1*FACTOR
                DEL2 = DEL2*FACTOR
                G = XG-DEL1
                H = XH-DEL2
                Z = G+H*0.725
    
#############################################################

def pelnor(xmom):
    if xmom[1] <= 0:
        print("L-Moments Invalid")
        return
    else:
        para = [xmom[0],xmom[1]*_sp.sqrt(_sp.pi)]
        return(para)

#############################################################
    
def pelpe3(xmom):
    Small = 1e-6
    #Constants used in Minimax Approx:

    C1 = 0.2906
    C2 = 0.1882
    C3 = 0.0442
    D1 = 0.36067
    D2 = -0.59567
    D3 = 0.25361
    D4 = -2.78861
    D5 = 2.56096
    D6 = -0.77045

    T3=abs(xmom[2])
    if xmom[1] <= 0 or T3 >= 1:
        para = [0]*3
        print("L-Moments Invalid")
        return(para)

    if T3<= Small:
        para = []
        para.append(xmom[0])
        para.append(xmom[1]*_sp.sqrt(_sp.pi))
        para.append(0)
        return(para)

    if T3 >= (1.0/3):
        T = 1-T3
        Alpha = T*(D1+T*(D2+T*D3))/(1+T*(D4+T*(D5+T*D6)))
    else:
        T=3*_sp.pi*T3*T3
        Alpha=(1+C1*T)/(T*(1+T*(C2+T*C3)))
                    
    RTALPH=_sp.sqrt(Alpha)
    BETA=_sp.sqrt(_sp.pi)*xmom[1]*_sp.exp(_spsp.gammaln(Alpha)-_spsp.gammaln(Alpha+0.5))
    para = []
    para.append(xmom[0])
    para.append(BETA*RTALPH)
    para.append(2/RTALPH)
    if xmom[2] < 0:
        para[2]=-para[2]

    return(para)

#############################################################

def pelwak(xmom):
    if xmom[1] <= 0:
        print("Invalid L-Moments")
        return()
    if abs(xmom[2]) >= 1 or abs(xmom[3]) >= 1 or abs(xmom[4]) >= 1:
        print("Invalid L-Moments")
        return()

    ALAM1 = xmom[0]
    ALAM2 = xmom[1]
    ALAM3 = xmom[2]*ALAM2
    ALAM4 = xmom[3]*ALAM2
    ALAM5 = xmom[4]*ALAM2

    XN1= 3*ALAM2-25*ALAM3 +32*ALAM4
    XN2=-3*ALAM2 +5*ALAM3  +8*ALAM4
    XN3= 3*ALAM2 +5*ALAM3  +2*ALAM4
    XC1= 7*ALAM2-85*ALAM3+203*ALAM4-125*ALAM5
    XC2=-7*ALAM2+25*ALAM3  +7*ALAM4 -25*ALAM5
    XC3= 7*ALAM2 +5*ALAM3  -7*ALAM4  -5*ALAM5

    XA=XN2*XC3-XC2*XN3
    XB=XN1*XC3-XC1*XN3
    XC=XN1*XC2-XC1*XN2
    DISC=XB*XB-4*XA*XC
    skip20 = 0
    if DISC < 0:
        pass
    else:       
        DISC=_sp.sqrt(DISC)
        ROOT1=0.5*(-XB+DISC)/XA
        ROOT2=0.5*(-XB-DISC)/XA
        B= max(ROOT1,ROOT2)
        D=-min(ROOT1,ROOT2)
        if D >= 1:
            pass
        else:          
            A=(1+B)*(2+B)*(3+B)/(4*(B+D))*((1+D)*ALAM2-(3-D)*ALAM3)
            C=-(1-D)*(2-D)*(3-D)/(4*(B+D))*((1-B)*ALAM2-(3+B)*ALAM3)
            XI=ALAM1-A/(1+B)-C/(1-D)
            if C >= 0 and A+C>= 0:
                skip20 = 1
                
    if skip20 == 0:
        IFAIL=1
        D=-(1-3*xmom[2])/(1+xmom[2])
        C=(1-D)*(2-D)*xmom[1]
        B=0
        A=0
        XI=xmom[0]-C/(1-D)
        if D <= 0:
            A = C
            B=-D
            C = 0
            D = 0

    para =[XI,A,B,C,D]
    return(para)


#############################################################
def pelwei(xmom):
    if len(xmom) < 3:
        print("Insufficient L-Moments: Need 3")
        return
    if xmom[1] <= 0 or xmom[2] >= 1:
        print("L-Moments Invalid")
        return
    pg = pelgev([-xmom[0],xmom[1],-xmom[2]])
    delta = 1/pg[2]
    beta = pg[1]/pg[2]
    out = [-pg[0]-beta,beta,delta]
    return(out)

#############################################################
##QUANTILE FUNCTIONS
#############################################################

def quaexp(F,para):
    U = para[0]
    A = para[1]
    if A <= 0:
        print("Parameters Invalid")
        return
    if F <= 0 or F >= 1:
        print("F Value Invalid")
        return

    QUAEXP = U-A*_sp.log(1-F)
    return(QUAEXP)

#############################################################

def quagam(F,para):
    EPS = 1e-10
    maxit = 30
    QUAGAM = 0
    Alpha = para[0]
    Beta = para[1]
    if Alpha <= 0 or Beta <= 0:
        print("Parameters Invalid")
        return
    if F<=0 or F>= 1:
        print("F Value Invalid")
        return
    
    AM1 = Alpha - 1
    if AM1 != 0:
        DLOGG = _spsp.gammaln(Alpha)
        if AM1 <= 0:
            Root = _sp.exp((_sp.log(Alpha*F)+DLOGG)/Alpha)
        else:
            Root = Alpha*(1-1/(9*Alpha) + quastn(F)/_sp.sqrt(9*Alpha))**3

        if Root <= 0.01*Alpha:
            Root = _sp.exp((_sp.log(Alpha*F)+DLOGG)/Alpha)

        for it in range(1,maxit+1):
            FUNC = _spsp.gammainc(Alpha,Root)-F
            RINC = FUNC*_sp.exp(DLOGG+Root-AM1*_sp.log(Root))
            Root = Root-RINC
            if abs(FUNC) <= EPS:
                QUAGAM = Root*Beta
                return(QUAGAM)
    else:
        QUAGAM = -_sp.log(1-F)*Beta
        return(QUAGAM)

    print("Result failed to converge")
    return

#############################################################

def quagev(F,para):
    U = para[0]
    A = para[1]
    G = para[2]
    if A <= 0:
        print("Parameters Invalid")
        return
    if F <= 0 or F >= 1:
        if F == 0 and G < 0:
            QUAGEV = U+A/G
        elif F == 1 and G > 0:
            QUAGEV = U+A/G
        else:
            print("F Value Invalid")
            return

        
        print("F Value Invalid")
        return
    else:
        Y = -_sp.log(-_sp.log(F))
        if G != 0:
            Y = (1-_sp.exp(-G*Y))/G
        QUAGEV = U+A*Y
        return(QUAGEV)

#############################################################

def quaglo(F,para):
    U = para[0]
    A = para[1]
    G = para[2]
    if A <= 0:
        print("Invalid Parameters")
        return
    if F <= 0 or F >= 1:
        if F == 0 and G < 0:
            QUAGLO = U+A/G
            return(QUAGLO)
        elif F == 1 and G > 0:
            QUAGLO = U+A/G
            return(QUAGLO)
        else:
            print("F Value Invalid")
            return

    Y = _sp.log(F/(1-F))
    if G != 0:
        Y = (1-_sp.exp(-G*Y))/G
    QUAGLO = U+A*Y
    return(QUAGLO)

#############################################################

def quagno(F,para):
    U = para[0]
    A = para[1]
    G = para[2]
    if A <= 0:
        print("Invalid Parameters")
        return
    if F <= 0 or F >= 1:
        if F == 0 and G < 0:
            QUAGNO = U+A/G
            return(QUAGNO)
        elif F == 1 and G > 0:
            QUAGNO = U+A/G
            return(QUAGNO)
        else:
            print("F Value Invalid")
            return

    Y = quastn(F)
    if G != 0:
        Y = (1-_sp.exp(-G*Y))/G
    QUAGNO = U+A*Y
    return(QUAGNO)    
 
#############################################################

def quagpa(F,para):
    U = para[0]
    A = para[1]
    G = para[2]
    if A <= 0:
        print("Invalid parameters")
        return
    if F <= 0 or F >= 1:
        if F == 0:
            QUAGPA = U
            return(QUAGPA)
        elif F == 1 and G > 0:
            QUAGPA = U + A/G
            return(QUAGPA)
        else:
            print("F Value Invalid")
            return

    Y = -_sp.log(1-F)
    if G !=0:
        Y = (1-_sp.exp(-G*Y))/G
    QUAGPA = U+A*Y
    return(QUAGPA)

#############################################################

def quagum(F,para):

    U = para[0]
    A = para[1]
    
    if A <= 0:
        print("Parameters Invalid")
        return
    if F <= 0 or F >= 1:
        print("F Value Invalid")
        return
    QUAGUM = U-A*_sp.log(-_sp.log(F))
    return(QUAGUM)

#############################################################

def quakap(F,para):
    U = para[0]
    A = para[1]
    G = para[2]
    H = para[3]
    if A <= 0:
        print("Invalid Parameters")
        return
    if F <= 0 or F>= 1:
        if F==0:
            if H<=0 and G < 0:
                QUAKAP = U+A/G
            if H<= 0 and G>= 0:
                print("F Value Invalid")
                return
            if H > 0 and G!= 0:
                QUAKAP = U+A/G*(1-H**(-G))
            if H > 0 and G == 0:
                QUAKAP = U+A*_sp.log(H)

            return(QUAKAP)
        
        if F == 1:
            if G <= 0:
                print("F Value Invalid")
                return
            else:
                QUAKAP = U+A/G
                return(QUAKAP)

    else:
        Y = -_sp.log(F)
        if H!=0:
            Y = (1-_sp.exp(-H*Y))/H
            
        Y = -_sp.log(Y)
        if G!= 0:
            Y = (1-_sp.exp(-G*Y))/G
        QUAKAP = U+A*Y
        return(QUAKAP)

#############################################################

def quanor(F,para):

    if para[1] <= 0:
        print("Parameters Invalid")
        return
    if F <= 0 or F >= 1:
        print("F Value Invalid")
        return
    QUANOR = para[0]+para[1]*quastn(F)
    return(QUANOR)

#############################################################

def quape3(F,para):
    SMALL = 1e-6

    if para[1]<= 0:
        print("Paremters Invalid")
        return
    Gamma = para[2]
    if F <= 0 or F >= 1:
        if F == 0 and Gamma >0:
            QUAPE3 = para[0]-2*para[1]/Gamma
            return(QUAPE3)
        elif F == 1 and Gamma < 0:
            QUAPE3 = para[0]-2*para[1]/Gamma
            return(QUAPE3)
        else:
            print("F Value Invalid")
            return


    if abs(Gamma) < SMALL:
        QUAPE3 = para[0] + para[1]*quastn(F)
        return(QUAPE3)

    Alpha = 4/(Gamma*Gamma)
    Beta = abs(0.5*para[1]*Gamma)
    par = [Alpha,Beta]
    if Gamma > 0:
        QUAPE3 = para[0]-Alpha*Beta+quagam(F,par)
    if Gamma < 0:
        QUAPE3 = para[0]+Alpha*Beta-quagam(1-F,par)
    return(QUAPE3)

#############################################################

def quastn(F):
    _split1 = 0.425
    _split2 = 5
    const1 = 0.180625
    const2 = 1.6
    [A0,A1,A2,A3,A4,A5,A6,A7,B1,B2,B3,B4,B5,B6,B7] = [0.338713287279636661e1,
     0.133141667891784377e3,  0.197159095030655144e4,
     0.137316937655094611e5,  0.459219539315498715e5,
     0.672657709270087009e5,  0.334305755835881281e5,
     0.250908092873012267e4,  0.423133307016009113e2,
     0.687187007492057908e3,  0.539419602142475111e4,
     0.212137943015865959e5,  0.393078958000927106e5,
     0.287290857357219427e5,  0.522649527885285456e4]

    [C0,C1,C2,C3,C4,C5,C6,C7,D1,D2,D3,D4,D5,D6,D7] = [0.142343711074968358e1,
     0.463033784615654530e1,  0.576949722146069141e1,
     0.364784832476320461e1,  0.127045825245236838e1,
     0.241780725177450612e0,  0.227238449892691846e-1,
     0.774545014278341408e-3,  0.205319162663775882e1,
     0.167638483018380385e1,  0.689767334985100005e0,
     0.148103976427480075e0,  0.151986665636164572e-1,
     0.547593808499534495e-3,  0.105075007164441684e-8]
                                                      
    [E0,E1,E2,E3,E4,E5,E6,E7,F1,F2,F3,F4,F5,F6,F7] = [0.665790464350110378e1,
     0.546378491116411437e1,  0.178482653991729133e1,
     0.296560571828504891e0,  0.265321895265761230e-1,
     0.124266094738807844e-2,  0.271155556874348758e-4,
     0.201033439929228813e-6,  0.599832206555887938e0,
     0.136929880922735805e0,  0.148753612908506149e-1,
     0.786869131145613259e-3,  0.184631831751005468e-4,
     0.142151175831644589e-6,  0.204426310338993979e-14]

    Q = F-0.5
    if abs(Q) > _split1:
        R=F
        if Q >= 0:
            R = 1-F
        if R <= 0:
            print("F Value Invalid")
        R = _sp.sqrt(-_sp.log(R))
        if R > _split2:
            R = R - _split2
            QUASTN=((((((((E7*R+E6)*R+E5)*R+E4)*R+E3)*R+E2)*R+E1)*R+E0)/
            (((((((F7*R+F6)*R+F5)*R+F4)*R+F3)*R+F2)*R+F1)*R+1))
            if Q < 0:
                QUASTN = -QUASTN
            return(QUASTN)
        else:
            R=R-const2
            QUASTN=((((((((C7*R+C6)*R+C5)*R+C4)*R+C3)*R+C2)*R+C1)*R+C0)/
            (((((((D7*R+D6)*R+D5)*R+D4)*R+D3)*R+D2)*R+D1)*R+1))
            if Q < 0:
                QUASTN = -QUASTN
            return(QUASTN)

    else:
        R = const1-Q*Q
        QUASTN = Q*((((((((A7*R+A6)*R+A5)*R+A4)*R+A3)*R+A2)*R+A1)*R+A0)/
        (((((((B7*R+B6)*R+B5)*R+B4)*R+B3)*R+B2)*R+B1)*R+1))
        return(QUASTN)
    
#############################################################

def quawak(F,para):
    ufl = -170
  
    XI = para[0]
    A = para[1]
    B = para[2]
    C = para[3]
    D = para[4]
    
    fail = 0
    if (B+D) <= 0 and (B != 0 or C != 0 or D!= 0):
        fail = 1
    if A == 0 and B != 0:
        fail = 1
    if C == 0 and D != 0:
        fail = 1
    if C <0 or (A+C)< 0:
        fail = 1
    if A == 0 and C == 0:
        fail = 1

    if fail == 1:
        print("Parameters Invalid")
        return
    
    if F<= 0 or F>= 1:
        if F == 0:
            QUAWAK = XI
        elif F == 1:
            if D > 0:
                fail = 1
            if D < 0:
                QUAWAK = XI + A/B - C/D
            if D == 0 and C > 0:
                fail = 1
            if D == 0 and C == 0 and B == 0:
                fail = 1
            if D == 0 and C == 0 and B >0:
                QUAWAK = XI+A/B

            if fail == 1:
                print("Function Failed")
            else:
                return(QUAWAK)


    Z=-_sp.log(1-F)
    Y1 = Z
    if B == 0:
        Y2 = Z
        if D !=0:
            Y2 = (1-_sp.exp(D*Y2))/(-D)
        QUAWAK = XI+A*Y1+C*Y2
        return(QUAWAK)
    else:
        TEMP = -B*Z
        if TEMP < ufl:
            Y1 = 1/B
        if TEMP >= ufl:
            Y1 = (1-_sp.exp(TEMP))/B

        Y2 = Z
        if D !=0:
            Y2 = (1-_sp.exp(D*Y2))/(-D)
        QUAWAK = XI+A*Y1+C*Y2
        return(QUAWAK)

#############################################################

def quawei(f,para):
    if len(para) != 3:
        print("Invalid number of parameters")
    if para[1] <= 0 or para[2] <= 0:
        print("Invalid Parameters")
    if f <0 or f > 1:
        print("F Value Invalid")

    return(para[0]+para[1]*((-_sp.log(1-f))**(1/para[2])))

##############################################################
#PDF FUNCTIONS
##############################################################
def pdfexp(x,para):
    [U,A] = para
    f = []
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)

    for i in x:
        Y = (i-U)/A
        if Y <= 0:
            f.append(0)
        else:
            f.append(_sp.exp(-Y)/A)
    if len(f) == 1:
        f = f[0]
        
    return(f)

#############################################################

def pdfgam(x,para):
    [K, theta] = para
    f = []
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)

    for i in x:
        if i <= 0:
            f.append(0)
        else:
            f.append(1/(_spsp.gamma(K)*theta**K)*i**(K-1)*_sp.exp(-i/theta))
         
    if len(f) == 1:
        f = f[0]
    return(f)

#############################################################

def pdfgev(x,para):
    SMALL =1e-15 
    [XI,A,K] = para
    f = []
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in x:
        Y = (i-XI)/A
        if K == 0:
            f.append(A**(-1)*_sp.exp(-(1-K)*Y-_sp.exp(-Y)))
            continue
        ARG = 1-K*Y
        if ARG > SMALL:
            Y = -_sp.log(ARG)/K
            f.append(A**(-1) * _sp.exp(-(1-K)*Y-_sp.exp(-Y)))
            continue
        if K < 0:
            f.append(0)
            continue
        f.append(1)
        
    if len(f) == 1:
        f = f[0]
        
    return(f)

#############################################################

def pdfglo(x,para):
    SMALL = 1e-15
    [XI,A,K] = para
    f = []
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in x:
        Y = (i-XI)/A
        if K ==0:
            f.append(A**(-1)* _sp.exp(-(1-K)*Y)/(1+_sp.exp(-Y))**2)
            continue
        ARG = 1-K*Y
        if ARG > SMALL:
            Y = -_sp.log(ARG)/K
            f.append(A**(-1)*_sp.exp(-(1-K)*Y)/(1+_sp.exp(-Y))**2)
            continue
        if K < 0:
            f.append(0)
            continue
        if K > 0:
            f.append(1)
            continue

    if len(f) == 1:
        f = f[0]
        
    return(f)

#############################################################
   
def pdfgno(x,para):
    SMALL = 1e-15
    [XI,A,K] = para
    f = []

    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in x:
        Y = (i-XI)/A
        if K != 0:
            ARG = 1-K*Y
            if ARG > SMALL:
                Y = -_sp.log(ARG)/K
            else:
                if K < 0:
                    f.append(0)
                    continue
                else:
                    f.append(1)
                    continue

        f.append(_sp.exp(K*Y-Y**2/2)/(A*_sp.sqrt(2*_sp.pi)))

    if len(f) == 1:
        f = f[0]
        
    return(f)

#############################################################

def pdfgpa(x,para):
    SMALL = 1e-15
    [XI,A,K] = para
    f = []
    
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)

    for i in x:
        Y = (i-XI)/A
        if Y <= 0:
            f.append(0)
            continue
        if K == 0:
            f.append(A**(-1)*_sp.exp(-(1-K)*Y))
        else:
            ARG = 1-K*Y
            if ARG > SMALL:
                Y = -_sp.log(ARG)/K
                f.append(A**(-1)*_sp.exp(-(1-K)*Y))
            else:
                f.append(1)

    if len(f) == 1:
        f = f[0]
        
    return(f)

#############################################################

def pdfgum(x,para):
    [U,A] = para
    f = []

    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in x:
        Y = -(i-U)/A
        f.append(A**(-1)*_sp.exp(Y)*_sp.exp(-_sp.exp(Y)))
    if len(f) == 1:
        f = f[0]
    return(f)

#############################################################

def pdfkap(x,para):
    SMALL = 1e-15
    [XI,A,K,H] = para
    Fs = cdfkap(x, para)
    if type(x) == int or type(x) == float:
        Fs = [Fs]
        
    f = []

    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in range(0,len(x)):
        Y = (x[i]-XI)/A
        if K != 0:
            Y = 1-K*Y
            if Y <= SMALL:
                f.append(0)
            else:
                Y = (1-1/K)*_sp.log(Y)

        Y = _sp.exp(-Y)
        f.append(Y/A * Fs[i]**(1-H))
    if len(f) == 1:
        f = f[0]
    return(f)

#############################################################

def pdfnor(x,para):
    f = []
    
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in x:
        f.append(_spst.norm(para[0],para[1]).pdf(i))
    if len(f) == 1:
        f = f[0]
    return(f)

#############################################################

def pdfpe3(x,para):    
    [mu, sigma, gamma] = para
    f = []
    
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    alpha = 4/gamma**2
    tmp = _spsp.gamma(alpha)
    if gamma == 0 or math.isinf(tmp):
        for i in x:
            f.append(_spst.norm(0,1).pdf(((i-mu)/sigma)))
        return(f)

    beta = 0.5 * sigma * abs(gamma)
    xi = mu-2*sigma/gamma
    if gamma > 0:
        for i in x:
            Y = i-xi
            f.append((Y)**(alpha-1) * _sp.exp(-Y/beta)/(beta**alpha*tmp))
        if len(f) == 1:
            f = f[0]
        return(f)
    else:
        for i in x:
            Y = xi - i
            f.append((Y)**(alpha-1) * _sp.exp(-Y/beta)/(beta**alpha*tmp))
        if len(f) == 1:
            f = f[0]
        return(f)

#############################################################
    
def pdfwak(x,para):
    [XI,A,B,C,D] = para
    f = []
    
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    for i in x:
        Fc = 1-cdfwak(i,para)
        tmp = A*Fc**(B - 1) + C * Fc**(-D - 1)
        f.append(1/tmp)
    if len(f) == 1:
        f = f[0]
    return(f)

#############################################################

def pdfwei(x,para):
    f = []
    
    if type(x) == int or type(x) == float:
        x = [x]
    else:
        x = list(x)
        
    [ZETA,B,D] = para
    K = 1/D
    A = B/D
    XI = ZETA -B
    
    for i in x:
        f.append(pdfgev(-i,[XI,A,K]))

    if len(f) == 1:
        f = f[0]
        
    return(f)

##############################################################
#LMOM FUNCTIONS
##############################################################
def lmomexp(para):
    A = para[1]
    L1 = para[0]+A
    L2 = 0.5*A
    TAU3 = 2.0/6
    TAU4 = 2.0/12
    TAU5 = 2.0/20
    L3 = TAU3*L2
    L4 = TAU4*L2
    L5 = TAU5*L2

    return([L1,L2,L3,L4,L5])

##############################################################
def lmomgam(para):
    CONST = 0.564189583547756
    A0 = 0.32573501
    A1 = 0.1686915
    A2 = 0.078327243
    A3 = -0.0029120539
    B1 = 0.46697102
    B2 = 0.24255406
    C0 = 0.12260172
    C1 = 0.05373013
    C2 = 0.043384378
    C3 = 0.011101277
    D1 = 0.18324466
    D2 = 0.20166036
    E1 = 2.3807576
    E2 = 1.5931792
    E3 = 0.11618371
    F1 = 5.1533299
    F2 = 7.142526
    F3 = 1.9745056
    G1 = 2.1235833
    G2 = 4.1670213
    G3 = 3.1925299
    H1 = 9.0551443
    H2 = 26.649995
    H3 = 26.193668
    ALPHA = para[0]
    BETA = para[1]
    L1 = ALPHA*BETA
    L2 = BETA*CONST*_sp.exp(_spsp.gammaln(ALPHA+0.5)-_spsp.gammaln(ALPHA))
    if ALPHA < 1:
        Z = ALPHA
        TAU3 = (((E3*Z+E2)*Z+E1)*Z+1)/(((F3*Z+F2)*Z+F1)*Z+1)
        TAU4 = (((G3*Z+G2)*Z+G1)*Z+1)/(((H3*Z+H2)*Z+H1)*Z+1)
    else:
        Z = 1/ALPHA
        TAU3 = _sp.sqrt(Z)*(((A3*Z+A2)*Z+A1)*Z+A0)/((B2*Z+B1)*Z+1)
        TAU4 = (((C3*Z+C2)*Z+C1)*Z+C0)/((D2*Z+D1)*Z+1)
    L3 = TAU3 * L2
    L4 = TAU4 * L2

    return([L1,L2,L3,L4])



##############################################################
def lmomgev(para):
    
    ZMOM = [0.577215664901533, 0.693147180559945, 0.169925001442312, 
        0.150374992788438, 0.0558683500577583]
    SMALL = 1e-06

    [U,A,G] = para
    if abs(G) <= SMALL:
        L1 = U
        L2 = A*ZMOM[1]
        L3 = L2*ZMOM[2]
        L4 = L2*ZMOM[3]
        L5 = L2*ZMOM[4]
        return([L1,L2,L3,L4,L5])
   
    else:
        GAM = _sp.exp(_spsp.gammaln(1 + G))
        L1 = U+A*(1-GAM)/G
        XX2 = 1-2**(-G)
        L2 = A * XX2 * GAM/G
        Z0 = 1
        save = []
        for J in range(3,6):
            BETA = (1-J**(-G))/XX2
            Z0 = Z0*(4*J-6)/J
            Z = Z0*3*(J-1)/(J+1)
            SUM = Z0*BETA - Z
            if J > 3:
                for I in range(2,J-1):
                    Z = Z*(I+I+1)*(J-I)/((I+I-1)*(J+I))
                    SUM = SUM - Z *save[I-2]

            save.append(SUM)

        L3 = save[0]*L2
        L4 = save[1]*L2
        L5 = save[2]*L2
        return([L1,L2,L3,L4,L5])
            
##############################################################
def lmomglo(para):
    SMALL = 1e-04
    C1 = 1.64493406684823
    C2 = 1.89406565899449
    [XI,A,K] = para
    KK = K*K
    ALAM1 = -K * (C1 + KK * C2)
    ALAM2 = 1 + KK * (C1 + KK * C2)
    if abs(K) > SMALL:
        ALAM2 = K * _sp.pi/_sp.sin(K*_sp.pi)
        ALAM1 = (1 - ALAM2)/K
    L1 = XI + A * ALAM1
    L2 = A * ALAM2
    TAU3 = -K
    TAU4 = (1 + 5 * K**2)/6
    LCV = L2/L1
    L3 = TAU3 * L2
    L4 = TAU4 * L2
    return([L1,L2,L3,L4])
    
##############################################################
def lmomgno(para):

    SUM = [0,0,0,0,0]
    EST = [0,0,0,0,0]
    ESTX = [0,0,0,0,0]
    ZMOM = [0, 0.564189583547756, 0, 0.122601719540891, 0]
    RRT2 = 1/_sp.sqrt(2)
    RRTPI = 1/_sp.sqrt(_sp.pi)
    RANGE = 5
    EPS = 1e-08
    MAXIT = 10
    [U,A,G] = para
    if abs(G) <= EPS:
        L1 = U
        L2 = A * ZMOM[1]
        TAU3 = ZMOM[2]
        TAU4 = ZMOM[3]
        TAU5 = ZMOM[4]
        LCV = 2/L1
        L3 = TAU3 * L2
        L4 = TAU4 * L2
        L5 = TAU5 * L2
        return([L1,L2,L3,L4,L5])
    
    EGG = _sp.exp(0.5 * G**2)
    ALAM1 = (1 - EGG)/G
    L1 = U + A * ALAM1
    ALAM2 = EGG * _spsp.erf(0.5 * G)/G
    L2 = A * ALAM2
    CC = -G * RRT2
    XMIN = CC - RANGE
    XMAX = CC + RANGE
    N = 16
    XINC = (XMAX - XMIN)/N
    for i in range(1,N):
        X = XMIN + i * XINC
        E = _sp.exp(-((X - CC)**2))
        D = _spsp.erf(X)
        P1 = 1
        P = D
        for m in range(3,6):
            C1 = m + m - 3
            C2 = m - 2
            C3 = m - 1
            P2 = P1
            P1 = P
            P = (C1 * D * P1 - C2 * P2)/C3
            SUM[m-1] = SUM[m-1] + E * P

    EST[2] = SUM[2] * XINC
    EST[3] = SUM[3] * XINC
    EST[4] = SUM[4] * XINC
    for it in range(1, MAXIT+1):
        ESTX[2] = EST[2]
        ESTX[3] = EST[3]
        ESTX[4] = EST[4]
        N = N * 2
        XINC = (XMAX - XMIN)/N
        for i in range(1, N, 2):
            X = XMIN + i * XINC
            E = _sp.exp(-((X - CC)**2))
            D = _spsp.erf(X)
            P1 = 1
            P = D
            for m in range(3, 6):
                C1 = m + m - 3
                C2 = m - 2
                C3 = m - 1
                P2 = P1
                P1 = P
                P = (C1 * D * P1 - C2 * P2)/C3
                SUM[m-1] = SUM[m-1] + E * P

        NOTCGD = 0
        for m in range(5, 2, -1):
            EST[m-1] = SUM[m-1] * XINC
            if abs(EST[m-1] - ESTX[m-1]) > EPS * abs(EST[m-1]):
                NOTCGD = m
        
        if NOTCGD == 0:
            break
    
    if NOTCGD != 0:
        print("ITERATION HAS NOT CONVERGED. ONLY THE FIRST "+str(NOTCGD - 1)+" L-MOMENTS ARE RELIABLE")
    
    CONST = -_sp.exp(CC * CC) * RRTPI/(ALAM2 * G)
    TAU3 = CONST * EST[2]
    TAU4 = CONST * EST[3]
    TAU5 = CONST * EST[4]
    LCV = L2/L1
    L3 = TAU3 * L2
    L4 = TAU4 * L2
    L5 = TAU5 * L2
    return([L1,L2,L3,L4,L5])
    
##############################################################
def lmomgpa(para):
    [XI,A,K] = para
    Y = 1/(1 + K)
    L1 = XI + A*Y
    Y = Y/(2+K)
    L2 = A*Y
    x = [0,0,0,0,0]
    Y = 1
    for m in range(3, 6):
        AM = m - 2
        Y = Y * (AM - K)/(m + K)
        x[m-1] = Y
    
    TAU3 = x[2]
    TAU4 = x[3]
    TAU5 = x[4]
    LCV = L2/L1
    L3 = TAU3 * L2
    L4 = TAU4 * L2
    L5 = TAU5 * L2
    return([L1,L2,L3,L4,L5])

    
##############################################################
def lmomgum(para):
    ZMOM = [0.577215664901533, 0.693147180559945, 0.169925001442312, 
        0.150374992788438, 0.0558683500577583]
    A = para[1]
    L1 = para[0] + A * ZMOM[0]
    L2 = A * ZMOM[1]
    TAU3 = ZMOM[2]
    TAU4 = ZMOM[3]
    TAU5 = ZMOM[4]
    LCV = L2/L1
    L3 = TAU3*L2
    L4 = TAU4*L2
    L5 = TAU5*L2
    return([L1,L2,L3,L4,L5])
    
##############################################################
def lmomkap(para):

    def kapicase1(U,A,G,H):
        BETA = [0,0,0,0,0]
        OFL = _sp.log(sys.float_info.max)
        DLGAM = _spsp.gammaln(1+G)
        for R in range(1,6):
            ARG = DLGAM +_spsp.gammaln(-R/H-G)-_spsp.gammaln(-R/H)-G*_sp.log(-H)
            if abs(ARG) > OFL:
                print("Calculations of L-Moments have Failed")
                return()
            BETA[R-1] = _sp.exp(ARG)
        return(BETA)

    def kapicase2(U,A,G,H):
        BETA = [0,0,0,0,0]
        DLGAM = _spsp.gammaln(1+G)
        for R in range(1,6):
            BETA[R-1] = _sp.exp(DLGAM-G*_sp.log(R))*(1-0.5*H*G*(1+G)/R)
        return(BETA)

    def kapicase3(U,A,G,H):
        BETA = [0,0,0,0,0]
        OFL = _sp.log(sys.float_info.max)
        DLGAM = _spsp.gammaln(1+G)
        for R in range(1, 6):
            ARG = DLGAM + _spsp.gammaln(1+R/H)-_spsp.gammaln(1+G+R/H)-G*_sp.log(H)
            if abs(ARG) > OFL:
                print("Calculations of L-moments have broken down")
                return()
            BETA[R-1] = _sp.exp(ARG)
        return(BETA)
    

    def kapicase4(U,A,G,H):
        BETA = [0,0,0,0,0]
        EU = 0.577215664901533
        for R in range(1,6): 
            BETA[R-1] = EU + _sp.log(-H) + _spsp.psi(-R/H)
        return(BETA)

    def kapicase5(U,A,G,H):
        BETA = [0,0,0,0,0]
        EU = 0.577215664901533
        for R in range(1,6):
            BETA[R-1] = EU + _sp.log(R)
        return(BETA)

    def kapicase6(U,A,G,H):
        BETA = [0,0,0,0,0]
        EU = 0.577215664901533
        for R in range(1,6):
            BETA[R-1] = EU + _sp.log(H)+_spsp.psi(1+R/H)
        return(BETA)
    
    SMALL = 1e-08
    [U,A,G,H] = para
    ICASE = 1
    if H > 0:
        ICASE = 3
    if abs(H) < SMALL:
        ICASE = 2
    if G == 0:
        ICASE = ICASE + 3
    if ICASE == 1:
        BETA = kapicase1(U, A, G, H)
    if ICASE == 2:
        BETA = kapicase2(U, A, G, H)
    if ICASE == 3:
        BETA = kapicase3(U, A, G, H)
    if ICASE == 4:
        BETA = kapicase4(U, A, G, H)
    if ICASE == 5:
        BETA = kapicase5(U, A, G, H)
    if ICASE == 6:
        BETA = kapicase6(U, A, G, H)
    if G == 0:
        L1 = U+A*BETA[0]
    else:
        L1 = U+A*(1 - BETA[0])/G
    ALAM2 = BETA[1] - BETA[0]
    if G == 0:
        L2 = A*ALAM2
    else:
        L2 = A*ALAM2/(-G)
    
    LCV = L2/L1
    Z0 = 1
    x = [0,0,0,0,0]
    for J in range(3, 6):
        Z0 = Z0 * (4 * J - 6)/J
        Z = Z0 * 3 * (J - 1)/(J + 1)
        SUM = Z0 * (BETA[J-1] - BETA[0])/ALAM2 - Z
        if J == 3:
            x[J-1] = SUM
        else:
            for I in range(2, J - 1):
                Z = Z*(I+I+1)*(J-I)/((I+I-1)*(J+I))
                SUM = SUM - Z * x[I]
            
            x[J-1] = SUM
        
    
    TAU3 = x[2]
    TAU4 = x[3]
    TAU5 = x[4]
    L3 = TAU3 * LCV
    L4 = TAU4 * LCV
    L5 = TAU5 * LCV
    return([L1,L2,L3,L4,L5])

##############################################################
def lmomnor(para):
    ZMOM = [0, 0.564189583547756, 0, 0.122601719540891, 0]
    RRT2 = 1/_sp.sqrt(2)
    RRTPI = 1/_sp.sqrt(_sp.pi)
    L1 = para[0]
    L2 = para[1] * ZMOM[1]
    TAU3 = ZMOM[2]
    TAU4 = ZMOM[3]
    TAU5 = ZMOM[4]
    LCV = L2/L1
    L3 = TAU3 * L2
    L4 = TAU4 * L2
    L5 = TAU5 * L2
    return([L1,L2,L3,L4,L5])

##############################################################
def lmompe3(para):
    SMALL = 1e-06
    CONST = 1/_sp.sqrt(_sp.pi)
    A0 = 1/_sp.sqrt(3*_sp.pi)
    A1 = 0.1686915
    A2 = 0.078327243
    A3 = -0.0029120539
    B1 = 0.46697102
    B2 = 0.24255406
    C0 = 0.12260172
    C1 = 0.05373013
    C2 = 0.043384378
    C3 = 0.011101277
    D1 = 0.18324466
    D2 = 0.20166036
    E1 = 2.3807576
    E2 = 1.5931792
    E3 = 0.11618371
    F1 = 5.1533299
    F2 = 7.142526
    F3 = 1.9745056
    G1 = 2.1235833
    G2 = 4.1670213
    G3 = 3.1925299
    H1 = 9.0551443
    H2 = 26.649995
    H3 = 26.193668
    SD = para[1]
    L1 = para[0]
    GAMMA = para[2]
    if abs(GAMMA) < SMALL:
        L2 = CONST * para[1]
        TAU3 = 0
        TAU4 = C0
        L3 = L2 * TAU3
        L4 = L2 * TAU4
    
    else:
        ALPHA = 4/(GAMMA*GAMMA)
        BETA = abs(0.5*SD*GAMMA)
        ALAM2 = CONST*_sp.exp(_spsp.gammaln(ALPHA+0.5) - _spsp.gammaln(ALPHA))
        L2 = ALAM2*BETA
        if ALPHA < 1:
            Z = ALPHA
            TAU3 = (((E3 * Z + E2) * Z + E1) * Z + 1)/(((F3 * 
                Z + F2) * Z + F1) * Z + 1)
            if GAMMA < 0:
                TAU3 = -TAU3
            TAU4 = (((G3 * Z + G2) * Z + G1) * Z + 1)/(((H3 * 
                Z + H2) * Z + H1) * Z + 1)
            L3 = L2 * TAU3
            L4 = L2 * TAU4
        
        else:
            Z = 1/ALPHA
            TAU3 = _sp.sqrt(Z) * (((A3 * Z + A2) * Z + A1) * Z + 
                A0)/((B2 * Z + B1) * Z + 1)
            if GAMMA < 0:
                TAU3 = -TAU3
            TAU4 = (((C3 * Z + C2) * Z + C1) * Z + C0)/((D2 * 
                Z + D1) * Z + 1)
            L3 = L2 * TAU3
            L4 = L2 * TAU4


    LCV = L2/L1
    return([L1,L2,L3,L4])


##############################################################
def lmomwak(para):
    [XI,A,B,C,D] = para

    Y = A/(1+B)
    Z = C/(1-D)
    L1 = XI+Y+Z
    Y = Y/(2 + B)
    Z = Z/(2 - D)
    ALAM2 = Y + Z
    L2 = ALAM2
    x = [0,0,0,0,0]
    for M in range(3, 6):
        Y = Y * (M - 2 - B)/(M + B)
        Z = Z * (M - 2 + D)/(M - D)
        x[M-1] = (Y + Z)/ALAM2

    TAU3 = x[2]
    TAU4 = x[3]
    TAU5 = x[4]
    LCV = L2/L1
    L3 = TAU3 * L2
    L4 = TAU4 * L2
    L5 = TAU5 * L2
    return([L1,L2,L3,L4,L5])

##############################################################
def lmomwei(para):
    [ZETA,B,D] = para
    K = 1/D
    A = B/D
    XI = ZETA - B
    z = lmomgev([XI,A,K])
    z[0] = -z[0]
    z[2] = -z[2]
    z[4] = -z[4]
    return(z)

##############################################################
#MODEL SELECTION AND INFORMATION STATISTICS: AIC
##############################################################
def NlogL(data,dist,*args):

    if len(args) >= 2:
        print("Invalid number of arguments")
    elif len(args) == 1:
        peldist = args[0]
        if dist == "EXP":
            pdf = pdfexp
        elif dist == "GAM":
            pdf = pdfgam
        elif dist == "GEV":
            pdf = pdfgev
        elif dist == "GLO":
            pdf = pdfglo
        elif dist == "GNO":
            pdf = pdfgno
        elif dist == "GPA":
            pdf = pdfgpa
        elif dist == "GUM":
            pdf = pdfgum
        elif dist == "KAP":
            pdf = pdfkap        
        elif dist == "NOR":
            pdf = pdfnor
        elif dist == "PE3":
            pdf = pdfpe3
        elif dist == "WAK":
            pdf = pdfwak
        elif dist == "WEI":
            pdf = pdfwei
    else:
        if dist == "EXP":
            pdf = pdfexp
            peldist = pelexp(samlmu(data))
        elif dist == "GAM":
            pdf = pdfgam
            peldist = pelgam(samlmu(data))
        elif dist == "GEV":
            pdf = pdfgev
            peldist = pelgev(samlmu(data))
        elif dist == "GLO":
            pdf = pdfglo
            peldist = pelglo(samlmu(data))
        elif dist == "GNO":
            pdf = pdfgno
            peldist = pelgno(samlmu(data))
        elif dist == "GPA":
            pdf = pdfgpa
            peldist = pelgpa(samlmu(data))
        elif dist == "GUM":
            pdf = pdfgum
            peldist = pelgum(samlmu(data))
        elif dist == "KAP":
            pdf = pdfkap
            peldist = pelkap(samlmu(data))
        elif dist == "NOR":
            pdf = pdfnor
            peldist = pelnor(samlmu(data))
        elif dist == "PE3":
            pdf = pdfpe3
            peldist = pelpe3(samlmu(data))
        elif dist == "WAK":
            pdf = pdfwak
            peldist = pelwak(samlmu(data))
        elif dist == "WEI":
            pdf = pdfwei
            peldist = pelwei(samlmu(data))

    L = pdf(data,peldist)
    NLL =-sum(_sp.log(L))
    return(NLL)

##############################################################
def NumParam(dist):
    if dist == "EXP":
        return(2)
    elif dist == "GAM":
        return(2)
    elif dist == "GEV":
        return(3)
    elif dist == "GLO":
        return(3)
    elif dist == "GNO":
        return(3)
    elif dist == "GPA":
        return(3)
    elif dist == "GUM":
        return(2)
    elif dist == "KAP":
        return(4)
    elif dist == "NOR":
        return(2)
    elif dist == "PE3":
        return(3)
    elif dist == "WAK":
        return(5)
    elif dist == "WEI":
        return(3)

##############################################################
def AIC(data,dist,*args):
    if len(args) >= 2:
        print('Invalid Number of Arguments')
        return()
    elif len(args) == 1:
        peldist = args[0]
        NLL = NlogL(data,dist,peldist)
        k = len(peldist)
        AIC = 2*k+2*NLL
        return(AIC)
    else:
        NLL = NlogL(data,dist)
        k = NumParam(dist)
        AIC = 2*k+2*NLL
        return(AIC)

##############################################################
def AICc(data,dist,*args):
    AICbase = AIC(data,dist,*args)
    k = NumParam(dist)
    diff = 2*k*(k+1)/(len(data)-k-1)
    AICc = AICbase + diff
    return(AICc)


    
