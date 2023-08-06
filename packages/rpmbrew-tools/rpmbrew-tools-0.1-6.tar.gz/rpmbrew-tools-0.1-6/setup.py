import os
from setuptools import setup

setup(
    name = "rpmbrew-tools",
    version = "0.1-6",
    author = "Jason Viloria",
    author_email = "jnvilo@gmail.com",
    description = ("Some utility tools that helps in building rpms"),
    license = "BSD",
    keywords = "rpmbuild spec tar2rpm tar",
    url = "https://bitbucket.org/jnvilo/rpmbrew-tools",
    install_requires=["requests","docopt","beautifulsoup4","sh"],
    packages=['rpmbrew'],
    long_description="""Some utility tools used in building rpms. tar2rpm.""",
    entry_points={
        'console_scripts': [
            'rpmbrew = rpmbrew:main',
        ]
    },
 classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)

