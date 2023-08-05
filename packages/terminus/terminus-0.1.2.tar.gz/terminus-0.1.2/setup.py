from setuptools import setup


setup(
    name='terminus',
    version='0.1.2',
    author='Brian Cline',
    author_email='brian.cline@gmail.com',
    description=('Updates interfaces file on Debian Linux-based distros'),
    long_description=open('README.md').read(),
    license='MIT',
    keywords='network interface interfaces file debian configuration',
    url='https://github.com/briancline/terminus',
    packages=['terminus'],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
