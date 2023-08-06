var PARAMETER_DESCRIPTORS = (function (){
		return{
			descriptors: {
					'workspace_base':{
						type: 'text',
						maps_to:'global:workspace:base'
					},
//
// 					// In case we are working with compress, this is the one which will be used
// 					'trajectory_list_compress':{
// 						maps_to:'data:files',
// 						defaults_to: {"function":function(){return GLOBAL.loaded_files;}},
// 						depends_on: {
// 							"function_global_action_is_compress":function(){
// 									return GLOBAL.selected_action === "compress";
// 							}
// 						}
// 					},
//
// 					// If we are not compressing, this one will be used.
// 					'trajectory_list':{
// 						type:'list',
// 						maps_to:'data:files',
// 						depends_on: {
// 							"function_global_action_is_compress":function(){
// 									return GLOBAL.selected_action !== "compress";
// 							}
// 						}
// 					},
//
					'trajectory_list_':{
						type:'list',
						maps_to:'data:files',
						defaults_to: {
							"function":function (){
								var value = get_value_of("#clustering_creation_generate","radio");
								// compress can use an already generated clustering
								if (GLOBAL.selected_action === "compress"){
									// but only if 'load' generation method is selected
									if (value === "load"){
										console.log("We have to load")
										// then, it return loaded files
										console.log("GLOBAL FILES", GLOBAL.loaded_files)
										return GLOBAL.loaded_files;
									}
									else{
										console.log("We do not have to load")
										// if not, it returns the current contents of the trajectory list
										return get_value_of("#trajectory_list","list");
									}
								}
								else{
									console.log("We are not compressing")
									return get_value_of("#trajectory_list","list");
								}
							}
						}
					},

					'matrix_creation_options':{
						type:'radio',
						maps_to:'data:matrix:method'
					},

					'matrix_save_path':{
						type:'text',
						maps_to:'data:matrix:filename',
						defaults_to: {"value": "matrix"}
					},

					'rmsd_fit_selection':{
						type:'text',
						maps_to:'data:matrix:parameters:fit_selection',
						defaults_to: {"value":  "name CA"},
						depends_on: {'matrix_creation_options':[{"value":"rmsd"}]}
					},

					'rmsd_calc_selection':{
						type:'text',
						maps_to:'data:matrix:parameters:calc_selection',
						defaults_to: {"value":  "name CA"},
						depends_on: {'matrix_creation_options':[{"value":"rmsd"}]}
					},

					'dist_fit_selection':{
						type:'text',
						maps_to:'data:matrix:parameters:dist_fit_selection',
						defaults_to: {"value":  "name CA"},
						depends_on: {'matrix_creation_options':[{"value":"distance"}]}
					},

					'dist_calc_selection':{
						type:'text',
						maps_to:'data:matrix:parameters:body_selection',
						defaults_to: {"value":  "name CA"},
						depends_on: {'matrix_creation_options':[{"value":"distance"}]}
					},

					'matrix_creation_path':{
						type:'text',
						maps_to:'data:matrix:parameters:path',
						depends_on: {'matrix_creation_options':[{"value":"load"}]}
					},

					"matrix_calculator":{
						type:'text',
						maps_to:'data:matrix:parameters:calculator_type',
						defaults_to: {"value":  "QCP_OMP_CALCULATOR"}
					},

					'evaluation_maximum_noise':{
						type:'float',
						maps_to:'clustering:evaluation:maximum_noise',
						defaults_to: {"value":  15.0}
					},

					'evaluation_minimum_clusters':{
						type:'int',
						maps_to:'clustering:evaluation:minimum_clusters',
						defaults_to: {"value":  10}
					},

					'evaluation_maximum_clusters':{
						type:'int',
						maps_to:'clustering:evaluation:maximum_clusters',
						defaults_to: {"value":  30}
					},

					'evaluation_minimum_cluster_size':{
						type:'int',
						maps_to:'clustering:evaluation:minimum_cluster_size',
						defaults_to: {"value":  50}
					},

					'query_list':{
						type:'list',
						maps_to:'clustering:evaluation:query_types',
						defaults_to: {"value": ["NumClusters", "NoiseLevel", "MeanClusterSize"]}
					},

					'criteria_list':{
						type:'list:criteria',
						maps_to:'clustering:evaluation:evaluation_criteria',
						defaults_to: {"value":  {
										"criteria_0": { "CythonSilhouette":{"action": ">","weight": 3},
			                                         	"CythonMirrorCohesion":{"action": ">","weight": 2}
										}
							}
						}
					},

//
//		ALGORITHMS
//
 					'gromos_algorithm_default_use':{
 						maps_to:'clustering:algorithms:gromos',
 						defaults_to: {"value":{"max":  25}},
 						depends_on: {
 							// If it is not advanced mode, all algorithms are used
 							"function":function(){
 								return GLOBAL.selected_action !== "advanced";
 							},
 							// else we add it if it is into the list
 							'algorithms_list':[{"list contains":"GROMOS Algorithm"}]
 						}
 					},

 					'hierarchical_algorithm_default_use':{
 						maps_to:'clustering:algorithms:hierarchical',
 						defaults_to: {"value":{}},
 						depends_on: {
 							"function":function(){
 								return GLOBAL.selected_action !== "advanced";
 							},
 							'algorithms_list':[{"list contains":"Hierarchical Algorithm"}]
 						}
 					},

 					'kmedoids_algorithm_default_use':{
 						maps_to:'clustering:algorithms:kmedoids',
 						defaults_to: {"value":{"max":  25}},
 						depends_on: {
 							"function":function(){
 								return GLOBAL.selected_action !== "advanced";
 							},
 							'algorithms_list':[{"list contains":"K-Medoids Algorithm"}]
 						}
 					},

 					'spectral_algorithm_default_use':{
 						maps_to:'clustering:algorithms:spectral',
 						defaults_to: {"value":{"max":  25}},
 						depends_on: {
 							"function":function(){
 								return GLOBAL.selected_action !== "advanced";
 							},
 							'algorithms_list':[{"list contains":"Spectral Algorithm"}]
 						}
 					},

 					'dbscan_algorithm_default_use':{
 						maps_to:'clustering:algorithms:dbscan',
 						defaults_to: {"value":{}},
 						depends_on: {
 							"function":function(){
 								return GLOBAL.selected_action !== "advanced";
 							},
 							'algorithms_list':[{"list contains":"DBSCAN Algorithm"}]
 						}
 					},

//
//		CONTROL
//
					'number_of_processors':{
						maps_to:'global:control:number_of_processes',
						defaults_to: {"value":  6}
					},

					'scheduler_type':{
						type: 'string',
						maps_to:'global:control:scheduler_type',
						defaults_to: {"value":  "Process/Parallel"}
					},

//
//		CLUSTERING GENERATION
//
					'clustering_generation_method':{
						type:'radio',
						maps_to:'clustering:generation:method',
						defaults_to: {"value":  "generate"}
					},

					'clustering_loading_path':{
						type: 'string',
						defaults_to: {"function":function(){return GLOBAL.loaded_clustering["clustering"]["clusters"];}},
						maps_to: 'clustering:generation:clusters',
						depends_on: {'clustering_generation_method':[{"value":"load"}]},
					},
//
//		POSTPROCESSING
//

					'representatives':{
						defaults_to: {"value":
							{
							'keep_remarks':false,
							'keep_frame_number':false
							}
						},
						maps_to: 'postprocess:representatives'
					},

					'pdb_clusters':{
						defaults_to: {"value":
							{
							'keep_remarks':false,
							'keep_frame_number':false
							}
						},
						maps_to: 'postprocess:pdb_clusters'
					},

					'rmsf':{
						defaults_to: {"value":{}},
						maps_to: 'postprocess:rmsf',
						depends_on: {'matrix_creation_options':[{"value":"rmsd"}]}
					},

					'centers_and_trace':{
						defaults_to: {"value":{}},
						maps_to: 'postprocess:centers_and_trace',
						depends_on: {'matrix_creation_options':[{"value":"distance"}]}
					},


					'final_frames':{
						type: 'int',
						depends_on: {
							"function_global_action_is_compress":function(){
									return GLOBAL.selected_action === "compress";
							}
						},
						maps_to: 'postprocess:compression:final_number_of_frames',
					},

					'compression_type':{
						type: 'selectmenu',
						defaults_to: {"value": "KMEDOIDS"},
						depends_on: {
							"function_global_action_is_compress":function(){
									return GLOBAL.selected_action === "compress";
							}
						},
						maps_to: 'postprocess:compression:type',
					}

				},

		};
}());
