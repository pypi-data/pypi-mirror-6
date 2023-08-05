from distutils.core import setup

setup(
    name='colorscheme',
    version='0.2',
    url='https://github.com/gardaud/colorscheme',
    author='Guillaume Ardaud',
    author_email='gardaud@acm.org',
    description=('A basic terminal application that displays the active color palette'),
    license='MIT',
    packages=['colorscheme'],
    package_data={},
    scripts=[
        'bin/colorscheme'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Topic :: Artistic Software',
    ],
)
