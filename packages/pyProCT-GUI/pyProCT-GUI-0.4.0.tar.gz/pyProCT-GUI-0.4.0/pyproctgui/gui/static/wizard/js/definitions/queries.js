var QUERIES = (function(){
	var query_types = [
	                   "NumClusters", 
	                   "NumClusteredElems", 
	                   "MeanClusterSize",
	                   "PercentInTop4", 
	                   "PercentInTop", 
	                   "ClustersTo90", 
	                   "Cohesion",
	                   "Compactness", 
	                   "Separation",
	                   "GaussianSeparation",
	                   "NoiseLevel", 
	                   "MirrorCohesion", 
	                   "MinimumMeanSeparation",
	                   "Silhouette", 
	                   "Calinski-Harabasz", 
	                   "Dunn", 
	                   "Davies-Bouldin",
	                   "CythonMirrorCohesion", 
	                   "CythonMinimumMeanSeparation",
	                   "CythonSilhouette", 
	                   "RatioCut", 
	                   "NCut",
	                   "CythonNormNCut", 
	                   "NormNCut", 
	                   "MinMaxCut",
	                   "PCAanalysis", 
	                   "Details"
	                   ];
	
	var criteria_types = [
	                      "MeanClusterSize", 
	                      "CythonMirrorCohesion", 
	                      "Compactness",
	                      "Separation", 
	                      "GaussianSeparation",
	                      "CythonMinimumMeanSeparation", 
	                      "Calinski-Harabasz", 
	                      "Dunn",
	                      "Davies-Bouldin",
	                      "CythonSilhouette", 
	                      "RatioCut", 
	                      "NCut",
	                      "CythonNormNCut", 
	                      "MinMaxCut", 
	                      "PCAanalysis" 
	                      ];

	return {
		query_types:query_types,
		criteria_types:criteria_types
	}
}());
