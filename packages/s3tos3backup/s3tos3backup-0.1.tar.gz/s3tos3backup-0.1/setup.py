import sys
from setuptools import setup, find_packages
from pkg_resources import require, DistributionNotFound

requirements = open('requirements.txt')
required_to_install = []
for dist in requirements.readlines():
    dist = dist.strip()
    try:
        require(dist)
    except DistributionNotFound:
        required_to_install.append(dist)

extra_kwargs = {'tests_require': ['mock>1.0']}
if sys.version_info < (2, 7):
    extra_kwargs['tests_require'].append('unittest2')

setup(
    name='s3tos3backup',
    version='0.1',
    url="https://github.com/YD-Technology/s3tos3backup",
    author='YD Technology',
    author_email="team@ydtechnology.com",
    description="S3 To S3 Backup",
    long_description=open('README.rst').read(),
    zip_safe=False,
    install_requires=required_to_install,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    license="MIT",
    entry_points={
        'console_scripts': [
            's3tos3backup = s3tos3backup.runner:main',
        ],
    },
    # test_suite="test_project.runtests.runtests",
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    **extra_kwargs
)
