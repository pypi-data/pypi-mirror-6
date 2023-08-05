import os.path

from setuptools import setup, Command


long_description = ''
with open('README.rst') as f:
    long_description = f.read()


class PilboxTest(Command):
    user_options=[]
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call(
            [sys.executable, os.path.join('pilbox', 'test', 'runtests.py')])
        raise SystemExit(errno)


setup(name='pilbox',
      version='0.9.5',
      description='Pilbox is an image resizing application server built on the Tornado web framework using the Pillow Imaging Library',
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        ],
      url='https://github.com/agschwender/pilbox',
      author='Adam Gschwender',
      author_email='adam.gschwender@gmail.com',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      include_package_data=True,
      packages=['pilbox'],
      package_data={
        'pilbox': ['frontalface.xml'],
        },
      install_requires=[
        'tornado==3.1.1',
        'Pillow==2.2.1',
        ],
      zip_safe=True,
      cmdclass={'test': PilboxTest}
      )
