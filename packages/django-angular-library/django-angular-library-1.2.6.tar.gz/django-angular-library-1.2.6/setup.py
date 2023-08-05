from os.path import join, dirname
from distutils.core import setup

try:
    f = open(join(dirname(__file__), 'README.md'))
    long_description = f.read().strip()
    f.close()
except IOError:
    long_description = None

setup(
    name='django-angular-library',
    version='1.2.6',
    url="https://github.com/IxDay/django-angular-library",
    description='Angular packaged in an handy django app to speed up new applications and deployment.',
    long_description=long_description,
    author='Maxime Vidori',
    author_email='maxime.vidori@gmail.com',
    license='MIT',
    keywords='django angular staticfiles'.split(),
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['angular'],
    package_data={'angular': ['static/js/*.js']},
)
