from distutils.core import setup

setup(
    name='DjangoLightbox',
    version='0.1.0',
    author='Geert Dekkers',
    author_email='geert@djangowebstudio.nl',
    packages=['lightbox', ],
    scripts=[],
    url='http://pypi.python.org/pypi/DjangoLightbox/',
    license='LICENSE.txt',
    description='alternative for a full screen javascript lightbox for the django framework',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.5",
    ],
)