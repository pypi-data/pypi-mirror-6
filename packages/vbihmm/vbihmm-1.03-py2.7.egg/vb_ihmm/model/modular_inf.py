'''
Created on Oct 17, 2013

@author: James McInerney
'''

#a new attempt at modular variational inference, this time involving DiscreteState objects (instead of HMM or mixture directly)

from numpy import *

def infer(latents,visuals=None,thres=1e-6,itr=0,max_itr=200,min_itr=10,VERBOSE=0,startEstep=0,showThres=1.,presetLatents=0):
    
    diff = 9999. #infinity
    #stop when parameters have converged (local optimum)
    while (itr<min_itr) or (itr<max_itr and diff>thres):
        prev_ln_obs_lik = latents.ln_obs_lik().copy()
                        
        #M-step:
        if itr>0 or startEstep==0: latents.m()
        
        #E-step:
        latents.e()
       
        #update visualisations (if any):
        if visuals is not None: visuals.update(itr,showThres)
        
        diff = latents.diff()
#        if itr!=0: diff = abs(latents._ln_obs_lik - prev_ln_obs_lik).mean() #average difference in previous expected value of transition matrix
#        else: diff = inf
        
        (ks,) = where(latents.expZ().sum(axis=0)>0.5)
        print 'itr,diff,NK',itr,diff,len(ks)
        itr += 1
    return itr


