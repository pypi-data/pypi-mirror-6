var ALGORITHM = (function(){
	
	var clustering_algorithm_titles = { "gromos":"GROMOS Algorithm", 
	                                    "kmedoids":"K-Medoids Algorithm",
	                                    "hierarchical":"Hierarchical Algorithm",
	                                    "spectral":"Spectral Algorithm",
	                                    "dbscan":"DBSCAN Algorithm",
	                                    "random":"Random Algorithm"};
	                                    
	var clustering_algorithm_titles_reverse = { "GROMOS Algorithm":"gromos", 
	                                            "K-Medoids Algorithm":"kmedoids",
	                                            "Hierarchical Algorithm":"hierarchical",
	                                            "Spectral Algorithm":"spectral",
	                                            "DBSCAN Algorithm":"dbscan",
	                                            "Random Algorithm":"random"};
	
	return{
		titles: clustering_algorithm_titles,
		titles_reverse: clustering_algorithm_titles_reverse,
		types: Object.keys(clustering_algorithm_titles)
	};

}());