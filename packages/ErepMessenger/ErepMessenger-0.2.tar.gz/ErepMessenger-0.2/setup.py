import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "ErepMessenger",
    version = "0.2",
    scripts = ['ez_setup.py', 'messenger.pyw','config.cfg'],
    install_requires = ['requests>=2.2.1', 'beautifulsoup4>=4.3.2'],

    # metadata for upload to PyPI
    author = "Mike Ontry",
    author_email = "mr.ontry@gmail.com",
    description = "App to send mass in game messages for Erepublik",
    license = "PSF",
    keywords = "erepublik mass messaging",
    url = "http://ereptools.tk",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
