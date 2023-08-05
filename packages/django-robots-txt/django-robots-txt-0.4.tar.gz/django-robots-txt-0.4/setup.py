try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "django-robots-txt",
    version = "0.4",
    author = "Nicolas Kuttler",
    author_email = "pypi@nicolaskuttler.com",
    description = "Simple robots.txt app for django",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/nkuttler/django-robots-txt",
    packages = ['robots_txt'],
    include_package_data = True,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    install_requires = [
        "Django >= 1.4",
    ],
    zip_safe = True,
)
