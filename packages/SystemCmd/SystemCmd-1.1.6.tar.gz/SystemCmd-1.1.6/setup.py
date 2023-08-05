from setuptools import setup, find_packages
import os

version = "1.1.6"
 

def read(fname):
    try:
      return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
      return ""
    
setup(name='SystemCmd',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://github.com/AndreaCensi/system_cmd',
      
      description="""My wrappers for subprocess.POpen""" ,
      long_description=read('README.rst'),
      keywords="",
      license="",
      
      classifiers=[
        'Development Status :: 4 - Beta',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        # 'Topic :: Software Development :: Quality Assurance',
        # 'Topic :: Software Development :: Documentation',
        # 'Topic :: Software Development :: Testing'
      ],

      version=version,
      download_url='http://github.com/AndreaCensi/system_cmd/tarball/%s' % version,
      
      entry_points={
        'console_scripts': [
       # 'comptests = comptests:main_comptests' 
        ]
      },
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[],
      tests_require=['nose'],
)

