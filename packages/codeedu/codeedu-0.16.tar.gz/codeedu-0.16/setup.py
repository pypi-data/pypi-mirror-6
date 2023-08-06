from setuptools import setup

setup(name='codeedu',
      version='0.16',
      description='a simple tool to pick a random github repo',
      url='https://github.com/jxieeducation/codeEDU',
      author='Jason Xie',
      author_email='jxieeducation@berkeley.edu',
      license='BST',
      install_requires=[
        'markdown',
      ],
      scripts=['bin/codeedu.py'],
      packages=['codeEDU'],
      zip_safe=False)

#thanks to http://www.scotttorborg.com/python-packaging/minimal.html