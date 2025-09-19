#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
# ]
# ///
"""Load a Coriell catalog CSV into a SQLite database."""
import sqlite3
import pandas as pd
import os
import argparse


__version__ = "0.1.0"


def load_csv_to_sqlite(csv_file, db_name, table_name):
  """
  Load a CSV file into a SQLite database.

  Args:
      csv_file (str): Path to the CSV file.
      db_name (str): Name of the SQLite database file.
      table_name (str): Name of the table to create in the database.
  """
  # Check if the CSV file exists
  if not os.path.exists(csv_file):
    print(f"Error: The file '{csv_file}' does not exist.")
    return

  # Load the CSV file into a Pandas DataFrame
  try:
    df = pd.read_csv(csv_file)
  except Exception as e:
    print(f"Error reading CSV file: {e}")
    return

  # Connect to the SQLite database (or create it if it doesn't exist)
  conn = sqlite3.connect(db_name)

  # Write the DataFrame to the SQLite database
  try:
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(
      f"Successfully loaded '{csv_file}' into the '{db_name}' database as table '{table_name}'."
    )
  except Exception as e:
    print(f"Error writing to SQLite database: {e}")
  finally:
    # Close the database connection
    conn.close()


def main():
  # Set up argument parser
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("csv_file", help="Path to the CSV file to load.")
  parser.add_argument("db_name", help="Name of the SQLite database file.")
  parser.add_argument("table_name", help="Name of the table to create in the database.")

  # Parse arguments
  args = parser.parse_args()

  # Call the function with parsed arguments
  load_csv_to_sqlite(args.csv_file, args.db_name, args.table_name)


if __name__ == "__main__":
  main()
