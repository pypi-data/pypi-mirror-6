from distutils.core import setup
import parallel

setup(
    name='python-parallel-collections',
    data_files=[('', ['requirements.txt', 'README.md', '.gitignore']),],
    version='0.1.1',
    packages=['parallel',],
    description='parallel implementations of collections with support for map/reduce style operations',
    long_description='''In this package you'll find very simple parallel implementations of list and dict. 
    The parallelism is achieved using the Python 2.7 backport of the concurrent.futures package.
    If you can define your problem in terms of map/reduce/filter/flatten operations, it will run on several parallel Python processes on your machine, taking advantage of multiple cores. 
    Otherwise these datastructures are equivalent to the non-parallel ones found in the standard library.
    http://gterzian.github.io/Python-Parallel-Collections/''',
    author='Gregory Terzian',
    author_email='gregory.terzian@gmail.com',
    license='BSD License',
    url='https://github.com/gterzian/Python-Parallel-Collections',
    platforms=["any"],
    requires=['futures',],
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)