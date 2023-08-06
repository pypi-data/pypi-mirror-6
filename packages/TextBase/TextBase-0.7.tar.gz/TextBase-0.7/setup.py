from distutils.core import setup

setup(name="TextBase",
      version="0.7",
      description="TextBase library to manipulate DBText style data files.",
      long_description=open('README.rst').read(),
      author="Etienne Posthumus",
      author_email="ep@epoz.org",
      url="https://github.com/epoz/textbase/",
      py_modules = ["textbase",],
      data_files=[('', ['README.rst'])]
      )
