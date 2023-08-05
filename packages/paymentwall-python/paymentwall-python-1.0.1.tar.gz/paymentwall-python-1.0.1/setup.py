import os
from distutils.core import setup

def read(fname):
    result = open(os.path.join(os.path.dirname(__file__), fname)).read()
    result = result.replace("source=gh-py", "source=pypi")
    return result

setup(
	name='paymentwall-python',
	version='1.0.1',
	packages=['paymentwall'],
	url='http://www.paymentwall.com',
	description='Paymentwall Python Library',
	long_description=read('README.md'),
	license='MIT',
	author='Paymentwall Team',
	author_email='devsupport@paymentwall.com'
)