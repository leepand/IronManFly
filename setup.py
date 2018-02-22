from setuptools import setup, find_packages


setup(
  name = 'IronManFly',
  version = '0.2.1',
  description = 'A tool for creating a REST API for any machine learning model, in seconds.',
  author = 'leepand',
  author_email = 'hello@galiboo.com',
  url = 'https://github.com/leepand', # use the URL to the github repo
  py_modules=['IronManFly'],
  keywords = ['machine learning', 'python', 'rest', 'api', 'deep learning'],
  packages=find_packages(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python'
  ],

  install_requires=['requests','flask_profiler','flask','paste','importlib']
)