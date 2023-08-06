from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

try:
    readme = open('README.md').read()
except IOError:
    readme = ''

install_requires = ['PyJWT == 0.1.9', 'requests == 2.2.1']

setup(
    name='livefyre',
    cmdclass={'build_py': build_py},
    version='1.1.3',
    description='Livefyre Python utility classes',
    long_description=readme,
    license='MIT',
    keywords='livefyre',
    author='Livefyre',
    author_email='tools@livefyre.com',
    url='http://livefyre.com/',
    packages=find_packages(),
    install_requires=install_requires,
    test_suite='livefyre.tests',
    use_2to3=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])