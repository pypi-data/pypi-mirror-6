from setuptools import setup

required_modules = []

setup(name='state_machine',
      version='0.2.1',
      description='Python State Machines for Humans',
      url='http://github.com/jtushman/state_machine',
      author='Jonathan Tushman',
      author_email='jonathan@zefr.com',
      install_requires=required_modules,
      license='MIT',
      packages=['state_machine'],
      zip_safe=False)