try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
readme_file = os.path.join(os.path.dirname(__file__),
                           'README')
long_description = open(readme_file).read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Framework :: Django',
    'License :: OSI Approved :: MIT License']


setup(name='django-gannett-polling',
      version='1.1.46',
      classifiers=classifiers,
      description='Django app for collecting and displaying surveys.',
      long_description=long_description,
      author='sparky',
      author_email='sparky.mockingbird@gmail.com',
      url='',
      packages=['crowdsourcing', 'crowdsourcing.templatetags'],
      license='MIT',
     )
