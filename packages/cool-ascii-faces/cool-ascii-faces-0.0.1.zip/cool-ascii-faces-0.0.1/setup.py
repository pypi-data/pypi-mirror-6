from setuptools import setup

setup(
    name='cool-ascii-faces',
    version='0.0.1',
    url='https://github.com/vape/cool-ascii-faces',
    license='MIT',
    author='Taylan Aydinli',
    author_email='taylanaydinli@gmail.com',
    description='get some cool ascii faces',
    packages=['coolasciifaces'],
    zip_safe=True,
    entry_points='''
    [console_scripts]
    caf = coolasciifaces.cli:main
    ''',
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)