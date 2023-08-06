'''
Created on 8 Oct 2013

@author: James McInerney
'''

#extension of Sensors to deal with slotted data (i.e., multiple observations per time slot)

from sensors import MVGaussianSensor, Sensor
from numpy import *



class SlottedSensor(Sensor):
    def __init__(self,NS,T,K,sensor):
        self._sensor = sensor
        self._K = K
        self._T = T #time slot data (time slot assignment corresponding to each observation belonging to |sensor|
        self._NS = NS #num of time slots
        self._diff = 0.
    
    #need to aggregate each time slot:
    def loglik(self):
        T = self._T
        #NS = T.max()+1
        NS = self._NS
        K = self._K
        ln_obs_uns = self._sensor.loglik()
        #all that remains is to convert the unslotted version to slotted likelihoods:
        ln_obs_lik = zeros((NS,K))
        #requires: T value of each X is in ascending order:
        t = 0 #position in X, T and ln_obs_uns
        for n in range(NS): #for each time slot
            while t<len(T) and T[t]==n:
                ln_obs_lik[n,:] += ln_obs_uns[t,:] #product of likelihoods for same time slot
                t+=1 
        return ln_obs_lik
    
    def m(self,exp_z):
        #idea: repeat exp_z for obs in same time slot
        T = self._T
        (N,XDim) = shape(self._sensor._X)
        (NS,K) = shape(exp_z)
        Z = zeros((N,K))
        t = 0 #position in X, T and ln_obs_uns
        for n in range(NS): #for each time slot
            while t<len(T) and T[t]==n:
                Z[t,:] = exp_z[n,:]
                t+=1         
        self._sensor.m(Z)
        return Z #return unslotted version of exp_z
        
    def assignments(self,zs,defaultVal=0.):
        #map observation assignments to time slot assignments:
        T = self._T
        #NS = T.max()+1
        NS = self._NS
        K = self._K
        zs_slt = defaultVal + zeros(NS)
        #requires: T value of each X is in ascending order:
        t = 0 #position in X, T and ln_obs_uns
        for n in range(NS): #for each time slot
            while t<len(T) and T[t]==n:
                zs_slt[n] = zs[t]
                t+=1 
        return zs_slt

    def slotted(self,vs):
        #tranlsates vs to slotted assignments (similar to 'assignmnets' method but for vectors rather than scalars)
        #map observation assignments to time slot assignments:
        T = self._T
        #NS = T.max()+1
        NS = self._NS
        K = self._K
        vs_slt = zeros((NS,K))
        #requires: T value of each X is in ascending order:
        t = 0 #position in X, T and ln_obs_uns
        for n in range(NS): #for each time slot
            while t<len(T) and T[t]==n:
                vs_slt[n,:] = vs[t,:]
                t+=1 
        return vs_slt
    
    def setK(self,K0):
        self._K = K0
        self._sensor.setK(K0)
        
        
