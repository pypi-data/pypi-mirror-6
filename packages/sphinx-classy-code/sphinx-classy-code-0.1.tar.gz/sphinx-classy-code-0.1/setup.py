from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1'

install_requires = [
    'Sphinx',
]


setup(name='sphinx-classy-code',
    version=version,
    description="",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    keywords='',
    author='Nathan Yergler',
    author_email='nathan@yergler.net',
    url='https://github.com/nyergler/sphinx-classy-code',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    test_suite='classycode.tests',
    tests_require=[
        'six',
        'mock',
    ],
)
