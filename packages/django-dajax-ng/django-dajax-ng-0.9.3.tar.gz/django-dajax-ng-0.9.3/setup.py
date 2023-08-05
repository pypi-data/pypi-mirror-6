from distutils.core import setup

setup(
    name='django-dajax-ng',
    version='0.9.3',
    author='Steffen Zieger',
    author_email='me@saz.sh',
    description=('Easy to use library to create asynchronous presentation '
                 'logic with django and dajaxice-ng'),
    url='https://github.com/saz/django-dajax',
    license='BSD',
    packages=['dajax'],
    package_data={'dajax': ['static/dajax/*']},
    long_description=('dajax is a powerful tool to easily and super-quickly '
                      'develop asynchronous presentation logic in web '
                      'applications using python and almost no JS code. It '
                      'supports up to four of the most popular JS frameworks: '
                      'jQuery, Prototype, Dojo and mootols.'
                      'This is the Next Gen dajax maintained by saz.'),
    install_requires=[
        'django-dajaxice-ng>=0.5.6.4'
    ],
    classifiers=['Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Utilities']
)
