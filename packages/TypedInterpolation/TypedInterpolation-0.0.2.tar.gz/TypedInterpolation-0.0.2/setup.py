from setuptools import setup


def get_readme():
    with open('./README.rst') as f:
        return f.read()

setup(
    name='TypedInterpolation',
    version='0.0.2',
    url='https://bitbucket.org/the_metalgamer/typedinterpolation',
    license='GPLv3+',
    author='Fink Dennis',
    author_email='dennis.fink@c3l.lu',
    descripts='Interpolations for configparser which uses ast.literal_eval.',
    long_description=get_readme(),
    py_modules=['typedinterpolation'],
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Topic :: Other/Nonlisted Topic',
    ],
    keywords='configparser interpolation typed',
)
