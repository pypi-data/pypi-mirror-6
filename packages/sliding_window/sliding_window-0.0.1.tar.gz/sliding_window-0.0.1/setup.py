from distutils.core import setup

setup(name='sliding_window',
    maintainer='Thomas Levine',
    maintainer_email='_@thomaslevine.com',
    description='Move a window over an iterater (ngrams).',
    url='https://github.com/tlevine/sliding_window.git',
    classifiers=[
        'Intended Audience :: Developers',
    ],
    packages=['sliding_window'],
    install_requires = [],
    tests_require = ['nose'],
    version='0.0.1',
    license='CC-BY-SA'
)
