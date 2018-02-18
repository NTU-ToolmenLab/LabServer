from setuptools import setup

setup(
    name='tzfserver',
    packages=['tzfserver'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-login',
        'flask-bcrypt',
    ],
)

