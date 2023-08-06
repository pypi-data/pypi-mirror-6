WIZARD.components_behaviour = (function(){

	function general_widget_behaviour (){
		$("select").selectmenu();
        $(".button_widget").button();
        $(':text').not('.spinner_widget')
          .button()
          .css({
                'font' : 'inherit',
                'color' : 'inherit',
                'text-align' : 'left',
                'outline' : 'none',
                'cursor' : 'text'
          });
        $(".spinner_widget").spinner({min:0});
	}

	var apply_behaviour = function(action){
		general_widget_behaviour();

		switch (action){

			case MAIN_MENU.RESULTS_ACTION:

				this.setup_browse_results_folder_button();
				this.setup_show_results_button();
				break;

			case MAIN_MENU.ADVANCED_ACTION:

				// Lists
				this.setup_trajectory_list();
				this.setup_algorithms_list();
				this.setup_queries_list();
				this.setup_criteria_list();

				// Buttons
				this.setup_run_button();
				this.setup_get_script_button();
				this.setup_browse_workspace_button();
				this.setup_browse_matrix_button();

				// Checkbox (guess params; algorithm steps may be created beforehand)
				this.setup_guess_params_checkbox();
				this.setup_kmedoids_method_selector();

				// Previewers
				this.setup_rmsd_previewer();
				this.setup_distance_previewer();
				break;

			case MAIN_MENU.CLUSTERING_ACTION:

				// Lists
				this.setup_trajectory_list();

				// Buttons
				this.setup_browse_workspace_button();
				this.setup_run_button();
				this.setup_get_script_button();

				// Previewers
				this.setup_rmsd_previewer();
				this.setup_distance_previewer();
				break;

			case MAIN_MENU.COMPRESS_ACTION:
				// Clustering related stuff
				//-------------------------
				// Lists
				this.setup_trajectory_list();

				// Buttons
				this.setup_browse_workspace_button();
				this.setup_run_button();
				this.setup_get_script_button();

				// Previewers
				this.setup_rmsd_previewer();
				this.setup_distance_previewer();

				//Loading results
				//----------------------
				this.setup_browse_results_folder_button();
				break;

			default:
				break;
		}

	}

	return {
		apply_behaviour:apply_behaviour,
	};

}());