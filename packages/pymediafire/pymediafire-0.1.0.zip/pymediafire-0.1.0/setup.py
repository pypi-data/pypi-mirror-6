from setuptools import setup

setup(name='pymediafire',
      version='0.1.0',
      py_modules=['pymediafire'],
      author='Stefan Champailler',
      author_email='schampailler@skynet.be',
      description='A basic module to access MediaFire\'s rest API',
      long_description=open('README.rst').read(),
      license='LICENSE.txt',
      url='https://pypi.python.org',
      classifiers = [ 
          'Intended Audience :: Developers',
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet'
      ],
      install_requires = ['lxml >= 2.3'],
)
