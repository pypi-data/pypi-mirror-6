var STEPS = (function(){

	var courses = {
			"clustering":[
			              {id:"workspace-1", next:"trajectory-1"},
			              {id:"trajectory-1", next:"matrix_creation-2"},
			              {id:"matrix_creation-2",next:{
								id:"matrix_creation_options",
								branches:{
									"rmsd":[{id:"rmsd-1",next:"criteria-1"}],
									"distance":[{id:"distance-1",next:"criteria-1"}],
								}
							}
			              },
			              {id:"criteria-1",next:"run-1"},
			              {id:"run-1",next:""}
			],

			"advanced":[
						{id:"workspace-1",next:"trajectory-1"},
						{id:"trajectory-1",next:"matrix_creation-1"},
						{id:"matrix_creation-1",next:{
								id:"matrix_creation_options", // transition
								branches:{
									"rmsd":[{id:"rmsd-1",next:"algorithms-1"}],
									"distance":[{id:"distance-1",next:"algorithms-1"}],
									"load":[{id:"load-matrix",next:"algorithms-1"}]
								}
							}
						},
						{id:"algorithms-1",next:""},
						{id:"criteria-1",next:"query-1"},
						{id:"query-1",next:"criteria-2"},
						{id:"criteria-2",next:"run-1"},
						{id:"run-1",next:""}
			],

			"compress":[{id:"workspace-1",next:"clustering-loading-method-1"},
						{id:"clustering-loading-method-1",next:{
								id:"clustering_loading_method",
								branches:{
									"load":[{id:"browse-results-1",next:"compression-options-1"}],

									"generate":[{id:"trajectory-1", next:"matrix_creation-2"},
									            {id:"matrix_creation-2",next:{
														id:"matrix_creation_options",
														branches:{
															"rmsd":[{id:"rmsd-1",next:"criteria-1"}],
															"distance":[{id:"distance-1",next:"criteria-1"}],
														}
													}
									              },
									              {id:"criteria-1",next:"compression-options-1"}],
								}
							}
						},
						{id:"compression-options-1",next:"run-1"},
						{id:"run-1",next:""}

			],

			"results":[
			           {id:"browse-results-1",next:"run-2"},
			           {id:"run-2",next:""}
			]
	};

	var navigation_html = "navigation.html";

	var descriptor = {
		"browse-results-1":{
			"title": "Choose a results folder",
			"html": "browse-results-1.html"
		},
		"workspace-1":{
			"title": "Select the project's workspace folder",
			"html": "workspace-1.html"
		},
		"workspace-2":{
			"title": "Select the project's workspace folder",
			"html": "workspace-2.html"
		},
		"trajectory-1":{
			"title": "Add trajectories to work with",
			"html": "trajectory-1.html"
		},
		"matrix_creation-1":{
			"title": "Choose the matrix obtention method",
			"html": "matrix_creation-1.html"
		},
		"matrix_creation-2":{
			"title": "Choose the matrix obtention method",
			"html": "matrix_creation-2.html"
		},
		"rmsd-1":{
			"title": "Define the part of the molecule used for superposition",
			"html": "rmsd-1.html"
		},
		"distance-1":{
			"title": "Define the part of the molecule used for superposition",
			"html": "distance-1.html"
		},
		"load-matrix":{
			"title": "Choose the matrix file to load",
			"html": "load-matrix.html"
		},
		"algorithms-1":{
			"title": "Choose the algorithms to be used",
			"html": "algorithms-1.html"
		},
		"criteria-1":{
			"title": "Define clustering desired properties",
			"html": "criteria-1.html"
		},
		"query-1":{
			"title": "Getting information from the generated clusterings",
			"html": "query-1.html"
		},
		"criteria-2":{
			"title": "Add selection criteria",
			"html": "criteria-2.html"
		},
		"run-1":{
			"title": "Run",
			"html": "run-1.html"
		},
		"run-2":{
			"title": "Run",
			"html": "run-2.html"
		},
		"clustering-loading-method-1":{
			"title": "Generate or reuse a clustering?",
			"html": "clustering-loading-method-1.html"
		},
		"compression-options-1":{
			"title": "Compression options",
			"html": "compression-options-1.html"
		}
	};

	return {
		courses:courses,
		descriptor:descriptor,
		navigation_html:navigation_html
	};

}());
