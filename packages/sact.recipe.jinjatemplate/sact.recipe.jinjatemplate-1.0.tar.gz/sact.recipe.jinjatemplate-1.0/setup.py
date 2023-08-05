from setuptools import setup, find_packages

setup(
      name="sact.recipe.jinjatemplate",
      version="1.0",
      author="Sebastien Douche",
      author_email="sdouche@gmail.com",
      url="http://github.com/securactive/sact.recipe.jinjatemplate",
      description="Buildout recipe for making files out of Jinja2 templates",
      long_description=open("README.rst").read() + open("CHANGELOG.rst").read(),
      classifiers=(
          "Framework :: Buildout",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development",
          "Topic :: Software Development :: Code Generators",
          "Topic :: Software Development :: Pre-processors",
      ),
      keywords="zc.buildout recipe template Jinja2",
      license="BSD",
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'':'src'},
      namespace_packages=("sact", "sact.recipe"),
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zc.recipe.egg',
          'Jinja2',
      ],
      entry_points="""
        [zc.buildout]
        default = sact.recipe.jinjatemplate:Recipe
    """,
      )
