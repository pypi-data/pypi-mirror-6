from setuptools import setup, find_packages

setup(
   name='qscollect-withings',
   version='0.1.2',
   namespace_packages=['qscollect', 'qscollect.collectors', 'qscollect.collectors.contrib'],
   packages = ['qscollect.collectors.contrib'],
   url='http://bitbucket.org/russellhay/qscollect-withings',
   author='Russell Hay',
   author_email='me@russellhay.com',
   description='A qscollect collector for WiThings Weight',
   install_requires=[
       "qscollect>=1.1",
       "withings",
       "requests-oauthlib",
   ]
)
