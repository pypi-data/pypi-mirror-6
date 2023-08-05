from setuptools import setup

setup(
    name='nose-easy-init',
    version='1.0',
    packages=['nose_easy_init',],
    description='A plugin for nose to easily specify an initialization  script',
    url = 'https://github.com/sprin/nose-easy-init',
    author = 'sprin',
    author_email = 'sprin.pypi@fastmail.net',
    download_url = 'https://github.com/sprin/nose-easy-init/tarball/1.0',
    entry_points = {
        'nose.plugins.0.10': [
            'nose_easy_init = nose_easy_init:NoseEasyInit'
        ]
    },
)

