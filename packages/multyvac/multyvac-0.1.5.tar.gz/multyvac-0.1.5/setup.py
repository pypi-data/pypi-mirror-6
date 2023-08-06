from distutils.core import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = [str(ir.req) for ir in parse_requirements('requirements.txt')]

dist = setup(
    name='multyvac',
    version='0.1.5',
    description='Multyvac for Python',      
    author='Multyvac, Inc.',
    author_email='dev@multyvac.com',
    url='http://www.multyvac.com',
    install_requires=install_reqs,
    license='LICENSE.txt',
    packages=['multyvac', 'multyvac.util'],
    long_description=open('README.rst').read(),
    platforms=['CPython 2.6', 'CPython 2.7'],      
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        ],
)

