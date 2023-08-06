from setuptools import find_packages, setup

with open("requirements/package.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

setup(name="keepass_http",
      version="0.3",
      description="Python Keepass HTTPD for ChromeIPass",
      long_description=long_description,
      author="Benjamin Hedrich",
      author_email="kiwisauce@pagenotfound.de",
      url="https://github.com/bhedrich/python-keepass-httpd/",
      package_dir={"": "src"},
      packages=find_packages("src/", exclude="tests"),
      install_requires=requirements,
      scripts=["bin/python-keepass-httpd"],
      include_package_data=True,
      zip_safe=False,
)
