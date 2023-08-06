from distutils.core import setup

setup(
    name='PyTam',
    author="Camilo A. Ospina A.",
    author_email='camilo.ospinaa@gmail.com',
    version='0.2.1',
    packages=['pytam',],
    license='MIT license',
    platforms=['Linux','Mac','Windows'],
    long_description=open('README.txt').read(),
    description="Python Tables Manager (PyTam) is a module that allows managing data as a DBMS in Tables.",
)
