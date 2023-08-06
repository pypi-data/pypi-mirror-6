from distutils.core import setup

setup(
    name='html2bbcode',
    version='2.1.0',
    packages=['html2bbcode'],
    url='https://bitbucket.org/amigo/html2bbcode',
    license='BSD',
    author='Vladimir Korsun',
    author_email='korsun.vladimir@gmail.com',
    description='HTML to BBCode converter',
    scripts = ['scripts/html2bbcode'],
    package_data = {'html2bbcode': ['data/defaults.conf']},
    classifiers= [
        'Topic :: Utilities',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
