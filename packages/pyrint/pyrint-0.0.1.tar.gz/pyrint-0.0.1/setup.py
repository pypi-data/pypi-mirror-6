from setuptools import setup

version = '0.0.1'

setup(name='pyrint',
      version=version,
      description="POS print utility. Copyright 2014 BOS Sales, LLC",
      long_description="",
      classifiers=[],
      keywords='',
      author='@orderbliss',
      author_email='dev@orderbliss.com',
      url='http://github.com/orderbliss/pyrint',
      license='Copyright 2014 Order Bliss',
      packages=['pyrint'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points={'console_scripts': ['pyrint=pyrint:main']})
