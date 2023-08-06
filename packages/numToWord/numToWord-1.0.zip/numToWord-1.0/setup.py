from distutils.core import setup

setup(name="numToWord",
      version = '1.0',
      author = "Adam Smith",
      author_email = "uo.asmith@gmail.com",
      url = "https://github.com/NotTheEconomist/numToWord",
      description = "Spells numbers from numerals",
      long_description = "Changes strings containing wholly numbers to their spelled-out versions. Currently accepts numbers < one million (1,000,000)",
      py_modules = ['numToWord.py'])
      
