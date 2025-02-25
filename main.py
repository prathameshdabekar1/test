import requests
import toml

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'w') as f:  # Use 'w' instead of 'wb' for text files
        f.write(response.text)

def read_version_from_toml(filename):
    with open(filename, 'r') as f:
        data = toml.load(f)
        try:
            version = data['tool']['setuptools']['version']
            return version
        except KeyError:
            print("Version not specified in pyproject.toml.")
            return None

# Use the raw GitHub URL
url = "https://raw.githubusercontent.com/prathameshdabekar1/test/main/pyproject.toml"

# Download the file
download_file(url, 'pyproject.toml')

# Read and print the version
version = read_version_from_toml('pyproject.toml')
if version:
    print(f"Project version on Github: v{version}")
print(f"Running Daily Maintenance v{toml.load(open('version.toml'))['tool']['setuptools']['version']}")
