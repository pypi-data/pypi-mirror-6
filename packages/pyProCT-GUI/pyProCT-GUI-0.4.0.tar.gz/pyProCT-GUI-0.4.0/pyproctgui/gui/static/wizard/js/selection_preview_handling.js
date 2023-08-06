//previewers [{input_id:"",button_id:""}]
function create_previewer(
						previewer_canvas_id,
						trajectories_dynamic_list_id, 
						base_workspace_field_id, 
						previewers
						){
	
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
			  shadow: false, // Whether to render a shadow
			  hwaccel: false, // Whether to use hardware acceleration
			  className: 'spinner', // The CSS class to assign to the spinner
	};
	
	$("#"+previewer_canvas_id).wrap("<div id="+previewer_canvas_id+"_context style='position:absolute'/>");
	$("#"+previewer_canvas_id+"_context").append("<div id="+previewer_canvas_id+"_spinner class = 'selection_preview'/>");
	$("#"+previewer_canvas_id).css('background-color', '#eeeeee');
	
	$("#"+previewer_canvas_id+"_spinner").spin(opts);
	$("#"+previewer_canvas_id+"_spinner").spin(false);
	$("#"+previewer_canvas_id+"_spinner").css("z-index",-10);

	var viewer = new ChemDoodle.TransformCanvas3D(previewer_canvas_id, 210, 210);
	$("#"+previewer_canvas_id).addClass("selection_preview");
    viewer.specs.set3DRepresentation('Ball and Stick');
    viewer.specs.backgroundColor = '#eeeeee';
    viewer.specs.atoms_useJMOLColors = true;
    
    $("#"+previewer_canvas_id+"_spinner").offset($("#"+previewer_canvas_id).offset());

    // Attach callbacks to active elements
    var button_bindings = {};
    for (var i = 0; i < previewers.length; i++){
    	button_bindings[previewers[i].button_id] = "#"+previewers[i].input_id;
    }
    console.log(button_bindings)
    for(var i = 0; i < previewers.length; i++){
    	console.log("#"+previewers[i].input_id)
    	var input_field_c_id = "#"+previewers[i].input_id;
	    
	    $(input_field_c_id).keypress(function(event) {
			if (event.which == 13 ) {
				event.preventDefault();
				console.log("key triggered")
				do_preview(
						  	"#"+$(this).attr("id"),
							trajectories_dynamic_list_id, 
							base_workspace_field_id, 
							previewer_canvas_id,
							viewer);
			}
	    });
	    
	    $("#"+previewers[i].button_id).click(function(){
	    	console.log($(this).attr("id"));
	    	do_preview(
	    			$(button_bindings[$(this).attr("id")]),
					trajectories_dynamic_list_id,
					base_workspace_field_id,
					previewer_canvas_id,
					viewer);
	    });
    }
}

function do_preview(	
						input_field_id,
						trajectories_dynamic_list_id, 
						base_workspace_field_id, 
						previewer_canvas_id,
						viewer){
	
	var input_field = $(input_field_id);
	$("#"+previewer_canvas_id+"_spinner").spin();
	$("#"+previewer_canvas_id+"_spinner").css("z-index",10); 
	
	var selection = input_field.val();
	var dl = $("#"+trajectories_dynamic_list_id).dynamiclist("getListHandler");
	var pdb_file = dl.value().split(",")[0];
	
	$.ajax({
	     url: "/do_selection",
	     type: "POST",
	     async: true,
	     data: JSON.stringify({
	    	 selection: selection,
	    	 pdb: pdb_file,
	    	 base: $("#"+base_workspace_field_id).val()
	     }),
	     dataType: "text",
	     complete: function(jqXHR, textStatus){
		      var molFile = decodeURIComponent(jqXHR.responseText);
		      if (molFile == "ERROR:ImproductiveSelection"){
		    	  DIALOG.warning("Improoductive selection (returned 0 atoms).");
		    	  input_field.val("");
		    	  viewer.clear();
		      }
		      else {
		    	  if (molFile == "ERROR:MalformedSelection"){
		    		  DIALOG.warning("Malformed selection.");
			    	  input_field.val("");
			    	  viewer.clear();
		      	  }
			      else{
			    	  if (molFile == "EMPTY"){
			    		  DIALOG.warning("Fields cannot be empty.");
				    	  input_field.val("");
				    	  viewer.clear();
			    	  }
			    	  else{
				          var molecule = ChemDoodle.readXYZ(molFile, 1);
					      viewer.loadMolecule(molecule);
				      }
			      }
		      }
		      
		      $("#"+previewer_canvas_id+"_spinner").spin(false);
		      $("#"+previewer_canvas_id+"_spinner").css("z-index",-10);
	     },
	     error:function( jqXHR, textStatus, errorThrown ){
	         alert( "Unexpected Error: " + textStatus+". Is the server working?" );
	         $("#"+previewer_canvas_id+"_spinner").spin(false);
	         $("#"+previewer_canvas_id+"_spinner").css("z-index",-10);
	         input_field.val("");
	         viewer.clear();
	     }
	   });
}
