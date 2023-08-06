from setuptools import setup, find_packages

from pip.req import parse_requirements


version = '0.2.2'


setup(name="helga-isup",
      version=version,
      description=('Helga plugin to check down for everyone or just me'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Topic :: Communications :: Chat :: Internet Relay Chat',
          'Framework :: Twisted',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='helga isup down for everyone or just me',
      author='Shaun Duncan',
      author_email='shaun.duncan@gmail.com',
      url='https://github.com/shaunduncan/helga-isup',
      license='MIT',
      packages=find_packages(),
      py_modules=['helga_isup'],
      install_requires=[
          str(req.req) for req in parse_requirements('requirements.txt')
      ],
      entry_points = dict(
          helga_plugins=[
              'isup = helga_isup:isup'
          ],
      ),
)
