var MAIN_MENU = (function(){
		// Actions  enumeration (the different kind of actions that can be performed with the wizard).
		var CLUSTERING_ACTION = "clustering";
		var ADVANCED_ACTION =  "advanced";
		var RESULTS_ACTION = "results";
		var COMPRESS_ACTION = "compress";
		
		// Wether if we currently are in the main menu window or not.
		var currently_in_wizard = false;
		
		// Description of the buttons we can find in the main menu.
		var buttons = [
					   {
						   id: CLUSTERING_ACTION,
						   text:"Clustering",
						   action:CLUSTERING_ACTION,
					   },
					   
		               {
		            	   id: ADVANCED_ACTION,
		            	   text:"Clustering (advanced)",
		            	   action:ADVANCED_ACTION
		               },
		               
		               {
		            	   id: COMPRESS_ACTION,
		            	   text:"Compress trajectory",
		            	   action:COMPRESS_ACTION
		               },
		               
		               {
		            	   id: RESULTS_ACTION,
		            	   text:"See results",
		            	   action:RESULTS_ACTION
			           }
		];
		
		/**
		 * Adds the buttons to the main menu and sets up some properties and events.
		 **/
		var setup_main_menu = function(container_selector){
			$(".main_menu_window").show();
            $(".wizard_window").hide();
            
			for (var i = 0 ; i < buttons.length; i++){
				var button_descriptor = buttons[i];
				$(container_selector).append("<div id='"+button_descriptor.id+"' class='main_menu_button' style = 'text-align:center;'>"+button_descriptor.text+"</div></br>");
			}
			$(".main_menu_button").button();
			$(".main_menu_button").click(function(){
				if (! currently_in_wizard){
					GLOBAL.selected_action = $(this).attr("id");
					switch_to_wizard(GLOBAL.selected_action);
				}
			});
		};
		
		/**
		 * Changes from the main menu to the wizard (hides m. menu and creates the wizard).
		 */
		function switch_to_wizard(action){
			WIZARD.generate_wizard_course("#steps_wrapper", action);
            WIZARD.control.setup_wizard(action);
        	WIZARD.components_behaviour.apply_behaviour(action);
        	set_defaults_to_fields();
        	$(".main_menu_window").hide();
            $(".wizard_window").show();
            currently_in_wizard = true;
		}

		/**
		 * Changes from the wizard to the menu (destroys the wizard and shows the m. menu).
		 */
		function switch_to_menu(){
			// Destroy wizard
			$("#wizard-wrapper").wizard("destroy");
			$("#steps_wrapper").empty();
			// Show the main menu again
			$(".main_menu_window").show();
			$(".wizard_window").hide();
			currently_in_wizard = false;
		}
		
		/**
		 * Function to return to the main menu.
		 */
		function start_over(){
			if(currently_in_wizard){
				DIALOG.yes_or_no("Start Over","Return to main menu?",function(){
					switch_to_menu();
				});
			}
		}
		
		// Accessible constants and functions
		return {
			RESULTS_ACTION:RESULTS_ACTION,
			ADVANCED_ACTION:ADVANCED_ACTION,
			CLUSTERING_ACTION:CLUSTERING_ACTION,
			COMPRESS_ACTION:COMPRESS_ACTION,
			setup_main_menu:setup_main_menu,
			start_over:start_over
		};

}());