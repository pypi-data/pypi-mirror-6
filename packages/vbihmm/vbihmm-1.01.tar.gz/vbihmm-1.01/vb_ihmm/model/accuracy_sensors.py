'''
Created on 23 Oct 2013

@author: James McInerney
'''

#implementation of sensors where the accuracy is reported (and may or may not be trustworthy)

from sensors import MVGaussianSensor
from numpy import *
from numpy.linalg.linalg import inv
import pickle


#just like a multivariate Gaussian (with unknown mean and covariance matrix), but with reported accuracy for each obs.
class ReportedGaussian(MVGaussianSensor):
    
    def __init__(self,X,A,K,hyp=None):
        self._A = A
        MVGaussianSensor.__init__(self,X,K,hyp=hyp)

    def m(self,exp_z):
        #optimise variational parameters:
        X = self._X
        A = self._A
        (N,XDim) = shape(X)
        (N1,K) = shape(exp_z)
        assert N==N1,'N=%i, N1=%i'%(N,N1)
        
        #access hyperparameters
        m0 = self._hyperparams['m0']
        W0 = self._hyperparams['m1']
        #find max hyperparam updates:
        self._W = self._mW(W0,exp_z,A,XDim,K)
        self._m = self._mM(N,K,X,A,exp_z,self._W,W0,m0,XDim)
        self._NK = exp_z.sum(axis=0)
    
    def loglik(self):
        #return log lik of each data point x latent component
        X = self._X
        A = self._A
        K = self._K
        (N,XDim)=shape(X)
        #ll = -reshape(0.5*XDim*log(2*pi) + log(A),(N,1)) * ones((N,K))
        ll = reshape(log(A), (N,1)) * ones((N,K))
        for n in range(N):
            for k in range(K):
                v1 = reshape(X[n,:] - self._m[k,:],(1,XDim)) # N x XDim
                ll[n,k] = ll[n,k] - 0.5*A[n]*dot(v1,v1.T)
        return ll
    
    def expC(self):
        #return expected covariance for each observation, (N x XDim x XDim) (in contrast to, normally, each latent component)
        (N,XDim) = shape(self._X)
        expC = zeros((N,XDim,XDim))
        for n in range(N):
            expC[n,:,:] = eye(XDim) / self._A[n]
        return expC
    
    def _mW(self,W0,exp_z,A,XDim,K):
        W = zeros((K,XDim,XDim))
        for k in range(K):
            W[k,:,:] = W0[k] + (exp_z[:,k]*A).sum()*eye(XDim)
        return W 
    
    def _mM(self,N,K,X,A,exp_z,W,W0,m0,XDim):
        m = zeros((K,XDim))
        for k in range(K):
            m[k,:] = dot(inv(W[k,:,:]), dot(W0[k],m0[k,:]).T + (X*reshape(A*exp_z[:,k],(N,1))).sum(axis=0) )
        return m

    def save(self,filepath):
        save(filepath+'_K',self._K)
        save(filepath+'_NK',self._NK)
        save(filepath+'_m',self._m)
        save(filepath+'_W',self._W)
        pickle.dump(self._hyperparams, open(filepath+'_hyp.pck','w'))
        print 'saved ReportedGaussian',filepath
        
    def load(self,filepath):
        self._K = load(filepath+'_K.npy')
        self._NK = load(filepath+'_NK.npy')
        self._m = load(filepath+'_m.npy')
        self._W = load(filepath+'_W.npy')
        self._hyperparams = pickle.load(open(filepath+'_hyp.pck','r'))
        print 'loaded ReportedGaussian',filepath

#like a reported Gaussian, but where the reported precisions are untrustworthy:
#(specifically, we assume fixed prior alpha_tau controlling gamma precisions tau_n for each observation of this modality): 
class TrustGaussian(ReportedGaussian):
    
        
    def __init__(self,X,A,K,hyp=None):
        (N,_)=shape(X)
        self._exp_tau = ones(N)
        self._exp_mu_diff = ones((N,K))
        ReportedGaussian.__init__(self,X,A,K,hyp=hyp)
        print 'prior trust alpha_tau0',hyp['alpha_tau0']
        print 'prior trust alpha_tau1',hyp['alpha_tau1']
        print 'prior trust C',hyp['C']
        
        
    def m(self,exp_z):
        X = self._X
        (N,XDim) = shape(X)
        A = self._A #reported precision for each data point x_n
        (N1,K) = shape(exp_z)
        assert N==N1,'N=%i, N1=%i'%(N,N1)
        #access hyperparameters
        m0 = self._hyperparams['m0']
        W0 = self._hyperparams['m1']
        alpha_tau0, alpha_tau1 = self._hyperparams['alpha_tau0'], self._hyperparams['alpha_tau1']
        #find max hyperparam updates:
        A1 = A*self._exp_tau #N.B. difference between Reported and Trust is that we are scaling A by expected trust value
        self._W = self._mW(W0,exp_z,A1,XDim,K)
        self._m = self._mM(N,K,X,A1,exp_z,self._W,W0,m0,XDim)
        self._NK = exp_z.sum(axis=0)
        #calculate variational params to each trust value tau_n:
        self._alpha_tau_n0 = alpha_tau0*ones(N) + 0.5*XDim
        self._alpha_tau_n1 = alpha_tau1*ones(N)
        for k in range(K): self._alpha_tau_n1 += 0.5*A*(exp_z[:,k]*self._exp_mu_diff[:,k])

        
    def loglik(self):
        #return log like of each data point and latent component
        #just like ReportedGaussian, except that we need to consider the expected trust values E(tau_n)

        X = self._X
        A = self._A
        K = self._K
        C = self._hyperparams['C'] #constant scaling factor
        (N,XDim) = shape(X)
        
        exp_tau = C * self._alpha_tau_n0 / self._alpha_tau_n1
        
        #consider fixed values from trust:
        for (ts,val) in self._hyperparams['modtrust']: exp_tau[ts] = 1*val 
        
        self._exp_tau = exp_tau
        #calculate E[ (x-mu).T (x - mu) ]:
        self._exp_mu_diff = zeros((N,K))
        for n in range(N):
            for k in range(K):
                v1 = reshape(X[n,:] - self._m[k,:], (1,XDim)) # 1 x XDim
                self._exp_mu_diff[n,k] = dot(v1,v1.T)
        #now calculate loglik:
        ll = reshape(log(A) + log(exp_tau), (N,1)) * ones((N,K))
        for n in range(N):
            for k in range(K):
                v1 = reshape(X[n,:] - self._m[k,:],(1,XDim)) # N x XDim
                ll[n,k] -= 0.5*A[n]*exp_tau[n]*dot(v1,v1.T)
        return ll

    def expC(self):
        #return expected covariance for each observation, (N x XDim x XDim) (in contrast to, normally, each latent component)
        (N,XDim) = shape(self._X)
        expC = zeros((N,XDim,XDim))
        for n in range(N):
            expC[n,:,:] = (self._hyperparams['C'][n] * eye(XDim)) /(max(1e-7,self._exp_tau[n]) * self._A[n]) #ensure denominator is not zero
        return expC

    def save(self,filepath):
        save(filepath+'_exp_tau',self._exp_tau)
        ReportedGaussian.save(self, filepath)
        
    def load(self,filepath):
        self._exp_tau = load(filepath+'_exp_tau.npy')
        ReportedGaussian.load(self, filepath)
        
    