import ast
import codecs
import os

from setuptools import setup, find_packages


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


setup(
    name="home",
    version=find_version("home", "__init__.py"),
    url='https://github.com/d0ugal/home',
    license='BSD',
    description="",
    long_description=read('README.rst'),
    author='Dougal Matthews',
    author_email='dougal@dougalmatthews.com',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        'alembic==0.6.3',
        'Flask-SQLAlchemy==1.0',
        'Flask==0.10.1',
        'psycopg2==2.5.2',
        'rfxcom==0.0.1',
        'simplejson==3.3.3',
        'SQLAlchemy==0.9.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'home-collect = home.collect:run',
            'home-report = home.report:run',
            'home-syncdb = home.util:syncdb',
            'home-dash = home.dash:run',
        ]
    },
    zip_safe=False,
)
