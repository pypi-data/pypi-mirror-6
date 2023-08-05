from setuptools import setup


def deps():
    with open('requirements.txt') as f:
        return f.readlines()

setup(
    name='accessall',
    version='1.2',
    long_description=__doc__,
    packages=['accessall'],
    include_package_data=True,
    install_requires=deps(),
    author='Anthony Grimes',
    description='Export library info from google music.',
    license='MIT',
    url='https://github.com/Raynes/accessall',
    entry_points={
        'console_scripts': [
            'accessall = accessall.__main__:main'
            ],
        }
)
