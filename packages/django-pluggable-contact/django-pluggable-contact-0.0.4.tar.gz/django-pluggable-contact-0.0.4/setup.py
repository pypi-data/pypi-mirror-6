from distutils.core import setup

setup(
    name='django-pluggable-contact',
    version='0.0.4',
    packages=['contact', 'contact.migrations'],
    package_data={
        '': ['templates/contact/*.html', 'templates/contact/email/*.html'],
    },
    license='BSD',
    author='Branko Vukelic',
    author_email='branko@brankovukelic.com',
    summary='Pluggable contact app for Django with support for in-DB inboxes and topic-based addressing',
    description=open('README.rst').read(),
    url='https://bitbucket.org/brankovukelic/django-pluggable-contact',
    download_url='https://bitbucket.org/brankovukelic/django-pluggable-contact/downloads',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ]
)
