import csv

def dictionary_annotations_time_per_species(file_name: str):
    """Bar plot, y = time [hr] used for the annotation, x = species"""
    with open(file_name, encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=";")
        data = [row for row in reader]
    annotation_time_for_species = {}
    for line in data:
        annotation_time = line[0]
        name = line[1].split("_")[0]
        specie = name.upper().strip()
        if specie in annotation_time_for_species:
            annotation_time_for_species[specie].append(annotation_time)
        else:
            annotation_time_for_species[specie] = [annotation_time]
    return annotation_time_for_species

#print(dictionary_annotations_time_per_species("ej.csv_files"))



