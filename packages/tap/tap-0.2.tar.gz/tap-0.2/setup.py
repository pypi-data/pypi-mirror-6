from setuptools import setup

setup(
    name='tap',
    version='0.2',
    description='/dev/null as TAP consumer',
    author='Pavel Paulau',
    author_email='pavel.paulau@gmail.com',
    py_modules=['tap'],
    entry_points={
        'console_scripts': ['tap = tap:main']
    },
    install_requires=[
        'mc_bin_client',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
