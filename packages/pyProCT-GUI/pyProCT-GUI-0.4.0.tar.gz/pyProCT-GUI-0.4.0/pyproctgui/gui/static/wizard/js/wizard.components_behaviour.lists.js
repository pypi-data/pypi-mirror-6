WIZARD.components_behaviour = (function(module){

	module.setup_trajectory_list = function (){
		//******************************
	 	// List of trajectories
	 	//******************************
        $("#trajectory_list").dynamiclist({height:150,buttons:["Add","Remove"]});
        var dl = $("#trajectory_list").dynamiclist("getListHandler");
        //dl.addElement('/home/victor/Desktop/test/1M94.pdb');
        //dl.addElement('/home/victor/Escritorio/test/ubi_9_clusters.pdb');
        dl.buttons["Add"].click(function(){
        	var callback = function(value){
        		var abs_path = COMM.synchronous.absolute_path(DIALOG.browsing.last_root); // TODO: Refactorizable 100% !!
	        	DIALOG.browsing.last_root = abs_path;
	        	abs_path = COMM.synchronous.absolute_path(value);
        		dl.addElement(abs_path);
            };
            DIALOG.browsing.browse("file::pdb", callback);
        });
        dl.buttons["Remove"].click(function(){
            dl.deleteSelectedElements();
        });
	}

	module.setup_algorithms_list = function (){
		//******************************
	 	// List of algorithms
	 	//******************************
        $("#algorithms_list").dynamiclist({height:160,buttons:["Algorithms","Add","Remove"]});
        var dl2 = $("#algorithms_list").dynamiclist("getListHandler");
        dl2.buttons["Algorithms"].replaceWith("<select class='dynListButton' id = 'algorithms_listbox'></select>")
     	// Add options to the cluster algorithms selection widget
       	$("#algorithms_listbox").append("<option id='all_option'>All</option>");
        for (clustering_algorithm in ALGORITHM.titles){
            var title = ALGORITHM.titles[clustering_algorithm];
            $("#algorithms_listbox").append("<option id='"+clustering_algorithm+"_option'>"+title+"</option>");
        }
        dl2.buttons["Add"].click(function(){
        	var algorithm = $("#algorithms_listbox option:selected").val();
        	if (algorithm != "All"){
        		dl2.addUniqueElement(algorithm);
        	}
        	else{
        		for (clustering_algorithm in ALGORITHM.titles){
        			if (clustering_algorithm!="random"){
        				dl2.addUniqueElement(ALGORITHM.titles[clustering_algorithm]);
        			}
        		}
        	}
        });
        dl2.buttons["Remove"].click(function(){
            dl2.deleteSelectedElements();
        });
	}

	module.setup_queries_list = function(){
		//******************************
		// List of queries
		//******************************
		$("#query_list").dynamiclist({height:160,buttons:["Queries","Add","Remove"]});
        var dl4 = $("#query_list").dynamiclist("getListHandler");
        dl4.buttons["Queries"].replaceWith("<select class='dynListButton' id = 'queries_listbox'></select>")
        // Add options to the query listbox
        for (var i = 0; i < QUERIES.query_types.length; i++){
            $("#queries_listbox").append("<option>"+QUERIES.query_types[i]+"</option>");
        }
        dl4.buttons["Add"].click(function(){
            dl4.addUniqueElement($("#queries_listbox option:selected").val());
        });
        dl4.buttons["Remove"].click(function(){
            dl4.deleteSelectedElements();
        });
	}

	var	dialog_contents_template = COMM.synchronous.load_text_resource("wizard/templates/dialog_contents.template");

	module.setup_criteria_list = function(){
		//******************************
		// List of criteria
		//******************************
		$("#criteria_list").dynamiclist({height:155,buttons:["Add Criteria","Remove"]});
        var dl3 = $("#criteria_list").dynamiclist("getListHandler");
        dl3.buttons["Add Criteria"].click(function(){
            DIALOG.criteria.criteria_creation(dl3, dialog_contents_template);
        });
        dl3.buttons["Remove"].click(function(){
            dl3.deleteSelectedElements();
        });
	}

	return module;

}(WIZARD.components_behaviour));