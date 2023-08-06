"""
===============
django-redirect
===============

A slightly more robust version of the native django redirect

::

    pip install django-redirect

"""
import os
from distutils.core import setup

__version__ = "0.2"


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


EXCLUDE_FROM_PACKAGES = []


def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}


root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_dir = 'redirect'

# This and the code above was taken from https://github.com/django/django/blob/master/setup.py
for dirpath, dirnames, filenames in os.walk(django_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


setup(
    author = 'Glen Zangirolami',
    author_email = 'glenbot@gmail.com',
    maintainer = 'Glen Zangirolami',
    maintainer_email = 'glenbot@gmail.com',
    description = 'A slightly more robust version of the native django redirect',
    long_description = __doc__,
    fullname = 'django-redirect',
    name = 'django-redirect',
    url = 'https://github.com/glenbot/django-redirect',
    download_url = 'https://github.com/glenbot/django-redirect',
    version = __version__,
    platforms = ['Linux'],
    packages = packages,
    package_data = package_data,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License'
    ]
)
