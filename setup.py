import todo_summary

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


setup(
    name='TodoSummary',
    version=todo_summary.__version__,
    author="Ruoran Wang",
    author_email='dashuiwa@gmail.com',
    url='http://pypi.python.org/pypi/TodoSummary/',
    packages=['todo_summary', 'todo_summary.test'],
    scripts=['bin/todo_summary.py'],
    license=open('LICENSE.txt').read(),
    description='TodoSummary simply combines todo and summary.',
    long_description=open('README.txt').read(),
    install_requires=[
      'urwid >= 1.1.1'
    ],
)
