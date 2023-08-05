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

import numpy as np
import os,sys
import scipy.interpolate 
import math
import cestam
import xml.dom.minidom as xdm
import re
import cestam.constants
from osmlevmar import *
import matplotlib.pyplot as plt
from osmmodes import *
import struct
from scipy import interpolate

class Target:
    name = ''
    value = 0.
    sigma = -1.
    
    def copy(self):
        new = Target()
        new.name = self.name
        new.value = self.value
        new.sigma = self.sigma
        return new

class OSMError(Exception):
	def __init__(self, value):
         	self.value = value
	def __str__(self):
		return repr(self.value) 

    
def files_search(dirs,path='./',pattern=''):

    test = re.compile(pattern, re.IGNORECASE) 


    files = []
    for dir in dirs: 
        for root, dirnames, filenames in os.walk(os.path.normpath(path)+'/'+dir):
            f = sorted(filenames)
            for filename in f:
                if(re.search(test,filename)):
                    files.append(root+'/'+filename)
    return files


def loadhrgrid(files,ntmax=10000,old=False):

## files : names of the files (full path)
##
## ; return a tuple (data,masses,ntimes)
## where data  is a  Numpy array data[k,j,i]:
## ; k : track index (track associated with files[k])
## ; j : index associated with the following quantities:
## ;   0 : age (My)    
## ;   1 : log Teff
## ;   2 : log L/Lo
## ;   3 : log R/Ro
## ;   4 : M/Mo
## ;   5 : log g
## ;   6 : Xc
## ;   7 : Yc
## ;   8 : Zc
## ;   9 : Xs
## ;  10 : Ys
## ;  11 : Zs
## ; i : time step index (age)
## ; Note that age[k] = -1 for  i>ntimes[k]
## ; masses[k] : masse associated with track k
## the number of time steps associated with trak k
    
    nfiles = len(files)
    data = np.zeros((nfiles,12,ntmax))
    masses = np.zeros(nfiles)
    ntimes = np.zeros(nfiles)
    cwd = os.getcwd()
    k = 0
    old = False
    for f in files:
        file =  re.sub('\.HR','',os.path.basename(f))
        
        os.chdir(os.path.dirname(f))
        print file
        m = cestam.CModel(file, read=False)
        try:
            m.read_hr(old=old)
        except:
	    try:	
            	m.read_hr(old=True)
	    except:
                k += 1
		print 'in loadhrgrid : unable to read ' + file + ', skipping this file'
		continue
            old = True
        nt = len(m) 
        masses[k] = m.mstar[0]
        ntimes[k] = nt
        if(nt < ntmax):
            data[k,0,nt:] = -1.
        else:
            nt = ntmax
        data[k,0,0:nt] = m.age[0:nt]
        data[k,1,0:nt] = m.log_teff[0:nt]
        data[k,2,0:nt] = m.log_l[0:nt]
        data[k,3,0:nt] = m.log_r[0:nt]
        data[k,4,0:nt] = m.mstar[0:nt]
        data[k,5,0:nt] = m.log_g[0:nt]

        data[k,6,0:nt] = m.ab_c[0,0:nt] # Xc
        data[k,7,0:nt] = m.ab_c[1,0:nt] + m.ab_c[2,0:nt] # Yc
        data[k,8,0:nt] = (m.ab_c[:,0:nt]).sum(0) # Zc

        data[k,9,0:nt] = m.ab_s[0,0:nt] # Xs
        data[k,10,0:nt] = m.ab_s[1,0:nt] + m.ab_s[2,0:nt] # Ys
        data[k,11,0:nt] = (m.ab_s[:,0:nt]).sum(0) # Zs
        
        k += 1
     
    os.chdir(cwd)
    return (data,masses,ntimes)
   


def search_model(hrin,masses,ntimes,logg,teff, dlogg=0.01,dteff=15. ,interactif=False):

    print 'teff = ', teff
    print 'log g =',logg
    logteff = math.log10(teff)

    vicinity = 0.05

    logg_sun = 4.438

    hr = hrin.copy()

    nmasses = masses.size
    ntmax = hr.shape[2]
    (massi,ri,agei) = (0.,0.,0.)
    ans = ''
    while( ans != 'n'):
        if(interactif):
            print  '\nChoose the evolutionnary status:'
            print 'Any -> a'
            print 'Main-sequence -> m'
            print 'Post-sequence -> p'
            print 'Helium burning phase -> h'
            print ''
            print 'Type n to exit\n'
            choices = ['a','m','p','n']
            ans = ''
            while ans not in choices:
                ans = raw_input("Your choice: ")
                ans = ans.lower()
        else:
            ans = 'a'
        selected = []
        if(ans != 'n'):
            
            for k in range(nmasses):
                if(ans == 'm'):
                    j = np.where(hr[k,6,0:ntimes[k]] > 1e-2)
                    if(len(j) > 0):
                        selected.append(j[0])
                elif (ans == 'p'):
                    j = np.where(hr[k,6,0:ntimes[k]] <= 1e-2)
                    if(len(j) > 0):
                        selected.append(j[0])
                elif (ans == 'h'):
                    j = np.where(hr[k,7,0:ntimes[k]] >= 1e-5)
                    if(len(j) > 0):
                        selected.append(j[0])
                else:
                    selected.append(np.arange(ntimes[k],dtype=np.int))  
            if(len(selected) ==0):
                print 'No models in the selected evolutionnary status'
        if( (ans != 'n') & (len(selected) >0)):
            chi2 = np.ones((nmasses,ntmax))*1e10
            distance = np.ones((nmasses,ntmax))*1e10

            for k in range(nmasses):
                if(len(selected[k]) > 0):
                    # ecarts quadratique:
                    chi2[k,selected[k]] = ((10.**hr[k,1,selected[k]]-teff)/dteff )**2 +  ((hr[k,5,selected[k]]-logg)/dlogg)**2
                    # distance eulerienne:
                    distance[k,selected[k]] = np.sqrt((hr[k,1,selected[k]]-logteff)**2 +  (hr[k,5,selected[k]]-logg)**2)

            # on recherche le minimum
            chi2min = 1e10
            distancemin = 1e10

            imin = -1
            kmin = -1
            for i in range(nmasses):
                k = np.argmin( distance[i,:] )
                minimun = distance[i,k]

                if( minimun  < distancemin):
                    distancemin  = minimun
                    imin = i
                    kmin = k

            chi2min = chi2[imin,kmin]

            plt.figure(0)
            plt.clf()
            for k in range(nmasses):
                if(len(selected[k])>0):
                    plt.plot(hr[k,1,selected[k]],hr[k,5,selected[k]])
            plt.plot([logteff],[logg],'bs')
            plt.axis([3.9,3.5,5,1])

            if( imin < 0 or kmin < 0):
                return (0.,0.)

            # ; modele correspondant au minimum du chi2:
            print 'closest model:'
            print 'chi2=',chi2min
            print 'distance=',distancemin
            print 'mass=', masses[imin]
            print 'age=', hr[imin,0,kmin]
            teff0 = 10.**hr[imin,1,kmin]
            logteff0 = math.log10(teff0)
            print 'teff=',  teff0
            print 'log teff=',  logteff0
            print 'r=', 10.**hr[imin,3,kmin]
            logg0 = hr[imin,5,kmin]
            print 'logg=', logg0

            plt.figure(1)
            plt.clf()
            for k in range(nmasses):
                if(len(selected[k])>0):
                    plt.plot(hr[k,1,selected[k]],hr[k,5,selected[k]])
            logg_v = np.array([])
            logteff_v = np.array([])
            r_v = np.array([])
            age_v = np.array([])

            for i in range(nmasses-1):
                if(len(selected[i]) > 0) :
                    j = np.where( (hr[i,1,selected[i]]  >= logteff-vicinity)  & (hr[i,1,selected[i]]  <= logteff+vicinity) &  (hr[i,5,selected[i]]  >= logg-vicinity)  & (hr[i,5,selected[i]]  <= logg+vicinity ) ) 
                    if (j[0].size >0):
                        u = (selected[i])[j[0]]
                        logg_v = np.append(logg_v,hr[i,5,u])
                        logteff_v= np.append(logteff_v,hr[i,1,u])
                        r_v = np.append(r_v,10.**hr[i,3,u])
                        age_v = np.append(age_v,hr[i,0,u])
            n= r_v.size

            plt.plot(logteff_v,logg_v,'go')

            plt.plot([logteff0],[logg0],'r^')
            plt.plot([logteff],[logg],'bs')

            plt.axis([logteff+vicinity,logteff-vicinity,logg+vicinity,logg-vicinity ])

            ri = float(scipy.interpolate.griddata( (logg_v,logteff_v) , r_v , (logg,logteff) , method='cubic'))
            agei = float(scipy.interpolate.griddata( (logg_v,logteff_v) , age_v , (logg,logteff) , method='cubic'))

            print 'Interpolated radius Ri=', ri

            massi = 10**(logg-logg_sun)*ri**2
            print 'Mass associated with Ri and log g:', massi
            print 'Interpolated age: ', agei

            plt.show()

    return  (massi,ri,agei)

def search_model_in_grid(logg,teff,gridname,path='./',dteff=50., dlogg=0.1,old=False):
    
    if (  not(os.access(path + gridname + '.npz',os.F_OK))):
        pattern='.HR'
        dirs= ['m0.8_m1.18','m1.2_m1.98','m2.0_3.95','m4.0_5.95']
        files= files_search(dirs,path=path,pattern='.HR')
        (hr,masses,ntimes) = loadhrgrid(files,old=old)
        np.savez(path+gridname,hr=hr,masses=masses,ntimes=ntimes)
    else:
        print 'Loading  ' + gridname + '.npz'
        hrdata = np.load(path + gridname +'.npz')
        hr = hrdata['hr']
        masses = hrdata['masses']
        ntimes = hrdata['ntimes']
    
    search_model(hr,masses,ntimes,logg,teff,dteff=dteff, dlogg = dlogg ,interactif=True)

sigma_stefan = cestam.constants.clight * cestam.constants.aradia/4.
logg_sun = math.log10(cestam.constants.ggrav) + math.log10(cestam.constants.msun) - 2.*math.log10(cestam.constants.rsun)

def get_first_value(name,dom) :
    return dom.getElementsByTagName(name)[0].childNodes[0].data

def clean_string(string):
    return re.sub("\s{1,}$","",re.sub("^\s{1,}","",string))

def write_amdl(file,data,AA, record_maker = 4, endian = '@'):
# INPUTS:
# file : name of the output file
# data : global parameters  (see ADIPLS user's manual)
# AA   : variables (see ADIPLS user's manual)
#  AA[0,:] = x
#  AA[1,:] = A1
#  ...
#  AA[n,:] = An
#
# OPTIONS:
# endian (='@'): to be setup depending on your system architecture, see the module 'struct'
# record_maker (=4) :  to be setup depending on the way adipls is compiled, look at the makefile and the compiler options
#
# Return :   0, if successful, 1 otherwise

    if(record_maker == 4): # 32 bits
	HEADER_PREC = 'i'
    elif(record_maker  == 8): # 64 bits
	HEADER_PREC = 'l'
    else:
	print 'Error in write_amdl: value of record_marke  not handled'
	return 1

    if( record_maker > struct.calcsize("P") ):
  	print 'Error in write_amdl: record_marker not compatible with your architecture'
	return 1
      
    f = open(file,'w')
    n = AA.shape[1]
    nb = AA.shape[0]*n*8 + len(data)*8  + 2*4  # 2 x 4-bytes integers
    if(AA[0,0] > AA[0,n-1]):
	B = ((AA[:,::-1]).transpose()).flatten()
    else:
	B = (AA.transpose()).flatten()
    f.write(struct.pack(endian+HEADER_PREC,nb))
    f.write(struct.pack(endian+'ii',1,n)) # 2x 4-bytes interger
    for s in data:
        f.write(struct.pack(endian+'d',s))
    for s in B:
	f.write(struct.pack(endian+'d',s))
    f.close()

    return 0


def cesam2amdl(model,bv=0):
    """
    (data,AA) = cesam2amdl(model,bv=0)
    
    INPUTS:
    model : cestam model
    bv  : if bv=1 the Brunt-Vaisala freq. is computed numerically, otherwise it is taken from the cestam model

    OUTPUT:
    ADIPLS model
    
    """
    nmodel = model.ntot
    data  = np.zeros(8)
    data[0] = model.glob[0] # M
    data[1] = model.glob[1] # R
    data[2] = model.var[3,nmodel-1]  #  Pc
    data[3] = model.var[4,nmodel-1]  #  rhoc
    data[4] = -model.glob[8]/model.var[9,nmodel-1] # -(d2p/dx^2)/p/Gamma1 at the center
    data[5] = -model.glob[9] # -(d2dho/dx^2)/rho at the center
    data[6] = -1.
    data[7] = 0.
    AA = np.zeros( (6,nmodel))
    # cesam.ggrav = 6.672320e-08
    
    AA[0,0:nmodel-1] = model.var[0,0:nmodel-1]/model.glob[1] # x = r/R
    AA[1,0:nmodel-1] = model.var[1,0:nmodel-1]/(AA[0,0:nmodel-1])**3 # (m/M)/x^3
    AA[2,0:nmodel-1] = cestam.ggrav*(model.var[1,0:nmodel-1]*model.glob[0]) * model.var[4,0:nmodel-1]/(model.var[9,0:nmodel-1]*model.var[3,0:nmodel-1]*model.var[0,0:nmodel-1])  # G*m*rho/ (Gamma1*p*r)
    AA[3,0:nmodel-1] = model.var[9,0:nmodel-1] # Gamma1
    if (bv !=0):
        # compute numerically brunt-vaisala freq.
        y = np.log(model.var[4,:-1])
        x = np.log(model.var[0,:-1])
        tck = interpolate.splrep(x[::-1],y[::-1],s=0)
        AA[4,0:nmodel-1] = - AA[2,0:nmodel-1] - interpolate.splev(x,tck,der=1)
    else:        
        AA[4,0:nmodel-1] = model.var[14,0:nmodel-1] # vaisala
    AA[5,0:nmodel-1] = 4.*math.pi*model.var[4,0:nmodel-1]* model.var[0,0:nmodel-1]**3 / (model.glob[0]*model.var[1,0:nmodel-1]) # U = 4pi*rho*r^3/m

    # at the center, asymptotic values:
    AA[0,nmodel-1] = 0.
    AA[1,nmodel-1] = 4.*math.pi*data[1]**3*data[3]/(3.*data[0])
    AA[2,nmodel-1] = 0.
    AA[3,nmodel-1] = model.var[9,nmodel-1] # Gamma1
    AA[4,nmodel-1] = 0.
    AA[5,nmodel-1] = 3.

# data must be filled from the center up to the surface
    if(AA[0,0] > AA[0,nmodel-1]):
    	AA = AA[:,::-1]

    return (data,AA)
   
    
def pmsmodel(model,mass):
    print ('\nWe build a PMS model with mass = %g') % (mass)

    model.GUI = False
    model.run.type_file = 'ASCII'
    model.params.agemax = 0.
    model.params.mtot = mass
    
##     X0 = model.params.x0
##     if(X0 < 0):
##         X0 = (1. - model.params.y0)/(1. + model.params.zsx0)
##     model.params.x_stop = X0*(1. - 1e-4)
##     model.params.arret= 'Other'
    
    if(model.run.c_iben < 8.1e-5):
        mod_init = '8d-5.pms'
    elif (model.run.c_iben < 5.1e-4):
        mod_init = '5d-4.pms'
    else:
        mod_init = '2d-2.pms'

    if( not(os.access(model.params.nom_chemin + '/' + mod_init,os.F_OK)))  :
	raise OSMError("Error in OSM: file " + model.params.nom_chemin + '/' + mod_init+" is missing")

    model(job='pms',mod_init= mod_init)
    model.run.type_file = 'Binary'

def zamsmodel(model,mass):
    print ('\nWe build a ZAMS model with mass = %g') % (mass)

    model.GUI = False
    model.run.type_file = 'ASCII'
    model.params.agemax = 0.
    
##     X0 = model.params.x0
##     if(X0 < 0):
##         X0 = (1. - model.params.y0)/(1. + model.params.zsx0)
##     model.params.x_stop = X0*(1. - 1e-4)
##     model.params.arret= 'Other'
    
    if(mass < 1.5):
        mod_init = 'm010.zams'
        mass0 = 1.
    elif (mass < 3.5):
        mod_init = 'm020.zams'
        mass0 = 2.
    else:
        mod_init = 'm050.zams'
        mass0 = 5.

    dmass = mass*0.02
    if(mass<mass0):
        dmass = - dmass

    if( not(os.access(model.params.nom_chemin + '/' + mod_init,os.F_OK)))  :
	raise OSMError("Error in OSM: file " + model.params.nom_chemin + '/' + mod_init+" is missing")
	
    print ('\nstarting with the initial m = %g') % (mass0)
    print ('proceeding then iteratively with a step dm=%g') % (dmass)

    model.params.mtot = mass0
    model(job='zams',mod_init= mod_init)
    model.run.type_file = 'Binary'
    model(job='zams',mod_init=model.name + '_B.hom')
    while (model.finished):
        model.params.mtot  = model.params.mtot + dmass
        if( abs(model.params.mtot - mass) < abs(dmass)*1.001 ):
            break
	print ('\ncomputing m=%g') % (model.params.mtot)
        model(job='zams',mod_init=model.name + '_B.hom')
        
    model.params.mtot = mass
    print ('\ncomputing the final value m=%g') % (mass)

    model(job='zams',mod_init=model.name + '_B.hom')

def setupparams(Model,Params,Settings):
    for s in Params:
        found = False
        for a in Model.params.nlist.values():
                for b in a:
                        if(b == s.name):
                                found = True
                                Model.params.__setattr__(b,s.value)
                                print ("%s = %g") % (s.name,s.value)
        if(not(found)):
		raise OSMError("Error in OSM/setupparams: Parameter named "+  s.name + " not found")
    # managing the diffusion:
    x0 = Model.params.x0
    if(x0 < 0.):
        zsx0 = -1.
        y0 = -1.
        for s in Params:
            if( s.name == 'zsx0' ):
                zsx0 = Model.params.zsx0
            if( s.name == 'y0' ):
                y0 = Model.params.y0
        if(  zsx0*y0 < 0. ):
            a = Settings['models']['dy_dz']
            yp = Settings['models']['yp']
            zp = Settings['models']['zp']
            if(y0 <0.):
                y0 = 1. - (1.+zsx0)*(1.+a*zp-yp)/(1.+zsx0+a*zsx0)
            if(zsx0<0.):
                zsx0 = (yp-y0-a*zp)/(y0*(1.+a)-a+a*zp)
            print 'dy_dz,yp,zp' , a , yp, zp

        Model.params.y0 = y0
        Model.params.zsx0 = zsx0
        print 'x0,y0,z0,zsx0,sum = ',Model.params.x0, Model.params.y0,Model.params.z0,Model.params.zsx0
          

def compute_optimal(modelname,Parameters,Targets,Settings,SeismicConstraints,Aux3DData=None):


    def getoutputs(Model):
        if(Aux3DData != None):
            pb = Aux3DData['pb'] # pressure at bottom (it is the total pressure if the tag pgas = 'no')
            tb= np.interp(pb,Model.var[3,:],Model.var[2,:]) # temperature at bottom
            rb = np.interp(pb,Model.var[3,:],Model.var[0,:])
	    if( abs(Model.params.cpturb) > 0): # the model includes turbulent pressure
            	ptrb = 1. - 1./np.interp(pb,Model.var[3,:],Model.var[20,:])
	    else:
		ptrb = 0.
            distb = Aux3DData['distb'] # distance photosphere - bottom
            R3d  =  rb + distb # radius
            logg3d = math.log10(cestam.ggrav) + math.log10(Model.glob[0])  - 2.*math.log10(R3d)
            log_teff3d =( math.log10(Model.glob[2]) - 2.*math.log10(R3d) - math.log10(4.) - math.log10(math.pi) -math.log10(sigma_stefan)) /4.
            teff3d = 10.**log_teff3d

        Outputs = np.zeros(len(Targets) + SeismicConstraints.number)
        log_teff =( math.log10(Model.glob[2]) - 2.*math.log10(Model.glob[1]) - math.log10(4.) - math.log10(math.pi) -math.log10(sigma_stefan)) /4.

        def Aux3DDataMissing():
		print "Error in OSM/getoutputs: missing auxiliary data"
            
        error = False
        i = 0 
        for Target in Targets:
	    s = Target.name.lower()
            if(s == 'logg'):
                Outputs[i] = math.log10(cestam.ggrav) + math.log10(Model.glob[0])  - 2.*math.log10(Model.glob[1])
            elif( s == 'teff'):
                Outputs[i] = 10.**log_teff 
	    elif( s == 'r'):
		Outputs[i] = Model.glob[1]/cestam.rsun
            elif ( s =='l'):
		Outputs[i] = Model.glob[2]/cestam.lsun
	    elif ( s =='logl'):
		Outputs[i] = math.log10(Model.glob[2])-math.log10(cestam.lsun)
            elif( s == 'log_teff'):
		Outputs[i] = log_teff 
            elif( s == 'tb'):
                if(Aux3DData == None):
                    Aux3DDataMissing()
		    error = True
                Outputs[i] = tb
            elif( s == 'logg3d'):
                if(Aux3DData == None):
                    Aux3DDataMisising()
		    error = True
                Outputs[i] = logg3d
            elif( s == 'teff3d'):
                if(Aux3DData == None):
                    Aux3DDataMissing()
		    error = True
                Outputs[i] = teff3d
            elif( s == 'log_teff3d'):
                if(Aux3DData == None):
                    Aux3DDataMissing()
 		    error = True
                Outputs[i] = log_teff3d
            elif( s == 'ptrb'):
                if(Aux3DData == None):
                    Aux3DDataMissing()
		    error = True
                Outputs[i] = ptrb
            elif( s == 'deltanuscl'):
                Outputs[i] = 135.5*math.sqrt( (Model.glob[0]/cestam.msun) * (cestam.rsun/Model.glob[1])**3)  # solar value (in muHz) from Mosser et al (2010, A&A, 517, A22)
            elif( s == 'largesep'):
                Outputs[i] = largesep(Model.name,Target,Settings)
	    elif( s =='mean_density'):
		Outputs[i] = (Model.glob[0]/cestam.constants.msun)*(cestam.constants.rsun/Model.glob[1])**3
            elif( s =='y_s' ):
                Outputs[i] =  Model.glob[7] # Y at the surface 
            elif( s =='z_s' ):
                Outputs[i] =  1. - Model.glob[6] - Model.glob[7] # Z  at the surface Z = 1 - X - Y
            elif( s =='zsx_s' ):
                Outputs[i] =  (1. - Model.glob[6] - Model.glob[7])/ Model.glob[6]   # Z/X at the surface Z/X = (1 - X - Y)/X
            else:
		print "Error in OSM/getoutputs: Target named "+  s + " not found"
		error = True
            print ("%s = %g") % (s,Outputs[i])
            i = i + 1

        if(SeismicConstraints.number > 0):
            Seismic_Model = seismic_model(Model.name,SeismicConstraints,path='')
            if(Seismic_Model.size != SeismicConstraints.number):
		print ("a problem occurs with model %s :") % (Model.name)
                print "the theoretical frequencies does not cover the observational range"
		print ("%d seismic constraints are expected while %d were computed") % (SeismicConstraints.number,Seismic_Model.size)
                print "we consider zeros values"
		Outputs[len(Targets):] = 0.
            else:
                Outputs[len(Targets):] = Seismic_Model
        
        return (Outputs,error)
    
    def compute_model(parameters,args,status):
        #   status : status of the model.
        #   status = -1 for the central model to be computed.
        #   status >= 0 for the model computed for the derivative associated with the parameter, which index is  given by the value of status

        error = True
        Models = args[0]
        Targets = args[1]
        index = status + 1
        Model = Models[index]
        print '----------------------------------------------------'
        print 'Model # :' , index 
        print 'Name: ' + Model.name
        setupparams(Model,parameters,Settings)
        Model.params.mkdon(replace_eos=False)

        if( status > -1 and parameters[status].evol == 1):
            print '-> evolving model named ' + Models[0].name+'_B.rep'
            (Model)(job='rep',mkdon=False,mod_init=Models[0].name+'_B.rep')
        else:
            if (model.run.job == 'From PMS'):
                print '-> starting the computation from PMS' 
                (Model)(job='hom',mkdon=False,mod_init=Model.name+'_B.pms')
            else:
                print '-> starting the computation from a homogeneous model' 
                (Model)(job='zams',mkdon=False,mod_init=Models[0].name+'_B.hom')
            #            print '-> starting the computation from a ZAMS model' 
            #            (Model)(job='zams',mkdon=False,mod_init=Models[0].name+'_B.zams')
        error = (Model.finished == False)
        if(not error):
            (data,AA) = cesam2amdl(Model)
            error = write_amdl(Model.name+'.amdl',data,AA)
            if(error):
                print 'Unable to build the amdl file'
            else:
                os.system('\\rm -f '+ Model.name  + '.gsm')
                os.system('\\rm -f '+ Model.name  + '.ssm')
                os.system('\\rm -f '+ Model.name  + '.ef')
                os.system('\\rm -f '+ Model.name  + '-adipls.log')
                os.system('runadipls.pl ' + Model.name + '.amdl ' +  Models[0].name+ '.adipls > /dev/null')

                          
        print '----------------------------------------------------'


        print '----------------------------------------------------'
        print 'Model # :' , index 

        if(error == False):
            print '-> Computation successfully finished'
            (Outputs,error) = getoutputs(Model)
            print '----------------------------------------------------'
            return (Outputs,error)
        else:
            print '-> The model named '+Model.name+' did not converge'
            print '----------------------------------------------------'
            return (np.zeros( len(Targets)) + 1e10,error)

    # --------------------------------------------

    npar = len(Parameters)

    text = ''
    
    model = cestam.CModel(modelname,read=False)
    model.GUI = False
    
    model.finished = False
    model.run.job = 'From ZAMS'
    if( Settings['models'] != None):
        if (  Settings['models']['start'] == 'pms'):
            model.run.c_iben = Settings['models']['cf']
            model.run.job = 'From PMS'
   
    for p in Parameters:
        if( (p.name == 'agemax') or (p.name == 't_stop')):
            p.evol = 1
        if( p.name == 't_stop'):
            model.params.agemax = 1e30
        if( p.name == 'agemax'):
            model.params.t_stop = 1e30

    model.run.type_file='Binary'
    models = [model]
    for i in range(npar):
        s= modelname+("_%3.3i") % (i+1)
        model_im_i = cestam.CModel(s,read=False)
        model_im_i.params.copy(model.params)
        model_im_i.run.c_iben = model.run.c_iben
        model_im_i.run.job = model.run.job
        model_im_i.params.mkdon(replace_eos=False)
        model_im_i.run.type_file='Binary'
        #        os.system('cp -f %s' )
        if (model.run.job == 'From PMS'):
            os.system(('cp -f %s_B.pms %s_B.pms') % (modelname,s))
        models.append(model_im_i)

    text += '\n\n'
    text += '====================================================\n'
    text += 'Initial parameters (name = value step min max rate):\n'
    for p in Parameters:
        text +=   ("%s = %g %g %g %g %g\n") % (p.name,p.value,p.step,p.bounds[0],p.bounds[1],p.rate)

    text += 'Targets (name = value sigma):\n'
    for t in Targets:
        text +=  ("%s = %g %g\n") % (t.name,t.value,t.sigma)

        #    setupparams(model,par,parnames)

    text += '\n'
    print text
    
    nt= len(Targets)
    ny = nt + SeismicConstraints.number
    y = np.empty(ny)
    for i in range(nt):
        y[i] = Targets[i].value
    covar = np.zeros( (ny,ny))
    for i in range(nt):
        covar[i,i] = Targets[i].sigma**2
    if(SeismicConstraints.number > 0):
        y[nt:] =  SeismicConstraints.y[:]
        covar[nt:,nt:] = SeismicConstraints.covar[:,:]

    np.savetxt('covar.txt',covar,fmt='%19.8e')
    
    maxiter = Settings['levmar']['maxiter']
    ftol = Settings['levmar']['ftol'] 
    chi2min = Settings['levmar']['chi2min'] 
  
    (chi2i,parout,iter,outputs,error) =   levmar(modelname,compute_model,Parameters,(models,Targets),y,covar,verbose=1,ftol=ftol,maxiter=maxiter,chi2min=chi2min)

    if(error):
	raise OSMError("Error in OSM/levmar")

    for i in range(npar):
        s= modelname+("_%3.3i") % (i+1)
        os.system('\\rm -f '+ s + '*')

    text2 = '\n'
    text2 +=  ("Chi2 = %g\n\n") %  (chi2i)
    text2 += 'Final parameters (name = value error):\n' 
    for p in parout:
	text2 +=   ("%s = %g %g\n") % (p.name,p.value,p.sigma)

    text2 += '\n'

    text2 += 'Distances to targets (name = model data sigma  model-data) :\n'
    for i in range(nt):
	text2 +=  ("%s = %g %g %g %g\n") % ( Targets[i].name,outputs[i],y[i],Targets[i].sigma , outputs[i] - y[i] )
    if(SeismicConstraints.number > 0):
	text2 += "\nDistances to seismic targets (# = model data sigma  model-data)\n"
    for i in range(nt,ny):
        text2 +=  ("# %i = %g %g %g %g\n") % ( i - nt,outputs[i],y[i], math.sqrt(covar[i,i]), outputs[i] - y[i])

    text2 += '====================================================\n'
    print text2
    
    text += text2

    return text

        
def read_setup(file):
    try:
        xml = xdm.parse(file)
    except:
        raise OSMError("Error in OSM: some errors occur while reading the XML file, please check its format")

    config =  []

    parameters = []
    targets = []
    
    for s in xml.getElementsByTagName('parameter'):
        parameter = Parameter()
    	a = get_first_value('bounds', s).split(',')
    	bounds =  [float(a[0]) , float(a[1])]
        parameter.step = float(get_first_value('step', s) )
        parameter.rate = float(get_first_value('rate', s) )
        parameter.bounds = bounds
        parameter.name = s.getAttribute('name')
        parameter.value = float(get_first_value('value', s) )
        parameters.append(parameter)

    for s in xml.getElementsByTagName('target'):
        target = Target()
        target.name = s.getAttribute('name')
        target.value = float(get_first_value('value', s) )
        target.sigma =  float(get_first_value('sigma', s) )
        targets.append(target)

    xmlsettings = xml.getElementsByTagName('settings')[0]

    levmar = xmlsettings.getElementsByTagName('levmar')[0]


 
    settings_levmar = {
        'maxiter': int( get_first_value('maxiter',levmar) ) ,
        'ftol':  float( get_first_value('ftol',levmar) ) ,
        'chi2min': float( get_first_value('chi2min',levmar) )
        }

    settings_modes = None
    modes = xmlsettings.getElementsByTagName('modes')
    if(len(modes) > 0):
        modes = modes[0]
        l = get_first_value('l', modes)
        settings_modes = {
            'l': np.fromstring(l,sep=',',dtype=np.int)  ,
            'nmin': int(get_first_value('nmin', modes)),
            'nmax': int(get_first_value('nmax', modes)),
            'dn': int(get_first_value('dn', modes)),
            'w2min': float(get_first_value('w2min', modes)) ,
            'w2max': float(get_first_value('w2max', modes)) 
            }

    settings_models = None
    models = xmlsettings.getElementsByTagName('models')
    
    if(len(models) > 0):
        models = models[0]
        start = (clean_string(get_first_value('start', models))).lower()
        if ( (start != 'zams') and (start != 'pms') ):
            raise OSMError("parameter start can only take the value 'zams' or 'pms'")
        settings_models = {
            'dy_dz': float(get_first_value('dy_dz', models)),
            'yp': float(get_first_value('yp', models)), 
            'zp': float(get_first_value('zp', models)),
            'start': start ,
            'cf': float(get_first_value('cf', models)) # contraction factor
          }
    settings = {
        'levmar': settings_levmar,
        'modes': settings_modes,
        'models': settings_models
        }

    return (config,parameters,targets,settings)


def read_seismic_constraints(file):
    xml = xdm.parse(file)


    xml = xml.getElementsByTagName('seismic_constraints')

    

    if(len(xml)>0):
        xml = xml[0]
        filename =  clean_string(get_first_value('file',xml))
        types =  (re.sub(r'\s', '', clean_string(get_first_value('types',xml)))).split(',')
        matching = 'frequency'
        if( len(xml.getElementsByTagName('matching')) > 0 ):
             matching= clean_string(get_first_value('matching',xml))
             print 'matching: ' + matching
        seismic_constraints =  SeismicConstraints(filename,types,matching=matching)
    else:
        seismic_constraints =  SeismicConstraints('')
        
    return seismic_constraints

#-----------------------------------------------------------------
#
#
#-----------------------------------------------------------------
def osm(name):

    (config,parameters,targets,settings) = read_setup(name+'.xml')

    seismic_constraints = read_seismic_constraints(name+'.xml')

    if (  not(os.access(name+'.don',os.F_OK)) ):
	raise OSMError("Error in OSM: missing file "+ name+".don")

    refmodel =  cestam.CModel(name)

#    if (  not(os.access('outputs/',os.F_OK)) ):
#        os.mkdir('outputs/')

    OutputPath = name+'/'

    if (  not(os.access(OutputPath,os.F_OK))):
        os.mkdir(OutputPath)

    if( os.access(name + '.mix',os.F_OK) ) :
        os.system('\cp -p '+ name+ '.mix ' + OutputPath + '/mixture')
    elif( os.access( 'mixture',os.F_OK) ) :
        os.system('\cp -p mixture ' + OutputPath)

    if( os.access(name + '.rg',os.F_OK) ) :
        os.system('\cp -p '+ name+ '.rg ' + OutputPath + '/reglages')
    elif( os.access( 'reglages',os.F_OK) ) :
        os.system('\cp -p reglages ' + OutputPath)

    adiplsin = name + '.adipls'

    if( os.access(adiplsin,os.F_OK) ) :
        os.system('\cp -p '+  adiplsin + '  ' +  OutputPath + '.')
    else:
        os.system('\cp -p  adipls.in ' + OutputPath +  adiplsin)

    os.system('\cp -p '+ name+ '.xml ' + OutputPath + '/.')

    os.chdir(OutputPath)

    model = cestam.CModel(name,read=False)

    model.params.copy(refmodel.params)
    if(model.params.x0 < 0.):
        model.params.x0 = (1. - model.params.y0)/(1. + model.params.zsx0)
        model.params.z0 = (1. - model.params.x0 - model.params.y0)
    
    setupparams(model,parameters,settings)
    print 'x0,y0,z0,zsx0 = ',model.params.x0, model.params.y0,model.params.z0,model.params.zsx0
    model.params.agemax = 0.
    model.params.t_stop = 1E30
    
    noguess = False
    for p in parameters:
	if(p.name == 'agemax' or p.name == 't_stop'):
		if(p.value < 0):
			noguess = True
    if(noguess):
        # we chech that Teff is among the targets
        teff = -1.
        for t in targets:
            if(t.name == 'teff' or t.name == 'log_teff'):
                if(t.name == 'teff'):
                    teff = t.value
                else:
                    teff = 10.**(t.value)
        if(teff < 0.):
            raise OSMError("Teff must be among the targets when there is no guess value for agemax or x_stop or t_stop")
                

    model.params.mkdon(replace_eos=False)
    model.GUI = False
 
##     #    if( not(os.access(name+'_B.zams',os.F_OK) ) ): 
##     print 'computing a ZAMS model from PMS'
##     model.params.agemax = 1E3
##     model.params.arret= 'ZAMS'
##     model(job='pms')
##     model.params.arret= 'Other'
##     model.params.mkdon(replace_eos=False)
##     if(model.finished == False):
##             print "cannot proceed further, we get out from OSM"
##             sys.exit(0)

    start = 'zams'
    cf = 8e-5
    model.finished = False
    if( settings['models'] != None):
        start = settings['models']['start']
        cf = settings['models']['cf']
    if (start == 'zams'):
        if( (os.access(name+'_B.hom',os.F_OK) ) ):
            print '\na homogeneous model is already present in the W.D., we try to start from it'
            model.params.agemax = 0.
            model.run.type_file= 'Binary'
            model(job='zams',mod_init='./'+ name+'_B.hom')

        if(model.finished == False) :
            zamsmodel(model,model.params.mtot)
        model.run.type_file= 'Binary'
        model.params.mkdon(replace_eos=False)
    if (start == 'pms'):
        model.run.c_iben = cf
        if( (os.access(name+'_B.pms',os.F_OK) ) ):
            print '\nan initial PMS model is already present in the W.D., we try to start from it'
            model.params.agemax = 0.
            model.run.type_file= 'Binary'
            model(job='pms',mod_init='./'+ name+'_B.pms')
        if(model.finished == False) :
            pmsmodel(model,model.params.mtot)

    if(model.finished == False):
	raise OSMError("Error in OSM: unable to compute the initial model")
        
    if (start == 'zams'):
        os.system('\cp -f ' + name+ '_B.dat' + ' ' + name + '_B.zams')

    if(noguess):
        print '\nno guess value is given for age or T_STOP'
        OK  = False
        teff = 1e10
        for T in targets:
            if T.name.lower() == 'teff':
                teff = T.value
                OK = True
            if T.name.lower() == 'log_teff':
                teff = 10.**T.value
                OK = True
        if(not OK):
            raise   OSMError("Error in OSM: when no guess value is provided, Teff must be among the targets")
        model.params.t_stop = 1E30
        model.params.agemax = 15E3
        model.run.type_file= 'Binary'
        print '\ncomputing a model that matches approximately Teff= %f K' % teff
 	for p in parameters:
		if(p.name == 'agemax'):
                    print ("we start with agemax =  %f") % (p.bounds[0])
                    model.params.agemax = p.bounds[0]	
                if(p.name == 't_stop'):
                    model.params.t_stop = p.bounds[0]	
                    print ("we start with T_STOP = %e") % (p.bounds[0])
        model.params.log_teff = 10
        model.params.mkdon(replace_eos=False)
        if (start == 'zams'):
            model(job='zams',mod_init=name+'_B.hom',mkdon=False)
        else:
            model(job='pms',mkdon=False,mod_init='./'+ name+'_B.pms')
        model.params.t_stop = 1E30
        model.params.agemax = 15E3
        model.params.log_teff = - math.log10(teff)
        model.params.mkdon(replace_eos=False)
        model(job='rep',mod_init=name+'_B.rep',mkdon=False)
        model.params.log_teff = 10
        model.params.mkdon(replace_eos=False)
        if(model.finished == False):
		raise OSMError("Error in OSM: unable to compute the guess model")
	for p in parameters:
		if(p.name == 'agemax'):	
			p.value = model.glob[10]	
		if(p.name == 't_stop'):
			model.read_osc()	
                        p.value = model.var[2,model.ntot-1] # temperature at the center
    results = compute_optimal(name,parameters,targets,settings,seismic_constraints)

    os.chdir("../.")

    return results

