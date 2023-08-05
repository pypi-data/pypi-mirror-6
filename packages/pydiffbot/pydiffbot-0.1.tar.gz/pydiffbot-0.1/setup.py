import pydiffbot

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=pydiffbot.__app_name__,
    version=pydiffbot.__version__,
    description=pydiffbot.__description__,
    author=pydiffbot.__author__,
    author_email=pydiffbot.__author_email__,
    packages=['pydiffbot'],
    url=pydiffbot.__app_url__,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'License :: Freeware',
    ),
    download_url=pydiffbot.__download_url__,
)