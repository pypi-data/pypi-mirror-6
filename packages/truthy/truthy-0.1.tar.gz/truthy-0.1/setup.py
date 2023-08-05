from setuptools import setup


setup(name='truthy',
      version='0.1',
      description='Small utility for parsing logic expressions and generating truth tables.',
      author='Michael Tom-Wing',
      author_email='mtomwing@gmail.com',
      url='https://github.com/mtomwing/truthy',
      packages=['truthy'],
      license='GPLv2',
      install_requires=['purplex', 'PrettyTable'],
      zip_safe=False)
