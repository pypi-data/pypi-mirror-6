try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='python-guerrillamail',
    version='0.1.0',
    description='Client for the Guerrillamail temporary email server',
    author='Nathan Jones',
    url='https://github.com/ncjones/python-guerrillamail',
    py_modules=['guerrillamail'],
    requires=[
        'requests(==2.2.1)',
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
    ],
)
