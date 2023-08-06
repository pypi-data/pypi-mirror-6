from setuptools import setup

setup(name='geograpy',
      version='0.2.3',
      description='Extract place names and meta data from text or URLs',
      url='https://github.com/ushahidi/geograpy',
      download_url ='https://github.com/ushahidi/geograpy/tarball/0.2.3',
      author='Jonathon Morgan',
      author_email='jonathon@ushahidi.com',
      license='MIT',
      packages=['geograpy'],
      install_requires=[
            'numpy',
            'nltk',
            'newspaper',
            'jellyfish',
            'pycountry'
      ],
      scripts=['geograpy/bin/geograpy-nltk'],
      package_data = {
            'geograpy': ['data/*.csv'],
      },
      zip_safe=False)