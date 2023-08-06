'''
Created on 12/03/2014

@author: victor
'''
import SimpleHTTPServer
import urlparse
import json
import time
import shutil
import hashlib
from pyproctgui.gui.execution import ExecutionThread
from pyproctgui.gui.browsing import browsing_connector
from pyproctgui.gui.pdbSelection import get_pdb_selection
from pyproct.driver.observer.observer import Observer
from pyproct.tools.commonTools import convert_to_utf8
from pyproct.tools.scriptTools import create_directory
from pyproct.driver.parameters import ProtocolParameters
from pyproct.tools.pdbTools import grab_existing_frame_from_trajectory,\
    extract_frames_from_trajectory_sequentially, get_number_of_frames
import os
import webbrowser

IP = "127.0.0.1"
PORT = 8000

executor = None
ongoing_clustering = False

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    Very simple implementation of a Request handler that accepts both GET and POST requests.
    """

    def post_handlers(self):
        return {
                "/run": self.run_handler,
                "/run_update_status": self.run_update_status,
                "/save_params": self.save_params_handler,
                "/file_exists": self.file_exists_handler,
                "/create_directory": self.create_directory,
                "/browse_folder":self.browse_folder,
                "/do_selection":self.do_selection,
                "/stop_calculations":self.stop_calculations,
                "/show_results":self.show_results_handler,
                "/normalize_path":self.normalize_path_handler,
                "/read_external_file":self.read_external_file_handler,
                "/save_frame": self.save_frame_handler,
                "/save_cluster": self.save_cluster_handler
        }

    def get_handlers(self):
        return {
                "/serve_file": self.serve_file_handler,
        }

    #############
    ##  POST
    #############

    def do_selection(self,data):
        data = convert_to_utf8(json.loads(data))
        print data
        self.wfile.write(get_pdb_selection(data))

    def browse_folder(self, data):
        chunks = data.split("=")
        print "Browsing", chunks[1], data
        print browsing_connector(chunks[1])
        self.wfile.write(browsing_connector(chunks[1]))

    def file_exists_handler(self, data):
        data = convert_to_utf8(json.loads(data))
        print data
        self.wfile.write(json.dumps({"exists":os.path.exists(data['location']),
                                     "isfile":os.path.isfile(data['location']),
                                     "isdir":os.path.isdir(data['location'])}))

    def create_directory(self,data):
        data = convert_to_utf8(json.loads(data))
        print data
        try:
            success = create_directory(data['location'], ensure_writability = True)
            self.wfile.write(json.dumps({"done":success}))
        except:
            self.wfile.write(json.dumps({"done":False}))

    def run_handler(self, data):
        json_script = convert_to_utf8(json.loads(data))
        print json_script
        parameters = None
        try:
            parameters = ProtocolParameters(json_script)
        except ValueError:
            self.wfile.write(json.dumps({"exit_status":"Malformed json script."}))

        observer = Observer()

        global executor
        global ongoing_clustering

        if ongoing_clustering == False:
            executor = ExecutionThread(observer, parameters)
            executor.start()
            self.wfile.write("OK")
        else:
            self.wfile.write("KO")

    def run_update_status(self, data):
        global executor
        self.wfile.write(json.dumps(executor.status))

    def stop_calculations(self, data):
        global executor
        global ongoing_clustering
        if ongoing_clustering == True:
            executor.raiseExc(Exception)
            time.sleep(5)
            if executor.is_alive():
                self.wfile.write('KO')
            else:
                self.wfile.write('OK')

    def save_params_handler(self, data):
        data = convert_to_utf8(json.loads(data))
        create_directory("wizard/scripts")
        my_hash = hashlib.sha1()
        my_hash.update(str(time.time()))
        path = os.path.join("wizard","scripts",my_hash.hexdigest()[:10]+".ppc")
        script_handler = open(path,"w")
        script_handler.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': ')))
        script_handler.close()
        self.wfile.write('{"file_url":"'+path+'"}')

    def show_results_handler(self, data):
        try:
            data = convert_to_utf8(json.loads(data))
            print "show_results_handler", data
            create_directory("results/tmp")
            results = data["results"] if "results" in data else "results"
            results_path = os.path.join(data["base"],results,"results.json")
            shutil.copyfile(results_path,os.path.join("results","tmp","data.json"))
            webbrowser.open("http://"+IP+":"+str(PORT)+"/results.html", new = 0, autoraise=True)
            self.wfile.write("OK")
        except IOError:
            self.wfile.write("KO")

    def normalize_path_handler(self, data):
        data = convert_to_utf8(json.loads(data))
        print "DATA", data
        print "PATH", data["path"].replace("%2F","/")
        print "NORM PATH", os.path.abspath(data["path"].replace("%2F","/"))
        self.wfile.write('{"path":"'+os.path.abspath(data["path"].replace("%2F","/"))+'"}')

    def read_external_file_handler(self, data):
        data = convert_to_utf8(json.loads(data))
        print "DATA", data
        try:
            self.wfile.write("".join(open(data["path"],"r").readlines()))
        except:
            self.wfile.write('KO')

    def save_frame_handler(self, data):
        data = convert_to_utf8(json.loads(data))
#             print "DATA", data
        path = os.path.join(data["paths"]["results"], "representatives.pdb")

#             try:
#             print "PRIM PATH",path
        file_handler_in = open(path,"r")
        file_handler_out = open("results/tmp/prototype.pdb","w")
        grab_existing_frame_from_trajectory(file_handler_in, file_handler_out, data["frame"])
        file_handler_in.close()
        file_handler_out.close()
        self.wfile.write('{"path":"results/tmp/prototype.pdb"}')
#             except:
#                 self.wfile.write('KO')

    def save_cluster_handler(self, data):
        data = convert_to_utf8(json.loads(data))
#             print "DATA", data
        path = os.path.join(data["paths"]["tmp"], "tmp_merged_trajectory.pdb")

#             try:
#             print "PRIM PATH",path
        file_handler_in = open(path,"r")
        file_handler_out = open("results/tmp/cluster.pdb","w")
        extract_frames_from_trajectory_sequentially(file_handler_in,
                                                    get_number_of_frames(path),
                                                    file_handler_out,
                                                    data["elements"],
                                                    keep_header=True,
                                                    write_frame_number_instead_of_correlative_model_number=True)
        file_handler_in.close()
        file_handler_out.close()
        self.wfile.write('{"path":"results/tmp/cluster.pdb"}')


    def do_POST(self):
        fp= self.rfile
        data = fp.read(int(self.headers['Content-Length']))
        handle = self.post_handlers()[self.path]
        print "PATH (POST) ", self.path
        handle(data)

    #############
    ##  GET
    #############
    def serve_file_handler(self, query):
        path = query["path"][0]
        if "filename" in query.keys():
            filename = query["filename"][0]
        else:
            filename = os.path.basename(path)
        self.send_response(200)
        self.send_header('Content-type', "application/octet-stream")
        self.send_header('Cache-Control', "private")
        self.send_header('Content-Length', "%d"%os.path.getsize(path))
        self.send_header('Content-Disposition', "attachment; filename=%s"%filename)
        self.end_headers()
        lines = open(path,"r").readlines()
        for l in lines:
            self.wfile.write(l)


    def do_GET(self):
        parsedParams = urlparse.urlparse(self.path)
        queryParsed = urlparse.parse_qs(parsedParams.query)
        print "PATH (GET) *", self.path,"*",parsedParams.path,"*", parsedParams.query,"*", queryParsed
        if parsedParams.path in self.get_handlers().keys():
            handler = self.get_handlers()[parsedParams.path]
            handler(queryParsed)
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

