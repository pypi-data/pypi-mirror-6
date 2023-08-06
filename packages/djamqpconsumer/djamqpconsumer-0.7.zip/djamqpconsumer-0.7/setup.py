from setuptools import setup, find_packages

version = '0.7'

setup(name='djamqpconsumer',
      version=version,
      description="Blocking custom django command to consume a AMQP queue",
      long_description=open("README.rst").read() + "\n" +
                       open("HISTORY.txt").read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django amql pika',
      author='Aitzol Naberan',
      author_email='anaberan@gmail.com',
      url='http://github.com/codesyntax/djamqpconsumer',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pika',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
