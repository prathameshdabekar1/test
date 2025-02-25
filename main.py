import toml
print(toml.load(open('pyproject.toml'))['tool']['setuptools']['version'])
