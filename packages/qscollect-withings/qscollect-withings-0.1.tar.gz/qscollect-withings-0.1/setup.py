from setuptools import setup, find_packages

setup(
   name='qscollect-withings',
   version='0.1',
   namespace_packages=['qscollect', 'qscollect.collectors', 'qscollect.collectors.contrib'],
   packages = ['qscollect.collectors.contrib'],
   url='http://bitbucket.org/russellhay/qscollect-withings',
   author='Russell Hay',
   author_email='me@russellhay.com',
   description='A qscollect collector for WiThings Weight'
)
