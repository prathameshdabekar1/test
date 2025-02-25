import toml
print(f"Running Daily Maintenance v{toml.load(open('pyproject.toml'))['tool']['setuptools']['version']}")
