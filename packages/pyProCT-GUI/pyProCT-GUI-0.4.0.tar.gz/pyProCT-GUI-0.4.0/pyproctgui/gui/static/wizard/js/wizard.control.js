WIZARD.control = (function(){
	
	function forward_move_common(action, event, state){
		var step = $(state.step[0]);
        var step_id = state.step[0].id;
        console.log("FORWD COMMON:",step_id);
        
        var transition_function = WIZARD.control.functions[action][step_id];
        if(typeof transition_function !== "undefined"){
        	var val = transition_function(event, state, step, step_id);
        	if (typeof val === "undefined"){
        		return false;
        	}
        	else{
        		return val;
        	}
        }
        else{
        	// if it does not exist, then it returns true as default.
        	return true;
        }
	};
	
	var setup_wizard = function(action){
       console.log("creating wizard for action", action);
       
       if (action === MAIN_MENU.ADVANCED_ACTION){ 
    	   // Add the algorithm steps 
    	   WIZARD.algorithms.insert_algorithm_steps("#algorithms-1");
    	   
    	   // Initialize wizard, set transition functions etc
	        $("#wizard-wrapper").wizard({
		        stepsWrapper: "#steps_wrapper",
		        
		        forward: ".forward",
		        
		        backward: ".backward",
		
			    onForwardMove: function(event, state) {	
			    	return forward_move_common(action, event, state);
			    },
			    
			    afterForward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			        
			        // detect an algorithm transition
			    	if(step_id.indexOf("algorithm-")!=-1){
			    		var algorithm_id = step_id.substring(10);
			    		if(!$("#algorithms_list").dynamiclist("getListHandler").isAlreadyInTheList(ALGORITHM.titles[algorithm_id])){
			    			$("#wizard-wrapper").wizard("forward",[event,1]);
			    		}
			    	}
			    },
			    
			    afterBackward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			        
			        // detect an algorithm transition
			    	if(step_id.indexOf("algorithm-")!=-1){
			    		var algorithm_id = step_id.substring(10);
			    		if(!$("#algorithms_list").dynamiclist("getListHandler").isAlreadyInTheList(ALGORITHM.titles[algorithm_id])){
			    			$("#wizard-wrapper").wizard("backward",[event,1]);
			    		}
			    	}
			    },
			    // Where to go in transitions
			    transitions: {
				    'matrix_creation_options': function($step, action) {
					    // The branch to go changes to reflect your choice.
					    var branch = $step.find("[name=matrix_creation_options]:checked").val();
					    return branch;
				    }
			    }
	        });
       }
       
       if (action === MAIN_MENU.RESULTS_ACTION){
    	   $("#wizard-wrapper").wizard({
		        stepsWrapper: "#steps_wrapper",
		        
		        forward: ".forward",
		        
		        backward: ".backward",
		        
		        onForwardMove: function(event, state) {	
		        	return forward_move_common(action, event, state);
			    },
			    
			    afterBackward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			    },
			    
			    afterForward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			    }
			    
    	   });
       }
       
       if (action === MAIN_MENU.CLUSTERING_ACTION){
    	   
    	   $("#wizard-wrapper").wizard({
		        stepsWrapper: "#steps_wrapper",
		        
		        forward: ".forward",
		        
		        backward: ".backward",
		        
		        onForwardMove: function(event, state) {	
		        	return forward_move_common(action, event, state);
			    },
			    
			    afterBackward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			    },
			    
			    afterForward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			    },
			    
			    transitions: {
				    'matrix_creation_options': function($step, action) {
					    // The branch to go changes to reflect your choice.
					    var branch = $step.find("[name=matrix_creation_options]:checked").val();
					    return branch;
				    }
			    }
    	   });
       }
       
       if (action === MAIN_MENU.COMPRESS_ACTION){
    	   $("#wizard-wrapper").wizard({
		        stepsWrapper: "#steps_wrapper",
		        
		        forward: ".forward",
		        
		        backward: ".backward",
		        
		        onForwardMove: function(event, state) {	
		        	return forward_move_common(action, event, state);
			    },
			    
			    afterBackward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			    },
			    
			    afterForward:function(event, state) {
			        var step_id = state.step[0].id;
			        GLOBAL.current_step = step_id;
			    },
			    
			    transitions: {
			    	
			    	'clustering_loading_method': function($step, action) {
					    // The branch to go changes to reflect your choice.
					    var branch = $step.find("[name=clustering_generation_method]:checked").val();
					    return branch;
				    },
			    	
				    'matrix_creation_options': function($step, action) {
					    // The branch to go changes to reflect your choice.
					    var branch = $step.find("[name=matrix_creation_options]:checked").val();
					    console.log(branch)
					    return branch;
				    }
			    }
    	   });
       }
       
       // Now add the help and start over buttons
       $("#navigation").append($("<div/>",
    		   {
    	   		'id':"#start_over_button",
    	   		'class':"start_over_button",
    	   		'click':function(){
			    	    	   MAIN_MENU.start_over();
			    			}
    		   }
       ));
       $("#navigation").append($("<div/>",
    		   {
		    	   'id':"#help_button",
		    	   'class':"help_button",
		    	   'click':function(){
		    		   DIALOG.help(GLOBAL.current_step);
		    	   }
    		   }
       ));
       
       
	};
	
	return {
		setup_wizard:setup_wizard,
	};
}());