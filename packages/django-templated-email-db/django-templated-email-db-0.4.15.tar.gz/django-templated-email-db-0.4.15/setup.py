from setuptools import setup

DESCRIPTION = "A Django oriented templated / transaction email abstraction"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='django-templated-email-db',
    version='0.4.15',
    packages=['templated_email', 'templated_email.backends', 'templated_email.backends.database'],
    include_package_data=True,
    author='Bradley Whittington',
    author_email='radbrad182@gmail.com',
    url='http://github.com/bradwhittington/django-templated-email/',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
)
