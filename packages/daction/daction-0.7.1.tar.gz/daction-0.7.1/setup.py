import os.path
import daction
from setuptools import setup, find_packages


here = os.path.dirname(__file__)

setup(
    name='daction',
    description='Performs custom action on all/specified elements in the directory.',
    version=daction.version,
    author='Ashot Seropian',
    author_email='ashot.seropyan@gmail.com',
    url='https://github.com/massanchik/daction',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='daction, action, directory, generate, path, command, pattern',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'daction=daction.main:main'
        ]
    }
)
