# coriell_lookup

Lookup information about DNA available from Coriell.

## Setup

1. Download the Coriell [DNA](https://www.coriell.org/Search?grid=0&q=*%3A*&csId=&f_2=DNA&_gl=1*18ur8fb*_gcl_au*MTgxODU1MTQ4NS4xNzU3MDg3MzU3) catalog CSV file from [Coriell's website](https://catalog.coriell.org/).

2. Use the `create_coriell_db.py` script to load the CSV into a SQLite database:

  ```bash
  python create_coriell_db.py path/to/coriell_dna_catalog.csv coriell_catalog.db coriell_dna
  ```

3. Use the `query_coriell_db.py` script to run a Flask API server or query the database directly:

  ```bash
  # to run the Flask API server
  python query_coriell_db.py --db_path coriell.db --debug
  # in a separate terminal
  curl -H "Accept: text/markdown" "http://127.0.0.1:5000/query?id=NA12878" > NA12878.md
  # or in a local web browser, go to http://127.0.0.1:5000/query?id=NA12878

  # to run a direct query
  python query_coriell_db.py --db_path coriell.db --query "SELECT * FROM coriell_dna WHERE id = 'NA12878';" > NA12878.md
  ```
