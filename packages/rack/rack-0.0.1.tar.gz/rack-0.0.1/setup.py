
from setuptools import setup

setup(name='rack',
      version='0.0.1',
      description='Minimal CLI for interacting with the rackspace cloud',
      url='https://github.com/thomseddon/rack',
      author='Thom Seddon',
      author_email='thom@seddonmedia.co.uk',
      license='MIT',
      packages=['rack'],
      scripts=['rack/rack'],
      zip_safe=False)
