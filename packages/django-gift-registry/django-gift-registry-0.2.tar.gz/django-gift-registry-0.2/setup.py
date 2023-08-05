from setuptools import setup

setup(
    name='django-gift-registry',
    version='0.2',
    packages=['gift_registry'],
    include_package_data=True,
    license='Apache License, Version 2.0',
    description='A gift registry for a wedding or similar event.',
    long_description=open('README').read(),
    url='https://launchpad.net/django-gift-registry',
    author='Ben Sturmfels',
    author_email='ben@sturm.com.au',
    install_requires=[
        "Django >= 1.6",
        "PIL == 1.1.7",
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],

)
