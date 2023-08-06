WIZARD.control = (function(module){

	if (typeof module.functions === "undefined"){
		module.functions = {};
	}

	module.functions[MAIN_MENU.ADVANCED_ACTION] = {
		'workspace-1':function(event, state, step, step_id){
			var file_path = step.find("#workspace_base").val();
			GLOBAL.workspace_path = file_path;

			if(file_path!=""){
				var file_check  = COMM.synchronous.file_exists(file_path);

				if(file_check["exists"]){
					return true;
				}
				else{
					DIALOG.yes_or_no(
									"Warning",
									"Folder does not exist, do you want to create it?",
									function(){
										COMM.synchronous.create_folder(file_path);
										$("#wizard-wrapper").wizard("forward",[event,1]);
									});
				}
			}
			else{
				DIALOG.warning("The field cannot be empty.");
			}

			return false;
		},
	    'trajectory-1':function(event, state, step, step_id){
	    	if (!$("#trajectory_list").dynamiclist("isEmpty")){
            	return true;
        	}
        	else{
        		DIALOG.warning("You have to add at least one trajectory.");
        		return false;
        	}
		},
	    "rmsd-1":function(event, state, step, step_id){
	    	if($("#rmsd_fit_selection").val() == "" ||
    				(!step.find("#usesamefitandcalc").is(':checked') &&
    						$("#rmsd_calc_selection").val() == "")){
	        	DIALOG.warning ("Fields cannot be empty.");
				return false;
        	}
    		if (step.find("#usesamefitandcalc").is(':checked')){
    			$("#rmsd_calc_selection").val($("#rmsd_fit_selection").val());
    		}
			return true;
		},
	    "distance-1":function(event, state, step, step_id){
	    	if($("#dist_fit_selection").val() == "" ||
					$("#dist_calc_selection").val() == ""){
		    	DIALOG.warning ("Fields cannot be empty.");
				return false;
			}
	    	return true;
		},
	    'load_matrix-1':function(event, state, step, step_id){
	    	if ($("#matrix_creation_path").val()!=""){
            	return true;
        	}
        	else{
        		DIALOG.warning ("You have to specify the file you want to load.");
        	}
	    	return false;
		},
	    'algorithms-1':function(event, state, step, step_id){
	    	if (!$("#algorithms_list").dynamiclist("isEmpty")){
        		var list = step.find(":custom-dynamiclist");
        		GLOBAL.selected_algorithms = list.dynamiclist("getValue").split(",");
            	return true;
        	}
        	else{
        		DIALOG.warning ("You have to add at least one clustering algorithm.");
        	}
	    	return false;
		},
	    'algorithm-gromos':function(event, state, step, step_id){
	    	var cbox = step.find("[name='guess_params']");
        	if(cbox.is(":checked")){
        		return true;
        	}
        	else{
        		var a_list_is_incorrect = false;

        		step.find(":text").each(function(){
        			if($(this).is(":visible")){
	        			if(!a_list_is_incorrect){
	            			if($(this).val() == ""){
            					DIALOG.warning ("Some mandatory fields are empty.");
	            				a_list_is_incorrect = true;
	            				return;
	            			}
	            			else{
	            				console.log($(this).val());
	            				if(!has_list_format($(this).val())){
	            					a_list_is_incorrect = true;
	            					DIALOG.warning ("List has not the correct format.");
	            					return;
	            				}
	            			}
	        			}
	        			else{
	        				return false;
	        			}
        			}
        		});

        		return ! a_list_is_incorrect;
        	}
		},
	    'criteria-2':function(event, state, step, step_id){
	    	if ($("#criteria_list").dynamiclist("isEmpty")){
        		DIALOG.warning ("You need to define at least one selection criterium.");
        		return false;
        	}
        	else{
        		return true;
        	}
		},
		'criteria-1':function(event, state, step, step_id){
			if (get_value_of($("#evaluation_maximum_clusters"), "int") < get_value_of($("#evaluation_minimum_clusters"), "int") ){
        		DIALOG.warning ("Minimum is bigger than maximum.");
        		return false;
        	}
        	else{
        		return true;
        	}
		}
	};

	module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-hierarchical'] = module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-gromos'];
	module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-random'] = module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-gromos'];
	module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-spectral'] = module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-gromos'];
	module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-dbscan'] = module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-gromos'];
	module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-kmedoids'] = module.functions[MAIN_MENU.ADVANCED_ACTION]['algorithm-gromos'];

	return module;

}(WIZARD.control));