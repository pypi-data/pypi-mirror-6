from distutils.core import setup

setup(
    name='AuthZ-Group',
    version='1.0',
    description='Group interface and implementations',
    packages=[ 'authz_group' ],
    install_requires=['Django'],
    author = "Patrick Michaud",
    author_email = "pmichaud@uw.edu",
    license = "Apache 2.0",
    keywords = "django groups authorization",
    url = "https://github.com/vegitron/authz_group/"
)
