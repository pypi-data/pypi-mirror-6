/**
 *   Helper function to get the value of an undetermined control.
 *
 *   @param {string} of_this_control The control we want to get the value.
 *
 *   @param {string} type A hint of the control type.
 *
 *   @returns {string/float/int/list/object} The value of the control.
 **/
function get_value_of(of_this_control, type){

    if (type == undefined){
        type = $(of_this_control).attr("type");
    }

    switch(type){
        case "list:float":
            return parse_list( of_this_control, parseFloat);

        case "list:int":
            return parse_list( of_this_control, parseInt);

        case "list":
        	return $(of_this_control).dynamiclist("getItems");

        case "list:criteria":
        	return parse_criteria($(of_this_control).dynamiclist("getItems"));

        case "text":
            return $(of_this_control).val();

        case "checkbox":
            return $(of_this_control).is(":checked");

        case "radio":
        	var name = $(of_this_control).attr('name');
        	var radiobutton = $($.find("[name='"+name+"']:checked"));
            return radiobutton.attr('value');

        case "int":
            return parseInt($(of_this_control).val());

        case "float":
            return parseFloat($(of_this_control).val());

        case "selectmenu":
        	return $(of_this_control).val();

        default:
            return $(of_this_control).val();
    }
}

/**
 * 	Sets the value of a field (jQuery object).
 *
 * @param {jQuery Object} this_field Field to set its value.
 * @param value The value we want to set.
 * @param {String} type Type of the field.
 */
function set_value_of(this_field, value, type){
	switch(type){
	    case "list:float":
	        $(this_field).val(""+value);
	        break;
	    case "list:int":
	    	$(this_field).val(""+value);
	        break;
	    case "list":
	    	$(this_field).dynamiclist("setItems",
	    									value);
	    	break;
	    case "list:criteria":
	    	$(this_field).dynamiclist("setItems",
	    									criteria_object_to_string(value));
	    	break;
	    case "checkbox":
	        $(this_field).prop('checked', value);
	        break;
	    case "radio":
	    	break;
	    default:
	    	$(this_field).val(value);
	}
}

/**
 * Converts a criteria object (as the one in parameters) to strings. Is the opposite operation of
 * 'parse_criteria' .
 *
 * @param {Object} value An object of objects containing all the criteria.
 *
 * @returns {Array} List containing the string representation of each criteria.
 */
function criteria_object_to_string (value){
	var criteria;
	var result_strings = [];
	var current_string;
	for (criteria_id in value){
		criteria = value[criteria_id];
		current_string = "";
		for (metric_id in criteria){
			if(criteria[metric_id]["action"] == ">"){
				current_string += "Maximize ";
			}
			else{
				current_string += "Minimize ";
			}
			current_string += metric_id+" (weight: "+criteria[metric_id]["weight"]+") and ";
		}
		result_strings.push(current_string.substring(0, current_string.length - 4));
	}
	return result_strings;
}
/**
 *   Parses the contents of a text control holding a list of numbers description. This list can
 *   have two forms:
 *  - Comma separated list of numbers Ex. "1, 2, 3, 4"
 *  - Range with this form : start, end : step  Ex. "4, 14 :2"  = "4, 6, 8, 10, 12"
 *
 *   @param {String} in_this_control The control holding the list.
 *
 *   @param {Function} using_this_conversor Function that, given a string, returns its numeric
 *   representation (Ex. parseInt)
 *
 *   @returns {Array} The expected list of numbers.
 **/
function parse_list( in_this_control, using_this_conversor){

    var conversor;
    var list_string = "";

    // Default value for conversor
    if (using_this_conversor == undefined){
        conversor = parseInt;
    }
    else{
        conversor = using_this_conversor;
    }

    try{
        // Getting value
        list_string = $(in_this_control).val();

        // Remove non dot, colon digit or character
        list_string = list_string.replace(/[^\d,.:]+/g, '');

        var sequence = [];

        // Analyze the string
        var parts = list_string.split(":");
        if (parts.length == 2){
            // Is the description of a range i,j :step, those can only be integers
            var range_parts = parts[0].split(",");
            if( range_parts.length != 2){
                return undefined;
            }
            var i = Math.abs(parseInt(range_parts[0]));
            var j = Math.abs(parseInt(range_parts[1]));
            if( isNaN(i) || isNaN(j)){
                return undefined;
            }
            var step = parseInt(parts[1]);

            for(var k = i; k<j; k+=step){
                sequence.push(k);
            }
        }
        else {
            // The list is a comma-separated sequence of numbers
            var string_sequence = parts[0].split(",");
            for(var i = 0; i < string_sequence.length; i++){
                var value = Math.abs(conversor(string_sequence[i]));
                if(!isNaN(value)){
                    sequence.push(value);
                }
            }
        }
    }
    catch(error_message){
        throw "There was an error while parsing this list:["+list_string+"]. Error was: "+error_mesage;
    }
    return sequence;
}

/**
 * Checks if a list in string format is ok or not.
 *
 * @param {String} string_list String representation of a list.
 *
 * @returns {Boolean}  Whether if the string list has list format or not.
 */
function has_list_format( string_list ){
	var list =  /\s*(?:\d+\.*\d*)\s*(?:,{1}\s*(?:\d+\.*\d*)\s*)*\s*$/;
	var compressed_list = /\s*\d+\.*\d*\s*,{1}\s*\d+\.*\d*\s*:\s*\d+\.*\d*\s*$/;
	return list.test(string_list) || compressed_list.test(string_list);
}

/**
 *	Given a list of string representations of criteria, creates a dictionary of objects defining them.
 *
 *	@param {Array} list_of_criteria Is the list of string representations of criteria.
 *
 *	@returns {Object} An object indexed by criteria name with the criteria representations.
 *
 **/
function parse_criteria(list_of_criteria){
    var all_criteria = {};
    for (var i = 0; i < list_of_criteria.length; i++){
        all_criteria["criteria_"+i] = parse_one_criteria(list_of_criteria[i]);
    }
    return all_criteria;
}

/**
 *	Converts one criteria string into a criteria object.
 *
 *	@param {String} criteria String representation of a criteria (and separated list).
 *
 *	@returns {Object} The object representation of that criteria.
 **/
function parse_one_criteria(criteria){
    var criterium_strings = criteria.split("and");
    var criteria = {};
    var criterium;

    for (var i = 0; i < criterium_strings.length; i++){
    	criterium = parse_criterium(criterium_strings[i]);
    	criteria[criterium["query"]] = {
                "action":criterium["action"],
                "weight":criterium["weight"]
    	};
    }
    return criteria;
}

/**
 *	Transforms one criterium into its object representation.
 *
 *	@param {String} criterium The criterium we want to convert.
 *
 *	@returns {Object} Its object representation.
 **/
function parse_criterium(criterium_string){
	var regex = /\s*(Minimize|Maximize)\s{1}(\w*)\s{1}\(weight:\s{1}(\d+\.*\d*)\)\s*/;
	var parts = regex.exec(criterium_string);
	var criterium = {
    		"query": "undefined",
    		"action":"undefined",
    		"weight": 1.0
    };

    criterium["action"] = "undefined";

    if(parts[1] == "Maximize"){
        criterium["action"] = ">";
    }

    if(parts[1] == "Minimize"){
        criterium["action"] = "<";
    }
    criterium["query"] = parts[2];

    criterium["weight"] = parseFloat(parts[3]);

    return criterium;
}


/**
 *	This function recursively generates a dictionary of objects in order to give a final
 *	value to its ending tag.
 *	Example: for a key list ["foo","bar","pi"] and value 3.1415, it will create:
 *
 *	{
 *		"foo":{
 *			"bar":{
 *				"pi":3.1415
 *			}
 *		}
 *	}
 *
 *	If called again, for instance with key list ["foo","lol"] and value [1,2], the resulting
 *	object will be:
 *
 *  {
 *		"foo":{
 *			"bar":{
 *				"pi":3.1415
 *			},
 *			"lol":[1,2]
 *		}
 *	}
 *
 * @param {Object} this_dictionary A dictionary where the new keys and values will be inserted.
 *
 * @param {Array} key_list The in-depth dictionary key representation
 *
 * @param {String|Int|Float|List|Object} value The value the field will have.
 *
 * @param {Int} key_index Index for recursive handling.
 */
function set_dictionary_entry( 	this_dictionary,
								key_list,
								value,
								key_index){

	var index;
	if (typeof key_index == "undefined"){
		index = 0;
	}
	else{
		index = key_index;
	}

    if (index == key_list.length-1){
		this_dictionary[key_list[index]] = value;
    }
    else{

		if(this_dictionary[key_list[index]] == undefined){
		    this_dictionary[key_list[index]] = {};
		}

		set_dictionary_entry(this_dictionary[key_list[index]],
							key_list,
							value,
							index+1);
    }
}

/**
 * Searches for a document object with the provided id or name.
 *
 * @param {String} id_or_name Name or Id of the field we want to retrieve.
 *
 * @returns {jQuery Object | String} The field or "undefined".
 */
function find_target_field(id_or_name){
	var field_by_id = $("[id='"+id_or_name+"']");
	var field_by_name = $("[name='"+id_or_name+"']");

	if(field_by_id.length != 0) return field_by_id;
	if(field_by_name.length != 0) return field_by_name;

	return "undefined";
}


function is_defined(dict, in_depth_keys, index){
	var f_index = 0;

	if(typeof index !== "undefined"){
		f_index = index;
	}

	if (index == in_depth_keys.length){
		return true;
	}

	if (typeof dict[in_depth_keys] == "undefined"){
		return false;
	}
	else{
		return is_defined(dict, in_depth_keys, index+1);
	}
}

/**
 * Chaks if a number is an integer. From: http://stackoverflow.com/questions/3885817/how-to-check-if-a-number-is-float-or-integer
 * @param n Number to test
 *
 * @returns {Boolean} Wether if n is an integer or not
 */
function isInt(n) {
   return typeof n === 'number' && parseFloat(n) == parseInt(n, 10) && !isNaN(n);
}
