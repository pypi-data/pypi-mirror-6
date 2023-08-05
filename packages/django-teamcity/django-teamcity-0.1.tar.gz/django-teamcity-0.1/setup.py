from setuptools import setup, find_packages

setup(name='django-teamcity',
      version='0.1',
      platforms=["any"],
      description="send test result to TeamCity and provide Selenium support",
      keywords='unittest teamcity test jetbrains django',
      author='Anton Ermak',
      author_email='Rayman.k26@gmail.com',
      license='BSD',
      packages = find_packages(),
      url="https://bitbucket.org/raymank26/django-teamcity",
      install_requires=[
          "django<1.6",
          "django-discover-runner",
          "teamcity-messages",
      ]
      )
