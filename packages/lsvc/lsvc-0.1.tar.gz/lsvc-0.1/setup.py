from setuptools import setup

setup(name='lsvc',
      version='0.1',
      description='A simple JSON-REST list service',
      url='https://github.com/langloisjp/lsvc',
      author='Jean-Philippe Langlois',
      author_email='jpl@jplanglois.com',
      license='MIT',
      py_modules=['lsvc'],
      install_requires=['tornado', 'tornado-logging-app'],
      zip_safe=False)
