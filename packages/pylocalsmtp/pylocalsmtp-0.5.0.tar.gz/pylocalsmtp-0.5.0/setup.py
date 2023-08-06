from setuptools import setup, find_packages

DATA_FILES = [
    ('pylocalsmtp', ["LICENSE", "README.md"])
]

LONG_DESCRIPTION = "%s\n\n%s" % (open('README.md').read(), open('CHANGES.md').read())

setup(
    name='pylocalsmtp',
    version='0.5.0',
    description='Ouvre un mini serveur SMTP en local avec inbox dans une interface web.',
    long_description=LONG_DESCRIPTION,
    url='https://bitbucket.org/m_clement/pylocalsmtp/',
    license='MIT',
    author='Martyn CLEMENT',
    author_email='martyn.clement@gmail.com',
    packages=find_packages(),
    data_files=DATA_FILES,
    include_package_data=True,
    install_requires=[
        'peewee==2.2.2',
        'tornado==3.2',
        'wsgiref==0.1.2',
        'sockjs-tornado==1.0.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: French',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'pylocalsmtpd=pylocalsmtp.cmd:run',
        ],
    }
)
