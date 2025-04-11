from setuptools import setup, find_packages

# Read requirements and filter out lines starting with "-e"
with open("requirements.txt", "r") as f:
    requirements = [req for req in f.read().splitlines() if not req.startswith("-e")]

setup(
    name="mas",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
) 