var CLUSTERS = (function(){
	var clusters = [];
	var MAX_DIAMETER = 150;


	var create_main_cluster_widget = function(){
		var data = [];

		for (var i  = 0; i< clusters.length; i++){
			data.push([clusters[i]["id"],clusters[i]["elements"].length]);
		}

		$("#main_cluster_pie").jqplot([data],
		{
			seriesColors: [ "#000000","#111111","#222222","#333333","#444444","#555555","#666666",
			                "#777777","#888888","#999999","#AAAAAA","#BBBBBB","#CCCCCC","#DDDDDD",
			                "#EEEEEE","#DDDDDD","#CCCCCC","#BBBBBB","#AAAAAA","#999999","#888888",
			                "#777777","#666666","#555555","#444444","#333333","#222222","#111111"],
			seriesDefaults: {
			        renderer: $.jqplot.PieRenderer,
			        rendererOptions:
			        {
			          sliceMargin: 3,
			          showDataLabels: false,
			          diameter:200,
			          showDataLabels: true,

			        }
		    },
		    grid: {
		    	borderWidth: 0,
		    	shadow:false,
		    	background: '#ffffff',
		    }
		});
		$("#main_cluster_pie").find(".jqplot-data-label").css({"color":"#ffffff"});

		$("#main_cluster_pie").bind('jqplotDataClick',
	        function (event, seriesIndex, pointIndex, data) {
				var clustering_id = data[0];
				$("#"+clustering_id).effect( "pulsate",{times:5});
				//$(event.target).effect( "transfer", { className:"transfer-effect",to: $("#"+clustering_id) }, 3000 );
	        }
	    );

	};

	var create_cluster_widgets = function(){
		var max_number_elements = 0;

		for (var i  = 0; i< clusters.length; i++){
			if(clusters[i]["elements"].length > max_number_elements){
				max_number_elements = clusters[i]["elements"].length;
			}
		}

		$("[id^='cluster_']").each(function(){
			// Change css
			$(this).css({
				width:200,
				height:200,
				float:"left",
				"margin-bottom":50
			});

			var cluster_descriptor = null;
			for (var i  = 0; i< clusters.length; i++){
				if (clusters[i]["id"] === $(this).attr("id")){
					cluster_descriptor = clusters[i];
					break;
				}
			}

			var data = [["elements",100]];

			$(this).jqplot([data],
			{
				seriesColors: [ "#bbbbcf"],
				captureRightClick:true,
				seriesDefaults: {
				        renderer: $.jqplot.PieRenderer,
				        rendererOptions: {
		                    showDataLabels: false,
		                    diameter:MAX_DIAMETER * cluster_descriptor["elements"].length/max_number_elements
				        }
			    },
			    grid: {
			    	borderWidth: 0,
			    	shadow:false,
			    	background: '#ffffff',
			    }

			});

		});
	};

	var create_tab = function(data){
		// Process data
		process_cluster_data(data);

		// Templating stuff
		var clusters_template = COMM.synchronous.load_text_resource("results/templates/clusters.template");
		template = Handlebars.compile(clusters_template);
		$("#clusters-tab").html(template(data));

		// Fill with cluster widgets
		create_cluster_widgets();
		create_main_cluster_widget();

		// Prepare contextual menus
		$(document).contextmenu({
    	    delegate: ".hasmenu",
    	    menu: [
    	        {title: "View representative", cmd: "view", uiIcon: "ui-icon-search" },
    	        {title: "View all", cmd: "view_all", uiIcon: "ui-icon-search" },
    	        {title: "Save representative", cmd: "save", uiIcon: "ui-icon-disk"},
    	        {title: "Save all from cluster", cmd: "save_all", uiIcon: "ui-icon-disk"}
    	        ],
    	    select: function(event, ui) {
    	    	var menuId = ui.item.find(">a").attr("href");
    	    	if(menuId !== "#view_all"){
	    	        var cluster_id = $(event.relatedTarget).closest(".cluster_widget_wrapper").attr("id");
	    	        /*var number_id = parseInt(cluster_id.split("_")[1]);*/
	    	        var best_clustering = data["best_clustering"];
	    	        var clusters = data["selected"][best_clustering]["clustering"]["clusters"];
	    	        var selected_cluster = null;
	    	        // Find the cluster with that id
	    	        for(var i = 0; i < clusters.length; i++){
	    	        	if(clusters[i]["id"] === cluster_id){
	    	        		selected_cluster = clusters[i];
	    	        		break;
	    	        	}
	    	        }
	    	        if(menuId === "#save" || menuId === "#view"  ){
		    	        // Save the prototype
		    	        var file = COMM.synchronous.save_frame(selected_cluster["prototype"], data["workspace"]);

		    	        // And download or visualize it
		    	        if(menuId === "#save"){
		    	       		// Retrieve the file
		    	        	window.location.href = "/serve_file?path="+file+"&filename="+cluster_id+"_proto.pdb";
		    	        }

		    	        if(menuId === "#view"){
		    	        	// See the file
		    	        	var molecule = COMM.synchronous.load_text_resource(file);
		    	        	DIALOGS.show_molecule_dialog(molecule);
		    	        }

		    	    }

	    	        if(menuId === "#save_all"){
	    	        	// Save all cluster elements
		    	        // TODO: parse elements is redundant (it was first parsed at the begining, but this function does not use it)
		    	        var file = COMM.synchronous.save_cluster(parse_elements(selected_cluster["elements"]), data["workspace"]);

	    	        	// Retrieve the file
	    	        	window.location.href = "/serve_file?path="+file+"&filename="+cluster_id+"_all.pdb";
	    	        }
    	    	}
    	    	else{
    	    		preview_all_conformations(data);
    	    	}
    	    }
    	});
	};

	function parse_elements(elements_string){
		// Delete spaces
		var list_string = elements_string.replace(/[\s]+/g, '');
		var parts = list_string.split(",");
		var elements = [];
		for (var i = 0; i<parts.length; i++){
			if(parts[i].indexOf(":") != -1){
				var numbers = parts[i].split(":");
				for(var j = parseInt(numbers[0]); j<= parseInt(numbers[1]); j++){
					elements.push(j);
				}
			}
			else{
				elements.push(parseInt(parts[i]));
			}
		}
		return elements.sort();
	}

	function process_cluster_data(data){
		var best_clustering_clusters = data["selected"][data["best_clustering"]]["clustering"]["clusters"];
		for(var i = 0; i < best_clustering_clusters.length; i++){
			var elements = parse_elements(best_clustering_clusters[i]["elements"]);

			var cluster_data = {
				id: best_clustering_clusters[i].id,//  "cluster_"+i,
				centroid: best_clustering_clusters[i]["prototype"],
				elements: elements,
				number_of_elements: elements.length
			};
			CLUSTERS.clusters.push(cluster_data);
		}
		data["clusters"] = CLUSTERS.clusters;
	}

	function preview_all_conformations(data){
		var all_molecules = [];
		var all_ids = [];

		for (var i = 0; i < clusters.length; i++ ){
			var cluster_proto = clusters[i].centroid;
			console.log( clusters[i])
			var file = COMM.synchronous.save_frame(cluster_proto, data["workspace"]);
			all_molecules.push(COMM.synchronous.load_text_resource(file));
			all_ids.push(clusters[i].id);
		}

		DIALOGS.show_all_molecules_dialog(all_molecules, all_ids, "#spinner_preview");

	}

	return {
		clusters:clusters,
		create_cluster_widgets:create_cluster_widgets,
		create_main_cluster_widget:create_main_cluster_widget,
		create_tab:create_tab
	};
}());