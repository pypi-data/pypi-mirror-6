from setuptools import setup
from distutils.command.build_ext import build_ext
from distutils.extension import Extension
import glob

MADOKA_FILES = glob.glob('src/*.cc')
setup (
        name = 'madoka',
        version = '0.5',
        author = "Yukino Ikegami",
        author_email='yukinoik@icloud.com',
        url='https://github.com/ikegami-yukino/madoka-python',
        description = """Memory-efficient CountMin Sketch key-value structure (based on Madoka C++ library)""",
        long_description = open('README.rst').read() + "\n\n" + open('CHANGES.rst').read(),

        py_modules = ["madoka"],
        ext_modules = [
            Extension('_madoka',
            sources=['madoka_wrap.cxx'] + MADOKA_FILES,
            language = "c++"
            ),
        ],

        cmdclass = {'build_ext': build_ext },

        license = 'New BSD License',
        keywords = ['Count-Min Sketch', 'counter', 'word count'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Text Processing :: Linguistic',
            ],
        )

