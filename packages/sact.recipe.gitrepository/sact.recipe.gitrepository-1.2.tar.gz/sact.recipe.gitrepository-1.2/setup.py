from setuptools import setup, find_packages

setup(
      name="sact.recipe.gitrepository",
      version="1.2",
      author="Sebastien Douche",
      author_email="sdouche@gmail.com",
      url="http://github.com/securactive/sact.recipe.gitrepository",
      description="Buildout recipe for fetching sources in a git repository",
      long_description=open("README.rst").read() + open("CHANGELOG.rst").read(),
      classifiers=(
          "Framework :: Buildout",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development",
          "Topic :: Software Development :: Pre-processors",
      ),
      keywords="zc.buildout recipe git",
      license="BSD",
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'':'src'},
      namespace_packages=("sact", "sact.recipe"),
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zc.recipe.egg',
      ],
      entry_points="""
        [zc.buildout]
        default = sact.recipe.gitrepository:Recipe
    """,
      )

