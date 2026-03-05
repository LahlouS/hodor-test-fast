import os
from dotenv import load_dotenv
import psycopg2
import json
from datetime import datetime
import sys

# Connect to the PostgreSQL database
def connect_to_db():
	try:
		connection = psycopg2.connect(
			dbname=DB_NAME,
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT
		)
		connection.autocommit = True
		return connection
	except Exception as e:
		print(f"Error connecting to the database: {e}")
		exit(1)

# Get the list of applied migrations
def get_applied_migrations(cursor):
	cursor.execute("CREATE TABLE IF NOT EXISTS migrations (id SERIAL PRIMARY KEY, migration_name VARCHAR(255) NOT NULL, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
	cursor.execute("SELECT migration_name FROM migrations;")
	return {row[0] for row in cursor.fetchall()}

# Apply a migration
def apply_migration(cursor, migration_file):
	with open(migration_file, "r") as file:
		sql = file.read()
	cursor.execute(sql)
	cursor.execute(
		"INSERT INTO migrations (migration_name) VALUES (%s);",
		(os.path.basename(migration_file),)
	)
	print(f"Applied migration: {os.path.basename(migration_file)}")

# Main function to execute migrations
def run_migrations(path):
	connection = connect_to_db()
	cursor = connection.cursor()

	try:
		applied_migrations = get_applied_migrations(cursor)
		migration_files = sorted(
			[f for f in os.listdir(path) if f.endswith(".sql")]
		)

		for migration_file in migration_files:

			if migration_file not in applied_migrations:
				apply_migration(cursor, os.path.join(path, migration_file))

		print("All migrations applied successfully!")
	
	except Exception as e:
		print(f"Error during migration: {e}")
	finally:
		cursor.close()
		connection.close()

if __name__ == "__main__":
		
	# Load environment variables from .env file
	if len(sys.argv) != 2 and (sys.argv[1] != "prod" or sys.argv[1] != "dev"):
		raise AssertionError("Wrong usage: run migration should be called like:\n>> python run_migrations [prod || dev]\n accordingly migration_[prod || dev] should be in the current directory")
	env_file = './.env.prod' if sys.argv[1] == "prod" else './.env.dev'
	load_dotenv(env_file)

	# Fetch environment variables
	DB_NAME = os.getenv("DB_NAME")
	DB_USER = os.getenv("POSTGRES_USER")
	DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
	DB_HOST = os.getenv("DB_HOST")
	DB_PORT = os.getenv("DB_PORT", 5432)
	print(sys.argv)
	print(f"Running in {sys.argv[1]} db")
	print(f"LOG env: (for env_file: {env_file})")
	print("DB_NAME:", DB_NAME + "\n", 
	   "DB_USER:", DB_USER + "\n", 
	   "DB_PASSWORD:", DB_PASSWORD + "\n", 
	   "DB_HOST:", DB_HOST + "\n", 
	   "DB_PORT:", DB_PORT + "\n")
	
	if sys.argv[1] == "prod":
		run_migrations("./migrations_prod")
	elif sys.argv[1] == "dev":
		run_migrations('./migrations_test')
