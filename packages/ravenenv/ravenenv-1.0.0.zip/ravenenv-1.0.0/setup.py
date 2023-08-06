from setuptools import setup


raven_requires = [
    'raven>=4.0.0',
]

setup(
    name='ravenenv',
    version='1.0.0',
    author='Slawomir Boguslawski',
    author_email='sbbogus@gmail.com',
    url='http://github.com/cooklee/raven-env',
    description='raven-env is plugging for raven that allow add env variable to contex of a massage',
	py_modules =['ravenenv.processors','ravenenv.__init__'],
    extras_require={
        'raven': raven_requires,
    }, 
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.2',
    ],
)