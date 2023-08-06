# encoding: utf-8
import os.path
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


# Load the version.
__version__ = None
with open(os.path.join('src', 'pdefc', 'version.py')) as f:
    exec(f.read())


setup(
    name='pdef-compiler',
    version=__version__,
    license='Apache License 2.0',
    url='http://github.com/pdef/pdef',
    description='Pdef compiler',
    long_description=open('README.md', 'r').read(),

    author='Ivan Korobkov',
    author_email='ivan.korobkov@gmail.com',

    packages=['pdefc',
              'pdefc.lang'],
    package_dir={'': 'src'},
    package_data={
        '': ['*.jinja2']
    },

    install_requires=[
        'argparse',
        'jinja2>=2.7',
        'ply>=3.4',
        'PyYAML'
    ],

    tests_require=[
        'mock'
    ],

    entry_points={
        'console_scripts': ['pdefc = pdefc:main'],
        'pdefc.generators': []
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers'
    ]
)
