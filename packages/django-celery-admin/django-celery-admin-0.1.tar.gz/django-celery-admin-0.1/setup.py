from setuptools import setup, find_packages

setup(
    name='django-celery-admin',
    version='0.1',
    description='A django application that lets you kick off periodic celery tasks from the admin.',
    long_description=open('README.md').read(),
    author='Matt Caldwell',
    author_email='mcaldwel@ngs.org',
    url='http://github.com/mattcaldwell/django-celery-admin-ext',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
)
