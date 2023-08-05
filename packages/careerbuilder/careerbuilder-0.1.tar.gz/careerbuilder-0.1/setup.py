from distutils.core import setup

setup(
    name='careerbuilder',
    version='0.1',
    description='CareerBuilder API Wrapper for Python',
    author='JobDash.com',
    author_email='team@jobdash.com',
    packages=['careerbuilder'],
    install_requires=['requests==2.1.0', 'xmltodict==0.8.3'],
    url='https://github.com/neutroninteractive/careerbuilder-python.git',
)
