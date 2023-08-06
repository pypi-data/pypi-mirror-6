# -*- encoding: utf8 -*-
from setuptools import setup, find_packages

import os

setup(
    name="django-uwsgi-admin2",
    version="0.2.1",
    url='https://github.com/ionelmc/django-uwsgi-admin',
    download_url='',
    license='BSD',
    description="uWSGI monitoring page in django admin and debug_toolbar panel.",
    long_description=file(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    maintainer='Ionel Cristian Mărieș',
    maintainer_email='contact@ionelmc.ro',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'Django',
        'django-admin-utils>=0.1.2',
    ],
    extras_require={
        'uwsgi': ['uWSGI'],
    },
)
