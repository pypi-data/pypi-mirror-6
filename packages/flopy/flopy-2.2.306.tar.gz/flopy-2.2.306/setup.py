from distutils.core import setup

# To use:
#	   python setup.py bdist --format=wininst

setup(name='flopy',
      version='2.2.306',
      description='FloPy is a Python package to create, run, and post-process MODFLOW-based models.',
      long_description='FloPy includes support for MODFLOW-2000, MODFLOW-2005, and MODFLOW-NWT. Other supported MODFLOW-based models include MT3D and SEAWAT.',
      author='Mark Bakker, Vincent Post, Chris Langevin, Joe Hughes, Jeremy White, and Alain Frances',
      author_email='mark.bakker@tudelft.nl, vincent.post@flinders.edu.au, langevin@usgs.gov, jdhughes@usgs.gov, jwhite@usgs.gov, frances.alain@gmail.com',
      url='https://code.google.com/p/flopy/',
      license='New BSD',
      platforms='Windows, Mac OS-X',
      packages=['flopy','flopy.modflow','flopy.mt3dms','flopy.seawat','flopy.utils'],
     )
