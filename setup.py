import todo_summary

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(
    name='todo-summary',
    version=todo_summary.__version__,
    author="Ruoran Wang",
    author_email='dashuiwa@gmail.com',
    url='http://pypi.python.org/pypi/todo-summary/',
    packages=['todo_summary', 'todo_summary.test'],
    package_data={'todo_summary': ['sound_effects/*.wav']},
    py_modules = ['todo_summary.todo'],
    scripts=['bin/tosu'],
    license=open('LICENSE.txt').read(),
    description='todo-summary simply combines todo and summary.',
    long_description=open('README.md').read(),
    install_requires=[
      'urwid >= 1.0.0',
      'pync >= 1.0'
    ],
)
