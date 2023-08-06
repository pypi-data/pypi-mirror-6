var DIALOG = (function(){

	/**
	 * Creates a 'yes or no' type dialog (that is, a dialog that can be only answered with a yes or a no. If
	 * yes is pressed, then 'ok_function_callback' is executed.
	 */
	 var yes_or_no = function(dialog_title, message, ok_function_callback){

	    $("<div/>", {
	    	id:'yes_or_no_dialog',
	    	title: dialog_title,
	    	html:message})
	    .dialog(
	            {
	                modal:true,
	                autoResize:true,
	                width:'auto',
	                close: function( event, ui ){
	                    $(this).dialog("destroy");
	            },
	            buttons: [
	                        {
	                            text: "Yes",
	                            click: function() {
	                            	ok_function_callback();
	                                $(this).dialog("destroy");
	                            }
	                        },
	                        {
	                            text: "No",
	                            click: function() {
	                                $(this).dialog("destroy");
	                            }
	                        }
	            ]
	    });
	};
	 /**
	  * Shows a general warning message.
	  */
	 var warning = function (message){
		    $("<div/>", {
		    	id: 'warning_dialog',
		    	title: 'Warning',
		    	html: message})
		    .dialog({
		                modal:true,
		                autoResize:true,
		                width:'auto',
		                close: function( event, ui ){
		                    $(this).dialog("destroy");
		                },
		                buttons: [{
		                            text: "Ok",
		                            click: function() {
		                            	$(this).dialog("destroy")
		                            }
		                }]
		    });
		}
	/**
	 * Loads a help file and shows it using a dialog.
	 */
	 var help = function(step_id){
		 var markdown_file = "wizard/wizard.steps/help/"+step_id+".md";
		 var not_found_markdown_file = "wizard/wizard.steps/help/not_found.md";

		 var markdown_txt  = COMM.synchronous.load_text_resource(markdown_file, true);

		 if(markdown_txt === ""){ // Help file for this step not found
			 markdown_txt = COMM.synchronous.load_text_resource(not_found_markdown_file, true);
		 }

		 var help_html = markdown.toHTML( markdown_txt );

		 $("<div/>", {
		    	id: 'help_dialog',
		    	title: 'Help',
		    	html: help_html})
		    .dialog({
		                modal:true,
		                autoResize:false,
		                width: '600px',
		                close: function( event, ui ){
		                    $(this).dialog("destroy");
		                },
		                buttons: [{
		                            text: "Ok",
		                            click: function() {
		                            	$(this).dialog("destroy")
		                            }
		                }]
		    });

	 }


	 // BROWSING submodule
	 var browsing = (function(){
		 var last_root = "/";
		 var last_file = "";

		 var browse = function (target, ok_callback){
			    var what_we_search = target;
				var expected_extension = "";
			    if(target.substring(0,4) == "file"){
			    	var parts = target.split("::");
			    	if(parts.length>1){
			    		target = parts[0];
			    		expected_extension = parts[1];
			    		what_we_search = target +" (" +expected_extension+")";
			    	}
			    }
			    // If we have done a last search, then this will be our starting point.
			    var root = "";
			    if (DIALOG.browsing.last_root!="/"){
			    	root = DIALOG.browsing.last_root;
			    }
			    else{
			    	root = GLOBAL.workspace_path;
			    }
			    console.log("ROOT",root)
				$("<div title='Select a "+what_we_search+"' id = 'browse_dialog'>\
		        <div class = 'fileBrowserHeader'>\
	            <span> Current selection:</span></br>\
	            <div id='selected_file_or_folder' class='fileBrowserSelection'> </div>\
		        </div> <div id = 'browsing_area' class='fileBrowserWrapper'>\
		        </div>\
		        <div style='margin-top:10px;'> Current root:</div></br>\
				<div id='root' class='fileBrowserSelection'>"+ root +"</div>\
		        </div>")
			    .dialog({
			                modal:true,
			                autoResize:true,
			                width:'auto',
			                close: function( event, ui ){
			                    $(this).dialog("destroy");
			                },
				            buttons: [
				                        {
				                            text: "Ok",
				                            click: function() {
				                            	ok_callback($("#selected_file_or_folder").text());
				                                $(this).dialog("destroy");
				                            }
				                        },
				                        {
				                            text: "Cancel",
				                            click: function() {
				                                $(this).dialog("destroy");
				                            }
				                        }
				            ]
			    });

			    $('.ui-dialog button:nth-child(1)').button('disable');

			    $("#browsing_area").fileTree({
	                    root: root,
	                    script: "/browse_folder"
	                },
	                function(url,file_type) {
						$("#selected_file_or_folder").text(url);
						// Check extension
						var extension = url.split('.').pop();
						if(target == file_type){
							if(expected_extension=="" || expected_extension == extension){
								$('.ui-dialog button:nth-child(1)').button('enable');
								// Change last root
								DIALOG.browsing.last_root = url.substr(0,url.lastIndexOf("/"));
								// Change last file
								DIALOG.browsing.last_file = url.substr(url.lastIndexOf("/"), url.length-1);
							}
						}
						else{
						    $('.ui-dialog button:nth-child(1)').button('disable');
						}

	                }
			    );
		 };

		 return {
			 browse: browse,
			 last_root:last_root,
			 last_file:last_file
		 }
	 }());

	// CRITERIA submodule
	var criteria = (function(){

		/*
		    Prepares and shows the evaluation criteria dialog.
		*/
		var criteria_creation =  function (list_handler, template){
		    $("<div >", {title: "New Criteria",id:'criteria_creation_dialog'})
		    // Add contents to the dialog
		    .append(get_eval_dialog_contents(template))
		    // Set up dialog
		    .dialog({modal:true,
		            autoResize:true,
		            width:'auto',
		            create: function( event, ui ) {
		               $(".dialog_spinner").spinner({places:2,step:0.05});
		               $(".dialog_spinner").css({width:"35px"});
		            },
		            close: function( event, ui ){
		                 $(this).dialog("destroy");
		            },
		            buttons: [{
		            			text: "Discard",
		                        click: function() {
		                            $(this).dialog("destroy");
		                        }
		                      },
		                      {
		                        text: "Ok",
		                        click: function() {
		                            var criteria = criteria_to_string('criteria_creation_dialog');
		                            if(criteria != ""){
		                            	list_handler.addElement(criteria);
		                            }
		                            $(this).dialog("destroy");
		                        }
		                      }]
		            });
		};

		/*
		    Creates the contents of the dialog (using handlebars))
		*/
		function get_eval_dialog_contents(template_contents){
		    // Gather data
		    var data = {criteria:[]};
		    for (var i = 0;i < QUERIES.criteria_types.length; i++){
		        var criteria_name = QUERIES.criteria_types[i];
		        data.criteria.push({name:criteria_name,  initial_value:0});
		    }

		    // Render it
		    var template = Handlebars.compile(template_contents);
		    return template(data);
		}

		/*
		    Creates a string from the contents of the dialog that represents one evaluation criteria.
		*/
		function criteria_to_string(dialog_to_extract_data){
		    var string_criteria = "";
		    for (var i =0; i<QUERIES.criteria_types.length; i++){
		        var criteria_name = QUERIES.criteria_types[i];
		        // Get the spinners value, if different than 0, proceed
		        var weight =  $("#"+criteria_name+"_spinner").val();
		        if (weight != 0){
		            // Maximize or minimize?
		            var min_max = $("#"+criteria_name+"_listbox").val();
		            string_criteria += min_max + " " + criteria_name + " (weight: "+ weight + ") and ";
		        }
		    }
		    // remove last and return
		    return string_criteria.substring(0,string_criteria.length-4);
		}

		return{
			criteria_creation:criteria_creation
		};

	}());

	return{
		// functions
		yes_or_no:yes_or_no,
		warning: warning,
		help:help,

		// submodules
		browsing: browsing,
		criteria:criteria

	}

}());


