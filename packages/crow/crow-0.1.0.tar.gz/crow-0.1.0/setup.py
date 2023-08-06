from setuptools import setup, find_packages

requires = [ "py-etcd>=0.1.0", "gipc>=0.4.0", "pyyaml>=3.10" ]

setup(name="crow",
      version="0.1.0",
      platforms='any',
      packages = find_packages(),
      include_package_data=True,
      install_requires=requires,
      author = "Bogdan Gaza",
      author_email = "bc.gaza@gmail.com",
      url = "https://github.com/hurrycane/crow",
      description = """Service ochestration based on etcd""",
      entry_points = {'console_scripts': [ 'crow-agent = crow.agent.runner:execute_from_cli' ]},
      test_requirements = [],
      classifiers = [
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Topic :: Database :: Front-Ends",
      ]
)
