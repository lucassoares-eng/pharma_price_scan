from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pharma-price-scanner",
    version="1.0.0",
    author="Pharma Price Scanner Team",
    author_email="contact@example.com",
    description="Sistema de busca de preços de medicamentos em diferentes farmácias usando web scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pharma_price_scan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "pharma-scanner=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*", "static/*"],
    },
    keywords="pharma, medicine, price, scraper, selenium, flask",
    project_urls={
        "Bug Reports": "https://github.com/your-username/pharma_price_scan/issues",
        "Source": "https://github.com/your-username/pharma_price_scan",
        "Documentation": "https://github.com/your-username/pharma_price_scan#readme",
    },
) 