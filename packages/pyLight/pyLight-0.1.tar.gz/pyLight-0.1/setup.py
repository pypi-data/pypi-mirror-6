
from distutils.core import setup

setup(name='pyLight',
      version='0.1',
      description='BSE enhancement tool',
      long_description='BSE enhancement tool. Simple tool for highlighting color bands in a greyscale image',
      author='Jake Ross',
      author_email='jirhiker@gmail.com',
      scripts=['pylight'],
      url='https://github.com/NMGRL/pylight',
      packages=['src'],
      package_data={'src':['icons/*.png']}
      )

