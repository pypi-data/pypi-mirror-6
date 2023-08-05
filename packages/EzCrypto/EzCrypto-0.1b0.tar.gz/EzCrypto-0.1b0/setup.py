import os
from setuptools import setup

from ezcrypto import get_version

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('ezcrypto'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[13:] # Strip "common/" or "common\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='EzCrypto',
      version=get_version().replace(' ', '-'),
      description='Easy to use wrapper around ryptographic libraries for Python',
      author='Antonio Ognio',
      author_email='antonio@ognio.com',
      url='http://github/gnrfan/EzCrypto/',
      package_dir={'ezcrypto': 'ezcrypto'},
      packages=packages,
      package_data={'ezcrypto': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: Unix',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Security :: Cryptography'],
      install_requires=['PyCrypto >=2.6'],
      )
