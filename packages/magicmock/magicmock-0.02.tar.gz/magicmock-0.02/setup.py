from setuptools import setup


setup(
    name='magicmock',
    version='0.02',
    author='Mingze',
    author_email='mzxu@outlook.com',
    packages=['magicmock'],
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts' : [
            'magicmock = magicmock:main',
            'magicmocksetup = magicmock:setup'
        ]
    },
    license="MIT",
    url='https://github.com/mzxu/magicmock',
    install_requires=["httplib2"],
    description='A generic mock server',
    long_description="Fake http request and response",
    )
