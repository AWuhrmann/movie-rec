from setuptools import setup, find_packages

setup(
    name="movie-recommender",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.4.2",
        "python-multipart==0.0.6",
    ],
)