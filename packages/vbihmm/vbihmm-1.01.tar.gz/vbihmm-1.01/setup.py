'''
Created on Feb 2, 2014

@author: root
'''


#from distutils.core import setup

from setuptools import setup

setup(name='vbihmm',
      version='1.01',
      author='James McInerney',
      author_email='contact@jamesmc.com',
      url='http://jamesmc.com/', #this field was required
      packages=['vb_ihmm','vb_ihmm.model', 'vb_ihmm.testing'],
      description=
"""Set of classes to support inference in mixture models and HMMs with Gaussian and multinomial observations.
""",
      install_requires=['numpy>=1.6.2',
                        '']
      )