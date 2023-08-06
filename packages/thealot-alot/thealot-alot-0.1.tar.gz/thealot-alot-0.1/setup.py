from setuptools import setup
setup(name='thealot-alot',
      version='0.1',
      author='Edvin "nCrazed" Malinovskis',
      author_email='edvin.malinovskis@gmail.com',
      url='https://github.com/nCrazed/AlotPlugin',
      packages=['thealot.plugins'],
      namespace_packages=['thealot'],
      install_requires=[
          'thealot',
          ]
      )
