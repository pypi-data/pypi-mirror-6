## Defining your hipotesis (II)
Use the list to add as many criteria you need to define your clustering hypothesis. Each criteria comprises a set of queries (more commonly measures and Internal Validity Indices) that will be used
to calculate a score. The best clustering (the one which will be selected as result of this job) will be the one that gets a better scoring for **all** criteria.
Use the list widget to add or remove new criteria (using the "*Add*" and "*Remove*" buttons).
When clicking the "*Add*" button a small window will appear. Use the controls on this window to define the new criteria you want to add. Change the weights
of queries in order to give more or less importance to one query respect to the others. One query with weight 4 will have twice the contribution to the final
score than one with weight 2 (weights are always relative to the biggest weight). A query is selected when its weight is > 0. Tag the query as "Maximize" if you want
pyProCT to maximize its value, or "Minimize" if you want it to minimize the value.
You can remove any criteria by selecting them and clicking the "*Remove*" button.
See [this]() and [this]() to get more insigth about the different types of measures, queries and an explanation about criteria.