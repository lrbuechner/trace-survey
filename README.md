# TRACE Survey 

This is a component of a larger project to create a robust outlier detection algorithm for fixed-income transactions in FINRAS's Trade Reporting and Compliance Engine (TRACE). This survey was created to have professional financiers / researchers classify anomalies in time series data in order to have test data upon which to optimize our algorithms paramaters. 

You can try it out [here](https://trace-survey.herokuapp.com/).

## IMPORTANT

There is a csv hosted on heroku that is read with pandas upon session creation 
The final stage of the project is to use SQL to query each CUSIP at a time from a parent database in the cloud, instead of loading it all at once. I originally just used a csv for prototyping. This final phase is almost complete. 

## Directions
Use the selection tools provided on the scatter plot to select multiple points. Without holding shift during your selection, your previous selection will be forgotten. By holding shift and either clicking/lassoing points, you can select multiple points. 

Additionally, the 'Summary' tab displays the state of your information and indicies of your selected points prior to being stored in a database hosted on Heroku. This is just is/was the current state of the project and I thought it would be approptiate to use as the version to post on GitHub. 

Lastly, the data being used is just a subset of the bonds that will be in the live survey. 
