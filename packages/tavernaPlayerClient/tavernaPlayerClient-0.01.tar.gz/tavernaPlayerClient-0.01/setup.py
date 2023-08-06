#  Taverna Player Client for running Taverna Workflows from IPython Notebook.
#-----------------------------------------------------------------------------
#  Copyright (c) 2014, University of Manchester <support@mygrid.org.uk>
#
# 

#!/usr/bin/env python


from distutils.core import setup

setup(name='tavernaPlayerClient',
      version='0.01',
      description='Taverna Player Client for running Taverna Workflows from IPython Notebook',
      author='Alan R. Williams',
      author_email='support@mygrid.org.uk',
      url='http://www.mygrid.org.uk',
      license = 'MIT',
#      platform = '',      
      packages=['tavernaPlayerClient'],
      py_modules=['tavernaPlayerClient.TavernaPlayerClient', 'tavernaPlayerClient.Workflow'],
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering",       
      ],
     )
