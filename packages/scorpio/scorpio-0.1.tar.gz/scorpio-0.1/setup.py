from setuptools import setup

setup(
    name='scorpio',
    version='0.1',
    author='wangshuo',
    author_email='wangshuo@opstack.org',
    url='https://gitcafe.com/wangshuo/scorpio',
    packages=['scorpio'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'scorpio=scorpio.cli:main'
        ]
    },
)
