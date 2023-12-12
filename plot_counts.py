import matplotlib.pyplot as plt
import json


label_size = 16


# Load data from counts.json
with open("counts.json", "r") as file:
    data = json.load(file)

# Calculate the percentage of Wikidata coverage for each ontology
coverage_percentages = {
    ontology: min((info["wikidata_property_counts"] / info["unique_counts"]) * 100, 100)
    for ontology, info in data.items()
}

# Extract wikipedia_xrefs_counts values and sort by amount
wikipedia_xrefs_counts = sorted(
    [(ontology, info["wikipedia_xrefs_counts"]) for ontology, info in data.items()],
    key=lambda x: x[1],
)

# Split the sorted data into two lists for plotting
ontologies_wiki_xrefs, counts_wiki_xrefs = zip(*wikipedia_xrefs_counts)

# Plotting the Coverage Percentage
# Sort the data for the scatter plot
sorted_coverage = sorted(coverage_percentages.items(), key=lambda x: x[1])
ontologies_coverage, percentages_coverage = zip(*sorted_coverage)

plt.figure(figsize=(10, 6))
plt.scatter(ontologies_coverage, percentages_coverage, color="blue")

# Display numbers above each dot
for i, txt in enumerate(percentages_coverage):
    plt.text(
        ontologies_coverage[i],
        percentages_coverage[i] + 2,
        f"{txt:.0f}",
        ha="center",
        fontsize=label_size - 2,
    )


plt.title("Wikidata Coverage Percentage for Different Ontologies", fontsize=label_size)
plt.xlabel("Ontologies", fontsize=label_size)
plt.ylabel("Coverage Percentage", fontsize=label_size)
plt.xticks(rotation=45, fontsize=label_size)
plt.yticks(fontsize=label_size)
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("coverage_percentage.png")
plt.close()


# Plotting the Wikipedia Xref Counts in order
plt.figure(figsize=(10, 6))
plt.scatter(ontologies_wiki_xrefs, counts_wiki_xrefs, color="blue")


# Display numbers above each dot
for i, txt in enumerate(counts_wiki_xrefs):
    plt.text(
        ontologies_wiki_xrefs[i],
        counts_wiki_xrefs[i] + 2,
        f"{txt}",
        ha="center",
        fontsize=label_size - 2,
    )


plt.title("Wikipedia Xref Counts for Different Ontologies", fontsize=label_size)
plt.xlabel("Ontologies", fontsize=label_size)
plt.ylabel("Wikipedia Xref Counts", fontsize=label_size)
plt.xticks(rotation=45, fontsize=label_size)
plt.yticks(fontsize=label_size)
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("wikipedia_xrefs_counts.png")
plt.close()
