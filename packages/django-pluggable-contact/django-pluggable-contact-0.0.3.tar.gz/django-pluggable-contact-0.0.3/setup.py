from distutils.core import setup

setup(
    name='django-pluggable-contact',
    version='0.0.3',
    packages=['contact', 'contact.migrations'],
    license='BSD',
    author='Branko Vukelic',
    author_email='branko@brankovukelic.com',
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
