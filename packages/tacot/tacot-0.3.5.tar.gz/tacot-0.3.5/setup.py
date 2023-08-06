import os, re, sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

v = open(os.path.join(here, 'src', 'tacot', '__init__.py'))
version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

if (len(sys.argv) > 1) and (sys.argv[1] in ('develop', 'install')):
    import pip
    pip.main(['install', '--no-clean', '-r', 'requirements.txt'])

setup(
    name='tacot',
    version=version,
    description="With Tacot generate easily your statics web sites",
    long_description=README + '\n\n' + NEWS,
    keywords='static generator web',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP'
    ],
    author='Stephane Klein',
    author_email='contact@stephane-klein.info',
    url='http://packages.python.org/tacot/',
    license='MIT License',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts':
            ['tacot=tacot:main']
    }
)
