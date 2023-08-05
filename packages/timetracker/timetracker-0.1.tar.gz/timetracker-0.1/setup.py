from distutils.core import setup

setup(
    name='timetracker',
    version='0.1',
    url='https://github.com/gardaud/timetracker',
    author='Guillaume Ardaud',
    author_email='gardaud@acm.org',
    description=('A minimalistic timetracker.'),
    license='MIT',
    packages=['timetracker'],
    package_data={},
    scripts=[
        'bin/timetracker'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
    ],
)