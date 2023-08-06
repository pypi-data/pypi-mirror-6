import os
from pip.index import PackageFinder
from pip.req import parse_requirements
from setuptools import setup, find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(root_dir, 'requirements', 'base.txt')

finder = PackageFinder([], [])
requirements = parse_requirements(requirements_path, finder)
install_requires = [str(r.req) for r in requirements]

from sbo_sphinx import __version__

version = '.'.join(str(n) for n in __version__)

setup(
    name="sbo-sphinx",
    version=version,
    author="Jeremy Bowman",
    author_email="jbowman@safaribooksonline.com",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
    description="Sphinx configuration and libraries for Safari Books Online documentation",
    url='http://github.com/safarijv/sbo-sphinx',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={
        'sbo_sphinx': [
            '_static/favicon.ico',
            '_static/safari_logo.png',
            'jsdoc-toolkit/*.jar',
            'jsdoc-toolkit/*.sh',
            'jsdoc-toolkit/*.txt',
            'jsdoc-toolkit/app/*.js',
            'jsdoc-toolkit/app/frame/*.js',
            'jsdoc-toolkit/app/handlers/*.js',
            'jsdoc-toolkit/app/handlers/XMLDOC/*.js',
            'jsdoc-toolkit/app/lib/*.js',
            'jsdoc-toolkit/app/lib/JSDOC/*.js',
            'jsdoc-toolkit/app/plugins/*.js',
            'jsdoc-toolkit/app/t/*.js',
            'jsdoc-toolkit/app/test/*.js',
            'jsdoc-toolkit/app/test/scripts/*.js',
            'jsdoc-toolkit/app/test/scripts/*.txt',
            'jsdoc-toolkit/conf/*.conf',
            'jsdoc-toolkit/java/*.xml',
            'jsdoc-toolkit/java/classes/*.jar',
            'jsdoc-toolkit/java/src/*.java',
            'jsdoc-toolkit/templates/jsdoc/*.tmpl',
            'jsdoc-toolkit/templates/jsdoc/static/*.css',
            'jsdoc-toolkit/templates/jsdoc/static/*.html',
            'jsdoc-toolkit-rst-template/*.properties',
            'jsdoc-toolkit-rst-template/*.xml',
            'jsdoc-toolkit-rst-template/templates/rst/*.tmpl',
            'jsdoc-toolkit-rst-template/templates/rst/*.js',
        ],
    },
    scripts=['validate_readme.py'],
    zip_safe=False,
    install_requires=install_requires,
)
