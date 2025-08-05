#!/usr/bin/env python3
"""
FastTTS Setup Configuration
Professional Python package setup for pip installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Get project root directory
project_root = Path(__file__).parent

# Read README.md for long description
readme_path = project_root / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Advanced Chinese Text-to-Speech with AI Vocabulary Learning"

# Read requirements.txt for dependencies
requirements_path = project_root / "requirements.txt"
install_requires = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                install_requires.append(line)

# Development dependencies
dev_requires = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]

# Optional dependencies for enhanced features
extras_require = {
    "dev": dev_requires,
    "mfa": [
        "montreal-forced-alignment>=3.2.0",
    ],
    "full": dev_requires + [
        "montreal-forced-alignment>=3.2.0",
        "docker>=6.0.0",
    ],
}

setup(
    name="fasttts",
    version="1.0.0",
    
    # Metadata
    author="CGAlei",
    author_email="serinoac@gmail.com",
    description="Advanced Chinese Text-to-Speech with AI Vocabulary Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CGAlei/FastTTS",
    project_urls={
        "Bug Reports": "https://github.com/CGAlei/FastTTS/issues",
        "Source": "https://github.com/CGAlei/FastTTS",
        "Documentation": "https://github.com/CGAlei/FastTTS/wiki",
        "Discussions": "https://github.com/CGAlei/FastTTS/discussions",
    },
    
    # License and classification
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Environment :: Web Environment",
    ],
    keywords="chinese, tts, text-to-speech, ai, vocabulary, learning, education, pronunciation",
    
    # Package configuration
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.10",
    install_requires=install_requires,
    extras_require=extras_require,
    
    # Package data
    include_package_data=True,
    package_data={
        "": [
            "static/css/*.css",
            "static/js/*.js",
            "templates/*.html",
            "*.yml",
            "*.yaml",
            "*.json",
        ],
    },
    
    # Entry points for command line interface
    entry_points={
        "console_scripts": [
            "fasttts=main:main",
            "fasttts-server=main:main",
        ],
    },
    
    # ZIP safety
    zip_safe=False,
)