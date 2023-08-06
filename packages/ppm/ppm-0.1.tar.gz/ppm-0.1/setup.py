from setuptools import setup, find_packages

version = '0.1'

requirements=''
with open('requirements.txt') as f:
	requirements = f.read()

with open('README.txt') as file:
    long_description = file.read()

setup(name='ppm',
      version=version,
      url = 'https://github.com/predictix/ppm',
      description="project package manager, a tool for managing general project dependencies",
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='package manager',
      author='Amine Hajyoussef',
      author_email='hajyoussef.amine@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['registry', 'tests', 'repository']),
      install_requires = requirements,
      entry_points={
        'console_scripts': [
            'ppm=ppm.main:parseArguments',
        ],
      },
)
