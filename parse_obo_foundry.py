import subprocess
import os
import csv
import json
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


# Function to create directories if they do not exist
def create_directories():
    dirs = ["data", "results"]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


# Function to call the Bash script
def call_bash_script(arg):
    subprocess.run(["bash", "get_obo.sh", arg])


# Function to run a Wikidata query
def run_wikidata_query(arg, property_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(
        f"""
        SELECT ?item ?itemLabel ?wikipediaLink ?value WHERE {{
          ?item wdt:{property_id} ?value .
          OPTIONAL {{ ?wikipediaLink schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# Function to save results to Excel
def save_to_excel(arg, results):
    results_df = pd.DataFrame(results)
    results_df.to_excel(f"data/{arg}_wikidata_terms.xlsx", index=False)


# Function to cross-reference and filter data
def cross_reference(arg):
    # Load cleaned ontology table
    ontology_df = pd.read_csv(f"data/{arg}_clean.csv")

    # Load Wikidata terms
    wikidata_df = pd.read_excel(f"data/{arg}_wikidata_terms.xlsx")

    # Merge dataframes
    merged_df = pd.merge(
        ontology_df, wikidata_df, left_on="id", right_on="itemLabel", how="inner"
    )  # Replace 'ID' with the actual column name

    # Filter based on your criteria
    filtered_df = merged_df[
        (merged_df["wikipediaLink"].notnull())
        & (merged_df["ontology_wikipedia_link"].isnull())
    ]  # Replace 'ontology_wikipedia_link' with the actual column name

    return len(filtered_df)


# Function to get the required counts from the generated CSV files and Wikidata
def get_counts(arg, property_id):
    file_path = f"data/{arg}_clean.csv"
    unique_items = set()
    wikipedia_xrefs = 0
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            unique_items.add(row[0])  # Assuming the ID is the unique item
            print(row)
            try:
                if "wikipedia" in row[2].lower():
                    wikipedia_xrefs += 1
            except:
                pass

    # Get count of unique IDs for the property on Wikidata
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(
        f"""
        SELECT (COUNT(DISTINCT ?item) AS ?count) WHERE {{
          ?item wdt:{property_id} ?value .
        }}
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    wikidata_count = results["results"]["bindings"][0]["count"]["value"]
    missing_wikipedia_links_count = cross_reference(arg)
    return {
        "unique_counts": len(unique_items),
        "wikidata_property_counts": int(wikidata_count),
        "wikipedia_xrefs_counts": wikipedia_xrefs,
        "missing_wikipedia_links_count": missing_wikipedia_links_count,
    }


# Function to execute the SPARQL query and get short names and property IDs
def get_short_names_and_property_ids():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(
        """
        #title: Wikidata properties directly connected to OBO Foundry Ontologies 
        SELECT DISTINCT ?property ?propertyLabel ?short WHERE {

          ?ontology wdt:P31 wd:Q324254 . 
          ?ontology wdt:P361 wd:Q4117183 . 
          ?ontology wdt:P1687 ?property . 
          ?ontology wdt:P1813 ?short . 
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    short_names_and_property_ids = [
        (result["short"]["value"], result["property"]["value"].split("/")[-1])
        for result in results["results"]["bindings"]
    ]
    return short_names_and_property_ids


# Main execution
if __name__ == "__main__":
    # Create directories
    create_directories()

    # Get short names and property IDs from SPARQL query
    args = get_short_names_and_property_ids()

    # Dictionary to hold the counts for each ontology
    counts_dict = {}

    # Call Bash script and get counts for each argument
    for arg, property_id in args:
        if arg == "ro":
            continue
        call_bash_script(arg)
        wikidata_results = run_wikidata_query(arg, property_id)
        save_to_excel(arg, wikidata_results)
        counts_dict[arg] = get_counts(arg, property_id)

    # Write counts to a JSON file
    with open("counts.json", "w", encoding="utf-8") as f:
        json.dump(counts_dict, f, ensure_ascii=False, indent=4)
