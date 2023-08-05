__author__ = "jeff.revesz@buzzfeed.com (Jeff Revesz)"

try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='python-operative',
    version='0.1.1',
    packages=find_packages(),
    author='Jane Kelly & Jeff Revesz',
    author_email='jane.kelly@buzzfeed.com',
    description='A lightweight Python bridge to the Operative FTP flatfile system',
    test_suite='nose.collector',
    install_requires=[
        'nose<2.0.0',
        'pyftpdlib<2.0.0',
        'caliendo<3.0.0',
        'autopep8'
    ],
    url='http://github.com/buzzfeed/python-operative',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    keywords="api operative bridge",

)
