from setuptools import setup, find_packages

setup(
    name='assert_tools',
    url='http://mideo.github.io/assert_tools/',
    description='A Python Unit/Functional test library.',
    version='0.0.2',
    author='Mide Ojikutu',
    author_email='mide.ojikutu@gmail.com',
    packages=find_packages(),
    install_requires=['unittest2', 'requests', 'httplib2'],
    tests_require=["nose", 'mock', 'coverage', 'nosexcover'],
    classifiers=[
        'Topic :: Software Development :: Testing',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
    ],
    keywords=[
        'testing', 'python', 'rest', 'unit testing', 'functional testing']
)
