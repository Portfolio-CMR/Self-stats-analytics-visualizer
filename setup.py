from setuptools import setup, find_packages

setup(
    name='self_stats',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        "pandas==2.2.2",
        "numpy==1.26.4",
        "ruptures==1.1.9",
        "regex==2024.4.16",
        "tzlocal==5.2",
        "tldextract==5.1.2",
        "spacy==3.7.4",
        "spacy-legacy==3.0.12",
        "spacy-loggers==1.0.5",
        "urllib3==2.2.1",
    ],
    # Add additional metadata about your package
    author='Colton Robbins',
    author_email='coltonrobbins73@gmail.com',
    description='Process Google Takeout data and visualize it using Dash.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
