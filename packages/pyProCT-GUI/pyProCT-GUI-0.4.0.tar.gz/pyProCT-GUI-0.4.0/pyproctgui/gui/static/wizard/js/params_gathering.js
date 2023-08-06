
function fulfills_dependencies(parameter_description){
	var fulfilled;
	// If we have defined dependencies
	if( typeof parameter_description.depends_on !== "undefined" ){
		// Then check each dependency
		fulfilled = false;

		for (var depends_on_this_field in parameter_description.depends_on){
			if(depends_on_this_field.substring(0,8) === "function"){
				// Then it must be a function
				var exe_function = parameter_description.depends_on[depends_on_this_field];
				if (typeof exe_function === "function"){
					fulfilled = fulfilled || exe_function();
				}
				else{
					throw "[ERROR in fulfills_this_dependency] "+ depends_on_this_field+" is not a function."
				}
			}
			else{
				var field = find_target_field(depends_on_this_field);
				// Check the dependency only if the field exists
				if (field !== "undefined" && field.length > 0){
					// console.log("PARAMETER UNDER CHECK:",field_id, "OVER",parameter_description.depends_on,field);
					// Each dependency is an array of dictionaries representing single dependencies.
					// One dependency is fulfilled if any of this dicts is fulfilled.

					var dependencies_array = parameter_description.depends_on[depends_on_this_field];
					for (var i =0; i < dependencies_array.length; i++){
						var dependency = dependencies_array[i];
						// OR outside, AND inside
						fulfilled = fulfilled || fulfills_this_dependency(field,dependency);
					}
				}
			}
		}
	}
	else{
		fulfilled = true;
	}
	return fulfilled;
}

/**
 Says if a dependency is fulfilled or not. A dependency is a dictionary in whihc keys can be "value", "list contains" or function ids
 with a function.
**/
function fulfills_this_dependency(field, dependency){
	var fulfilled = true;
	for (var dependency_type in dependency){
		var dependency_value = dependency[dependency_type];
		switch(dependency_type){
			// single values
			case "value":
				fulfilled = fulfilled && get_value_of( field, field.type) === dependency_value;
				break;
			// only for lists
			case "list contains":
				fulfilled = fulfilled && get_value_of(field, "list").indexOf(dependency_value) != -1;
				break;
			default:

				throw "[ERROR in fulfills_this_dependency] "+dependency_type+" is an unexpected dependency key."
				break;
		}
	}
	return fulfilled;
}

function get_default_value(default_field){

	if (default_field === undefined){
		return undefined;
	}

	var default_type = Object.keys(default_field)[0];
	var default_value = default_field[default_type];

	switch(default_type){
		case "value":
			return default_value;
			break;

		case "function":
			return default_value();
			break;

		default:
			return undefined;
	};
}

/**
 * Generates a representation of the parameters that will be used by pyProClust
 *
 * @returns {object} The parameters object.
 */
function create_parameters(selected_algorithms){
	var parameter_descriptions = PARAMETER_DESCRIPTORS.descriptors;
	var field = "undefined";
	var value, description,dependencies_fulfilled;
	var parameters = {};
	var algorithm_type, parameter_parser, algorithm_field, guess_params_checkbox;

	// Gather all defined parameters
	for (var id_or_name in parameter_descriptions){
		field = find_target_field(id_or_name);
		description = parameter_descriptions[id_or_name];
		dependencies_fulfilled = fulfills_dependencies(description);
		console.log("Working with ", id_or_name, ":");
		console.log("\tChecking dependencies:", dependencies_fulfilled);

		if(field !== "undefined"){
		// We found the field, so it must be user-defined
			console.log("\tField found.");
			value = get_value_of(field, description.type);
			if(dependencies_fulfilled){
				console.log("\tDependencies ok. Value", value);
				set_dictionary_entry(
						parameters,
						description.maps_to.split(":"),
						value);
			}
		}
		else{
		// We did not find the field, if needed (dependencies are ok) we have to add the
		// default value. We check that it was not alreay defined!
			console.log("\tField not found.");
			if (!is_defined(parameters,description.maps_to.split(":"))
				&& dependencies_fulfilled){
				var default_value = get_default_value(description.defaults_to);

				if (typeof default_value !== "undefined"){
					set_dictionary_entry(
							parameters,
							description.maps_to.split(":"),
							default_value);
					console.log("\tDefault value found.");
				}
				else{
					value = "not defined";
					console.log("\tDefault value not found.");
				}
			}
		}
	}

 	// Now gather algorithm's parameters from algorithm steps (if any)
 	for(var i = 0; i < GLOBAL.selected_algorithms.length; i++){
 		algorithm_type = ALGORITHM.titles_reverse[GLOBAL.selected_algorithms[i]];
 		algorithm_field = find_target_field("algorithm-"+algorithm_type);

 		// If the wizard step is defined...
 		if (algorithm_field !== "undefined"){
 			// Do we want pyProClust to calculate the parameters itself?
 			guess_params_checkbox = algorithm_field.find("#guess_params_"+algorithm_type);
 			if(!guess_params_checkbox.is(":checked")){
	 			parameter_parser = get_algorithm_parameter_parsers(algorithm_type);
 				set_dictionary_entry(
 						parameters,
 						["clustering","algorithms",algorithm_type,"parameters"],
 						parameter_parser(algorithm_field));
 			}
 		}
 	}
	return parameters;
}

/**
 * Sets all known fields to their default values.
 */
function set_defaults_to_fields(){
	var parameter_descriptions = PARAMETER_DESCRIPTORS.descriptors;
	var field = "undefined";

	// Gather all defined parameters
	for (var id_or_name in parameter_descriptions){
		description = parameter_descriptions[id_or_name];

		//Search a parameter holder
		field = find_target_field(id_or_name);
		if(field !== "undefined"){
			var default_value = get_default_value(description.defaults_to);
			if(typeof default_value !== "undefined"){
				set_value_of(field,
							default_value,
							description.type);
			}
		}
	}
}
