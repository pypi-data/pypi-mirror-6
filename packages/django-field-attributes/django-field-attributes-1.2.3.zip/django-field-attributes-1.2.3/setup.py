from distutils.core import setup

setup(
    name='django-field-attributes',
    version='1.2.3',
    packages=['django-field-attributes',
              'django-field-attributes.templatetags'],
    url='http://bitbucket.org/amigo/django-field-attributes',
    license='BSD',
    author='Vladimir Korsun',
    author_email='korsun.vladimir@gmail.com',
    description='Django form field attribute substitute and widget class checker',
    requires=['django (>=1.4)'],
    package_dir={
        'django-field-attributes': 'src',
    },
    package_data={
        'django-field-attributes': ['templates/*.html'],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
