from setuptools import setup


def deps():
    with open('requirements.txt') as f:
        return f.readlines()

setup(
    name='accessall',
    version='1.4',
    long_description=__doc__,
    packages=['accessall'],
    include_package_data=True,
    install_requires=deps(),
    author='Anthony Grimes',
    description='Google Music command line tool.',
    license='MIT',
    url='https://github.com/Raynes/accessall',
    entry_points={
        'console_scripts': [
            'accessall = accessall.__main__:main'
            ],
        }
)
