from setuptools import setup, find_packages

setup(
    name='self_stats',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'alabaster==0.7.16',
        'Babel==2.14.0',
        'blinker==1.7.0',
        'certifi==2024.2.2',
        'charset-normalizer==3.3.2',
        'click==8.1.7',
        'dash==2.16.1',
        'dash-bootstrap-components==1.6.0',
        'dash-core-components==2.0.0',
        'dash-html-components==2.0.0',
        'dash-table==5.0.0',
        'docutils==0.20.1',
        'Flask==3.0.3',
        'idna==3.7',
        'imagesize==1.4.1',
        'importlib_metadata==7.1.0',
        'itsdangerous==2.2.0',
        'Jinja2==3.1.3',
        'MarkupSafe==2.1.5',
        'mypy-extensions==1.0.0',
        'nest-asyncio==1.6.0',
        'numpy==1.26.4',
        'packaging==24.0',
        'pandas==2.2.2',
        'pathspec==0.12.1',
        'platformdirs==4.2.0',
        'plotly==5.21.0',
        'Pygments==2.17.2',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.1',
        'regex==2024.4.16',
        'retrying==1.3.4',
        'ruptures==1.1.9',
        'scipy==1.13.0',
        'six==1.16.0',
        'snowballstemmer==2.2.0',
        'soupsieve==2.5',
        'Sphinx==7.2.6',
        'sphinxcontrib-applehelp==1.0.8',
        'sphinxcontrib-devhelp==1.0.6',
        'sphinxcontrib-htmlhelp==2.0.5',
        'sphinxcontrib-jsmath==1.0.1',
        'sphinxcontrib-qthelp==1.0.7',
        'sphinxcontrib-serializinghtml==1.1.10',
        'tenacity==8.2.3',
        'tomli==2.0.1',
        'typing_extensions==4.11.0',
        'tzdata==2024.1',
        'tzlocal==5.2',
        'urllib3==2.2.1',
        'webencodings==0.5.1',
        'Werkzeug==3.0.2',
        'zipp==3.18.1',
    ],
    # Add additional metadata about your package
    author='Colton Robbins',
    author_email='coltonrobbins73@gmail.com',
    description='Process Google Takeout data and visualize it using Dash.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
