from setuptools import setup

setup(name='distarkcli',
      version='0.2',
      description='Booya?',
      url='http://github.com/GustavePate/distarkcli',
      author='Gustave Pate',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['distarkcli',
                'distarkcli.utils',
                'distarkcli.protos',
                'distarkcli.protos.services',
                'distarkcli.protos.objects',
                'distarkcli.services',
                'distarkcli.transport'],
      zip_safe=False)
