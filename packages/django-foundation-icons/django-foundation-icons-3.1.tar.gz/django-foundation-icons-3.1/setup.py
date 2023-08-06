from setuptools import setup

setup(
    name='django-foundation-icons',
    version='3.1',
    url='https://github.com/benbacardi/django-foundation-icons',
    description='Zurb Foundation Icons (http://zurb.com/playground/foundation-icon-fonts-3) static files packaged in a Django app.',
    author='Ben Cardy',
    author_email='benbacardi@gmail.com',
    license='MIT',
    keywords='django zurb foundation staticfiles icons'.split(),
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
    packages=['foundation_icons', ],
    include_package_data=True,
)
