import itelsupply

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=itelsupply.__app_name__,
    version=itelsupply.__version__,
    description=itelsupply.__description__,
    author=itelsupply.__author__,
    author_email=itelsupply.__author_email__,
    packages=['itelsupply'],
    install_requires=['requests==2.0.1'],
    url=itelsupply.__app_url__,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'License :: Freeware',
    ),
    download_url=itelsupply.__download_url__,
)