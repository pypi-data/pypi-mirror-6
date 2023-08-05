from setuptools import setup, find_packages

version = '0.1'

entry_points = [
    "polaris = polaris.cmd:main"
]

setup(name='polaris',
      version=version,
      description="Dashboard made easy.",
      long_description="",
      classifiers=[],
      keywords='data virtualization analysis dashboard',
      author='Lx Yu',
      author_email='i@lxyu.net',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      entry_points={"console_scripts": entry_points},
      install_requires=[
          "Flask-Login>=0.2.9",
          "Flask-OAuthlib>=0.4.2",
          "Flask-Principal>=0.4.0",
          "Flask-SQLAlchemy>=1.0",
          "Flask-WTF>=0.9.4",
          "Flask>=0.10.1",
          "SQLAlchemy>=0.9.0",
          "dogpile.cache>=0.5.3",
          "pandas>=0.12.0",
          "psycopg2>=2.5.1",
          "vincent>=0.4.1",
      ])
