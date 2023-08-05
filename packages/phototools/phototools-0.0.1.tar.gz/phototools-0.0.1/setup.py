from distutils.core import setup

setup(
    name='phototools',
    version='0.0.1',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=[],
    scripts=['bin/printready'],
    include_package_data=True,
    package_data={
          'phototoos': ['profiles/*.icm'],
       },
    url='http://pypi.python.org/pypi/phototools/',
    license='LICENSE.txt',
    description='Process images into suitable jpegs for photo printing services.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
