from setuptools import setup, find_packages


setup(name="StackMan",
      description="Simple stack manager for developing websites for Python 3",
      version="0.1",
      packages=find_packages(),
      install_requires=['tornado>=3.0.0',
                        'gunicorn'],
      author='Colton J. Provias',
      author_email='cj@coltonprovias.com',
      url='http://github.com/ColtonProvias/stackman',
      include_package_data=True,
      zip_safe=True,
      entry_points="""
                   [console_scripts]
                   stackman = stackman.app:main
                   """)
