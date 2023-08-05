"""
Optimal Stellar Models (OSM)

Copyright (c) 2012 R. Samadi (LESIA - Observatoire de Paris)

This is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.
"""

import matplotlib.pyplot as plt
import numpy as np
import cestam.FortranIO
import math
from osmlib import *

msun = 1.98919e33           # solar mass
rsun = 6.9599e10            # solar radius
gmsun = 1.32712438e26       # G Msun
ggrav = gmsun/msun          # grav. constant G

class OSMError(Exception):
	def __init__(self, value):
         	self.value = value
	def __str__(self):
		return repr(self.value) 

## def dnu(modes):
##     # INPUTS:
##     # modes[:,0] : n order
##     # modes[:,1] : l degree
##     # modes[:,2] : nu frequency muHz
##     # modes[:,3] : sigma error in frequency mHz
##     # OUTPUTS:
##     # (y,covar):
##     #  y : Delta_nu [in muHz] as a function of frequency
##     #

##     l = modes[:,1]
##     nu = modes[:,2]

##     Nf =   len(nu)
##     # number of modes for each l degree
##     Nl = []
##     m = 1
##     for i in range(1,Nf):
##         if( l[i] != l[i-1]):
##             Nl.append(m)
##             m = 0
##         m += 1
##     Nl.append(m)
##     N = Nf - len(Nl)
##     coef = np.zeros( (N,Nf) ) #
##     m = 0
##     n = 0
##     for k in range(len(Nl)): # loop over the l values:
##         for p in range(Nl[k]-1):
##             for i in range(Nl[k]):
##                 if( i == p):
##                     coef[m+p, n + i] = -1.
##                 elif( i  == p + 1 ):
##                     coef[m+p, n + i] = 1.
##         m += Nl[k]-1
##         n += Nl[k]
##     y = np.empty(N)
##     for i in range(N):
##         y[i] = (coef[i,:]*nu).sum()
##     return (y,coef)

def dnu(modes,lval=None):
    # Delta_nu (n) = nu_{n,l} - nu_{n-1,l} 
    # 
    # INPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency muHz
    # modes[:,3] : sigma error in frequency mHz
    # OUTPUTS:
    # (y,coef):
    #  y : Delta_nu [in muHz] as a function of frequency
    #

    if(lval == None):
        lval = get_l_values(modes)

    l = modes[:,1]
    nu = modes[:,2]
    n =  modes[:,0]
    
    Nf =   len(nu)
    
    # number of modes for each l degree
    Nl = []
    N = 0
    for s in lval:
        j = np.where(l == s)
        m = len(j[0])
        Nl.append(m)
        N += m-1

    coef = np.zeros((N,Nf))  
    yn = np.empty(N)
    p = 0 
    for k in range(len(lval)):
        if(Nl[k] > 1):
            i = np.where( l ==  lval[k] ) [0]
            for m in i[1:]:
                for j in range(Nf):
                    if( n[j] == n[m] and l[j] == lval[k] ):
                        coef[p,j] = 1.
                        yn[p] = n[j]
                    if( n[j] == n[m]-1 and l[j] == lval[k]):
                        coef[p,j] = -1.
                p +=  1

    y = np.empty(N)
    for i in range(N):
        y[i] = (coef[i,:]*nu).sum()
    return (y,coef,yn)

def d01(modes):
    # d01 = nu_{n,0} - ( nu_{n-1,1} + nu_{n,1}) / 2
    # INPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency muHz
    # modes[:,3] : sigma error in frequency mHz
    # OUTPUTS:
    # (y,coef):
    #  y : d01 [in muHz] as a function of frequency
    #

    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)
    i1 = np.where(l == 1)

    i0 = i0[0]
    i1 = i1[0]
    


    if( l[i0[0]] !=0 and l[i1[0]] != 1):
        print 'error in d01, the l=1 modes must be placed after the l=0 modes'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])

    n0 = int(max([n0min,n1min+1]))
    n1 = int(min([n0max,n1max]))

    i00 = i0[np.argmin(np.abs(n[i0]-n0))]
    i01 = i0[np.argmin(np.abs(n[i0]-n1))]
   
    #    print n0,n1,i00,i01
    N = n1 - n0 +1
    yn = np.empty(N)
    coef = np.zeros((N,Nf))
    for i in range(i00,i01+1):
        #   print n[i],l[i]
        for j in range(Nf):
            if( n[j] == n[i] and  l[j] == 0 ):
                coef[i,j] = 1.
                yn[i] = n[j]
            if( (n[j] == n[i]-1 or n[j] == n[i])  and  l[j] == 1 ):
                coef[i,j] = -1./2.
        
    y = np.empty(N)
    for i in range(N):
        y[i] = (coef[i,:]*nu).sum()

    return (y,coef,yn)



def d02(modes):
    # d02 = nu_{n,0} - nu_{n-1,2} 
    # INPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency muHz
    # modes[:,3] : sigma error in frequency mHz
    # OUTPUTS:
    # (y,coef):
    #  y : d02 [in muHz] as a function of frequency
    #

    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)[0]
    i1 = np.where(l == 2)[0]

    if( l[i0[0]] !=0 and l[i1[0]] != 2):
        print 'error in d02, the l=2 modes must be placed after the l=0 modes'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])

    n0 = int(max([n0min,n1min+1]))
    n1 = int(min([n0max,n1max+1]))

    
    N = n1 - n0 +1
    yn = np.empty(N)
    coef = np.zeros((N,Nf))
    for i in range(N):
        #   print n[i],l[i]
        for j in range(Nf):
            if( n[j] == i + n0 and  l[j] == 0 ):
                coef[i,j] = 1.
                yn[i] = n[j]
            if( (n[j] == i + n0 - 1)  and  l[j] == 2 ):
                coef[i,j] = -1.
        
    y = np.empty(N)
    for i in range(N):
        y[i] = (coef[i,:]*nu).sum()

    return (y,coef,yn)
        
def sd(modes,lval=None):
    # second difference as a function of frequency (Gough 1990, Houdek & Gough 2007)
    # sd = nu_{n-1,l} - 2 nu_{n,l} + nu_{n+1,l}
    # 
    # INPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency muHz
    # modes[:,3] : sigma error in frequency mHz
    # OUTPUTS:
    # (y,coef):
    #  y : second difference [in muHz] as a function of frequency

    if(lval == None):
        lval = get_l_values(modes)

    l = modes[:,1]
    nu = modes[:,2]
    n =  modes[:,0]
    
    Nf =   len(nu)
    
    # number of modes for each l degree
    Nl = []
    N = 0
    for s in lval:
        j = np.where(l == s)
        m = len(j[0])
        Nl.append(m)
        N += m-2

    coef = np.zeros((N,Nf))  
    yn = np.empty(N)
    p = 0 
    for k in range(len(lval)):
        if(Nl[k] > 1):
            i = np.where( l ==  lval[k] ) [0]
            for m in i[1:-1]:
                for j in range(Nf):
                    if( n[j] == n[m] and l[j] == lval[k] ):
                        coef[p,j] = -2.
                        yn[p] = n[j]
                    if( n[j] == n[m]-1 and l[j] == lval[k]):
                        coef[p,j] = 1.
                    if( n[j] == n[m]+1 and l[j] == lval[k]):
                        coef[p,j] = 1.
                p +=  1

    y = np.empty(N)
    for i in range(N):
        y[i] = (coef[i,:]*nu).sum()
    return (y,coef,yn)

   
def sd01(modes):
    # sd01 second difference 01 as a function of frequency as defined in Eq. (4) of Roxburgh & Vorontsov (2003,A&A)
    #
    # sd01 (n) = (1/8) ( nu_{n-1,0} - 4 nu_{n-1,1} + 6 nu_{n,0} - 4 nu_{n,1} + nu_{n+1,0})
    # 
    # INPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency muHz
    # modes[:,3] : sigma error in frequency mHz
    # OUTPUTS:
    # (y,coef):
    #  y : sd01 second difference [in muHz] 
    #

    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)[0]
    i1 = np.where(l == 1)[0]

    if( l[i0[0]] !=0 and l[i1[0]] != 2):
        print 'error in sd01, the l=1 modes must be placed after the l=0 modes'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])

    n0 = int(max([n0min,n1min])) + 1
    n1 = int(min([n0max,n1max])) - 1
    #    print n0,n1,i00,i01

    N = n1 - n0 +1
    if( N < 1):
        print 'error in sd01, not enough l=0 and/or l=1 modes'
        return
    yn = np.empty(N)    
    coef = np.zeros((N,Nf))
    for i in range(N):
        #   print n[i],l[i]
        for j in range(Nf):
            if( n[j] == i + n0 -1  and  l[j] == 0 ):
                coef[i,j] = 1./8
            if( n[j] == i + n0   and  l[j] == 0 ):
                coef[i,j] = 6./8
                yn[i] = n[j]
            if( n[j] == i + n0+1   and  l[j] == 0 ):
                coef[i,j] = 1./8
            if( n[j] == i + n0 -1   and  l[j] == 1 ):
                coef[i,j] = -0.5
            if( n[j] == i + n0    and  l[j] == 1 ):
                coef[i,j] = -0.5
        
    y = np.empty(N)
    for i in range(N):
        y[i] = (coef[i,:]*nu).sum()

    return (y,coef,yn)

def sd10(modes):
    # sd10 second difference "10" as a function of frequency as defined in Eq. (5) of Roxburgh & Vorontsov (2003,A&A)
    #
    # sd10 (n) = -(1/8) ( nu_{n-1,1} - 4 nu_{n,0} + 6 nu_{n,1} - 4 nu_{n+1,0} + nu_{n+1,1})
    #
    #
    # INPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency muHz
    # modes[:,3] : sigma error in frequency mHz
    # OUTPUTS:
    # (y,coef):
    #  y : sd10 second difference [in muHz] 
    #

    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)[0]
    i1 = np.where(l == 1)[0]

    if( l[i0[0]] !=0 and l[i1[0]] != 2):
        print 'error in sd10, the l=1 modes must be placed after the l=0 modes'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])

    n0 = int(max([n0min,n1min])) + 1
    n1 = int(min([n0max,n1max])) - 1
    #    print n0,n1,i00,i10

    N = n1 - n0 +1
    if( N < 1):
        print 'error in sd10, not enough l=0 and/or l=1 modes'
        return
    yn = np.empty(N)    
    coef = np.zeros((N,Nf))
    for i in range(N):
        #   print n[i],l[i]
        for j in range(Nf):
            if( n[j] == i + n0 -1  and  l[j] == 1 ):
                coef[i,j] = -1./8
            if( n[j] == i + n0   and  l[j] == 1 ):
                coef[i,j] = -6./8
                yn[i] = n[j] 
            if( n[j] == i + n0+1   and  l[j] == 1 ):
                coef[i,j] = -1./8
            if( n[j] == i + n0    and  l[j] == 0 ):
                coef[i,j] = 0.5
            if( n[j] == i + n0 +1    and  l[j] == 0 ):
                coef[i,j] = 0.5
        
    y = np.empty(N)
    for i in range(N):
        y[i] = (coef[i,:]*nu).sum()

    return (y,coef,yn)

def rsd01(modes):
    # ratio sd01(n) / dnu1(n)
    # as defined in Eq. 1 of Lebreton & Goupil (2012, A&A)
    # with dnu1 = nu_{n,1} - nu_{n-1,1}
    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)[0]
    i1 = np.where(l == 1)[0]

    if( l[i0[0]] !=0 and l[i1[0]] != 2):
        print 'error in rsd01, the l=1 modes must be placed after the l=0 modes'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])

    n0 = int(max([n0min,n1min])) + 1
    n1 = int(min([n0max,n1max])) - 1
    #    print n0,n1,i00,i01

    N = n1 - n0 +1
    if( N < 1):
        print 'error in rsd01, not enough l=0 and/or l=1 modes'
        return
    yn = np.empty(N) 
    coef = np.zeros((N,Nf))
    coefd = np.zeros((N,Nf))
    for i in range(N):
        #   print n[i],l[i]
        for j in range(Nf):
            # sd01
            if( n[j] == i + n0 -1  and  l[j] == 0 ):
                coef[i,j] = 1./8
            if( n[j] == i + n0   and  l[j] == 0 ):
                coef[i,j] = 6./8
                yn[i] = n[j]
            if( n[j] == i + n0+1   and  l[j] == 0 ):
                coef[i,j] = 1./8
            if( n[j] == i + n0 -1   and  l[j] == 1 ):
                coef[i,j] = -0.5
            if( n[j] == i + n0    and  l[j] == 1 ):
                coef[i,j] = -0.5
            # dnu1
            if( n[j] == i + n0 -1   and  l[j] == 1 ):
                coefd[i,j] = -1.
            if( n[j] == i + n0    and  l[j] == 1 ):
                coefd[i,j] = 1.
        
    y = np.empty(N)
    sd01 = np.empty(N)
    dnu1 =np.empty(N)
    coefy = np.zeros((N,Nf)) 
    for i in range(N):
        sd01[i] = (coef[i,:]*nu).sum()
        dnu1[i] = (coefd[i,:]*nu).sum()
        y[i] = sd01[i]/dnu1[i]
        coefy[i,:] = y[i]* ( coef[i,:]/sd01[i]  - coefd[i,:]/dnu1[i])

    return (y,coefy,coef,coefd,yn)

def rsd10(modes):
    # ratio sd10 (n) / dnu0 (n)
    # as defined in Eq. 1 of Lebreton & Goupil (2012, A&A)
    # with dnu0 =  nu_{n+1,0} - nu_{n,0}
    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)[0]
    i1 = np.where(l == 1)[0]

    if( l[i0[0]] !=0 and l[i1[0]] != 2):
        print 'error in rsd10, the l=1 modes must be placed after the l=0 modes'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])

    n0 = int(max([n0min,n1min])) + 1
    n1 = int(min([n0max,n1max])) - 1
    #    print n0,n1,i00,i01

    N = n1 - n0 +1
    if( N < 1):
        print 'error in rsd10, not enough l=0 and/or l=1 modes'
        return
    yn = np.empty(N) 
    coef = np.zeros((N,Nf))
    coefd = np.zeros((N,Nf))
    for i in range(N):
        #   print n[i],l[i]
        for j in range(Nf):
            # sd10
            if( n[j] == i + n0 -1  and  l[j] == 1 ):
                coef[i,j] = -1./8
            if( n[j] == i + n0   and  l[j] == 1 ):
                coef[i,j] = -6./8
                yn[i] = n[j]
            if( n[j] == i + n0+1   and  l[j] == 1 ):
                coef[i,j] = -1./8
            if( n[j] == i + n0    and  l[j] == 0 ):
                coef[i,j] = 0.5
            if( n[j] == i + n0 +1    and  l[j] == 0 ):
                coef[i,j] = 0.5
            # dnu0
            if( n[j] == i + n0    and  l[j] == 0 ):
                coefd[i,j] = -1.
            if( n[j] == i + n0+1    and  l[j] == 0 ):
                coefd[i,j] = 1.
        
    y = np.empty(N)
    sd10 = np.empty(N)
    dnu0 =np.empty(N)
    coefy = np.zeros((N,Nf)) 
    for i in range(N):
        sd10[i] = (coef[i,:]*nu).sum()
        dnu0[i] = (coefd[i,:]*nu).sum()
        y[i] = sd10[i]/dnu0[i]
        coefy[i,:] = y[i]* ( coef[i,:]/sd10[i]  - coefd[i,:]/dnu0[i])

    return (y,coefy,coef,coefd,yn)
    
def rd02(modes):
    # ratio d02 (n) / dnu1 (n)
    # with dnu1 =  nu_{n,1} - nu_{n-1,1}
    n = modes[:,0]
    l = modes[:,1]
    nu = modes[:,2]

    Nf =   len(nu)
 
    i0 = np.where(l == 0)[0]
    i1 = np.where(l == 1)[0]
    i2 = np.where(l == 2)[0]

    if( l[i0[0]] !=0 and l[i1[0]] != 1 and l[i2[0]] != 2):
        print 'error in rd02, the l=0, l=1 and l=2 modes must placed in increasing l degree'
        return

    n0min = np.min(n[i0])
    n0max = np.max(n[i0])
    n1min = np.min(n[i1])
    n1max = np.max(n[i1])
    n2min = np.min(n[i2])
    n2max = np.max(n[i2])

    n0 = int(max([n0min,n1min+1,n2min+1])) 
    n1 = int(min([n0max,n1max+1,n2max+1])) 
    #    print n0,n1,i00,i01

    N = n1 - n0 +1
    if( N < 1):
        print 'error in rd02, not enough l=0, l=1,  and l=2 modes'
        return
    yn = np.empty(N) 
    coef = np.zeros((N,Nf))
    coefd = np.zeros((N,Nf))
    for i in range(N):
        #   print n[i],l[i]
        for j in range(Nf):
            # d02
            if( n[j] == i + n0 and  l[j] == 0 ):
                coef[i,j] = 1.
            if( (n[j] == i + n0 - 1)  and  l[j] == 2 ):
                coef[i,j] = -1.
            # dnu1
            if( n[j] == i + n0 -1    and  l[j] == 1 ):
                coefd[i,j] = -1.
            if( n[j] == i + n0    and  l[j] == 1 ):
                coefd[i,j] = 1.
                yn[i] = n[j]
        
    y = np.empty(N)
    d02 = np.empty(N)
    dnu1 =np.empty(N)
    coefy = np.zeros((N,Nf)) 
    for i in range(N):
        d02[i] = (coef[i,:]*nu).sum()
        dnu1[i] = (coefd[i,:]*nu).sum()
        y[i] = d02[i]/dnu1[i]
        coefy[i,:] = y[i]* ( coef[i,:]/d02[i]  - coefd[i,:]/dnu1[i])

    return (y,coefy,coef,coefd,yn)


def get_l_values(modes) :
    nm = modes.shape[0]
    if(nm > 0):
        lval = [int(modes[0,1])]
        for i in range(1,nm):
            if(modes[i,1] != modes[i-1,1]):
                        lval.append(int(modes[i,1]))
    else:
        lval = []

    return lval
       
       

class SeismicConstraints:

    file = ''
    type = ''
    matching = 'frequency'
    n = np.empty(0,dtype=np.int)
    l = np.empty(0,dtype=np.int)
    nu = np.empty(0)
    sigma = np.empty(0)
    y = np.empty(0)
    yn = np.empty(0)
    covar = np.empty(0)
    coef = np.empty(0)
    number = 0
    
    def __init__(self,file='',types=['nu'],matching = 'frequency',data=None):
        self.file = file
        self.types = types
        if (file != ''):
            print 'we read the table of frequencies: '+ file
            data = np.loadtxt(file,comments='#')        
        else:
            if (data == None):
                return
        
        self.n = np.array(data[:,0],dtype=np.int)
        self.l = np.array(data[:,1],dtype=np.int)
        self.nu =  data[:,2]
        self.sigma = data[:,3]
        self.lval = get_l_values(data)
        #            raise OSMError("Error in OSM / SeismicConstraints: unspecified file")
        if ( (matching != 'frequency') &  ( matching != 'order') ):
            raise OSMError("Error in OSM / SeismicConstraints: unhandled option matching : " +  matching)
        self.matching = matching
        print ('total number of frequencies: %d') % (len(self.nu))
        print 'n   l  nu  sigma'
        for i in range(len(self.nu)):
        	print ("%d %d %f %f") % (self.n[i],self.l[i],self.nu[i],self.sigma[i])
        if ( self.nu.size < 1 ):
            raise OSMError("Error in OSM / SeismicConstraints: more than one frequency is required" )
        self.coef = np.empty( (0,self.nu.size))
        for type in types:
            if( type == 'dnu'):
                (y,coef,yn) = dnu(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'dnu0'):
                (y,coef,yn) = dnu(data,lval=[0])
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'dnu1'):
                (y,coef,yn) = dnu(data,lval=[1])
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'dnu2'):
                (y,coef,yn) = dnu(data,lval=[2])
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'd01'):
                (y,coef,yn) = d01(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'd02'):
                (y,coef,yn) = d02(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'rd02'):
                (y,coef,a,b,yn) = rd02(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'sd'):
                (y,coef,yn) = sd(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'sd01'):
                (y,coef,yn) = sd01(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'sd10'):
                (y,coef,yn) = sd10(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'rsd10'):
                (y,coef,a,b,yn) = rsd10(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'rsd01'):
                (y,coef,a,b,yn) = rsd01(data)
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,yn)
                self.coef = np.append(self.coef,coef,axis=0)
            elif( type == 'nu'):
                y = np.empty(self.nu.size)
                coef = np.zeros((self.nu.size,self.nu.size))
                for i in range(self.nu.size):
                    y[i] = self.nu[i]
                    coef[i,i] = 1
                self.y = np.append(self.y,y)
                self.yn = np.append(self.yn,self.n)
                self.coef = np.append(self.coef,coef,axis=0)
            else:
                raise OSMError("Error in OSM / SeismicConstraints:  seimic consraint of type '"+ type + "' is not handled")
        nc = self.coef.shape[0]
        self.covar = np.empty( (nc,nc) )
        for i in range(nc):
            for j in range(nc):
                self.covar[i,j] = (self.coef[i,:] * self.coef[j,:] * self.sigma **2 ).sum()
        # plt.imshow(self.covar)
        self.number = nc
        print 'type(s) of seismic constraints:'
        for t in types:
            print t
        print 'total number of seismic constraints:', self.number
        print 'seismic constraints (#, value, sigma):'
        for i in range(self.number):
            print ("# %d = %f %f") % (i,self.y[i],math.sqrt(self.covar[i,i]))

def read_agsm(file):
    # OUTPUTS:
    # modes[:,0] : n order
    # modes[:,1] : l degree
    # modes[:,2] : nu frequency in muHz (eigenvalue)
    # modes[:,3] : square normalised frequency (w2)
    # modes[:,4] : Richardson frequency in muHz
    # modes[:,5] : variationnal frequency in muHz
    # modes[:,6] : icase


    f = cestam.FortranIO.FortranBinaryFile(file, mode='r')

    cs = []
    while True:
        try:
            csi = f.readRecordNative('d')
            cs.append(csi)
        except IndexError:
            break

    nmodes = len(cs)
    modes = np.zeros((nmodes,7))
    mstar = (cs[0])[1]
    rstar = (cs[0])[2]
    for i in range(nmodes):
        modes[i,0] = (cs[i]) [18] # n
        modes[i,1] = (cs[i]) [17] # l        
        sigma2 = (cs[i]) [19]
        omega2 = sigma2*ggrav*mstar/(rstar**3)
        modes[i,2] = math.sqrt(omega2)/(2.*math.pi)*1e6 # nu in muHz
        modes[i,3] = sigma2
        modes[i,4] = (cs[i]) [36]*1e3 # Richardson frequency in muHz
        modes[i,5] = (cs[i]) [26]*1e3 # variational frequency in muHz

    f.close()
    # reading the 'ics' integer variables
    f = cestam.FortranIO.FortranBinaryFile(file, mode='r')
    n = 38*2
    for i in range(nmodes):
        data = f.readRecordNative('i')
        ics = data[n:n+8]
        modes[i,6] = ics[4]

    f.close()

    return modes

def read_amde(name):
    # read eigenfunctions from file.
    # assumes that the file contains a full set of eigenfunctions
    # return (x,y,modes) where:
    # x[n] : radial mesh (r/R)
    # y[n,0:6,k] : the eigenfunctions
    # modes[k,0:7] : modes properties (see read_agsm)
    # k is the modes index
    # n is the mesh index
    
    f = open(name, 'r')
    cs = []
    ics = []
    while True:
        try:
            size = np.fromstring(f.read(4),'i') [0]  # record size in bytes
            record = f.read(size)
            f.read(4)
            n = 38*8
            csi = np.fromstring(record[0:n],'d')
            icsi = np.fromstring(record[n:n+8*4],'i')
            n = 50*8
            nn =    np.fromstring(record[n:n+4],'i')[0]
            cs.append(csi)
            ics.append(icsi)
        except IndexError:
            break
    f.close()
    nmodes = len(cs)
    modes = np.zeros((nmodes,7))
    mstar = (cs[0])[1]
    rstar = (cs[0])[2]
    for i in range(nmodes):
        modes[i,0] = (cs[i]) [18] # n
        modes[i,1] = (cs[i]) [17] # l        
        sigma2 = (cs[i]) [19]
        omega2 = sigma2*ggrav*mstar/(rstar**3)
        modes[i,2] = math.sqrt(omega2)/(2.*math.pi)*1e6 # nu in muHz
        modes[i,3] = sigma2
        modes[i,4] = (cs[i]) [36]*1e3 # Richardson frequency in muHz
        modes[i,5] = (cs[i]) [26]*1e3 # variational frequency in muHz
        modes[i,6] = (ics[i])[4]
    f = open(name, 'r')
    y = np.empty( (nn,6,nmodes) )
    x = np.empty( (nn) )
    for i in range(nmodes):
            size = np.fromstring(f.read(4),'i') [0]
            record = f.read(size)
            f.read(4)
            n = 50*8 + 4
            for k in range(nn):
                yi = np.fromstring(record[n:n+7*8],'d')
                n += 7*8
                y[k,:,i] = yi[1:]
                x[k] = yi[0]
    f.close()
    return (x,y,modes)

def largesep(name,Target,Settings,path=''):
    modes_ = read_agsm(path+name+'.gsm')
    modes = np.zeros( (modes_.shape[0],4))
    modes[:,0:3] = modes_[:,0:3]
    modesset = Settings['modes']
    if(modesset == None):
        (y,covar,yn) = dnu(modes)
        return y.mean()
    else:
        l = modesset['l']
        print 'we select the degrees l:',np.array_str(l)
        dn = modesset['dn']
        nmin = modesset['nmin'] 
        nmax = modesset['nmax'] 
        print ('we select the orders from nmin=%d to nmax=%d with a tolerrance dn = %d') % (nmin,nmax,dn)
        nm = modes.shape[0]
        lsep = np.zeros(dn*2+1)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        for i in range(dn*2+1):
            shift = i - dn
            print ('shift = %d') %(shift)
            selected = []
            for li in l:
                nl = 0
                for k in range(nm):
                    for n in range(nmin+shift,nmax+shift+1):
                        if( (abs(modes[k,0] -  n) < 1e-5 ) & ( abs(modes[k,1] - li)  < 1e-5) ):
                            print ('selected modes (l,n,nu,w2) = (%d,%d,%f,%f)') % (li,n,modes[k,2],modes[k,3])
                            selected.append(k)
                            nl = nl + 1
                if(nl ==0):
                    print ('l=%d modes missing') % (li)
                else:
                    if(nl < 2):
                        print ('WARNING ! not enough l=%d modes') % (li)
            nms =len(selected) 
            print ('number of modes selected = %d') % (nms)
            if(nms > 1 ):
                (y,covar,yn) = dnu(modes[selected,:])
                lsep[i]  = y.mean()
            else:
                if(nms ==0):
                    print 'WARNING ! no modes matching the requirements'
                if(nms < 2):
                    print 'WARNING ! not enough modes matching the requirements'
                lsep[i] = 0.
            print ('largsep = %f') % (lsep[i])
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        i = np.argmin( abs(Target.value-lsep) )
        print ('closest value of largesep = %f (shift = %d)') % (lsep[i],i-dn)
        return lsep[i]



def seismic_model(name,sc,path=''):

    modes_ = read_agsm(path+name+'.gsm')
    modes = np.zeros( (modes_.shape[0],4))
    modes[:,0:3] = modes_[:,0:3]

    modesn = np.empty( (0,4) )

    # we check that the th. frequencies cover the observations
    lval0 = get_l_values(modes)
    for lc in sc.lval:
        found = False
        for l in lval0:
            if(lc == l):
                found = True
                j = (np.where(modes[:,1] == lc))[0]
                jc = (np.where(sc.l == lc))[0]
                if (sc.matching == 'frequency'):
                    LS = (sc.nu[jc[1:]] - sc.nu[jc[0:-1]] ).mean()
                    #                print 'LS=',LS
                    if ( np.min(modes[j,2]) > np.min(sc.nu[jc])+ LS/2. or np.max(modes[j,2]) < np.max(sc.nu[jc]) - LS/2. ):
                        print 'warning in seismic_model: in  '+ name +', l=' +  ("%i") % (lc) + ' modes do not cover the observational range'

                    imin = np.argmin( np.abs(modes[j,2] - np.min(sc.nu[jc])) )
                elif (sc.matching == 'order'):
                    imin = np.argmin( np.abs(modes[j,0] - sc.n[jc][0]) )
                print ('first l=%i modes: n=%i  nu=%g') % (lc,modes[j[imin],0],modes[j[imin],2])
                imax = imin + len(jc) -1
                if( len(jc) > len(j)-imin):
                    print 'error in seismic_model: in '+ name +'  insufficient number of  l=' +  ("%i") % (lc) + ' we need ' + ("%i") %(len(jc)) + ' while only ' + ("%i") %(len(j)-imin) + '  lie in the frequency range' 
                    return np.empty(0)

                else:
                    print ('last l=%i modes: n=%i  nu=%g') % (lc,modes[j[imax],0],modes[j[imax],2])
                    modesn = np.append( modesn , modes[j[imin]:j[imax]+1,:] ,axis=0)

        if(not found):
            print 'error in seismic_model: in '+ name +'  l=' +  ("%i") % (lc) + ' modes are missing'
            return np.empty(0)


    print 'selected th. frequencies:'
    print 'n   l   nu [muHz]'
    for i in  range(modesn.shape[0]):
        print ("%2i %2i %15.5f" )% (modesn[i,0],modesn[i,1],modesn[i,2])

    Y = np.empty((0))
    for type in sc.types:
        if( type == 'dnu'):
            (y,coef,yn) = dnu(modesn)
            Y = np.append(Y,y)
        elif( type == 'dnu0'):
            (y,coef,yn) = dnu(modesn,lval=[0])
            Y = np.append(Y,y)
        elif( type == 'dnu1'):
            (y,coef,yn) = dnu(modesn,lval=[1])
            Y = np.append(Y,y)
        elif( type == 'dnu2'):
            (y,coef,yn) = dnu(modesn,lval=[2])
            Y = np.append(Y,y)
        elif( type == 'd01'):
            (y,coef,yn) = d01(modesn)
            Y = np.append(Y,y)
        elif( type == 'd02'):
            (y,coef,yn) = d02(modesn)
            Y = np.append(Y,y)
        elif( type == 'rd02'):
            (y,coef,a,b,yn) = rd02(modesn)
            Y = np.append(Y,y)
        elif( type == 'sd'):
            (y,coef,yn) = sd(modesn)
            Y = np.append(Y,y)
        elif( type == 'sd01'):
            (y,coef,yn) = sd01(modesn)
            Y = np.append(Y,y)
        elif( type == 'sd10'):
            (y,coef,yn) = sd10(modesn)
            Y = np.append(Y,y)
        elif( type == 'rsd01'):
            (y,coef,a,b,yn) = rsd01(modesn)
            Y = np.append(Y,y)
        elif( type == 'rsd10'):
            (y,coef,a,b,yn) = rsd10(modesn)
            Y = np.append(Y,y)
        elif( type == 'nu'):
            y = np.append(Y,modesn[:,2])
        else:
            print "error in seismic_model: seimic constraints of type '"+ type + "' is not handled"

            Y = np.append(Y,y)


    return Y
