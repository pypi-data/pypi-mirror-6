from setuptools import setup

setup(
    name="txsyncml",
    version="0.0.1",
    url='http://github.com/smn/txsyncml',
    license='BSD',
    description="Twisted based SyncML 1.1 server.",
    long_description=open('README.rst', 'r').read(),
    author='Simon de Haan',
    author_email='simon@praekeltfoundation.org',
    packages=[
        "txsyncml",
        "twisted.plugins",
    ],
    package_data={
        'twisted.plugins': ['twisted/plugins/txsyncml_plugin.py'],
    },
    include_package_data=True,
    install_requires=[
        'Twisted'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Framework :: Twisted',
    ],
)
