from setuptools import setup, find_packages

setup(
    name='imhotep_pep8',
    version='0.0.2',
    packages=find_packages(),
    url='https://github.com/justinabrahms/imhotep_pep8',
    license='MIT',
    author='Justin Abrahms',
    author_email='justin@abrah.ms',
    description='An imhotep plugin for pep8 validation',
    requires=['pep8'],
    entry_points={
        'imhotep_linters': [
            '.py = imhotep_pep8.plugin:Pep8Linter'
        ],
    },
)
