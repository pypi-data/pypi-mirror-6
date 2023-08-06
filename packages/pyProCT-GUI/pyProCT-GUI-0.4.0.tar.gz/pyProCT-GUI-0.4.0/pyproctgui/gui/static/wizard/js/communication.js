var COMM = (function(){
		var sync = {

				file_exists : function(location){
					var response = undefined;
					$.ajax({
					      url: "/file_exists",
					      type: "POST",
					      data: JSON.stringify({'location':location}),
					      dataType: "text",
					      async: false,

					      complete: function(jqXHR, textStatus) {
					          response =  $.parseJSON(jqXHR.responseText);
					      },

					      error:function( jqXHR, textStatus, errorThrown ){
					    	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
					          response = {'exists':false,'isfile':false};
					      }
					    });
					return response;
				},

				create_folder : function(location){
					var response = undefined;
				    $.ajax({
				      url: "/create_directory",
				      type: "POST",
				      data: JSON.stringify({'location':location}),
				      dataType: "text",
				      async: false,
				      complete: function(jqXHR, textStatus) {
				          response = $.parseJSON(jqXHR.responseText);
				      },

				      error:function( jqXHR, textStatus, errorThrown ){
				    	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
				          response = {'done':false};
				      }
				    });
				    console.log(response)
				    return response;
				},

				trigger_results_page: function (parameters, dialog_id){
					$.ajax({
			     		url: "/show_results",
			     		type: "POST",
			     		dataType: "text",
			     		async: false,
			     		data: JSON.stringify(parameters),
			     		complete: function(jqXHR, textStatus){
					          response =  jqXHR.responseText;
					          if(response === "KO"){
					        	  DIALOG.warning("No results found. Check server log.");
					          }
			     		},
			     		error:function(jqXHR, textStatus, errorThrown){
			     			DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
			     		}
			        });
				},

				/**
				 *   Loads a system resource, returning its contents. The function does not finish
				 *   until the contents have been loaded.
				 *
				 *   @param {string} resource path to the resource to be loaded.
				 *
				 *   @param {string} do_not_warn_if_error If the resource load fails, it does not show
				 *   the error dialog.
				 *
				 *   @returns {string} The contents of the resource or an empty string if it was impossible
				 *   to load it.
				 **/
				load_text_resource: function (resource, do_not_warn_if_error){
					if(do_not_warn_if_error === undefined){
						do_not_warn_if_error = false;
					}
				    var text_resource = "";
				    var error = false;

					$.ajax({
				              url: resource,
				              type: "GET",
				              dataType: "text",
				              async: false,
				              cache: false,

				              complete: function(jqXHR, textStatus){
				                  text_resource = jqXHR.responseText;
				              },

				              error:function( jqXHR, textStatus, errorThrown ){
				            	  if (!do_not_warn_if_error){
				            		  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?");
				            	  }
				            	  error = true;
				              }
				            });

					if (error){
				    	text_resource = "";
				    }

				    return text_resource;
				},

				load_external_text_resource: function (resource){
				    var text_resource = "";

				    $.ajax({
				              url: "/read_external_file",
				              type: "POST",
				              dataType: "text",
				              async: false,
				              cache: false,
				              data: JSON.stringify({"path":resource}),

				              complete: function(jqXHR, textStatus){
				                  text_resource = jqXHR.responseText;
				              },

				              error:function( jqXHR, textStatus, errorThrown ){
				            	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
				              }
				            });

				    return text_resource;
				},


				absolute_path: function (path){
					var abs = "";
					$.ajax({
			              url: "/normalize_path",
			              type: "POST",
			              dataType: "text",
			              async: false,
			              data: JSON.stringify({'path':path}),

			              complete: function(jqXHR, textStatus){
			                  abs = $.parseJSON(jqXHR.responseText)["path"];
			              },

			              error:function( jqXHR, textStatus, errorThrown ){
			            	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
			              }
			        });
					return abs;
				},

				save_frame: function(frame, workspace_paths){
					var save_path = "";
					$.ajax({
			              url: "/save_frame",
			              type: "POST",
			              dataType: "text",
			              async: false,
			              cache: false,
			              data: JSON.stringify({
			            	  "frame":frame,
			            	  "paths":workspace_paths
			              }),
			              complete: function(jqXHR, textStatus){
			            	  save_path = $.parseJSON(jqXHR.responseText)["path"];
			              },

			              error:function( jqXHR, textStatus, errorThrown ){
			            	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
			              }
			        });
					return save_path;
				},

				save_cluster: function(elements, workspace_paths){
					var save_path = "";
					$.ajax({
			              url: "/save_cluster",
			              type: "POST",
			              dataType: "text",
			              async: false,
			              cache: false,
			              data: JSON.stringify({
			            	  "paths":workspace_paths,
			            	  "elements":elements
			              }),
			              complete: function(jqXHR, textStatus){
			            	  save_path = $.parseJSON(jqXHR.responseText)["path"];
			              },

			              error:function( jqXHR, textStatus, errorThrown ){
			            	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
			              }
			        });
					return save_path;
				}
		};

		var async = {
				run_pyproclust:	function (parameters){
					/*
					 * Calls the run handler on the server so that it creates an executor thread.
					 * This executor thread changes status depending on the message it gets from
					 * pyProCT (from the observer). Executor status must have the form {status:"",value:""}
					 * where status is the actual action being performed.
					 *
					 */
					function start_monitoring_run( progress_dialog, parameters){
						$.ajax({
							url: "/run_update_status",
							type: "POST",
							dataType: "text",
							complete: function(jqXHR, textStatus){
							    var my_response_object =  $.parseJSON(jqXHR.responseText);
							    console.log(my_response_object);
							    if (my_response_object["status"] == "Ended"){
							    	// Then destroy the dialog
							    	progress_dialog.dialog("destroy");
							    	// Create the results dialog
							    	DIALOG.yes_or_no(
							    			"Results",
							    			"Do you want to check the results?",
							    			function(){
							    				COMM.synchronous.trigger_results_page(parameters["global"]["workspace"]);
							    			}
							    	);
							    }
							    else{
							    	// Capture Status
							    	progress_dialog.find("#status_label").text(my_response_object["status"]);
							    	progress_dialog.find("#progress_bar").progressbar("value",my_response_object["value"]);
							    	setTimeout(function(){
							    		start_monitoring_run(progress_dialog, parameters);
							    		},
							    		3000);
							    }
							},

							error:function( jqXHR, textStatus, errorThrown ){
								DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
							}
						});
					};

				    $.ajax({
				          url: "/run",
				          type: "POST",
				          data: JSON.stringify(parameters),
				          dataType: "text",

				          complete: function(jqXHR, textStatus){
				        	  var progress_dialog = $("<div title='Progress' id = 'progress_dialog'>" +
				        	  		"<span id='status_label'>Initializing... </span></br>"+
				        		    "<div id = 'progress_bar' style='width:250px;'>"+
				        			"</div></div>")
				        	       .dialog({
				                       modal:true,
				                       autoResize:true,
				                       width:'auto',
					       	           buttons: [
				       	                        {
				       	                            text: "Cancel",
				       	                            click: function() {
				       	                            	$("body").append("<div id='spinner_progress'>");

				       	                            	var opts = {
															  lines: 9, // The number of lines to draw
															  length: 13, // The length of each line
															  width: 4, // The line thickness
															  radius: 12, // The radius of the inner circle
															  corners: 1, // Corner roundness (0..1)
															  rotate: 12, // The rotation offset
															  direction: 1, // 1: clockwise, -1: counterclockwise
															  color: '#000', // #rgb or #rrggbb
															  speed: 1, // Rounds per second
															  trail: 67, // Afterglow percentage
															  zIndex: 20000000000,
															  shadow: false, // Whether to render a shadow
															  hwaccel: false, // Whether to use hardware acceleration
															  className: 'spinner', // The CSS class to assign to the spinner
				       	                            	};

				       	                            	$("#spinner_progress").spin(opts);
				       	                            	$("#spinner_progress").center();
				       	                            	$.ajax({
				       	                                 url: "/stop_calculations",
				       	                                 type: "POST",
				       	                                 async:true,
				       	                                 complete: function(jqXHR, textStatus){
				       	                                	 var response = jqXHR.responseText;
				       	                                	 console.log("RESPONSE", response);
				       	                                	 if(response == "OK"){
				       	                                		 DIALOG.warning("Process succesfully terminated.");
				       	                                		 $("#progress_dialog").dialog("destroy");
				       	                                	 }
				       	                                	 else{
				       	                                		DIALOG.warning("It was impossible to terminate the calculation process. Please try again.");
				       	                                	 }
				       	                                	 $("#spinner_progress").spin(false);
				       	                                	 $("body").remove("#spinner_progress");
				       	                                 }
				       	                            	});
				       	                            }
				       	                        }
					       	            ]
				        	       });
				        	  $( "#progress_bar" ).progressbar({ value: false});
				        	  $( ".ui-dialog-titlebar-close").remove();
				        	  setTimeout(function(){start_monitoring_run(progress_dialog, parameters);},5000);
				          },

				          error:function( jqXHR, textStatus, errorThrown ){
				        	  DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
				          }
				        });
				},

				download_script: function (parameters){
					console.log("saving");
					$.ajax({
						url: "/save_params",
						type: "POST",
						data: JSON.stringify(parameters),
						dataType: "text",
						complete: function(jqXHR, textStatus){
							var my_response_object =  $.parseJSON(jqXHR.responseText);
							window.location.href = "/serve_file?path="+my_response_object.file_url+"&filename=parameters.json";
						},
						error:function( jqXHR, textStatus, errorThrown ){
							DIALOG.warning( "Request failed: " + textStatus+". Is the server working?" );
						}
					});
				}
		};

		return {
			synchronous: sync,
			asynchronous: async
		};


}());