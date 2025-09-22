#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "flask",
#     "pandas",
# ]
# ///
"""Run a Flask API or query a SQLite database directly."""
from flask import Flask, request, render_template_string
import sqlite3
import argparse
import os
import sys
import json

app = Flask(__name__)


# Database setup
def query_database(db_path, query):
  connection = sqlite3.connect(db_path)
  cursor = connection.cursor()
  cursor.execute(query)
  rows = cursor.fetchall()
  connection.close()
  return rows


# Markdown formatting
def format_markdown(data, columns):
  if not data:
    return "No data available."

  markdown = f"# ID: {data[0][0]}\n\n"
  for col, value in zip(columns[1:], data[0][1:]):  # Skip the ID column
    if value is not None:  # Omit fields with null/None values
      markdown += f"## {col}\n\n{value}\n\n"
  return markdown


# JSON formatting
def format_json(data, columns):
  if not data:
    return json.dumps({"error": "No data available."}, indent=2)

  result = {columns[i]: value for i, value in enumerate(data[0]) if value is not None}
  return json.dumps(result, indent=2)


# HTML formatting
def format_html(data, columns):
  if not data:
    return "<p>No data available.</p>"

  html = f"<h1>ID: {data[0][0]}</h1>"
  for col, value in zip(columns[1:], data[0][1:]):  # Skip the ID column
    if value is not None:  # Omit fields with null/None values
      html += f"<h2>{col}</h2><p>{value}</p>"
  return html


@app.route("/query", methods=["GET"])
def query():
  record_id = request.args.get("id")
  if not record_id:
    return "Error: Missing 'id' parameter in the query string.", 400

  query = f"SELECT * FROM coriell_dna WHERE id = '{record_id}'"
  connection = sqlite3.connect(app.config["DATABASE_PATH"])
  cursor = connection.cursor()

  try:
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
  except sqlite3.Error as e:
    return f"Database error: {e}", 500
  finally:
    connection.close()

  if not data:
    return f"No record found with ID '{record_id}'.", 404

  if request.headers.get("Accept") == "text/markdown":
    return format_markdown(data, columns), 200, {"Content-Type": "text/markdown"}
  else:
    html_template = """
        <!DOCTYPE html>
        <html>
        <head><title>Query Results</title></head>
        <body>
        {{ content|safe }}
        </body>
        </html>
        """
    return render_template_string(html_template, content=format_html(data, columns))


def run_query_from_command_line(db_path, query, output_format):
  connection = sqlite3.connect(db_path)
  cursor = connection.cursor()

  try:
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
  except sqlite3.Error as e:
    print(f"Database error: {e}")
    sys.exit(1)
  finally:
    connection.close()

  if not data:
    print("No data found for the given query.")
    sys.exit(1)

  if output_format == "json":
    print(format_json(data, columns))
  else:  # Default to markdown
    print(format_markdown(data, columns))


def main():
  # Set up argument parser
  parser = argparse.ArgumentParser(
    description=__doc__
  )
  parser.add_argument(
    "--db_path",
    default="./data/coriell_catalog.db",
    help="Path to the SQLite database file.",
  )
  parser.add_argument(
    "--debug", action="store_true", help="Run the Flask app in debug mode."
  )
  parser.add_argument(
    "--query",
    help="Run a query directly on the database and print the result.",
  )
  parser.add_argument(
    "--output",
    choices=["markdown", "json"],
    default="markdown",
    help="Output format for direct query mode (default: markdown).",
  )

  # Parse arguments
  args = parser.parse_args()

  # Ensure the database file exists
  if not os.path.exists(args.db_path):
    print(f"Error: The database file '{args.db_path}' does not exist.")
    sys.exit(1)

  if args.query:
    # Run the query directly and exit
    run_query_from_command_line(args.db_path, args.query, args.output)
  else:
    # Set the database path in the app configuration
    app.config["DATABASE_PATH"] = args.db_path

    # Run the Flask app
    app.run(debug=args.debug)


if __name__ == "__main__":
  main()
