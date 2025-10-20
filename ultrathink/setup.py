from setuptools import setup, find_packages

setup(
    name="ultrathink",
    version="0.1.0",
    description="ADHD-friendly AI-powered task management for TickTick",
    author="Ultrathink",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "sqlalchemy>=2.0.23",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.1",
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "requests>=2.31.0",
        "oauthlib>=3.2.2",
        "requests-oauthlib>=1.3.1",
        "openai>=1.3.7",
        "python-dateutil>=2.8.2",
        "inquirer>=3.1.4",
    ],
    entry_points={
        "console_scripts": [
            "ultra=cli.main:app",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Scheduling",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
