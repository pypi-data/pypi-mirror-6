var GLOBAL = (function(){
	var selected_algorithms = [];
	var loaded_clustering = null;
	var selected_action = "";
	var current_step = null;
	var workspace_path = "";
	var loaded_files = [];

	return {
		selected_algorithms: selected_algorithms,
		loaded_clustering: loaded_clustering,
		selected_action: selected_action,
		loaded_files: loaded_files
	};

}());