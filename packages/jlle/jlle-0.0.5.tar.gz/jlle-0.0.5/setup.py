from setuptools import setup
import os

#here = os.path.abspath(os.path.dirname(__file__))
#with open(os.path.join(here, 'README.rst'), 'rt') as f:
#    README = f.read()

version = '0.0.5'

setup(name='jlle',
      version=version,
      author='José Luis Lafuente',
      author_email='jlesquembre@gmail.com',
      description='Utils to automate my process',
      #long_description=README,
      license='GNU General Public License v3 (GPLv3)',
      url='http://jlesquembre.github.io/termite/',
      packages=['jlle'],
      include_package_data=True,

      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        ],
      keywords=['automation', 'web'],
      entry_points = {
        'console_scripts': [
            'release = jlle.releaser.release:main',
            'jlcreate = jlle.scaffold.main:main'
          ],
        },
      install_requires=['pip-tools',
                        'Jinja2',
                       ]
    )
