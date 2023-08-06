'''
Created on 6 Dec 2013

@author: James McInerney
'''

#implementation of continuous states

from numpy import *
from scipy.linalg import inv
from matplotlib.pyplot import *
from random import choice
from anim_particles.DrawParticles import KalmanAnim
import time
from util import logLikMVG
#from anim_particles.DrawParticles import KalmanAnim

class KalmanFilter(object):  
    def __init__(self,X,T,N,hyperparams=None,fixed=None):
        self._X = X #observations (N,XDim)
        self._T = T #corresponding time steps for each obs (must be increasing, but may have missing time steps)
        self._N = N #num of obs
        self._hyperparams = hyperparams
        self._fixed = fixed
        self._activated = 1
        self._weightObs = ones(N) #we can choose to discount certain observations with this parameter
    
    def loglik(self,LD):
        #calculate the total log likelihood for each time step t and each observation n (of which there are max LD each time step)
        X, T = self._X, self._T
        NT = T.max() - T.min() + 1
        ll = zeros((NT,LD))
        for t in range(NT):
            ns, = where(T==t) #look up observations for this time step (todo: could be made more efficient)
            for n in ns:
                x_n = self._X[n,:]
                if not(any(isnan(x_n))):
                    #print 'em',self.expMu()[t,:]
                    #print 'ec',self.expCov()[t,:,:]
                    ll0 = logLikMVG(x_n, self.expMu()[t,:], self.expCov()[t,:,:])
                    #print 'loglik x_n',ll0
                    ll[t,n % len(ns)] = ll0
        return ll
    
    def m(self):
        #maximise variational parameters to the latent states.
        
        fixed = self._fixed
        if fixed is None:
#            self._A = fixed['A'] #linear transition function
#            self._G = fixed['G'] #transition covariance
#            self._C = fixed['C'] #linear observation function
#            self._S = fixed['S'] #observation covariance
#            self._mu0 = fixed['mu0'] #initial location mean
#            self._V0 = fixed['V0'] #initial location covariance
            #calculate variational updates to params here:
            [s.m(self._exp_z) for s in self._sensors]
            
    def e(self):
        if self._activated: self._do_e()
        
    def _do_e(self):
        #find expected value of continuous latent variables:
        self._exp_mu, self._exp_V = self._forwardsZ(self._X) #TODO: EXTEND TO DEAL WITH MULTIPLE SENSORS
        #TODO: IMPLEMENT KALMAN SMOOTHER
    
    def expMu(self):
        return self._exp_mu
    
    def expCov(self):
        return self._exp_V
    
    def _forwardsZ(self, X):
        #Equations taken from Bishop, section 13.3.1:
        
        fixed = self._fixed 
        if fixed is not None:
            A = fixed['A'] #linear transition function
            G = fixed['G'] #transition covariance
            C = fixed['C'] #linear observation function
            S = fixed['S'] #observation covariance
            mu0 = fixed['mu0'] #initial location mean
            V0 = fixed['V0'] #initial location covariance
        else:
            raise Exception('Not implemented')

        N = self._N
        T = self._T #time steps of each obs (assume T[0] = 0)
        NT = max(T)+1
        (_,XDim) = shape(X) #assumes all XDim same for all X
        mu = zeros((NT,XDim)) #mean of position at each time step
        V =  zeros((NT,XDim,XDim)) #covariance matrix of estimated position at each time step
        #K = zeros((N,XDim,XDim)) #Kalman gain matrices for each time step
        #P = zeros((N,XDim,XDim))
        
        #step 1. initial position:
        #K[0,:,:] = dot(V0, dot(C.T, inv(dot(C,dot(V0,C.T)) + S)) )
        mu[0,:] = mu0 # + dot(K[0,:,:], X[0,:] - dot(C, mu0))
        V[0,:,:] = V0 # - dot(dot(K[0,:,:],C),V0)
        prevMu, prevV = mu[0,:], V[0,:,:]
        P_tm1 = V0
        
        #step 2. iterate over time steps:
        t = T[0] #time ticker 
        for n in range(N): #iterate over observations (which may have same or different time steps)
            #print 'x_n,t,n,weightObs',X[n,:],t,n,self._weightObs[n]
            while t<T[n]:
                #move prediction forward by required number of time steps (until we reach time of next obs):
                t += 1                
                mu[t,:] = dot(A, mu[t-1,:]) #predicted current position (based only on prev position)
                P_tm1 = dot(A, dot(V[t-1,:,:], A.T)) + G #predicted cov of current position (based only on prev position)
                V[t,:,:] = P_tm1
                prevMu, prevV = mu[t,:], V[t,:,:]
            #incorporate new obs: #careful about P_tm1 for initial step:
            if not(any(isnan(X[n,:]))):
                K_n = dot(prevV, dot(C.T, inv(dot(C, dot(prevV, C.T)) + S))) #Kalman gain matrix
                mu[t,:] = prevMu + self._weightObs[n]*dot(K_n, X[n,:] - dot(C, dot(A, prevMu)))
                V[t,:,:] = prevV - dot(dot(K_n,C), prevV)
                prevMu, prevV = mu[t,:], V[t,:,:]
                #P_tm1 = V[t,:,:] #predicted cov of current position (based only on prev position)
            
        return mu, V

def genKalman(NT=100, XDim=2, L=1, sparsity=0.5, fixObsCount=1e5):
    X = zeros((NT,XDim)) #ground truth positions
    Y = [] #(N,L,XDim) observations
    T = [] #time steps
    A = lambda z: z #transition function (Kalman assumes linear, but we allow for arbitrary functions here)
    C = lambda x: x #observation function (Kalman assumes linear, but we allow for arbitrary functions here)
    G = 1e0*eye(XDim) #transition covariance
    S = 1e-2*eye(XDim) #observation covariance
    mu0 = zeros(XDim) #init position
    V0 = eye(XDim) #covariance of init position 
    IO = 1 #initial obs
    
    #draw initial position:
    X[0,:] = random.multivariate_normal(mu0, V0)
    for n in range(IO):
        #draw first obs:
        Y.append(random.multivariate_normal(C(X[0,:]), S))
        T.append(0) #first time step always zero
    
    for n in range(1,NT):
        #decide new position:
        X[n,:] = random.multivariate_normal(A(X[n-1,:]), G)
        c=0
        while c<fixObsCount and random.uniform(0,1)>sparsity:
            #draw next observation:
            Y.append(random.multivariate_normal(A(X[n,:]), S))
            T.append(n)
            c+=1
            
    return X,array(Y),array(T)

def testKalman(NT=20,XDim=2):
    L = 10 #num of obs per time step (held constant, but doesn't have to be)
    X_grnd, Y, T = genKalman(NT=NT,XDim=XDim,L=L,sparsity=0.5) #,fixObsCount=1) #ground truth position and observations
    N = len(T) #num of obs    
    print 'shape(x_grnd)',shape(X_grnd)
    print 'shape(Y)',shape(Y)
    print 'shape(T)',shape(T)
#    figure(figsize=(15,10))
#    scatter(X_grnd[0,0], X_grnd[0,1], marker='D', color='g', label='initial position') #initial position (ground)
#    scatter(X_grnd[1:,0], X_grnd[1:,1], marker='o', label='actual positions') #positions (ground)
#    plot(X_grnd[:,0], X_grnd[:,1]) #, label='actual transitions') #transitions (ground)
#    scatter(Y[:,0], Y[:,1], marker='x', color='g', label='observations') #observed
    
    #now run Kalman filter:
    fixedParams = { 'A' : eye(XDim), #linear transition function
                   'G' : 1e0*eye(XDim), #transition covariance
                   'C' : eye(XDim), #linear observation function
                   'S' : 1e-1*eye(XDim), #observation covariance
                   'mu0' : zeros(XDim), #initial location mean
                   'V0' : 1e1*eye(XDim) #initial location covariance
                   }
    
    KF = KalmanFilter(Y,T,N,fixed=fixedParams)
    KF.e()
    
#    #plot results of Kalman:
#    X_inf = KF.expMu()
#    scatter(X_inf[:,0], X_inf[:,1], marker='o', color='r', label='inferred positions')
#    plot(X_inf[:,0], X_inf[:,1], color='r', ls='--') #, label='inferred transitions')
#    print 'X_inf',X_inf
#    print 'X_grnd',X_grnd
#    print 'Y obs',Y
#    print 'T',T
#    
#    legend()
#    show()

    appl = lambda xs, ind, fn: fn([fn(x[:,ind]) for x in xs])

    As = [X_grnd, Y] #, KF.expMu()]
    x_min,x_max = appl(As, 0, min), appl(As, 0, max)
    y_min,y_max = appl(As, 1, min), appl(As, 1, max)
    pl = array([[x_min,x_max],[y_min,y_max]])
    kf_anim = KalmanAnim(T, KF, Y, grnd=X_grnd, plotLim=pl,F=0.1)
    print 'T',T
    for t in range(NT):
        kf_anim.update()
        time.sleep(5.)

if __name__ == "__main__":
    testKalman()
    
    
    
