'''
Created on 08/05/2013

@author: victor
'''
import os
import urllib

def browsing_connector(root_folder):
    print root_folder
    root_folder = root_folder.replace("%2F","/")
    r = ['<ul class="jqueryFileTree" style="display: none;">']
    r.append('<li class="directory collapsed"><a href="#" rel="%s/..">..</a></li>'%root_folder)
    try:
        d = urllib.unquote(root_folder)
        folders = []
        files = []
        for f in os.listdir(d):
            ff = os.path.join(d,f)
            # If it's not a hidden file
            if not f[0]==".":
                # If it is a folder
                if os.path.isdir(ff):
                    folders.append((f,ff))
                # If it is a file
                else:
                    e = os.path.splitext(f)[1][1:] # get .ext and remove dot
                    files.append((e,f,ff))

        for f,ff in sorted(folders):
            r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))

        for e,f,ff in sorted(files):
            r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))

        r.append('</ul>')
    except Exception,e:
        r.append('Could not load directory: %s' % str(e))
    r.append('</ul>')
    return ''.join(r)