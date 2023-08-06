from setuptools import setup

setup(name='svccache',
      version='0.1',
      description='Python caching utilities',
      url='http://github.com/langloisjp/pysvccache',
      author='Jean-Philippe Langlois',
      author_email='jpl@jplanglois.com',
      license='MIT',
      py_modules=['httpcache', 'lrucache', 'memcachemap', 'dllist'],
      install_requires=['memcache', 'requests'],
      zip_safe=True)
