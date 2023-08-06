var EVALUATION = (function(){

	function get_labels(table_id, columns_array, normalize){
		var heads = $("#"+table_id).find("th");
		var labels = [];
		for(var i = 0; i < columns_array.length; i++){
			labels.push($(heads[columns_array[i]]).text());
		}
		return labels;
	}

	function traverse_columns(table_id, columns_array, normalize){
		var data = [];
		var x = 0;
		$("#"+table_id).find("tr").each(function(){
			var cells = $(this).find("td");
			if(cells.length != 0){
				for(var i = 0; i < columns_array.length; i++){
					if(typeof data[columns_array[i]] === "undefined"){
						data[columns_array[i]] = [];
					}
					data[columns_array[i]].push([x, parseFloat($(cells[columns_array[i]]).text())]);
				}

				x = x+1;
			}
		});

		tmp_data  = [];
		console.log(normalize)
		for (datum_index in data){
			if(normalize[datum_index]){
				console.log(data[datum_index])
				tmp_data.push(normalize_data(data[datum_index]));
			}
			else{
				console.log(data[datum_index])
				tmp_data.push(data[datum_index]);
			}
		}
		return tmp_data;
	}

	// normalizes in range (0..1)
	function normalize_data(data){
		var max = data[0][1];
	    var min = data[0][1];

	    for(var i = 0; i < data.length; i++){
	    	max = Math.max(max, data[i][1]);
	    	min = Math.min(min, data[i][1]);
	    }

	    if(max !== min){
		    for(var i = 0; i < data.length; i++){
		    	data[i][1] = (data[i][1] - min) / (max - min);
		    }
	    }
	    else{
	    	for(var i = 0; i < data.length; i++){
		    	data[i][1] = 1;
		    }
	    }

	    return data;
	}

	var create_tab = function(tab_id, data){
		var evaluation_template = COMM.synchronous.load_text_resource("results/templates/evaluation.template");
		template = Handlebars.compile(evaluation_template);
		$("#"+tab_id).html(template(data));

		// Prepare show plot table
		$("#show_plot_table").css({width:$("#summary_table").css("width")});
		$(".button").button();

		// Add table sorting capability
		$("#summary_table").tablesorter({sortList: [[0,0]]});
		$("#do_plot_button").click(function(){
			do_plot();
		});
	};

	function do_plot(){
		var cells = $("#show_row").find("td");
		var norm_cells = $("#normalize_row").find("td");
		var columns_to_plot = [];
		var normalize = {};

		for (var i = 0; i < cells.length; i++){
			if($(cells[i]).find(".show_checkbox").length > 0){
				if($(cells[i]).find(".show_checkbox").is(":checked")){
					columns_to_plot.push(i);
					normalize[i] = false;
				}
			}
		}

		for (var i = 0; i < norm_cells.length; i++){
			if($(norm_cells[i]).find(".normalize_checkbox").length > 0){

				if($(norm_cells[i]).find(".normalize_checkbox").is(":checked")){
					normalize[i] = true;
				}
			}
		}

		if (columns_to_plot.length == 0) return;

		$("#summary_plot").empty().jqplot(traverse_columns("summary_table",
				columns_to_plot,
				normalize),
		{
			animate: true,
			legend: {
		        show: true,
		        labels:get_labels("summary_table",columns_to_plot),
		        renderer: $.jqplot.EnhancedLegendRenderer,
	            placement: "outsideGrid",
		        location: 'ne',
		    },
		    highlighter: {
		        show: true,
		        sizeAdjust: 7.5
		    }
		});
	}

	var process_data = function(data, accepted_ids){
		data["evaluation_tags"] = [];
		for (var evaluation_tag in data["selected"][Object.keys(data["selected"])[0]]["evaluation"]){
			if (evaluation_tag.substr(0,11) !== "Normalized_"){
				data["evaluation_tags"].push({tag:evaluation_tag});
			}
		}

		//-----------------
		var criteria_ids = [];
		for(var criteria_id in data["scores"]){
			criteria_ids.push(criteria_id);
		}
		criteria_ids.sort();
		for(var i=0; i <  criteria_ids.length; i++){
			data["evaluation_tags"].push({tag:criteria_ids[i]});
		}
		//-------------------

		data["evaluations"] = [];
		for (var clustering_id in data["selected"]){
			var clustering_evaluation = data["selected"][clustering_id]["evaluation"];
			var eval_data = {
				id:clustering_id,
				values:[],
				best_clustering : (clustering_id == data["best_clustering"])
			};
			for(var evaluation_tag in clustering_evaluation){
				if (evaluation_tag.substr(0,11) !== "Normalized_"){
					var value = clustering_evaluation[evaluation_tag];
					eval_data["values"].push({value:value});
				}
			}
			//-----------------
			for(var i=0; i <  criteria_ids.length; i++){
				eval_data["values"].push({value:data["scores"][criteria_ids[i]][clustering_id]});
			}
			//-----------------
			data["evaluations"] .push(eval_data);
		}
	};

	return {
		process_data:process_data,
		create_tab:create_tab
	};

}());