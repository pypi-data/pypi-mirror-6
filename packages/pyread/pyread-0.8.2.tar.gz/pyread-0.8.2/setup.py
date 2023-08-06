from setuptools import setup

setup(name='pyread',
      version='0.8.2',
      description='Automatically guessing file properties and loading data.',
      url='https://www.linkedin.com/profile/view?id=190745232',
      author='Pascal van Kooten',
      author_email='kootenpv@gmail.com',
      license='GPL',
      packages=['pyread'],
      install_requires=[
          'numpy',
          'pandas'
      ],
      zip_safe=False)
