import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


description = (
    "security panel for pyramid_debugtoolbar (principals, context acl, "
    "view permission)"
)

setup(
    name='pyramid_debugtoolbar_security',
    version='0.1.0',
    description=description,
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",  #need write test and documentation
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        #"Programming Language :: Python :: 2",  #not tested yet.
        #"Programming Language :: Python :: 2.6",  #not tested yet.
        "Programming Language :: Python :: 2.7",
        #"Programming Language :: Python :: 3",  #not tested yet.
        #"Programming Language :: Python :: 3.3",  #not tested yet.
        #"Programming Language :: Python :: 3.4",  #not tested yet.
    ],
    author='shimizukawa',
    author_email='shimizukawa@gmail.com',
    url='https://bitbucket.org/shimizukawa/pyramid_debugtoolbar_security',
    license='Apache Software License',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyramid',
        'pyramid_debugtoolbar',
    ],
    zip_safe=False,
)
