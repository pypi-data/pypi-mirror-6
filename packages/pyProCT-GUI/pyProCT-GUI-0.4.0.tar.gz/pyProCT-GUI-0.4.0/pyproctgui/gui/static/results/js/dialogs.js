var DIALOGS = (function(){
	
	var show_molecule_dialog = function(molecule_text){
		$("<div/>", { 
	    	id:'preview_dialog',
	    	title: "Previewer",
	    	html: "<div id ='previewer_wrapper'> <canvas id ='previewer_canvas'> Canvas/HTML5 is not supported. </canvas> </div>"})
	    	.dialog({
	                modal:true, 
	                autoResize:true,
	                width:'auto',
	                create:function(event, ui){
	                	var viewer = new ChemDoodle.TransformCanvas3D('previewer_canvas',
	                			parseInt($("#previewer_wrapper").css("width")), 
	                			parseInt($("#previewer_wrapper").css("height")));
	            		//viewer.specs.set3DRepresentation('Ball and Stick');
	            	    viewer.specs.backgroundColor = '#eeeeee';
	            	    viewer.specs.atoms_useJMOLColors = true;
	            	    viewer.clear();
	            	    var molecule = ChemDoodle.readPDB(molecule_text, 1);
	            	    viewer.loadMolecule(molecule);
	                },
	                close: function( event, ui ){
	                    $(this).dialog("destroy");
	                }
	    });
	};
	
	var show_all_molecules_dialog = function(molecules_text_array, cluster_ids, spinner_id){
		$("<div/>", { 
	    	id:'preview_dialog',
	    	title: "Previewer",
	    	html: "<div id = previewers_wrapper><div>"})
	    	.dialog({
	                modal:true, 
	                
	                autoResize:false,
	                
	                width:'auto',
	                
	                create:function(event, ui){
	                	for (var i = 0; i < molecules_text_array.length;i++){
	                		$("#previewers_wrapper").append("<div id ='previewer_wrapper_"+i
	                				+"' class='small_wrapper'> <canvas id ='previewer_canvas_"+i
	                				+"'> Canvas/HTML5 is not supported. </canvas> <div class='small_wrapper_cluster_id'><i>"+cluster_ids[i]
	                				+"</i></div></div>");
		                	
	                		var viewer = new ChemDoodle.TransformCanvas3D('previewer_canvas_'+i,
		                			parseInt($("#previewer_wrapper_"+i).css("width")), 
		                			parseInt($("#previewer_wrapper_"+i).css("height")));
		            		
		                	//viewer.specs.set3DRepresentation('Ball and Stick');
		            	    viewer.specs.backgroundColor = '#eeeeee';
		            	    viewer.specs.atoms_useJMOLColors = true;
		            	    viewer.clear();
		            	    var molecule = ChemDoodle.readPDB(molecules_text_array[i], 1);
		            	    viewer.loadMolecule(molecule);
		            	    
		            	    // Change canvas style
		            	    $("#previewer_canvas_"+i).css({
		            	    	"border": "1px dotted grey",
		            	    });
	                	}
	                },
	                close: function( event, ui ){
	                    $(this).dialog("destroy");
	                }
	    });
	};
	
	return {
		show_molecule_dialog:show_molecule_dialog,
		show_all_molecules_dialog:show_all_molecules_dialog
	};
}());