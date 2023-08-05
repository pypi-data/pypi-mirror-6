from setuptools import setup

version = "0.1.2"


setup(name="shorter",
      version=version,
      description="Robust url shorten service with zero config.",
      long_description=open("README.rst").read(),
      keywords="url short shorter flask",
      author="Lx Yu",
      author_email="i@lxyu.net",
      url="",
      license="MIT",
      py_modules=['shorter'],
      include_package_data=True,
      zip_safe=False,
      entry_points={"console_scripts": ["shorter = shorter:main"]},
      install_requires=[
          "Flask-SQLAlchemy>=1.0",
          "Flask>=0.10.1",
          "SQLAlchemy>=0.9.1"
      ],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
      ])
