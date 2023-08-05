from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'sitrep',
    version = '0.9.2',
    description = 'A console-based snapshot of Linux system resources',
    long_description = readme(),
    packages = ['sitrep'],
    scripts = ['bin/sitrep'],
    include_package_data = True,
    install_requires = ['netifaces', 'psutil', 'requests',],
    platforms = ['linux'],
    classifiers = [
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python :: 2.7',
      'Topic :: Utilities',
    ],
    url = 'http://github.com/vonbrownie/sitrep',
    author = 'Daniel Wayne Armstrong',
    author_email = 'daniel@circuidipity.com',
    license = 'GPLv2',
    zip_safe = False,
)

