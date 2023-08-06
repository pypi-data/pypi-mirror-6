from setuptools import setup
setup(name='thealot-excuse',
      version='0.1.2',
      author='Edvin "nCrazed" Malinovskis',
      author_email='edvin.malinovskis@gmail.com',
      url='https://github.com/nCrazed/ExcusePlugin',
      packages=['thealot.plugins'],
      namespace_packages=['thealot'],
      install_requires=[
          'thealot',
          'sqlalchemy',
          ]
      )
