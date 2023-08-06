Handlebars.registerHelper('formatted', function(number) {
	if(isInt(number)){
		return ""+number;
	}
	else{
		return number.toFixed(4);
	}
});

function process_result_data(data){
	console.log(data)
	var all_clusterings = jQuery.extend({}, data["selected"],data["not_selected"]);
	data['total_number_of_clusterings'] = Object.keys(all_clusterings).length;
	data['number_of_accepted_clusterings'] = Object.keys(data["selected"]).length;
	data['number_of_rejected_clusterings'] = Object.keys(data["not_selected"]).length;

	var tmp_data = {};

	for (clustering_id in all_clusterings){
		var clustering_definition = all_clusterings[clustering_id];
		var type = clustering_definition["type"];
		if(tmp_data[type] == undefined){
			tmp_data[type] = 1;
		}
		else{
			tmp_data[type] += 1;
		}
	}

	data['number_of_clusterings_by_type'] = [];
	for (clustering_type in tmp_data){
		data['number_of_clusterings_by_type'].push({"number_of_clusterings": tmp_data[clustering_type],
															"type":clustering_type});
	}

	data["accepted"] = [];
	var accepted_ids = [];
	for (var clustering_id in data["selected"]){
		accepted_ids.push({id:clustering_id});
		var clustering_definition = data["selected"][clustering_id];
		data["accepted"].push({
			id:clustering_id,
			type:clustering_definition["type"],
			parameters:JSON.stringify(clustering_definition["parameters"])
		});
	}

	data["rejected"] = [];
	for (var clustering_id in data["not_selected"]){
		var clustering_definition = data["not_selected"][clustering_id];
		data["rejected"].push({
			id:clustering_id,
			type:clustering_definition["type"],
			parameters:JSON.stringify(clustering_definition["parameters"]),
			reasons: clustering_definition["reasons"]
		});
	}

	EVALUATION.process_data(data, accepted_ids);

	return data;
}

function generate_all_tabs_contents(data){

	var summary_template = COMM.synchronous.load_text_resource("results/templates/summary.template");
	var template = Handlebars.compile(summary_template);
	$("#summary-tab").html(template(data));
	$("#expandList").button();
	$("#collapseList").button();

	var files_template = COMM.synchronous.load_text_resource("results/templates/files.template");
	template = Handlebars.compile(files_template);
	$("#files-tab").html(template(data));
	$(".file_retrieval").click(function(event){
		event.preventDefault();
		window.location.href = "/serve_file?path="+$(this).attr("href");
	});

	EVALUATION.create_tab("evaluation-tab",data);

	CLUSTERS.create_tab(data);

	DISPLACEMENTS.create_tab(data);

	DISTANCES.create_tab(data);

	$("#tabs").tabs();

}