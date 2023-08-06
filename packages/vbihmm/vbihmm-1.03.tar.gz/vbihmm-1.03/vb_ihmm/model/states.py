'''
Created on Oct 17, 2013

@author: James McInerney
'''
from sensors import Sensor, DiscreteSensor
from numpy import *
from scipy.special.basic import digamma
from viterbi import viterbiLog
import itertools as itt
import pickle

set_printoptions(threshold='nan') 

#a class to perform inference on a set of discrete latent states:   
class DiscreteStates(DiscreteSensor):
    def __init__(self,sensors,N,K,hyperparams=None):
        self._sensors = sensors #list of sensors giving the model it's log-likelihood
        #random initialisation of expected values of states:
        self.randomInit(N,K)
        self._init_exp_z = self._exp_z.copy()
        self._prevKs = zeros(K) #cumulative total counts for components (only useful in online setting)
        self._ln_obs_lik = zeros((N,K))
        self._activated = 1
        self._diff = inf #convergence management
        DiscreteSensor.__init__(self,zeros((N,K)),K,hyp=hyperparams)

    def e(self):
        #calculate expectation of latent states.
        #returns nothing (but internal updates are performed).
        #step 1. find the observation likelihoods:
        ln_obs_lik = array([s.loglik() for s in self._sensors]).sum(axis=0)
#        self._diff = (abs(self._ln_obs_lik - ln_obs_lik)).mean() #for approximate idea of convergence        
        prev_z = self._exp_z.copy()
        if self._activated: self._do_e(ln_obs_lik)
        #find out the difference in expected state since last iteration:
        diff = (abs(self._exp_z - prev_z)).mean()
        #now consider change in childrens' state (simple mean):
        self._diff = diff + array([s.diff() for s in self._sensors]).mean()
        self._ln_obs_lik = ln_obs_lik
        
    def _do_e(self, ln_obs_lik):
        #only called if we want to perform e-step at this level (i.e., states are activated)
        raise Exception('Not implemented.')

    def expPi(self):
        tau_pi0,tau_pi1,K = self._tau_pi0, self._tau_pi1, self._K
        exp_pi = zeros((1,K))
        acc = tau_pi0 / (tau_pi0 + tau_pi1)
        for k in range(K): exp_pi[0,k] = (acc[:k].prod()*tau_pi1[k]) / (tau_pi0[k] + tau_pi1[k])
        return exp_pi
    
    def expZ(self):
        return self._exp_z
    
    def ln_obs_lik(self):
        return self._ln_obs_lik
    
    def sigComponents(self,thres=1.0):
        #returns components that have more than trivial probability mass (along with total number):
        #totalKs = self._prevKs + self._exp_z.sum(axis=0)
        totalKs = self._exp_z.sum(axis=0)
        (ks,) = where(totalKs > thres)
        return self._K,ks
    
    def randomInit(self,N,K):
        #forget existing latent assignments, and randomly initialise to new size |newN|
        self._N = N
        #assign to lowest represented components:
        #concs = 1/((1.0+self._prevKs)**(2))
        #print 'concs',concs
#        if self._exp_z is None:
#            concs = ones(K)
#        else:
#            #online: decide on initialization based on likelihood of these points
#            #based on the idea that we want to find the points that are least well explained by existing components:
#            llk = array([s.loglik() for s in self._sensors]).sum(axis=0)
#            print 'llk',llk
#            concs =  llk + exp_z
        concs = ones(K)
        self._exp_z = array([random.dirichlet(concs) for _ in range(N)])
        self._ln_obs_lik = zeros((N,K))
    

    def extendN(self,N0):
        #extend number of possible latent states:
        assert N0>self._N
        N = self._N
        exp_z1 = zeros((N0,self._K))
        exp_z1[:N,:] = self._exp_z #copy over existing portion of exp_z
        exp_z1[N:,:] = array([random.dirichlet(ones(self._K)) for _ in range(N0-N)]) 
        self._exp_z = exp_z1
        self._N = N0 

    def estimateTransitions(self):
        #estimates the transition for each time step (N-1), given latent vars exp_z
        exp_z = self._exp_z
        (N,K) = shape(exp_z)
        exp_s = zeros((N-1,K,K))
        for n in range(N-1):
            v1,v2 = reshape(exp_z[n-1,:],(1,K)), reshape(exp_z[n,:],(K,1))
            exp_s[n,:,:] = dot(v1,v2)
        return exp_s
        
    #overloading of tau_pi0 and tau_pi1: in a mixture model, they refer to the variational parameters
    #of latent states of *all* time steps, whereas in HMM they refer to only the initial state:
    def _ePi(self,tau_pi0,tau_pi1,K):
        exp_ln_pi = zeros(K)
        acc = digamma(tau_pi0) - digamma(tau_pi0 + tau_pi1)
        for k in range(K-1):
            exp_ln_pi[k] = digamma(tau_pi1[k]) - digamma(tau_pi0[k] + tau_pi1[k]) + acc[:k].sum()
        exp_ln_pi[K-1] = acc[:K-1].sum()
        return exp_ln_pi        

    def _acc(self,tau_a0,tau_a1):
        return digamma(tau_a0) - digamma(tau_a0 + tau_a1)



class Mixture(DiscreteStates):

    def __init__(self,sensors,N,K,hyperparams=None):
        #randomly initialise expected values of random variables:
        self._prevKs = zeros(K)
        self.randomInit(N, K)
        #default hyperparams:
        if hyperparams is None:
            hyperparams = {'alpha_tau_pi0':ones(K),
                           'alpha_tau_pi1':ones(K),
                           'c':1e-6,
                           'd':0.1}
        self._alpha_tau_pi0 = hyperparams['alpha_tau_pi0']
        DiscreteStates.__init__(self,sensors,N,K,hyperparams=hyperparams)

    #allow initial setting of comopnents,:
    def initComponents(self,init_zs):
        N1 = len(init_zs)
        N,K = self._N, self._K
        assert N==N1,'N=%i N1=%i'%(N,N1)
        self._exp_z = zeros((N,K))
        for n in range(N): self._exp_z[n,init_zs[n]] = 1.

    def loglik(self):
        #step 1: calculate the total log likelihood for each observation n (for each sensor)
        0
    
    def m(self):
        #maximise variational parameters to the latent states.
        #alpha_tau_pi0, alpha_tau_pi1 = self._hyperparams['alpha_tau_pi0'], self._hyperparams['alpha_tau_pi1']
        alpha_tau_pi0, alpha_tau_pi1 = self._alpha_tau_pi0, self._hyperparams['alpha_tau_pi1']
        exp_z = self._exp_z
        self._tau_pi0,self._tau_pi1 = self._mixMPi(alpha_tau_pi0,alpha_tau_pi1,exp_z,self._K)
        self._tau_c = self._hyperparams['c'] + 1.
        self._tau_d = self._hyperparams['d'] - self._acc(alpha_tau_pi0, alpha_tau_pi1)
        #finally, maximize the variational parameters to all the sensors:
        [s.m(exp_z) for s in self._sensors]
        
    def _do_e(self, ln_obs_lik):
        (N,K) = shape(ln_obs_lik)
        #step 2. find the exp ln of component coefficients:
        exp_ln_pi = self._ePi(self._tau_pi0, self._tau_pi1, self._K)
        #step 3. combine information from steps 1 and 2 to give expected value of latent states:
        self._exp_z = self._mixEZ(ln_obs_lik, exp_ln_pi, N, K) #mixture model estimation of Z
        self._alpha_tau_pi0 = self._tau_c / self._tau_d
        
    def updateOnline(self,coeff=1.):
        #updates the hyperparameters to be the current variational parameters: to be used after the final iteration of variational inference optimisation
        alpha_tau_pi0, alpha_tau_pi1 = self._hyperparams['alpha_tau_pi0'], self._hyperparams['alpha_tau_pi1']
        hyp = {'alpha_tau_pi0':alpha_tau_pi0 + coeff*(self._tau_pi0-alpha_tau_pi0),
               'alpha_tau_pi1':alpha_tau_pi1 + coeff*(self._tau_pi1-alpha_tau_pi1)}
        self._hyperparams = hyp
        self._prevKs += coeff*self._exp_z.sum(axis=0)
        #print 'hyp',hyp
        DiscreteStates.updateOnline(self)

    def save(self,filepath):
        save(filepath+'_exp_z',self._exp_z)
        save(filepath+'_tau_pi0',self._tau_pi0)
        save(filepath+'_tau_pi1',self._tau_pi1)
        pickle.dump(self._hyperparams, open(filepath+'_hyp.pck','w'))
        
    def load(self,filepath):
        self._exp_z = load(filepath+'_exp_z.npy')
        self._tau_pi0 = load(filepath+'_tau_pi0.npy')
        self._tau_pi1 = load(filepath+'_tau_pi1.npy')
        self._hyperparams = pickle.load(open(filepath+'_hyp.pck','r'))


    def _mixMPi(self,alpha_tau_pi0,alpha_tau_pi1,exp_z,K):
        #alpha_pi: hyperparam for DP prior
        #exp_z: expectation of latent variables (we are only interested at time step 0 here)
        #K: truncation param. for DP
        tau_pi0,tau_pi1 = zeros(K), zeros(K)
        for k in range(K):
            #print 'exp_z',exp_z
            tau_pi0[k] = alpha_tau_pi0[k] + exp_z[:,k+1:].sum() #hyperparam for this component NOT explaining the data
            tau_pi1[k] = alpha_tau_pi1[k] + exp_z[:,k].sum() #hyperparam for this component explaining the data
        return tau_pi0,tau_pi1

    
    def _mixEZ(self,ln_obs_lik, exp_ln_pi, N, K):
        #follow mixture (not a time series):
        ln_exp_z = zeros((N,K))
        for k in range(K):
            ln_exp_z[:,k] = exp_ln_pi[k] + ln_obs_lik[:,k]
        
        #exponentiate and normalise:
        #make sure that none of the rows is -inf:
        (iv,) = where(isinf(ln_exp_z.max(axis=1)))
        #fix those rows, if necessary (interpretation is: for some time steps, there is zero evidence for the latent variable, so unnormalised pr of row is entirely -inf):
        ln_exp_z[iv,:] = 0.
        ln_exp_z -= reshape(ln_exp_z.max(axis=1), (N,1))
        exp_z = exp(ln_exp_z) / reshape(exp(ln_exp_z).sum(axis=1), (N,1))
        #exp_z = lnNorm(ln_exp_z,axis=1)
        return exp_z

class HMM(DiscreteStates):
    
    def __init__(self,sensors,N,K,hyperparams=None,fixedNs=None,valExpZFixed=None):
        #randomly initialise expected values of random variables:
        self._prevKs = zeros(K)
        self.randomInit(N, K)
        #default hyperparams:
        if hyperparams is None:
            hyperparams = {'alpha_tau_pi0':ones(K),
                           'alpha_tau_pi1':ones(K),
                           'alpha_tau_a0':ones((K,K)),
                           'alpha_tau_a1':ones((K,K)),
                           'c':1e-6*ones((K,K)),
                           'd':0.1*ones((K,K))} #settings from Paisley et al. (2010)
        self._alpha_tau_a0 = hyperparams['alpha_tau_a0']
        #for specifing fixed states:
        if fixedNs is not None:
            self._fixedNs = fixedNs
            self._valExpZFixed = valExpZFixed
            self._freeNs = array([i for i in range(N) if i not in fixedNs])
        else:
            self._fixedNs = zeros(0)
            self._freeNs = arange(N)
            self._valExpZFixed = None
        DiscreteStates.__init__(self,sensors,N,K,hyperparams=hyperparams)
    
    def loglik(self):
        #step 1: calculate the total log likelihood for each observation n (for each sensor)
        0
    
    def m(self,sensor_exp_z=None):
        #maximise variational parameters to the latent states.
        alpha_tau_pi0, alpha_tau_pi1 = self._hyperparams['alpha_tau_pi0'], self._hyperparams['alpha_tau_pi1']
#        alpha_tau_a0, alpha_tau_a1 = self._hyperparams['alpha_tau_a0'], self._hyperparams['alpha_tau_a1']
        alpha_tau_a0, alpha_tau_a1 = self._alpha_tau_a0, self._hyperparams['alpha_tau_a1']
        exp_z, exp_s = self._exp_z, self._exp_s
        self._tau_pi0,self._tau_pi1 = self._mPi(alpha_tau_pi0,alpha_tau_pi1,exp_z,self._K)
        self._tau_a0,self._tau_a1 = self._mA(alpha_tau_a0,alpha_tau_a1,exp_s,self._K)
        self._tau_c = self._hyperparams['c'] + 1. #hyper-hyperparams
        self._tau_d = self._hyperparams['d'] - self._acc(self._tau_a0, self._tau_a1) #hyper-hyperparams
        #finally, maximize the variational parameters to all the sensors:
        if sensor_exp_z is None: sensor_exp_z = exp_z
        [s.m(exp_z) for s in self._sensors]
        
    def _do_e(self, ln_obs_lik):
        (N,K) = shape(ln_obs_lik)
        #step 2. find the exp ln of component coefficients:
        exp_ln_pi = self._ePi(self._tau_pi0, self._tau_pi1, self._K)
        self._exp_ln_pi = exp_ln_pi
        #step 3. combine information from steps 1 and 2 to give expected value of latent states:
        exp_ln_a = self._eA(self._tau_a0,self._tau_a1,K)
        self._exp_ln_a = exp_ln_a
        ln_alpha_exp_z = self._eFowardsZ(exp_ln_pi, exp_ln_a, ln_obs_lik, N, K) #FORWARDS PASS
        ln_beta_exp_z = self._eBackwardsZ(exp_ln_pi, exp_ln_a, ln_obs_lik, N, K) #BACKWARDS PASS
        self._exp_z[self._freeNs,:] = self._eZ(ln_alpha_exp_z, ln_beta_exp_z, N)[self._freeNs,:] #find expected state for each time step
        for vi,i in zip(self._fixedNs,itt.count()): self._exp_z[vi,:] = self._valExpZFixed[i,:]
        self._exp_s = self._eS(exp_ln_a, ln_alpha_exp_z, ln_beta_exp_z, ln_obs_lik, N, K) #find expected transition for each time step
        #if self._K<3: print 'exp_z',self._exp_z
        self._alpha_tau_a0 = self._tau_c/self._tau_d
        #print 'self._alpha_tau_a0',self._alpha_tau_a0
        if self._K < 0:
            print 'T (for level with %i components)'%(self._K),self.expA()
            v = self.viterbi()
            print 'exp_z argmax (for level with %i components)'%(self._K),self._exp_z.argmax(axis=1)
            print 'viterbi',v
#            print 'exp_z.argmax() == 1 (for level with %i components)'%(self._K),where(self._exp_z.argmax(axis=1)==1)
            print 'viterbi == 1 (for level with %i components)'%(self._K),where(v==1)
        self._ln_obs_lik = ln_obs_lik #remember ln_obs_lik in case we want to run viterbi later
    
    def viterbi(self):
        #returns most likely *path* through time (i.e., sequence of states)
        return viterbiLog(self._ln_obs_lik,self.expA(),self.expPi())
    
    def expA(self):
        tau_a0,tau_a1,K = self._tau_a0, self._tau_a1, self._K
        exp_a = zeros((K,K))
        acc = tau_a0/(tau_a0+tau_a1)
        for i in range(K):
            for j in range(K-1):
                exp_a[i,j] = (acc[i,:j].prod()*tau_a1[i,j])/(tau_a0[i,j]+tau_a1[i,j])
            exp_a[i,K-1] = acc[i,:K-1].prod() 
        return exp_a
    
    def updateOnline(self):
        #updates the hyperparameters to be the current variational parameters: to be used after the final iteration of variational inference optimisation
        hyp = {'alpha_tau_pi0':self._tau_pi0,
               'alpha_tau_pi1':self._tau_pi1,
               'alpha_tau_a0':self._tau_a0,
               'alpha_tau_a1':self._tau_a1}
        self._hyperparams = hyp
        DiscreteStates.updateOnline(self)

    def randomInit(self,N,K):
        #forget existing latent assignments, and randomly initialise to new size |newN|
        self._N = N
#        self._exp_s = array([random.uniform(0,100,(K,K)) for _ in range(N-1)])
#        for n in range(N-1): self._exp_s[n,:,:] = self._exp_s[n,:,:] / self._exp_s[n,:,:].sum()
        DiscreteStates.randomInit(self,N,K)
        #use random values of exp_z to find initial random values of exp_s:
        self._exp_s = zeros((N,K,K))
        for n in range(1,N): #range(N,N0-1):
            z1,z2 = reshape(self._exp_z[n-1,:],(K,1)), reshape(self._exp_z[n,:],(1,K))
            self._exp_s[n,:,:] = dot(z1,z2)

    #allow initial setting of comopnents, and calculate transitions from this:
    def initComponents(self,init_zs):
        N1 = len(init_zs)
        N,K = self._N, self._K
        assert N==N1,'N=%i N1=%i'%(N,N1)
        self._exp_z = zeros((N,K))
        for n in range(N): self._exp_z[n,init_zs[n]] = 1.
        #use random values of exp_z to find initial random values of exp_s:
        self._exp_s = zeros((N,K,K))
        for n in range(1,N): #range(N,N0-1):
            z1,z2 = reshape(self._exp_z[n-1,:],(K,1)), reshape(self._exp_z[n,:],(1,K))
            self._exp_s[n,:,:] = dot(z1,z2)

    def extendN(self,N0,assignLeast=3):
        #extend number of possible latent states:
        assert N0>self._N
        N,K = self._N, self._K
        #exetend exp_z:
        exp_z1 = zeros((N0,self._K))
        exp_z1[:N,:] = self._init_exp_z #copy over existing portion of exp_z
        #assign to least three represented components:
#        cs = self._exp_z.sum(axis=0)
#        cso1 = sorted(zip(cs,itt.count()),key=lambda (a,b):a,reverse=1)
#        (cso,csi) = zip(*cso1)
#        print 'csi',csi
#        js = zeros(K)
#        js[array(csi[-assignLeast:])] = 1.
#        exp_z1[N:,:] = array([random.dirichlet(0.1*js) for _ in range(N0-N)]) #
        exp_z1 = array([random.dirichlet(ones(K)) for _ in range(N0)])
        self._exp_z = exp_z1        
        self._init_exp_z = exp_z1.copy()
#        print 'new data points assigned to components',where(js>0)
#        print 'new sig components',self.sigComponents()
#        print 'exp_z[N1:,:]',self._exp_z.argmax(axis=1)
        #now extend exp_s based on exp_z:        
        exp_s1 = zeros((N0-1,K,K))
        exp_s1[:(N-1),:,:] = self._exp_s #copy over existing portion of exp_z
        #use random values of exp_z to find initial random values of exp_s:
        for n in range(1,N0-1): #range(N,N0-1):
            z1,z2 = reshape(exp_z1[n-1,:],(K,1)), reshape(exp_z1[n,:],(1,K))
            exp_s1[n,:,:] = dot(z1,z2)
        self._exp_s = exp_s1
        self._N = N0 
    
    def save(self,filepath,skipSeq=0):
        save(filepath+'_exp_z',self._exp_z)
        if not(skipSeq): save(filepath+'_exp_s',self._exp_s)
        save(filepath+'_tau_pi0',self._tau_pi0)
        save(filepath+'_tau_pi1',self._tau_pi1)
        save(filepath+'_tau_a0',self._tau_a0)
        save(filepath+'_tau_a1',self._tau_a1)
        pickle.dump(self._hyperparams, open(filepath+'_hyp.pck','w'))
        
    def load(self,filepath,K):
        self._K = K
        self._exp_z = load(filepath+'_exp_z.npy')
        self._tau_pi0 = load(filepath+'_tau_pi0.npy')
        self._tau_pi1 = load(filepath+'_tau_pi1.npy')
        self._tau_a0 = load(filepath+'_tau_a0.npy')
        self._tau_a1 = load(filepath+'_tau_a1.npy')
        self._hyperparams = pickle.load(open(filepath+'_hyp.pck','r'))
        try:
            self._exp_s = load(filepath+'_exp_s.npy')
        except IOError:
            #then we didn't save sequence (very big file)
            print 'exp_s not loaded'

        
    def _mPi(self,alpha_tau_pi0,alpha_tau_pi1,exp_z,K):
        #alpha_pi: hyperparam for DP prior
        #exp_z: expectation of latent variables (we are only interested at time step 0 here)
        #K: truncation param. for DP
        tau_pi0,tau_pi1 = zeros(K), zeros(K)
        for k in range(K):
            #print 'k,K,shape exp_z,shape alpha',k,K,shape(exp_z),shape(alpha_tau_pi0)
            tau_pi0[k] = alpha_tau_pi0[k] + exp_z[0,k+1:].sum() #hyperparam for this component NOT explaining the data
            tau_pi1[k] = alpha_tau_pi1[k] + exp_z[0,k] #hyperparam for this component explaining the data
        return tau_pi0,tau_pi1

    def _mA(self,alpha_tau_a0,alpha_tau_a1,exp_s,K):
        #alpha_a: hyperparam for transition matrix
        #exp_s: expectation of latent variables (transitions)
        #K: truncation param. for DP
        tau_a0,tau_a1 = zeros((K,K)), zeros((K,K))
        for i in range(K):
            for j in range(K):
                tau_a0[i,j] = alpha_tau_a0[i,j] + exp_s[:,i,j+1:].sum() #hyperparam for this component NOT explaining the data
                tau_a1[i,j] = alpha_tau_a1[i,j] + exp_s[:,i,j].sum() #hyperparam for this component explaining the data
        return tau_a0,tau_a1
    
    def _eA(self,tau_a0,tau_a1,K):
        exp_ln_a = zeros((K,K))
        acc = digamma(tau_a0) - digamma(tau_a0 + tau_a1)
        for i in range(K):
            for j in range(K-1):
                exp_ln_a[i,j] = digamma(tau_a1[i,j]) - digamma(tau_a0[i,j] + tau_a1[i,j]) + acc[i,:j].sum()
            exp_ln_a[i,K-1] = acc[i,:K-1].sum()
        return exp_ln_a
    
    def _eZ(self,ln_alpha_exp_z, ln_beta_exp_z, N, parent_exp_z=None):
        #combine the alpha and beta messages to find the expected value of the latent variables:
        ln_exp_z = ln_alpha_exp_z + ln_beta_exp_z
        
        #exponentiate and normalise:
        ln_exp_z -= reshape(ln_exp_z.max(axis=1), (N,1))
        exp_z = exp(ln_exp_z) / reshape(exp(ln_exp_z).sum(axis=1), (N,1))
        #exp_z = lnNorm(ln_exp_z,axis=1)
        return exp_z
        

    def _eFowardsZ(self,exp_ln_pi,exp_ln_a,ln_obs_lik,N,K,parent_exp_z=None):
        ln_alpha_exp_z = zeros((N,K)) - inf
        #initial state distribution:
        #print 'exp_invc',exp_invc
        ln_alpha_exp_z[0,:] = exp_ln_pi + ln_obs_lik[0,:]
        for n in range(1,N):
            for i in range(K): #marginalise over all possible previous states:
                ln_alpha_exp_z[n,:] = logaddexp(ln_alpha_exp_z[n,:], ln_alpha_exp_z[n-1,i] + exp_ln_a[i,:] + ln_obs_lik[n,:])
        return ln_alpha_exp_z 
    
    def _eBackwardsZ(self,exp_ln_pi,exp_ln_a,ln_obs_lik,N,K,parent_exp_z=None):
        ln_beta_exp_z = zeros((N,K)) - inf
        #final state distribution:
        ln_beta_exp_z[N-1,:] = zeros(K)
        for n in range(N-2,-1,-1):
            for j in range(K): #marginalise over all possible next states:
                ln_beta_exp_z[n,:] = logaddexp(ln_beta_exp_z[n,:], ln_beta_exp_z[n+1,j] + exp_ln_a[:,j] + ln_obs_lik[n+1,j])
        return ln_beta_exp_z
    
    def _eS(self,exp_ln_a, ln_alpha_exp_z, ln_beta_exp_z, ln_obs_lik, N, K, parent_exp_z=None):
        ln_exp_s = zeros((N-1,K,K)) #we only care about the transitions, which is why the length of this var is (N-1)
        exp_s = zeros((N-1,K,K))
        for n in range(N-1):
            for i in range(K):
                ln_exp_s[n,i,:] = ln_alpha_exp_z[n,i] + ln_beta_exp_z[n+1,:] + ln_obs_lik[n+1,:]  + exp_ln_a[i,:]
            ln_exp_s[n,:,:] -= ln_exp_s[n,:,:].max()
            exp_s[n,:,:] = exp(ln_exp_s[n,:,:]) / exp(ln_exp_s[n,:,:]).sum()
        return exp_s
    