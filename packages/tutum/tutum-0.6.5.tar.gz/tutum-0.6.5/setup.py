from setuptools import setup, find_packages

setup(
    name = "tutum",
    version = "0.6.5",
    packages = find_packages(),
    install_requires = ['python-tutum==0.6.4', 'requests>=2.2.1', 'six==1.6.1', 'tabulate==0.7.2', 'wsgiref==0.1.2'],
    entry_points={
        'console_scripts':
            ['tutum = tutumcli.tutum_cli:main']
        },
    author = "Tutum, Inc.",
    author_email = "info@tutum.co",
    description = "CLI for Tutum",
    license = "Apache v2",
    keywords = "tutum docker cli",
    url = "http://www.tutum.co/",
)