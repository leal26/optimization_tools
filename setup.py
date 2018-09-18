"""optimization_tools: tools to vizualize and calculate relevant metrics for opt."""

from setuptools import setup, find_packages

setup(name='optimization_tools',
      version='0.0',
      description='An easy to use optimization tool.',
      url='NA',
      author='leal26',
      author_email='leal26@tamu.edu',
      license='MIT',
      packages=['optimization_tools'],
      zip_safe=False,
          package_data={
        # If any package contains *.exe and avian files, include them:
        '': ['*.exe', 'avian'],
        # And include any *.exe files found in the 'CST' package, too:
        'CST': ['*.exe', 'avian'],
        # And include any *.exe files found in the 'geometry' package, too:
        'geometry': ['*.exe'],
        }
      )
