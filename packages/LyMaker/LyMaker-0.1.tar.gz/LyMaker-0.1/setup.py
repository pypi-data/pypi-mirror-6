from distutils.core import setup
setup(name='LyMaker',
      version='0.1',
      description='Lilypond source file generator',
      long_description='LyMaker is a program which was designed to generate Lilypond source files. It can generate basslines, harmonies and drumlines.',	
      author='Acoustic E',
      author_email='mondlichtgestalt@gmail.com',
      py_modules = ['LyMaker','xmlreader'],
      )
