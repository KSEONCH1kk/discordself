"""Setup script for DiscordSelf library"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discordself",
    version="1.0.0",
    author="DiscordSelf",
    description="Полнофункциональная библиотека для Discord selfbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/discordself",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0,<4.0.0",
        "websockets>=10.0",
        "pynacl>=1.5.0",
        "opuslib>=3.0.0",
        "yt-dlp>=2023.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "voice": [
            "pynacl>=1.5.0",
            "opuslib>=3.0.0",
            "yt-dlp>=2023.0.0",
        ],
    },
)

