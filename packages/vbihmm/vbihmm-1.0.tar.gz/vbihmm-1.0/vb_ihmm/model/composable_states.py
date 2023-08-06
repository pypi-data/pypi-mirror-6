'''
Created on 22 Oct 2013

@author: James McInerney
'''

#implementation of Mixture that allows a set of parent latent states:

from numpy import *
from scipy.special.basic import digamma
from states import DiscreteStates, Mixture


class MixtureComp(Mixture):
    def __init__(self,sensors,N,L,K,hyperparams=None):
        self._L = L
        #randomly initialise expected values of random variables:
        self._prevKs = zeros((L,K))
        #self.randomInit(N, L, K)
        #default hyperparams:
        if hyperparams is None:
            hyperparams = {'alpha_tau_pi0':ones(K),
                           'alpha_tau_pi1':ones(K)}
        DiscreteStates.__init__(self,sensors,N,K,hyperparams=hyperparams)
        
    def m(self,parent_exp_z):
        #maximise variational parameters to the latent states.
        #calculate the conditional expected latent states:
        L = self._L #number of parent states
        K = self._K #number of latent states at this level
        N = self._N #number of obs.
        exp_z = zeros((N,L,K))
            
        Mixture.m()
         
    def randomInit(self,N,K):
        #forget existing latent assignments, and randomly initialise to new size |newN|
        L = self._L
        self._N = N
        concs = ones((L,K))
        self._exp_z = array([[random.dirichlet(concs[l,:]) for l in range(L)] for _ in range(N)])
        self._ln_obs_lik = zeros((N,L,K))
        
    def _mixMPi(self,alpha_tau_pi0,alpha_tau_pi1,exp_z,K):
        #alpha_pi: hyperparam for DP prior
        #exp_z: expectation of latent variables (we are only interested at time step 0 here)
        #L: number of parent states
        #K: truncation param. for DP
        L = self._L
        tau_pi0,tau_pi1 = zeros((L,K)), zeros((L,K))
        for l in range(L):
            tau_pi0[l,:], tau_pi1[l,:] = Mixture._mixMPi(alpha_tau_pi0,alpha_tau_pi1,exp_z[:,l,:],K)
        return tau_pi0,tau_pi1
    
    def _mixEZ(self,ln_obs_lik, exp_ln_pi, N, K):
        #follow mixture (not a time series):
        L = self._L
        exp_z = zeros((N,L,L))
        for l in range(L):
            exp_z[:,l,:] = Mixture._mixEZ(ln_obs_lik, exp_ln_pi[l,:], N, K)
        return exp_z
    
    def _ePi(self,tau_pi0,tau_pi1,K):
        L = self._L
        exp_ln_pi = zeros((L,K))
        for l in range(L):
            exp_ln_pi[l,:] = Mixture._ePi(tau_pi0, tau_pi1, K)
        return exp_ln_pi
