import setuptools

setuptools.setup(
    name='python-ridc',
    version='0.1',
    description='Python connector for Ridc',
    author='Rob Britton',
    author_email='rob@robbritton.com',
    keywords=[],
    packages=['ridc'],
    package_dir={"ridc": "ridc"},
    install_requires=[],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Database Engines/Servers"
    ],
    long_description="""\
    Python connector for Ridc.
""",
)
