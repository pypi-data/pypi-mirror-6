from distutils.core import setup

setup(
    name='django-dajaxice-ng',
    version='0.5.6',
    author='ifanr',
    author_email='tifan@ifanr.com',
    description='Agnostic and easy to use ajax library for django',
    url='http://dajaxproject.com',
    license='BSD',
    packages=['dajaxice',
              'dajaxice.templatetags',
              'dajaxice.core'],
    package_data={'dajaxice': ['templates/dajaxice/*']},
    long_description=("Easy to use AJAX library for django, all the "
                      "presentation logic resides outside the views and "
                      "doesn't require any JS Framework. Dajaxice uses the "
                      "unobtrusive standard-compliant (W3C) XMLHttpRequest "
                      "1.0 object.\n"
                      "This is the Next Gen dajaxice maintained by ifanrx."),
    install_requires=[
        'Django>=1.4'
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
