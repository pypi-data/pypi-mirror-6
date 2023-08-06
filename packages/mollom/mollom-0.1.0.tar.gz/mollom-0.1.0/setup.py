try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='mollom',
  version='0.1.0',
  description='Mollom client library.',
  author='Huan Lai',
  author_email='huan.lai@acquia.com',
  url='https://github.com/Mollom/mollom_python',
  packages=['mollom'],
  install_requires=['requests-oauthlib'],
  license='MIT',
  classifiers=(
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7'
  )
)
