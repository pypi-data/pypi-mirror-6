from distutils.core import setup

setup(
    name='barify',
    version='0.1.6',
    url='https://github.com/gardaud/barify',
    author='Guillaume Ardaud',
    author_email='gardaud@acm.org',
    description=('generate text progress bar for given values'),
    license='MIT',
    packages=['barify'],
    package_data={},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
    ],
)
