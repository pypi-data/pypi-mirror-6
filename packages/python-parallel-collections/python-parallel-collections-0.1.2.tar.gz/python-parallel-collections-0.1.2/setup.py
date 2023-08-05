from distutils.core import setup
import parallel

setup(
    name='python-parallel-collections',
    data_files=[('', ['requirements.txt', 'README.md', '.gitignore']),],
    version='0.1.2',
    packages=['parallel',],
    description='parallel implementations of collections with support for map/reduce style operations',
    long_description=open('PYPIREADME.rst').read(),
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
        'Topic :: System :: Distributed Computing',
    ],
)