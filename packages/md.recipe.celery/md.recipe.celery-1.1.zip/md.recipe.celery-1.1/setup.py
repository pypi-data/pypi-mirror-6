import os
from setuptools import setup, find_packages

version = '1.1'

setup(
    name='md.recipe.celery',
    version=version,
    description=
    "Buildout recipe for installing celery for use with Zope's" +
    " ZCA and configuring it using an ini file.",
    long_description=open("README.md").read() + "\n" +
    open(os.path.join("src", "md", "recipe", "celery", "README.md")).read()
    + "\n" +
    open('CHANGES.txt').read(),
    classifiers=[
        'Framework :: Buildout :: Recipe',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Remco Wendt',
    author_email='remco.wendt@gmail.com',
    url='https://github.com/minddistrict/md.recipe.celery',
    license='BSD',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    namespace_packages=['md'],
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg'],
    extras_require={
        'test': [
            'zope.testing',
            'z3c.recipe.scripts',
            'manuel']},
    entry_points={
        'zc.buildout': ['default = md.recipe.celery:Recipe']})
