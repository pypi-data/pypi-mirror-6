from setuptools import setup

def readme():
    with open("README.md") as f:
        return f.read()

setup(name='pypresenter',
      version='0.1',
      description='Presentations from the CommandLine',
      long_description = readme(),
      keywords = 'presentation shell commandline',
      url='https://github.com/neshkatrapati/pypresenter',
      author='Ganesh Katrapati',
      author_email='ganesh@swecha.net',
      license='GNU GPL V3+',
      packages=['pypresenter'],
      install_requires = [
        'pyfiglet',
        'python-aalib',
        'colorama',
        'termcolor',
      ],
      scripts = ['bin/pypresenter'],
      include_package_data=True,
      zip_safe=False)
