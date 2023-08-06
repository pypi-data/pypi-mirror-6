from setuptools import setup

setup(
    name='bw2simple',
    version="0.1",
    packages=["bw2simple"],
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE.txt').read(),
    url="https://bitbucket.org/cmutel/brightway2-simple",
    install_requires=[
        "brightway2",
        "bw2calc>=0.13",
        "bw2data>=0.15.1",
        "bw2ui>=0.12.1",
    ],
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
