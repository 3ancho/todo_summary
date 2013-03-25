import todo_summary

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


setup(
    name='todo_summary',
    version=todo_summary.__version__,
    author="Ruoran Wang",
    author_email='dashuiwa@gmail.com',
    url='http://pypi.python.org/pypi/todo_summary/',
    packages=['todo_summary', 'todo_summary.test'],
    scripts=['bin/tosu'],
    license=open('LICENSE.txt').read(),
    description='todo_summary simply combines todo and summary.',
    long_description=open('README.txt').read(),
    install_requires=[
      'urwid >= 1.1.1'
    ],
)
