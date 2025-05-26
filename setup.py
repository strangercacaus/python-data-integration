from setuptools import setup, find_packages

setup(
    name="python-data-integration",
    version="0.1.0",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Keep existing dependencies
    ],
    entry_points={
        'console_scripts': [
            'data-integration=src.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['config/*.yaml'],
    },
    python_requires=">=3.10",
)