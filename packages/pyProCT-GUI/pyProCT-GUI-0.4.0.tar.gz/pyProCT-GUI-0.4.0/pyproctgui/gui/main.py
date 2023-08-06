'''
Created on 21/01/2013

@author: victor
'''


import os.path
import webbrowser
import SocketServer
import pyproctgui
from pyproctgui.gui.serverHandler import ServerHandler, IP, PORT
from pyproct.tools.scriptTools import create_directory
import shutil

if __name__ == '__main__':

    print "Installing at home folder...",
    home = os.path.expanduser("~")
    dst_folder = os.path.join(home,".pyproct-gui", "pyproctgui")
    if os.path.exists(os.path.join(home,".pyproct-gui")):
        shutil.rmtree(os.path.join(home,".pyproct-gui"), ignore_errors = False )
    create_directory(os.path.join(home,".pyproct-gui"))
    pyproctgui_dir = os.path.dirname(pyproctgui.__file__)
    shutil.copytree(pyproctgui_dir, dst_folder, ignore=shutil.ignore_patterns('*.pyc', '*~'))
    print "Done"

    os.system("pwd")
    os.chdir(os.path.join(dst_folder,"gui","static"))
    Handler = ServerHandler
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer((IP, PORT), Handler)
    webbrowser.open("http://"+IP+":"+str(PORT), new = 0, autoraise=True)
    print "Serving at port", PORT
    httpd.serve_forever()
