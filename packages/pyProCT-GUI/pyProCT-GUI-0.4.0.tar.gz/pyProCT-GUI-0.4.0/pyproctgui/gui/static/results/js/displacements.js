var DISPLACEMENTS = (function(){

	var create_tab = function(data){
		var all_files = data["files"];
		var displacements_path = "";
		var plot_main_options;
		var plot_main_and_clusters_options;
		var plot_cluster_options;
		var main_plot;
		var all_series = [];
		var series_labels = [];

		//Look for the CA distance file
		for(var i = 0; i< all_files.length; i++){
			if (all_files[i]["description"] == "Alpha Carbon mean square displacements"){
				displacements_path = all_files[i]["path"];
			}
		}

		if(displacements_path !== ""){
			// Add the tab
			$("<li><a href='#displacements-tab'>Displacements</a></li>").insertAfter("#clusters_tab");

			// handle data
			data["ca_displacements"] = JSON.parse(COMM.synchronous.load_external_text_resource(displacements_path));

			// Add contents
			var displacements_template = COMM.synchronous.load_text_resource("results/templates/displacements.template");
			template = Handlebars.compile(displacements_template);
			$("#displacements-tab").html(template(data));

			// Add plots
			plot_cluster_options = {
				axesDefaults: {
			        labelRenderer: $.jqplot.CanvasAxisLabelRenderer
			     },
				axes: {
					xaxis: {
						label: "Residue Number",
						pad: 0
					},
					yaxis: {
						label: "Rmsf",
						pad: 0
						}
					},
					cursor:{
						show: true,
						zoom:true,
						showTooltip:true
					},
					seriesDefaults:{
						 lineWidth:1,
				    	 markerOptions: { size: 2 }
					},
					series:[
					       {
					    	   lineWidth:2,
					    	   markerOptions: { size: 3 }
					       }
					]
			};
			// To ensure that global is the first one
			all_series = [data["ca_displacements"]["global"]];
			series_labels = ["global"];
			var cluster_ids = [];
			for(var cluster_id in data["ca_displacements"]){
				if(cluster_id !== "global"){
					cluster_ids.push(cluster_id);
				}
			}
			cluster_ids.sort();

			for(var i  = 0; i < cluster_ids.length; i++){
				all_series.push(data["ca_displacements"][cluster_id]);
				series_labels.push(cluster_id);
				var cluster_id = cluster_ids[i];
				plot_cluster_options["title"] = "Id: "+ cluster_id;
				$("#plot_"+cluster_id).jqplot([data["ca_displacements"][cluster_id]], plot_cluster_options);
			}

			plot_main_options = $.extend({}, plot_cluster_options);
			plot_main_options["title"] = "Global";
			plot_main_options["seriesColors"] = ["#000000","#007D34","#F6768E","#00538A","#FF7A5C",
			                                     "#53377A","#FF8E00","#B32851","#F4C800",
			                         		     "#7F180D","#93AA00","#593315","#F13A13","#232C16"];
			plot_main_options["legend"]= {
		            show: true,
		            placement:"outsideGrid",
		            renderer: $.jqplot.EnhancedLegendRenderer,
		            labels: series_labels,
		            location: "ne",
		            rendererOptions: {
			            numberRows: 3,
		                seriesToggle: 'normal',
		                seriesToggleReplot: {
		                	resetAxes: true
		                	}
		            }
	        };
			main_plot = $.jqplot("main_cluster_plot",[data["ca_displacements"]["global"]], plot_main_options);
		}
		else{
			$("#displacements-tab").css({display:"none"});
		}

		$("#show_all_clusters").click(function(){
			if($(this).is(":checked")){
				main_plot.data = all_series;
				main_plot.replot(plot_main_options);
			}
			else{
				main_plot.data = [data["ca_displacements"]["global"]];
				main_plot.replot(plot_main_options);
			}
		});
	};


	return {
				create_tab:create_tab
			};
}());