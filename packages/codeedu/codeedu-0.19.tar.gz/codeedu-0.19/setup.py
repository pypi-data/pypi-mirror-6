from setuptools import setup
import os

setup(name='codeedu',
      version='0.19',
      description='a simple tool to pick a random github repo',
      long_description = 'example input: codeEDU python',
      url='https://github.com/jxieeducation/codeEDU',
      author='Jason Xie',
      author_email='jxieeducation@berkeley.edu',
      license='BST',
      install_requires=[
        'splinter',
      ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
      ],
      entry_points = {
        'console_scripts': ['codeEDU=codeEDU.code_edu:command_line'],
      },
      keywords='github learn read code',
      packages=['codeEDU'],
      zip_safe=False)

#thanks to http://www.scotttorborg.com/python-packaging/minimal.html