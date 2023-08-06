from distutils.core import setup

requires = [
    'some_package_you_require',    
    'another_package_you_require',
]
classifiers=[
    "Programming Language :: Python",
    "Framework :: Pyramid",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
]
version='0.0.12'
name='pscriptslib'
setup(name=name,
      version=version,
      description='Library for pscripts',
      author='Fenton Travers',
      author_email='fenton.travers@gmail.com',
      url='http://www.python.org/pscripts-lib/', # url of project
      packages=[name],
      classifiers=classifiers
     )
