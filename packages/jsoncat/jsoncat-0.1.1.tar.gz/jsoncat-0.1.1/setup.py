from setuptools import setup, find_packages

requires = []

setup(name="jsoncat",
      version="0.1.1",
      platforms='any',
      packages = find_packages(),
      include_package_data=True,
      install_requires=requires,
      author = "Bogdan Gaza",
      author_email = "bc.gaza@gmail.com",
      url = "https://github.com/hurrycane/jsoncat",
      description = """Simple way of print json files""",
      keywords = ['jsoncat', 'json', 'cat', 'print', 'pretty'],
      entry_points = {'console_scripts': [ 'jsoncat = jsoncat.runner:execute_from_cli' ]},
      test_requirements = [],
      classifiers = [
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Topic :: Database :: Front-Ends",
      ]
)
