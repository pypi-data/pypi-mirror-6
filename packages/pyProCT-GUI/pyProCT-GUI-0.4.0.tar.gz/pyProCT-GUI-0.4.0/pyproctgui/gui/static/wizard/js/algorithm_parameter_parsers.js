/**
 *  Returns the parameters parser for a given algorithm. A parameter parser
 *  is a function whose only parameter is a parameter with the field containing
 *  the fields holding one clustering algorithm parameters.
 *
 *  @param {string} algorithm_type Is the type of algorithm from which we want the parser.
 *
 *  @returns {object} An object composed of parsing functions for each one of the algorithms.
 **/
function get_algorithm_parameter_parsers(algorithm_type){
    var type_to_parser ={   
			                "gromos":parse_gromos_parameters, 
			                "kmedoids": parse_kmedoids_parameters,
			                "hierarchical":parse_hierarchical_parameters,
			                "spectral":parse_spectral_parameters,
			                "dbscan":parse_dbscan_parameters,
			                "random":parse_random_parameters
    };
    return type_to_parser[algorithm_type];
}

function parse_gromos_parameters(my_field){
    var cutoff_list = get_value_of(my_field.find("#cutoff_list"),"list:float");
    
    return bind_parameters({
                            "cutoff":cutoff_list
                            });
}

function parse_hierarchical_parameters(my_field){
    var cutoff_list = get_value_of(my_field.find("#cutoff_list"),"list:float");
    var method = get_value_of(my_field.find("#method_type"));
    
    return bind_parameters({
                            "cutoff":cutoff_list
                            },
                            {
                            "method":method
                            });
}

function parse_dbscan_parameters(my_field){
    var eps_list = get_value_of(my_field.find("#eps_list"),"list:float");
    var minpts_list = get_value_of(my_field.find("#minpts_list"),"list:float");
    
    return bind_parameters({
                                "eps":eps_list,
                                "minpts": minpts_list        
                            });
}

function parse_kmedoids_parameters(my_field){
    var clustering_size_list = get_value_of(my_field.find("#number_of_clusters"),"list:int");
    var seeding_type = get_value_of(my_field.find("#kmedoids_seeding_type"),"selectmenu");
    var tmp_params = {};
    if(seeding_type !== "GROMOS"){
    	tmp_params = bind_parameters({
            "k": clustering_size_list,
           });
    }
    else{
    	console.log("GROMOS SEEDING!!!")
    	var cutoff = get_value_of(my_field.find("#kmedoids_gromos_seeding_cutoff"),"float");
    	
    	tmp_params = combine_parameters(bind_parameters({
            "k": clustering_size_list
           }),"seeding_max_cutoff",[cutoff]);
    	console.log(tmp_params);
    }
    return combine_parameters(tmp_params,
	                            "seeding_type",[seeding_type]);
}

function parse_spectral_parameters(my_field){
    var sigma_list = get_value_of(my_field.find("#sigma"),"list:float");
    var k_list = get_value_of(my_field.find("#number_of_clusters"),"list:int");
    
    return combine_parameters(bind_parameters({
                                                //"use_k_medoids": ,
                                                "k": k_list        
                                                }), 
                                                "sigma", sigma_list );
}

function parse_random_parameters(my_field){
    var number_of_clusters_list = get_value_of(my_field.find("#number_of_clusters"),"list:int");
    
    return bind_parameters({
                             "num_clusters": number_of_clusters_list      
                            });
}


/**
 *  Creates a copy of one parameter.
 *   
 *  @param {object} this_param  Is the param to be copied.
 *   
 *  @returns {object} A copy of the parameter. 
 **/
function clone_param(this_param){
    var cloned = {};
    for (key in this_param){
        cloned[key] = this_param[key];
    }
    return cloned;
}

/**
 *   Extends a parameter list with an attribute that can have diverse values.
 *   For instance, extending [{"a":3,"b":4},{"d":7}] with "c" = [5,6] would produce:
 *   [{"a":3,"b":4,"c":5} , {"a":3,"b":4,"c":6}, {"d":7,"c":5}, {"d":7,"c":6}]
 *
 * 	 @param this_parameters
 * 
 * 	 @param with_this_parameter
 * 
 * 	 @param with_this_values
 * 
 * 	 @returns {list}
 **/
function combine_parameters(this_parameters, with_this_parameter, with_this_values){
    var extended_parameters = [];
    for(var i = 0; i < with_this_values.length; i++){
        for(var j = 0; j < this_parameters.length; j++){
           var new_param = clone_param(this_parameters[j]);
           new_param[with_this_parameter] =  with_this_values[i];
           extended_parameters.push(new_param);
        }
    }
    return extended_parameters;
}

/**
 *   Generates the parameters for one or more list of values.
 *   Example:
 *   bind_parameters({"a":[1,2],"b":[3,4]}) == [{"a":1,"b":3},{"a":2,"b":4}]
 *   bind_parameters({"a":[1,2],"b":[3,4]},{"d":2}) ==  [{"a":1,"b":3,"d":2},{"a":2,"b":4,"d":2}]
 *
 *   @param {As. Array} lists_dic is a dictionary where the key will be the name of the parameter,
 *   and the value for this key will be the list of values for this parameter.
 *
 *   @param {As. Array} singular a dictionary with values that remain constant for all parameters.
 *
 *   @returns {list} A list of parameters.      
 **/
function bind_parameters(lists_dic, singular){
    var parameters = [];
    
    // Pick the length of the last list
    var len = 0;
    for (var key in lists_dic) {
        len = lists_dic[key].length;
    }
    
    // Create parameters from lists
    for(var i = 0; i < len; i++){
        var parameter = {};
        for(name in lists_dic){
            parameter[name] = lists_dic[name][i]; 
        }
        parameters.push(parameter);
    }
    
    // Singular values
    if(singular != undefined){
        for(var i = 0; i < len; i++){
            for(sing in singular){
                parameters[i][sing] = singular[sing];
            }
        }
    }
    
    return parameters;
}