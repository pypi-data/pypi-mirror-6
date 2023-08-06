from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="M_robot",
      version="0.38",
      description="2-D movement robot simulation",
      py_modules=['robot','funkcie','ez_setup','pohyb','rCBK2','robotCezBody3','robotCezBody4','robotCezBodySum','robotKruh','robotKruhsChybou','robotKruhsChybou_live','zapisDoSuboru'],
      long_description="""\
2-D Robot movement simulation created in matplotlib
""",
      author="Martin Bednar",
      author_email="martin.bednar@hotmail.sk",
      #packages=find_packages(exclude='tests'),
      #package_data={'mypackage': ['data/*.xml']},
      install_requires=['numpy>=1.7.1','matplotlib>=1.2.1','scipy>=0.12'],
      )