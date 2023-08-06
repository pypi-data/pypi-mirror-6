from setuptools import setup, find_packages

setup(
    name = 'brownfox',
    version = '0.1',
    packages = find_packages(),

    scripts = ['brownfox.py'],

    author = 'introom',
    author_email = "i@introo.me",
    description = "The quick brown fox switches directories amazingly fast",
    keywords = "shell bookmark directory",
    classifiers = [
        'Topic :: Terminals',
        ]
)

