# encoding: utf-8
import os.path
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


__version__ = None
with open(os.path.join('../python', 'src', 'pdef', 'version.py')) as f:
    exec(f.read())


setup(
    name='pdef-python',
    version=__version__,
    license='Apache License 2.0',
    description='Pdef python generator',
    long_description=open('README.md', 'r').read(),
    url='http://github.com/pdef/pdef-python',

    author='Ivan Korobkov',
    author_email='ivan.korobkov@gmail.com',

    packages=['pdef_python'],
    package_data={
        '': ['*.jinja2']
    },

    install_requires=[
        'pdef-compiler'
    ],
    entry_points={
        'pdefc.generators': [
            'python = pdef_python:PythonGenerator',
        ]
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
