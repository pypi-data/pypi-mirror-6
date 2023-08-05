from setuptools import setup

setup(
    name='jinjer',
    version='0.2',
    packages=['jinjer'],
    package_dir={'': 'src'},
    url='https://github.com/andrematheus/jinjer',
    license='BSD',
    author='André Roque Matheus',
    author_email='amatheus@ligandoospontos.com.br',
    description='Tool to render Jinja templates from command line',
    install_requires=['docopt', 'jinja2', 'PyYaml'],
    entry_points={
        'console_scripts': [
            'jinjer = jinjer.jinjer:main'
        ]
    }
)
