""" ncsdaemon setup script """

from distutils.core import setup

setup(
    name='ncsdaemon',
    version='0.01a',
    url='http://github.com/braincomputationlab/ncs-daemon',
    license='MIT',
    author='Nathan Jordan',
    author_email='natedagreat27274@gmail.com',
    description='A service running on a master node that allows clients to interact with the NCS brain simulator using a restful API',
    long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read(),
    packages=['ncsdaemon'],
    scripts=['scripts/ncsdaemon.py'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
