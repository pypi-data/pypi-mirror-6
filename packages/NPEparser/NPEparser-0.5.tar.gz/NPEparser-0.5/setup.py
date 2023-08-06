from distutils.core import setup

packages=[
    'npeparser',
]
    
requiredPackages=[]

setup(
    name='NPEparser',
    version='0.5',
    author='Charles Fracchia',
    author_email='charlesfracchia@gmail.com',
    packages=packages,
    scripts=[],
    url='https://github.com/charlesfracchia/NPEparser',
    license='LICENSE',
    description='Python library for parsing, instantiating and converting biological protocols from Nature Protocol Exchange',
    requires=requiredPackages,
    provides=packages,
)
