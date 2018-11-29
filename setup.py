from setuptools import setup

setup(name='scopuspep',
      version='0.0.1',
      description='.',
      url='https://github.com/PedroRegisPOAR/scopuspep',
      author='Pedro Osvaldo Alencar Regis',
      author_email='pedroalencarregis@hotmail.com',
      license='MIT',
      packages=['scopuspep'],
      install_requires=['pandas>=0.23.4', 'scopus>=0.10.0'],
      zip_safe=False)