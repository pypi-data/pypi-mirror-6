'''
Created on 29/11/2013

@author", victor
'''
from setuptools import setup
#from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyProCT-GUI',
    version='0.4.0',
    description='A Graphical User Interface for pyProCT clustering toolkit.',
    author='Victor Alejandro Gil Sepulveda',
    author_email='victor.gil.sepulveda@gmail.com',
    url='https://github.com/victor-gil-sepulveda/pyProCT-GUI.git',
    packages=[
              'pyproctgui',
              'pyproctgui.gui'
    ],
    include_package_data = True,
    package_data={'': [
                                    "pyproctgui/gui/static",
                                    "pyproctgui/gui/static/results",
                                    "pyproctgui/gui/static/results/css",
                                    "pyproctgui/gui/static/results/css/jquery",
                                    "pyproctgui/gui/static/results/css/jquery/jqplot",
                                    "pyproctgui/gui/static/results/img",
                                    "pyproctgui/gui/static/results/js",
                                    "pyproctgui/gui/static/results/js/jquery",
                                    "pyproctgui/gui/static/results/js/jquery/jqplot",
                                    "pyproctgui/gui/static/results/js/jquery/jqplot/plugins",
                                    "pyproctgui/gui/static/results/js/jquery/ui",
                                    "pyproctgui/gui/static/results/js/threejs",
                                    "pyproctgui/gui/static/results/templates",
                                    "pyproctgui/gui/static/results/tmp",
                                    "pyproctgui/gui/static/wizard",
                                    "pyproctgui/gui/static/wizard/css",
                                    "pyproctgui/gui/static/wizard/css/libs",
                                    "pyproctgui/gui/static/wizard/css/libs/chemdoodle",
                                    "pyproctgui/gui/static/wizard/css/libs/smoothness",
                                    "pyproctgui/gui/static/wizard/css/libs/smoothness/images",
                                    "pyproctgui/gui/static/wizard/css/libs/ui",
                                    "pyproctgui/gui/static/wizard/img",
                                    "pyproctgui/gui/static/wizard/js",
                                    "pyproctgui/gui/static/wizard/js/definitions",
                                    "pyproctgui/gui/static/wizard/js/libs",
                                    "pyproctgui/gui/static/wizard/js/libs/chemdoodle",
                                    "pyproctgui/gui/static/wizard/js/libs/handlebars",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/center",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/filetree",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/filetree/images",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/ui",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/ui/dynamiclist",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/ui/selectmenu",
                                    "pyproctgui/gui/static/wizard/js/libs/jquery/wizard",
                                    "pyproctgui/gui/static/wizard/js/libs/markdown",
                                    "pyproctgui/gui/static/wizard/js/libs/spinjs",
                                    "pyproctgui/gui/static/wizard/js/libs/spinner",
                                    "pyproctgui/gui/static/wizard/scripts",
                                    "pyproctgui/gui/static/wizard/templates",
                                    "pyproctgui/gui/static/wizard/wizard.steps",
                                    "pyproctgui/gui/static/wizard/wizard.steps/help"
                                      ]},
    license = 'LICENSE.txt',
    long_description = read('README.rst'),
    #entrypoints for script
    install_requires=[
        "pyProCT>=1.0.0"
    ]
)
