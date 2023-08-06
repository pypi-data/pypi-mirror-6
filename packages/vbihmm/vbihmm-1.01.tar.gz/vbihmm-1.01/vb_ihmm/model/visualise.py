'''
@author: James McInerney
'''

#module to visualise the parameters of Sensor objects


from matplotlib.pyplot import *
from numpy import *
from testing.util import create_cov_ellipse
from util import inv0
from scipy import stats
import os


class Anim(object):
    def __init__(self, sensor, fig, axLabels=None, plotLim=None, ellipseColor='r', dataSelect=0, savePath=None, mu_grnd=None):
        self._sensor = sensor
        self._fig = fig
        self._savePath = savePath #savepath should specify somewhere an 'itr' integer parameter for substitution (e.g., /foo/bar/image_%(itr)i.png)
        self._mu_grnd = mu_grnd #provide option to also show ground truth params (usually for synthetic data)
        self._titleText = None
        self._sctX = None
        self._cumulativeX = None
        self._dataSelect = dataSelect
        self._N = 0 #previous data points already visualised
        self._plotLim = plotLim
        self._axLabels = axLabels
        self._graphMargin=0.1
    
    def update(self,itr,showThreshold):
        #only look at active components (ks):
        pl = self._plotLim
        if pl is None:
            mn,mx = findLim(self._cumulativeX, graphMargin=self._graphMargin)
            pl = zeros((2,2))
            pl[:,0], pl[:,1] = mn, mx
        self._ax_spatial.set_xlim(pl[0,0],pl[0,1])
        self._ax_spatial.set_ylim(pl[1,0],pl[1,1]) #-0.05,0.6)
        if self._axLabels is not None:
            self._ax_spatial.set_xlabel(self._axLabels[0])
            self._ax_spatial.set_ylabel(self._axLabels[1])
        if self._titleText is not None: self._ax_spatial.set_title(self._titleText)
        self._fig.canvas.draw()
        if self._savePath is not None: self._fig.savefig(self._savePath % {'itr':itr})

    def setTitleText(self,txt):
        self._titleText = txt


#2D animation:
class Anim2D(Anim):
    def __init__(self, sensor, plotLim=None, ellipseColor='r', dataSelect=arange(2), savePath=None, mu_grnd=None):
        ion()    
        fig = figure(figsize=(10,10))
        self._ax_spatial = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111
        self._circs = []
        self._ellipseColor = ellipseColor
        self._newPlot = 1
        Anim.__init__(self, sensor, fig, plotLim=plotLim, dataSelect=dataSelect, savePath=savePath, mu_grnd=mu_grnd)
    
    def update(self,itr,showThreshold):
        #only look at active components (ks):
        sensor = self._sensor
        X = sensor.X()[:,self._dataSelect]
        mu_grnd = self._mu_grnd
        (currentN,_) = shape(X) #update number of data points already visualised 
        if self._sctX is None: self._sctX = self._ax_spatial.scatter(X[:,0],X[:,1],marker='x',color='g') #plot only the new points added to X since last update (assumes already plotted data is constant)
        else: self._sctX.set_offsets(self._cumulativeX)
        self._N = currentN
        ks_all = sensor._NK
        K = len(ks_all)
        (ks,) = where(ks_all>showThreshold)
        if self._newPlot:
            self._sctZ = self._ax_spatial.scatter(sensor._m[:,0],sensor._m[:,1],color='r')
            if mu_grnd is not None:
                (K_grnd,_) = shape(mu_grnd)
                for k in range(K_grnd): 
                    print 'plotting',mu_grnd[k,0],mu_grnd[k,1]
                    self._ax_spatial.scatter(mu_grnd[k,0],mu_grnd[k,1],color='k',marker='d',s=50) #plot ground truth means
            self._newPlot = 0
        else:
            #ellipses to show covariance of components
            self._updateCovariances(showThreshold, sensor)
            hiddenOffsets = 99999*ones((K,len(self._dataSelect))) #hide non-significant components
            hiddenOffsets[ks,:] = sensor._m[ks,:][:,self._dataSelect]
            self._sctZ.set_offsets(hiddenOffsets)
        Anim.update(self, itr, showThreshold)
    
    def _updateCovariances(self,showThreshold, sensor):
        ks_all = sensor._NK
        for circ in self._circs: circ.remove()
        self._circs = []
        (ks,) = where(ks_all>showThreshold)
        for k in ks:
            sensor._m[k,:]
            #slice covariance matrix by the selected dimensions of the data:
            W = sensor.expC()
            C = W[k][self._dataSelect,:][:,self._dataSelect]
            #circ = create_cov_ellipse(0.1*sign(C)*sqrt(abs(C)), sensor._m[k,self._dataSelect],color=self._ellipseColor,alpha=0.1) #calculate params of ellipses (adapted from http://stackoverflow.com/questions/12301071/multidimensional-confidence-intervals)
            circ = create_cov_ellipse(C, sensor._m[k,self._dataSelect],color=self._ellipseColor,alpha=0.1) #calculate params of ellipses (adapted from http://stackoverflow.com/questions/12301071/multidimensional-confidence-intervals)
            self._circs.append(circ)
            #add to axes:
            self._ax_spatial.add_artist(circ)

#animation of covariances *per observation* (e.g., for reported accuracies)
class AnimReported(Anim2D):
    def _updateCovariances(self,showThreshold, sensor):
        for circ in self._circs: circ.remove()
        self._circs = []
        X = sensor._X
        (N,XDim) = shape(X)
        C = sensor.expC() #per-observation covariance
        assert shape(C)==(N,XDim,XDim)
        for n in range(N):
            #slice covariance matrix by the selected dimensions of the data:
            D = C[n,:,:][self._dataSelect,:][:,self._dataSelect]
            circ = create_cov_ellipse(D, X[n,self._dataSelect],color=self._ellipseColor,alpha=0.1) #calculate params of ellipses (adapted from http://stackoverflow.com/questions/12301071/multidimensional-confidence-intervals)
            self._circs.append(circ)
            #add to axes:
            self._ax_spatial.add_artist(circ)

#1D animation:
class Anim1D(Anim):
    def __init__(self, sensor, plotLim=None, ellipseColor='r', dataSelect=0, savePath=None, mu_grnd=None):
        self._sensor = sensor
        ion()    
        fig = figure(figsize=(10,10))
        self._ax_spatial = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111
        self._lines = []
        self._ellipseColor = ellipseColor
        self._savePath = savePath #savepath should specify somewhere an 'itr' integer parameter for substitution (e.g., /foo/bar/image_%(itr)i.png)
        self._mu_grnd = mu_grnd #provide option to also show ground truth params (usually for synthetic data)
        self._newPlot = 1
        self._titleText = None
        self._sctX = None
        self._cumulativeX = None
        self._N = 0 #previous data points already visualised
        self._dataSelect = dataSelect
        Anim.__init__(self, sensor, fig, plotLim=plotLim, dataSelect=dataSelect, savePath=savePath, mu_grnd=mu_grnd)

    
    def update(self,itr,showThreshold):
        #only look at active components (ks):
        sensor = self._sensor
        X = sensor.X()[:,self._dataSelect]
        mu_grnd = self._mu_grnd
        ds = self._dataSelect
        (currentN,) = shape(X) #update number of data points already visualised
        ks_all = sensor._NK
        K = len(ks_all) 
        (ks,) = where(ks_all>showThreshold)
        if self._sctX is None: self._sctX = self._ax_spatial.scatter(X,zeros(currentN),marker='x',color='g') #plot only the new points added to X since last update (assumes already plotted data is constant)
#        else:  #online stuff that we are not worrying about at the moment...
#            Nall = len(self._cumulativeX)
#            Xall = zeros((Nall,2))
#            Xall[:,0] = self._cumulativeX[:,ds]
#            self._sctX.set_offsets(Xall)
        self._N = currentN
        xs = arange(0,24,0.01)
        if self._newPlot:
            self._sctZ = self._ax_spatial.scatter(sensor._m[:,ds],zeros(K),color='r')
            if mu_grnd is not None:
                (K_grnd,_) = shape(mu_grnd)
                for k in range(K_grnd): self._ax_spatial.scatter(mu_grnd[k,ds],0,color='k',marker='d',s=50) #plot ground truth means
            self._newPlot = 0
            W = sensor.expC()
            for k in range(K):
                C = W[k][self._dataSelect]
                ys = stats.norm.pdf(xs,sensor._m[k,ds],C)
                p, = self._ax_spatial.plot(xs,ys,color='r')
                self._lines.append(p)
        else:
            for k in range(K):
                sensor._m[k,:]
                #slice covariance matrix by the selected dimensions of the data:
                W = sensor.expC()
                C = sqrt(W[k][self._dataSelect])
                if k in ks: ys = stats.norm.pdf(xs,sensor._m[k,ds],C)
                else: ys = inf+zeros(len(xs))
                self._lines[k].set_ydata(ys)
            mus = zeros((K,2))
            mus[:,0] = sensor._m[:,ds]
            self._sctZ.set_offsets(mus)
        Anim.update(self, itr, showThreshold)

#1D animation of an arbitrary line:
class AnimLine(Anim):
    def __init__(self, data, plotLim=None, savePath=None, lineColor='b', scatY=None, plotVert=None, labels=['','','']):
        self._data = data
        self._lineColor = lineColor
        ion()    
        fig = figure(figsize=(10,10))
        self._ax_spatial = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111
        self._lines = []
        self._savePath = savePath #savepath should specify somewhere an 'itr' integer parameter for substitution (e.g., /foo/bar/image_%(itr)i.png)
        self._newPlot = 1
        self._titleText = None
        self._N = 0 #previous data points already visualised
        self._scatY = scatY
        self._plotVert = plotVert
        self._labels = labels
        Anim.__init__(self, None, fig, plotLim=plotLim, savePath=savePath)

    
    def update(self,itr,showThreshold):
        xs,ys = self._data()[:,0], self._data()[:,1]
        if self._scatY: scatY = self._scatY() 
        if self._newPlot:
            if self._scatY is not None:
                self._scatAx = self._ax_spatial.scatter(scatY[:,0],scatY[:,1],marker='x',color='r',label=self._labels[2])
            if self._plotVert is not None:
                doneLbl = 0
                for xpoint in self._plotVert:
                    if xpoint>0: 
                        if not(doneLbl): 
                            self._ax_spatial.plot([xpoint, xpoint], [0,1], color='gray',label=self._labels[1])
                            doneLbl = 1
                        else: self._ax_spatial.plot([xpoint, xpoint], [0,1], color='gray') #, ls='--')
            self._newPlot = 0
            p, = self._ax_spatial.plot(xs,ys,color=self._lineColor,label=self._labels[0])
            self._lines.append(p)
        else:
            self._lines[0].set_ydata(ys)
            if self._scatY: self._scatAx.set_offsets(scatY)
        self._cumulativeX = array([[xs.min(), ys.min()],[xs.max(),ys.max()]])
        if any([l!='' for l in self._labels]): self._ax_spatial.legend() #loc='lower right') 
            
        Anim.update(self, itr, showThreshold)
        
#1D animation of arbitrary scatter data:
class AnimScatter(Anim):
    def __init__(self, data, targetArg, axLabels=None, plotLim=None, savePath=None, lineColor='b', scatY=None, plotVert=None, labels=['','','']):
        self._data = data
        self._targetArg = targetArg #used to select the data
        self._lineColor = lineColor
        ion()    
        fig = figure(figsize=(10,10))
        self._ax_spatial = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111
        self._ax_spatial.minorticks_on()
        self._lines = []
        self._savePath = savePath #savepath should specify somewhere an 'itr' integer parameter for substitution (e.g., /foo/bar/image_%(itr)i.png)
        self._newPlot = 1
        self._titleText = None
        self._N = 0 #previous data points already visualised
        self._scatY = scatY
        self._plotVert = plotVert
        self._labels = labels
        Anim.__init__(self, None, fig, plotLim=plotLim, savePath=savePath, axLabels=axLabels)

    
    def update(self,itr,showThreshold):
        xs,ys = self._data(self._targetArg)[:,0], self._data(self._targetArg)[:,1]
        if self._scatY: scatY = self._scatY() 
        if self._newPlot:
            if self._scatY is not None:
                self._scatAx = self._ax_spatial.scatter(scatY[:,0],scatY[:,1],marker='x',color='r',label=self._labels[2])
            if self._plotVert is not None:
                doneLbl = 0
                for xpoint in self._plotVert:
                    if xpoint>0: 
                        if not(doneLbl): 
                            self._ax_spatial.plot([xpoint, xpoint], [0,1], color='g',label=self._labels[1],marker='x')
                            doneLbl = 1
                        else: self._ax_spatial.plot([xpoint, xpoint], [0,1], color='gray') #, ls='--')
            self._newPlot = 0
            print 'xs',xs
            print 'ys',ys
            p = self._ax_spatial.scatter(xs,ys,color=self._lineColor,marker='x',label=self._labels[0])
            self._lines.append(p)
        else:
            self._lines[0].set_offsets(vstack((xs,ys)).T)
            if self._scatY: self._scatAx.set_offsets(scatY)
        self._cumulativeX = array([[xs.min(), ys.min()],[xs.max(),ys.max()]])
        if any([l!='' for l in self._labels]): self._ax_spatial.legend() #loc='lower right') 
            
        Anim.update(self, itr, showThreshold)

#2D animation:
class AnimBlocks(Anim):
    def __init__(self, sensor, slice=None, plotLim=None, savePath=None):
        ion()    
        fig = figure(figsize=(10,10))
        self._fig = fig
        self._ax_spatial = fig.add_subplot(1,1,1) #http://stackoverflow.com/questions/3584805/in-matplotlib-what-does-111-means-in-fig-add-subplot111
        self._newPlot = 1
        self._slice = slice
        self._rects = []
        self._graphMargin = 0.
        Anim.__init__(self, sensor, fig, plotLim=plotLim, dataSelect=None, savePath=savePath, mu_grnd=None)
    
    def update(self,itr,showThreshold):
        slice = self._slice
        if slice is not None:
            #then take a slice of the transition matrix (because it is higher than 2D)
            exp_a = self._sensor.expA()[:,:,slice] #expected state of block (N,M)
        else:
            exp_a = self._sensor.expA()[:,:]
        (N,M) = shape(exp_a)
        self._cumulativeX = array([[0,0],[N-1,M-1]]) #to make sure the limits of the figure are right
        if self._newPlot:
            #draw grid of size LxL:
            for j in range(N): #columns
                self._ax_spatial.plot([j,j],[0,N],color='gray',alpha=0.3)
            for i in range(M): #rows
                self._ax_spatial.plot([0,M],[i,i],color='gray',alpha=0.3)
            ax = self._ax_spatial
            for i in  range(N):
                self._rects.append([])
                for j in range(M):
                    #paint state of block:
                    rect = Rectangle((i,j),1,1,alpha=0.)
                    ax.add_patch(rect)
                    self._rects[-1].append(rect)
            self._newPlot = 0
        else:
            self._fig.gca().invert_yaxis() #transition matrix feels more natural going top to bottom
            #update: show beliefs about blocks in plot:
            K,ks = self._sensor.sigComponents(thres=showThreshold)
            #print 'exp_a:\n',exp_a
            for i in  range(N):
                for j in range(M):
                    #paint state of block:
                    if j in ks: self._rects[j][i].set_alpha(exp_a[i,j])
                    else: self._rects[j][i].set_alpha(0.) #not significant row, so paint it completely transparent:
                    
        Anim.update(self, itr, showThreshold)
        

#class to composite animations using more than one Anim object:
class AnimComposite(Anim):
    def __init__(self,animations,numRows=2,savePath=None,montageLoc='/opt/local/bin/montage'):
        self._animations = animations
        self._numRows = numRows
        self._savePath = savePath
        self._montageLoc = montageLoc
    
    def update(self,itr,showThreshold):
        #update all animations:
        [a.update(itr,showThreshold) for a in self._animations]
        if self._savePath is not None:
            #for those animations that have saved files, create a composite image with unix commands (not ideal, I know):
            plotNames = [a._savePath % {'itr':itr} for a in self._animations if a._savePath is not None]
            print 'plotNames',plotNames
            print 'composite path',self._savePath % {'itr':itr}
            fileStr = ' '.join(plotNames)
            numRows = self._numRows
            #os.system("su - jem1c10 -c 'montage -mode concatenate -tile x%i %s %s'" % (numRows,fileStr,self._savePath % {'itr':itr}))
            
            #uncomment this line:
            os.system("%s -mode concatenate -tile x%i %s %s" % (self._montageLoc, numRows,fileStr,self._savePath % {'itr':itr}))
            
            #finally, remove the individual images, leaving only the composite:
            [os.system('rm %s' % p) for p in plotNames]
            #if itr>0: [os.system('rm %s' % a._savePath % {'itr':itr-1}) for a in self._animations if a._savePath is not None]

