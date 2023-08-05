
from setuptools import setup, find_packages

REQUIREMENTS = (
    'django>=1.5',
)

setup(
    name="django-appengine-utils",
    version="0.0.1",
    author="Aaron Madison",
    description="Helpers for working with Django and Google App Engine.",
    long_description=open('README', 'r').read(),
    url="https://github.com/madisona/django-appengine-utils",
    packages=find_packages(exclude=["example"]),
    install_requires=REQUIREMENTS,
    zip_safe=False,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
