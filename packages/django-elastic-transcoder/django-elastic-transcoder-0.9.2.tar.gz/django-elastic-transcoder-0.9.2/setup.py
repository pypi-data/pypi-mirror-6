from setuptools import setup, find_packages
from dj_elastictranscoder import __version__


setup(
    name='django-elastic-transcoder',
    version=__version__,
    description="Django with AWS elastic transcoder",
    long_description=open("README.rst").read(),
    author='tzangms',
    author_email='tzangms@streetvoice.com',
    url='http://github.com/StreetVoice/django-elastic-transcoder',
    license='MIT',
    test_suite='runtests.runtests',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        "django >= 1.4",
        "boto >= 2.5",
        "South >= 0.8",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
    keywords='django,aws,elastic,transcoder',
)
