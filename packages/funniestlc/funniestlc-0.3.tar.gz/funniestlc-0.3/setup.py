from setuptools import setup

setup(name='funniestlc',
      version='0.3',
      description='The funniest joke in the world',
      url='https://bitbucket.org/leechau/pynote',
      author='Li Chao',
      author_email='leechau@126.com',
      license='MIT',
      packages=['funniest'],
      install_requires=[
          'markdown',
      ],
      entry_points={
          'console_scripts': ['funjoke=funniest.command_line:main'],
      },
      zip_safe=False)
