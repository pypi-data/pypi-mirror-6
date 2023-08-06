# chardet's setup.py
from setuptools import setup, find_packages


def get_requirements():
    lines = []
    for f in ["requirements.txt", "requirements-dashboard.txt"]:
        lines += [line.strip() for line in open(f).readlines() if not line.startswith("#")]
    return lines

setup(
    name="mrq",
    packages=find_packages(exclude=['tests']),
    version="0.0.1",
    description="Mongo Redis Queue",
    author="Pricing Assistant",
    license='MIT',
    author_email="contact@pricingassistant.com",
    url="http://github.com/pricingassistant/mrq",
    # download_url="http://chardet.feedparser.org/download/python3-chardet-1.0.1.tgz",
    keywords=["worker", "task", "distributed", "queue", "asynchronous"],
    platforms='any',
    entry_points={
        'console_scripts': [
            'mrq-worker = mrq.bin.mrq_worker:main',
            'mrq-run = mrq.bin.mrq_run:main',
            'mrq-dashboard = mrq.dashboard.app:main'
        ]
    },
    zip_safe=False,
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities"
    ],
    long_description=open("README.md").read()
)
