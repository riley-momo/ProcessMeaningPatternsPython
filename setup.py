from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='ProcessMeaningPatternsPython',
    version='0.10',
    package_dir={'': 'ProMean4Py'},
    packages=find_packages(where='ProMean4Py'),
    description='An app to map event logs into ontology-based process knowledge and analyze the data through a library of knowledge patterns',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Riley Moher',
    author_email='riley.moher@mail.utoronto.ca',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: English'
    ],
    url='https://github.com/riley-momo/ProcessMeaningPatternsPython',
    install_requires=[
        'numpy',
        'pandas',
        'pm4py',
        'kglab',
        'yatter',
        'ruamel.yaml'
        ],
    extras_require={
        'dev' : ['twine>=4.0.2']
    },
    python_requires='>=3.9',  
)