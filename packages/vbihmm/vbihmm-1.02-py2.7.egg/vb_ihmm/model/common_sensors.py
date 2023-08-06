'''
Created on Nov 6, 2013

@author: James McInerney
'''


#implementation of sensors that share a common parameter (most common use case is common mean to set of Gaussian sensors)


from numpy import *
from sensors import Sensor, MVGaussianSensor
from accuracy_sensors import ReportedGaussian
from numpy.linalg.linalg import inv
from util import inv0, inv00

#aggregates a set of multivariate Gaussian sensors (reported or not reported)
class CommonMeanSensor(Sensor):
    def __init__(self, sensors, sensorTypes, hyperparams, setM=None):
        self._sensors = sensors #list of slotted MVGaussian sensors
        m0 = hyperparams['m0'] #prior mean of mean
        g0 = hyperparams['g0'] #prior precision of mean
        #assert all([s._sensor._hyperparams['m0']==m0 for s in self._sensors]), 'm0 hyperparam needs to be the same for all child sensors'
        self._hyperparams = {'m0':m0, 'g0':g0}
        self._sensorTypes = sensorTypes #describes each sensor as having either 'component' or 'obs' - wise precision
        self._setM = setM

    def loglik(self):
        return array([s.loglik() for s in self._sensors]).sum(axis=0) #just aggregate the child sensors
        
        
    def m(self,exp_z_slotted):
        #invoke m functions of child sensors, then aggregate properties to arrive at common mean parameter for all:
        Zs = [s.m(exp_z_slotted) for s in self._sensors]
        #now find common mean:
        m0,g0 = self._hyperparams['m0'], self._hyperparams['g0']
        (NS,K) = shape(exp_z_slotted) #todo: need to consider slotted sensors here...
        XDim = 2
        #numer, denom_inv = [dot(g0,m0) for _ in range(K)], [g0 for _ in range(K)]
        numer, denom_inv = [zeros(2) for _ in range(K)], [zeros((2,2)) for _ in range(K)] 
        for s1,t,exp_z in zip(self._sensors, self._sensorTypes, Zs):
            s = s1._sensor
            X = s.X() #data for this sensor (modality)
            Nk = exp_z.sum(axis=0)
            (N,XDim) = shape(X) #sensors can have different # data points but not dimensionalities (should check this in __init__)
            (N1,K) = shape(exp_z)
            assert N==N1,'N=%i, N1=%i'%(N,N1)
            if t=='unreported':
                #not reported, so precision is component-wise:
                #Pk = map(inv, s.expC()) #precision for each component k
                C = s.expC()
                for k in range(K):
                    Pk = inv(C[k,:,:])
                    denom_inv[k] += Nk[k]*Pk
                    for n in range(N):
                        x_n = reshape(X[n,:], (XDim,1))
                        numer[k] += exp_z[n,k]*dot(Pk,x_n).flatten() #.flatten() # (D,D) x (D,1) = (D,1)
            elif t=='reported':
                #reported, so precision is observation-wise:
                Cn = s.expC()
                for k in range(K):
                    for n in range(N):
                        Pn = inv(Cn[n])
                        x_n = reshape(X[n,:], (XDim,1))
                        numer[k] += exp_z[n,k]*dot(Pn,x_n).flatten() # (D,D) x (D,1) = (D,1)
                        denom_inv[k] += exp_z[n,k]*Pn
            else:
                raise Exception('Unknown sensor type ' + t)
        #calculate common mean:
        m = zeros((K,XDim))
        for k in range(K): 
            m[k,:] = dot(inv00(denom_inv[k]), numer[k])
        if self._setM is not None: #force last mean to be certain value (for presetting, if desired)
            m[K-1,:] = self._setM
        #set all the means to the same (aggregate) result:
        for s1 in self._sensors:
            s = s1._sensor
            s._m = m
        
    #calculate total change in this iteration for each component sensor:    
    def diff(self):
        return array([s.diff() for s in self._sensors]).sum()

    
    def means(self):
        #return common means (should be identical for all sensors):
        return self._sensors[0]._sensor._m
    
    
