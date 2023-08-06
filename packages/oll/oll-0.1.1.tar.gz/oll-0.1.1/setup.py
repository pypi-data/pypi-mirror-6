# -*- coding: utf-8 -*-
from setuptools import setup, Extension, find_packages

oll_module = Extension('_oll',
                           sources=['lib/oll.cpp', 'oll_swig_wrap.cxx'],
                           include_dirs=['lib'],
                           depends=['lib/oll.hpp'],
                           language='c++'
                           )

setup (name = 'oll',
        version = '0.1.1',
        author      = "Yukino Ikegami",
        author_email='yukino0131@me.com',
        url='https://github.com/ikegami-yukino/madoka-python',
        description = """Online machine learning algorithms library (wrapper for OLL C++ library)""",
        long_description = open('README.rst').read() + "\n\n" + open('CHANGES.rst').read(),
        ext_modules = [oll_module],
        py_modules = ["oll"],
        headers=['lib/oll.hpp'],
        packages=find_packages(exclude=['test']),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Text Processing :: Linguistic'
            ],
        keywords = ['machine learning', 'online learning', 'perceptron', 'Passive Agressive', 'PA', 'ALMA', 'Confidence Weighted Linear-Classification'],
        )


