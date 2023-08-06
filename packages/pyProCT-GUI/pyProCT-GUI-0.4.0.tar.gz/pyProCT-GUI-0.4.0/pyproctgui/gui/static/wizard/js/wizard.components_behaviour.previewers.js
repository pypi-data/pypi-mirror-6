WIZARD.components_behaviour = (function(module){
	
	module.setup_rmsd_previewer = function(){
		create_previewer(
        		'rmsdViewer',
        		"trajectory_list", 
        		"workspace_base",
        		[	
        		 	{
        		 		input_id:'rmsd_fit_selection',
        				button_id:"preview_rmsd_fit_button"
        		 	},
        		 	{
        		 		input_id:'rmsd_calc_selection',
        				button_id:"preview_rmsd_calc_button"
        		 	}
        		]
        );
        // Disable calc
        $("#calc_selection_label").addClass("disabled");
        $("#rmsd_calc_selection").prop('disabled', true);
        $("#rmsd_calc_selection").button("disable");
        $("#preview_rmsd_calc_button").button("disable");
        
        //Allow enabling calculation selection
        $("#usesamefitandcalc").click(function(){
        	 if($(this).prop('checked')){
        		 $("#calc_selection_label").addClass("disabled");
                 $("#rmsd_calc_selection").prop('disabled', true);
                 $("#rmsd_calc_selection").button("disable");
                 $("#preview_rmsd_calc_button").button("disable");
        	 }
        	 else{
        		 $("#calc_selection_label").removeClass("disabled");
                 $("#rmsd_calc_selection").prop('disabled', false);
                 $("#rmsd_calc_selection").button("enable");
                 $("#preview_rmsd_calc_button").button("enable");
        	 }
        });
	}
	
	module.setup_distance_previewer = function(){
		create_previewer(
        		'distanceViewer',
        		"trajectory_list", 
        		"workspace_base",
        		[	
        		 	{
        		 		input_id:'dist_fit_selection',
        				button_id:"preview_dist_fit_button"
        		 	},
        		 	{
        		 		input_id:'dist_calc_selection',
        				button_id:"preview_dist_calc_button"
        		 	}
        		]
        );
	}
	
	
	return module;
	
}(WIZARD.components_behaviour));