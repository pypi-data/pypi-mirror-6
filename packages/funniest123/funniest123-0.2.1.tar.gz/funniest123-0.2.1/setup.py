from setuptools import setup

setup(name='funniest123',
      version='0.2.1',
      description='The funniest joke in the world',
      url='https://github.com/nickytong/funniest123',
      author='nickytong',
      author_email='ptong1@mdanderson.org',
      license='MIT',
      packages=['funniest123'],
	  scripts=['bin/jokeByScript'],
	  entry_points = {
        'console_scripts': ['jokeByEntryPoint=funniest123.command_line:main'],
		},
      zip_safe=False)