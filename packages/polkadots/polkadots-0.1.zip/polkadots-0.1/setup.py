from distutils.core import setup

VERSION = '0.1'

setup(
    name = 'polkadots',
    author = 'Christoph Lassner',
    author_email = 'Christoph.Lassner@googlemail.com',
    package_dir = {'polkadots': '.'},
    scripts=['polkadots.py'],
	requires=['traits', 'traitsui', 'PIL', 'numpy', 'pyside'],
    version = VERSION,
    license='MIT License',
)
