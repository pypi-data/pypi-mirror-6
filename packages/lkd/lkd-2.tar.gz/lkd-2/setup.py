try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='lkd',
    version='2',
    packages=['lkd', 'tests'],
    author='Karan Goel',
    author_email='karan@goel.im',
    maintainer='Karan Goel',
    maintainer_email='karan@goel.im',
    url='http://www.goel.im/',
    license='MIT License',
    long_description='Python wrapper for lkd.to API.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
