from setuptools import setup, find_packages

setup(
    name="dach-vorabpauschale",
    version="2026.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dach-vorabpauschale=vorabpauschale_dach.cli:main",
        ],
    },
)
