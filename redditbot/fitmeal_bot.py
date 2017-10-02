from praw import Reddit
import re, sqlite3
from sqlite3 import Error
import os 

title_regex = re.compile(r'\[\w+\s\w+\]\s(.+)')
flair_regex = re.compile(r'\[\w+\s\w+\]')
recipeurl_regex = re.compile(r'Recipe: \[.+\]\((.+)\)')
nutrition_regex = re.compile(r'Nutrition Info: (.+)')
preptime_regex = re.compile(r'Prep Time\s(.+)')
cooktime_regex = re.compile(r'Cook Time\s(.+)')
servings_regex = re.compile(r'Servings\s(.+)')
ingredients_regex = re.compile(r'\*\s.+', re.MULTILINE)
instructions_regex = re.compile(r'\d\.\s.+', re.MULTILINE)

# Create the projects table	
sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS fitmeal (title text PRIMARY KEY,flair text,recipeurl text,nutrition text,preptime text,cooktime text,servings text,ingredients text, instructions text); """

dir_path = os.path.dirname(os.path.realpath(__file__))
database = "{}/fitmeal.db".format(dir_path)


class FitMealBot():

	def __init__(self):
		self.dir_path = os.path.dirname(os.path.realpath(__file__))
		self.database = "{}/fitmeal.db".format(dir_path)
		self.sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS fitmeal (
			title text PRIMARY KEY,
			flair text,
			recipeurl text,
			nutrition text,
			preptime text,
			cooktime text,
			servings text,
			ingredients text, 
			instructions text); """

		# Create the database when the class is initialized
		self.conn = self.sqlite_connect()
		if self.conn is not None:
			# create projects table
			self.create_table()
		else:
			print("Error! cannot create the database connection.")

	def sqlite_connect(self):

		try:
			conn = sqlite3.connect(self.database)
			return conn
		except Error as e:
			print(e)

		return None

	def create_table(self):

		try:
			c = self.conn.cursor()
			c.execute(self.sql_create_projects_table)
		except Error as e:
			print(e)

	def filter_title(self, posts, regex):

		s = []
		for p in posts:
			if regex.match(p.title):
				s.append(p)

		return s


	def run_bot(self):

		print("Running.......")

		reddit = Reddit('mealplanner')

		subreddit = reddit.subreddit("fitmeals")

		submissions = self.filter_title(subreddit.hot(), title_regex)

		for s in submissions:
			title = title_regex.search(s.title)
			flair = flair_regex.findall(s.title)
			recipeurl = recipeurl_regex.search(s.selftext)
			nutrition = nutrition_regex.findall(s.selftext)
			preptime = preptime_regex.search(s.selftext)
			cooktime = cooktime_regex.search(s.selftext)
			servings = servings_regex.search(s.selftext)
			ingredients = ingredients_regex.findall(s.selftext)
			instructions = instructions_regex.findall(s.selftext)

			if recipeurl:
				print(recipeurl.group(1))
			else:
				recipeurl = ''

		# # Prepare SQL query to INSERT a record into the database.
		# format_str = """INSERT INTO fitmeal(title, flair, recipeurl, nutrition, preptime, cooktime, servings, ingredients, instructions) VALUES ({title}, {flair}, {recipeurl}, {nutrition}, {preptime}, {cooktime}, {servings}, {ingredients}, {instructions});"""

		# sql = format_str.format(title=title.group(1), , flair=flair, recipeurl=recipeurl, nutrition=nutrition, preptime=preptime, cooktime=cooktime, servings=servings, ingredients=ingredients, instructions=instructions)

			db = self.sqlite_connect()
			cursor = db.cursor()

			try:
				cursor.execute("INSERT INTO fitmeal(title, flair, recipeurl, nutrition, preptime, cooktime, servings, ingredients, instructions) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
					(title.group(1), flair, recipeurl, nutrition, preptime, cooktime, servings, ingredients, instructions))
				# Commit your changes in the database
				db.commit()
			except Exception as e:
				print("Shit didnt work\n {}".format(e))
				# Rollback in case there is any error
				db.rollback()

				# disconnect from server
				db.close()