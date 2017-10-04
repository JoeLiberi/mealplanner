from praw import Reddit
import re, sqlite3
from sqlite3 import Error
import os, itertools
from collections import OrderedDict

title_regex = re.compile(r'\[\w+\s\w+\]\s(.+)')
flair_regex = re.compile(r'\[\w+\s\w+\]')
recipeurl_regex = re.compile(r'Recipe: \[.+\]\((.+)\)')
nutrition_regex = re.compile(r'Nutrition Info: (.+)')
preptime_regex = re.compile(r'Prep Time\s(.+)')
cooktime_regex = re.compile(r'Cook Time\s(.+)')
servings_regex = re.compile(r'Servings\s(.+)')
ingredients_regex = re.compile(r'\*\s.+', re.MULTILINE)
instructions_regex = re.compile(r'\d\.\s.+', re.MULTILINE)
alpha_regex = re.compile('[\W_]+')
alpha_keep_spaces_regex = re.compile('[\W_]+[\s]+')

dir_path = os.path.dirname(os.path.realpath(__file__))
database = "{}/fitmeal.db".format(dir_path)


class FitMealBot():

	def __init__(self):
		self.dir_path = os.path.dirname(os.path.realpath(__file__))
		self.database = "{}/fitmeal.db".format(dir_path)
		self.sql_create_fitmeal_table = """ CREATE TABLE IF NOT EXISTS fitmeal (
			id integer PRIMARY KEY AUTOINCREMENT,
			title text,
			flair_id integer NOT NULL,
			recipeurl text,
			preptime text,
			cooktime text,
			servings text,
			ingredients text, 
			instructions text
			); 
			"""

		self.sql_create_flair_table = """ CREATE TABLE IF NOT EXISTS flair (
			id integer PRIMARY KEY AUTOINCREMENT,
			fitmeal_id integer NOT NULL,
			HighCalorie boolean DEFAULT FALSE,
			LowCalorie boolean DEFAULT FALSE,
			HighProtein boolean DEFAULT FALSE,
			LowProtein boolean DEFAULT FALSE,
			HighCarb boolean DEFAULT FALSE,
			LowCarb boolean DEFAULT FALSE,
			HighFat boolean DEFAULT FALSE,
			LowFat boolean DEFAULT FALSE, 
			Vegetarian boolean DEFAULT FALSE,
			Vegan boolean DEFAULT FALSE,
			GlutenFree boolean DEFAULT FALSE,
			DairyFree boolean DEFAULT FALSE,
			Cheap boolean DEFAULT FALSE,
			Quick boolean DEFAULT FALSE,
			Snack boolean DEFAULT FALSE,
			Meta boolean DEFAULT FALSE,
			Tip boolean DEFAULT FALSE,
			Question boolean DEFAULT FALSE,
			Recipes boolean DEFAULT FALSE,
			Miscellaneous boolean DEFAULT FALSE,
			FOREIGN KEY (fitmeal_id) REFERENCES fitmeal (id)
			); 
			"""		

		# Create the database when the class is initialized
		self.conn = self.sqlite_connect()
		if self.conn is not None:
			# create projects table
			self.create_table(self.sql_create_fitmeal_table)
			self.create_table(self.sql_create_flair_table)
		else:
			print("Error! cannot create the database connection.")

	def sqlite_connect(self):

		try:
			conn = sqlite3.connect(self.database)
			return conn
		except Error as e:
			print(e)

		return None

	def create_table(self, create_table_sql):

		try:
			c = self.conn.cursor()
			c.execute(create_table_sql)
		except Error as e:
			print(e)

	def filter_title(self, posts, regex):

		s = []
		for p in posts:
			if regex.match(p.title):
				s.append(p)

		return s

	def create_flair(self, flair):

		sql = "INSERT INTO flair({}) VALUES(?)".format(row_name)

		cur = self.conn.cursor()
		cur.execute(sql, flair)
		return cur.lastrowid

	def create_fitmeal(self, meal):

		sql = " INSERT INTO fitmeal(cooktime,ingredients,instructions,preptime,recipeurl,servings,title) VALUES(?, ?, ? ,? ,? ,? ,?)"

		cur = self.conn.cursor()
		cur.execute(sql, meal)
		return cur.lastrowid
		

	def run_bot(self):

		print("Running.......")

		reddit = Reddit('mealplanner')

		subreddit = reddit.subreddit("fitmeals")

		submissions = self.filter_title(subreddit.hot(), title_regex)

		with self.conn:
			for s in submissions:
				title = title_regex.search(s.title)
				flair = flair_regex.findall(s.title)
				recipeurl = recipeurl_regex.search(s.selftext)
				preptime = preptime_regex.search(s.selftext)
				cooktime = cooktime_regex.search(s.selftext)
				servings = servings_regex.search(s.selftext)
				ingredients = ingredients_regex.findall(s.selftext)
				instructions = instructions_regex.findall(s.selftext)

				print(s.selftext)
				
				rows = {
					'title' : title, 
					'recipeurl' : recipeurl, 
					'preptime' : preptime, 
					'cooktime' : cooktime, 
					'servings' : servings, 
					'ingredients' : ingredients, 
					'instructions' : instructions}

				for key, value in rows.items():
					if rows[key]:
						if isinstance(rows[key], list):
							value = ''.join(rows[key])
							rows[key] = value
						else:
							v = alpha_keep_spaces_regex.sub('', rows[key].group(1))	
							rows[key] = v
					else:
						rows[key] = None

				# Create an empty list and append the values in alpha order based
				# on the key
				ordered_rows = []
				for key in sorted(rows.keys()):
					ordered_rows.append(rows[key])

				# self.create_fitmeal(ordered_rows)

				''' 
				Loop through the flair, string out the non-alpha chars including spaces.
				Call the "create_flair" method to enter flair into the sql table.

				'''
				# for f in flair:
				# 	f = alpha_regex.sub('', f)
				# 	create_flair(f, True)	

if __name__ == '__main__':

	bot = FitMealBot()
	bot.run_bot()