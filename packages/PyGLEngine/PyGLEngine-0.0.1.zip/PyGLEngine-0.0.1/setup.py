from setuptools import setup, find_packages

import PyGLEngine

setup( 
    name='PyGLEngine',
    version=PyGLEngine.__version__,
    author='Kyle Rockman',
    author_email='kyle.rockman@mac.com',
	install_requires=open('requirements.txt').read().splitlines(),
    packages = find_packages(),
    package_data = {
        # If any subfolder contains these extensions, include them:
        '': ['*.json',],
        },
    zip_safe=False,
    url='https://github.com/rocktavious/PyGLEngine',
    license=open('LICENSE.txt').read(),
    description='Python Based OpenGL Game Engine',
    long_description=open('README.txt').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing',
    ],
)