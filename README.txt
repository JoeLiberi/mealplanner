# Clean Meal Planner

## Objective

This "Clean Meal Planner" will look for clean meals on www.reddit.com/r/fitmeals for clean 
recepies and build a weekly meal plan and shopping list. It will be built out as a web app using 
the most recent version of Django

## Models

 - Reddit bot for scrapping the meals from reddit
 	- will constantly pole reddit (maybe every day) and grab posts submitted to "self.fitmeals" 
 	and that have valid tags
 	- will sort through submissions and provide tags accordingly
 - Breakfast, lunch and dinner model
 	- obviosly will lay out breakfast lunch and dinner for each day
 - Shopping list generator
 - Meal planner generator
 - Email or notification
 - 

### How r/fitmeals tag posts

 - It uses square brakets to apply flair. 

