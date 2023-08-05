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
import math
import multiprocessing
import os
import osmlib

class OSMError(Exception):
	def __init__(self, value):
         	self.value = value
	def __str__(self):
		return repr(self.value) 

class Parameter:
    name = ''
    value = 0.
    step = 0.
    rate = 0.
    bounds = [0.,0.]
    sigma = -1.
    evol = 0 # = 1 if the parameters controls the evolution
    

    def copy(self):
        new = Parameter()
        new.name = self.name
        new.value = self.value
        new.step = self.step
        new.rate = self.rate
        new.bounds = self.bounds
        new.sigma = self.sigma
        new.evol = self.evol
        return new

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

    
multiproc =  True

def levmar(modelname,func,parameters,func_args,y,covar,verbose=1,ftol=1e-3,maxiter=30,chi2min=1e-4,lamb0=1e-4):

    
    # def func (par,args,status): the function that computes the model and that we want to search for the optimal parameters
    #
    # status : =-1, if the function is called for the central values of the parameters (par)
    #          >-1  if the function is called for  the derivatives, in that case status
    #               is the index of the parameter for which we cant to compute the derivatives
    # parameters : parameters of the function
    # args: the other arguments passed to the function (can be 'None' if no others arguments need to be transmitted) 
    # 
    #  return : (model,error) 
    #


 
    def Chi2(model,y,W):
        # chi2 =  Chi2(func,par,func_args,y,w )  
        #
        # Y : (IN) le jeux de donnees 
        #
        # model : (IN) le modele 
        #
        # w : (IN)  inverse de la matrice de covariance
        #
        tmp = 0.
        n = len(y)
        for i in range(n):
            for j  in range(n):
                tmp = tmp + (y[i]-model[i]) * W[i,j] * (y[j]-model[j])
        return  tmp

    def levmar_der(model,func, parameters, func_args, y ,  der):
        

        def func_der(parameters,args,index):
            error  = True
            pari = list( i.copy() for i in parameters)
            iter = 0
            while( error == True and iter < 3):
                for i in range(len(pari)):
                    pari[i].value = parameters[i].value
		step = parameters[index].step/(1. + iter)
                pari[index].value = parameters[index].value  + step
                (model,error) = func(pari,func_args, index )
                iter += 1
                if(error):
                    print ('Error in OSM/levmar: unable to compute the derivative (model #%i), we reduce the step by a factor %i') % (index+1,iter+1)
            if(error):    
                print ('Error in OSM/levmar: unable to compute the derivative (mode #%i) after %i iterations') % (index+1,iter)
                model = 0 
            return (model,step,error)
        
        def func_shell(parameters,args,index,pipe):
            error  = True
            (model,error) = func(parameters ,args,  index  )
            pipe.send((model,0.,error))
            pipe.close()
            return

        def func_der_shell(parameters,args,index,pipe):
            error = True
            (model,step,error) = func_der(parameters,args,index)
            pipe.send( (model,step,error)   )
            pipe.close()
            return 

        error = False
        npar = len(parameters)
        models = np.zeros((model.size,npar))
	steps = np.zeros(npar)
        if ( multiproc == True):
            processes=[]
            parents=[]
            childs=[]
            res = []
            pipe = multiprocessing.Pipe()
            parents.append(pipe[0])
            childs.append(pipe[1])
            processes.append(multiprocessing.Process(target=func_shell,args=(parameters,func_args,  -1 , childs[0])))
            processes[0].start()
            nproc = 1
            for i in range(npar):
                if(parameters[i].evol == 0):
                    pipe = multiprocessing.Pipe()
                    parents.append(pipe[0])
                    childs.append(pipe[1])
                    processes.append(multiprocessing.Process(target=func_der_shell,args=(parameters,func_args,   i  , childs[nproc])))
                    processes[nproc].start()
                    nproc += 1
            for i in range(nproc):
                try:
                    processes[i].join()
                except:
                    for k in range(nproc):
                        processes[k].terminate()
                    sys.exit(1)

            for i in range(nproc):
                res.append(parents[i].recv())

            error = (res[0])[2]
            if(error):    
                return True
            model[:] = (res[0])[0]
            nproc = 1
            for i in range(npar):
                if(parameters[i].evol == 0):
                    error = (res[nproc])[2]
                    if(error):    
                        return True
                    models[:,i] = (res[nproc])[0]
		    steps[i] = (res[nproc])[1]
                    nproc += 1
                else:
                    (result,step,error) = func_der(parameters,func_args,i)
                    models[:,i] = result
		    steps[i] = step
                    if(error):    
                        return True
     	    # os.exit(0)
        else:
            (result,error) = func(parameters ,func_args, -1 )
            model[:] = result
#            print resutl
            if(error):
                return True
            for i in range(npar):
                (result,step,error) = func_der(parameters,func_args,i)
                models[:,i] = result
		steps[i] = step
 #               print result, step
                if(error):    
                    return True

        # on alimente la variable der
        for i in range(npar):
            der[i,:] = ((models[:,i] - model).flatten())/steps[i]

        return error
       
    def levmar_coef(model, npar,  y , W , der, lamb):
        
	alpha=np.zeros((npar,npar))
        beta=np.zeros((npar))
        n = len(y)
        for i in range(npar):
            tmp = 0.
            for l in range(n):
                for m in range(n):
                    tmp = tmp + 0.5 * W[l,m]* ( ( y[l] - model[l]) * der[i,l] +  (y[m] - model[m]) * der[i,m] )
            beta[i] = tmp
            for j in range(i,npar):
                tmp = 0.
                for l in range(n):
                     for m in range(n):
                         tmp = tmp + 0.5 * W[l,m]* ( der[i,l]*der[j,m]    +  der[i,m]*der[j,l] )
                alpha[i,j] = tmp * (1. + lamb*(i ==j) )
##                 alpha[i,j] = ((der[i,:]) * \
##                               (der[j,:])  \
##                               /sigma/sigma).sum() \
##                               * (1. + lamb*(i ==j) )
        for i in range(1,npar):
        	for j in range(0,i):
			alpha[i,j] = alpha[j,i]
        return (alpha,beta)
        
    lamb=lamb0
    ny  = len(y)
    y =   np.array(y)
    W = np.array(np.linalg.inv(np.matrix(covar)))
    npar = len(parameters)
    parn=list( p.copy() for p in parameters)
    global der
    der=np.zeros((npar,y.size))
    global dern
    dern=np.zeros((npar,y.size))
    model = np.zeros(ny)
    modeln = np.zeros(ny)
    k=0
    cont=1
    iter=0
    new=True
    f =open(modelname+'.log','w')
    text = ''
    text += '\n##############################################\n'
    text += 'Initial values:\n'
    for p in parameters:
        text += ("%s = %g\n") % (p.name,p.value)
    text +=  ('lambda= %g\n') % (lamb)
    if(verbose):
	print text
    f.write(text)
    error = levmar_der(model,func, parameters , func_args, y ,  der)
    
    if(error):
        text = 'Error in OSM/levmar: unable to compute the first model, we exit from levmar'
        if(verbose):
            print text
        f.write(text)
        f.close()
	raise OSMError(text)
    
    chi2i=Chi2(model,y,W)
    chi2n=chi2i

    def copyfiles(modelname):
        s = modelname + '_fin'
        os.system('\cp -p '+ modelname +'_B.dat ' + s+'_B.dat')
        os.system('\cp -p  '+ modelname +'.don ' + s+'.don')
        os.system('\cp -p  '+ modelname +'.HR ' + s+'.HR')
        if ( os.access(modelname+'-nad.osc',os.F_OK)  ):
            os.system('\cp -p  '+ modelname +'-nad.osc ' + s+'-nad.osc')
    	else:
            os.system('\cp -p  '+ modelname +'-ad.osc ' + s+'-ad.osc')
        if ( os.access(modelname+'.gsm',os.F_OK)  ):
            os.system('\cp -p  '+ modelname +'.gsm ' + s+'.gsm')

    copyfiles(modelname)

    text = '\n##############################################\n'
    text += "Initial model:\n"
    text += ('chi2= %g\n') % (chi2i)
    text += 'Parameters:\n'
    for p in parameters:
            text += ("%s = %g\n") % (p.name, p.value)
    text += "\n"
    text += "Model:" +  np.array_str(model) + "\n"
    text += "Constraints: " +  np.array_str(y) + "\n"
    #    text += "Sigma: " +  np.array_str(sigma) + "\n"
    text += "Distances (target-model):" +  np.array_str(y - model) + "\n"

    if(verbose):
	print text
    f.write(text)
    f.flush()
    modeln[:] = model[:]
    def sign(a):
        if(a < 0):
            return -1.
        else:
            return 1.
        
    while(cont):
        text = '\n'

        (alpha,beta)=levmar_coef(model,npar,y,W,der,lamb)
 	print alpha
	print beta
        alpha=np.linalg.inv(np.matrix(alpha))
        dpar= (np.array(alpha * np.matrix(beta.reshape((npar,1))))).flatten()
	print dpar
        for i in range(npar):
            if( math.fabs(dpar[i]) >  math.fabs(parameters[i].value*parameters[i].rate/100.) ):
                dpar[i] = math.fabs(parameters[i].value*parameters[i].rate/100.) * sign(dpar[i])
            if( ( parameters[i].value+ dpar[i] - parameters[i].bounds[0]   < 0 ) ):
                dpar[i] = parameters[i].bounds[0] - parameters[i].value 
            elif( (  parameters[i].value+ dpar[i] - parameters[i].bounds[1]  > 0 ) ):
                dpar[i] = parameters[i].bounds[1] - parameters[i].value
            parn[i].value  = parameters[i].value+ dpar[i]
	print dpar

        text +=  '\n##############################################\n'
        text += ('Iter # %i\n') % (iter)
        text += 'New parameters: \n'
        for p in parn:
            text += ("%s = %g\n") % (p.name,p.value)
        text += 'Change (new-old): ' +  np.array_str(dpar) + "\n"
	text +=  '.................................................\n'
	
        if(verbose):
            print text
        f.write(text)
	f.flush()

        error = levmar_der(modeln,func,parn, func_args, y , dern)
        if(error):
            text = ('Error in OSM/levmar: unable to compute the model at iteration # %i, we exit from levmar')  % (iter)
            if(verbose):
                print text
            f.write(text)
            f.close()
	    raise OSMError(text)

        chi2n=Chi2(modeln,y,W)
        text = ("New chi2: %g\n") % (chi2n)
        text += ("Old chi2: %g\n") % (chi2i)       
        text += "Parameters: "
        for p in parn:
            text += ("%g ") % (p.value)
        text += "\n"
        text += "Model:" +  np.array_str(modeln) + "\n"
        text +=  "Constraints: " +  np.array_str(y) + "\n" 
        #        text +=  "Sigma: " +  np.array_str(sigma) + "\n" 
        text +=  "Distances (target-model):" +  np.array_str(y - modeln) + "\n"

        df = (chi2n-chi2i)/chi2i # relative variation of the chi2
        cont= (iter < maxiter) & (abs(df) > ftol ) & (chi2n > chi2min)
        if(chi2n>=chi2i):
        	lamb = lamb*10.
            	text += 'Leaving the parameters unchanged: \n'
        else:
            lamb = lamb/4.
            for i in range(npar):
                parameters[i].value =parn[i].value
            chi2i=chi2n
            model[:]=modeln[:]
            der[:,:]=dern[:,:]
            text += 'Adopted parameters: \n' 
            for p in parameters:
                text += ("%s = %g\n") % (p.name,p.value)

            copyfiles(modelname)

        text +=  ('chi2 , dchi2/chi2 , lambda : %g %g %g\n') % (chi2i ,  df , lamb)
        text +=  '##############################################\n'
        if(verbose):
            print text
	f.write(text)
	f.flush()
        iter=iter+1

    text =  '\n##############################################\n'
    text += "stoped because:\n"
    if(iter >= maxiter):
    	text += ("\tnumber of iterations >= %i\n") % (maxiter)
    if(abs(df) <= ftol ):
    	text += ("\trelative variation of the chi2 <  %g\n") % (ftol)
    if( chi2n <= chi2min):
	text += ("\tchi2 <= %g\n") % (chi2min)
 
    lamb = 0.
    (alpha,beta)=levmar_coef(model,npar,y,W,der,lamb)
    alpha=np.linalg.inv(np.matrix(alpha))
    for i in range(npar):
        parameters[i].sigma = math.sqrt(alpha[i,i])
        
    text += 'Final values:\n'
    text +=  ('\tchi2= %g\n') % (chi2i)
    for p in parameters:
        text += ("%s = %g  +/- %g\n") % (p.name,p.value,p.sigma)

    text += ('\nlambda= %g\n') % (lamb)
    text += ('\dchi2/chi2= %g\n') % (df)
    text += ('number of iteration iter= %i\n\n') % (iter)
    for s in y:
	text += ("%g ") % (s)
    for i in range(ny):
        text += ("%g ") % (math.sqrt(covar[i,i]))
    for i in range(len(model)):
	text += ("%g ") % (model[i])
    for s in parameters:
    	text += ("%g ") % (s.value)
    for s in parameters:
        text += ("%g ") % (s.sigma)
    text += ("%g\n") % (chi2i)
    text +=  '##############################################\n'

    if(verbose):
	print text

    f.write(text)
    f.close()
    return (chi2i,parameters,iter,model,error)

