import datetime

import matplotlib.pyplot as plt
from pipeline2 import Specie, Tray
from csv_files.annotation_times import dictionary_annotations_time_per_species


def calculate_total_number_of_wrong_plants_across_all_species(species: list[Specie]):  # species es del tipo lista que contiene elementos del tipo Species
    """sum of all different plants across all species"""
    sum_wrong_plants = 0
    for specie in species:
        sum_wrong_plants += specie.count_type_plant()[-1]
    return sum_wrong_plants


def number_of_wrong_plants_per_tray(specie: Specie):
    """return list of number of wrong plants per tray.

    Gesamtzahl der falschen Pflanzen pro Tray (falsche Pflanze = andere spezies als im Tray sein sollte)"""
    list_wrong_plants = []
    for tray in specie.trays:
        a = tray.count_type_plant()[-1]
        list_wrong_plants.append(a)
    return list_wrong_plants


def plot_average_number_of_wrong_plants_per_tray_per_species(species: list[Specie], show=True):  # plant different when: label_id of bbox = 1
    """Bar plot, y = avg. number of different plants per tray, x = species"""
    x = []
    y = []
    for specie in species:
        nominator = specie.count_type_plant()[-1]
        denominator = len(specie.trays)
        name = specie.directory.split("/")[-1]
        x.append(name)
        y.append(nominator / denominator)
    plt.bar(x, y)
    plt.xlabel('Species')
    plt.ylabel('avg. number of wrong plants per tray per species')
    if show:
        plt.show()
    else:
        plt.savefig("plot_average_number_of_wrong_plants_per_tray_per_species.png")

def total_number_of_labelled_plants(species: list[Specie]):  # sample = 1 annotated bbox
    """sum of all annotated bboxes across all species"""
    total_number_of_plants = 0
    for specie in species:
        total_number_of_plants += specie.total_number_plants()
    return total_number_of_plants

def calculate_avg_number_of_labelled_plants_per_tray(specie: Specie):
    """Calculate the number of labelled plants per tray"""
    nominator = specie.total_number_plants()
    denominator = len(specie.trays)
    return nominator/denominator

def plot_avg_number_of_labelled_plants_per_species(species: list[Specie], show=True):  # plant = track_id bbox
    """Bar plot, y = sum number of plants per species, x = species"""
    x = []
    y = []
    for specie in species:
        x_values = specie.directory.split("/")[-1]
        x.append(x_values)
        y_values = calculate_avg_number_of_labelled_plants_per_tray(specie)
        y.append(y_values)
    plt.bar(x, y)
    plt.xlabel('Species')
    plt.ylabel('avg. number of labelled plants per tray')
    if show:
        plt.show()
    else:
        plt.savefig("plot_avg_number_of_labelled_plants_per_species.png")

def plot_avg_number_of_samples_per_tray_per_species(species: list[Specie], show=True):  # sample = 1 annotated bbox
    """Bar plot, y = number of samples per species, x = species"""
    x = []
    y = []
    for specie in species:
        x_values = specie.directory.split("/")[-1]
        y_values = specie.count_samples()/len(specie.trays)
        x.append(x_values)
        y.append(y_values)
    plt.bar(x, y)
    plt.xlabel('Species')
    plt.ylabel('avg. number of samples per tray')
    if show:
        plt.show()
    else:
        plt.savefig("plot_avg_number_of_samples_per_tray_per_species.png")


def plot_average_time_annotation_per_tray_per_species(file_name: str, show=True):
    """Bar plot, y = time [hr] used for the annotation, x = species"""
    dictionary_with_annotation_times = dictionary_annotations_time_per_species(file_name)
    x = dictionary_with_annotation_times.keys()
    y = []
    for element in x:
        list_of_times = dictionary_with_annotation_times[element]
        hrs = 0
        mins = 0
        for time in list_of_times:
            h, m = time.split(":")
            hrs += int(h)
            mins += int(m)
        while mins >= 60:
            mins -=60
            hrs += 1
        avg_time = (hrs + (mins/60))/len(list_of_times)
        y.append(avg_time)
    plt.bar(x, y)
    plt.xlabel('Species')
    plt.ylabel('avg. annotation time per tray per species [hrs]')
    if show:
        plt.show()
    else:
        plt.savefig("plot_avegare_time_annotation_per_tray_per_species.png")

def plot_bbox_area_distribution(specie: Specie, bins=20, show=True):
    """Bar plot, y = area, x = spezies"""
    area = []
    for bbox in specie.get_list_bboxes():  # bbox:[x-upper left corner, y-upper left corner, width, height]
        width = float(bbox.coordinates[2])
        height = float(bbox.coordinates[3])
        area.append(width*height)
    plt.hist(area, bins=bins, edgecolor="black")
    plt.title("distribution of the bbox area")
    plt.xlabel("pixels^2")
    #  TODO: x achse --> log scale
    plt.ylabel("count")
    plt.title("Distribution area of the bboxes in: " + specie.directory)
    if show:
        plt.show()
    else:
        plt.savefig("plot_bbox_area_distribution.png")

def get_date(plant_id):
    x = plant_id.split("/")[-1]
    date = x.split("_")[2]
    year = date[0:4]
    month = date[5:7]
    days = date[8:10]
    time = x.split("_")[3]
    hrs = time[0:2]
    minutes = time[3:5]
    seconds = time[6:8]
    z = year + ":" + month + ":" + days + ":" + hrs + ":" + minutes + ":" + seconds
    return datetime.datetime.strptime(z, '%Y:%m:%d:%H:%M:%S')


def plot_life_span_file(tray: Tray, show=True):
    """Bar plot, y = growth rate [cm^2], x = time [hr]"""
    x = tray.track_id_2_plant_ids.keys()
    y = []
    for track_id in x:
        germination, death = tray.track_id_2_plant_ids[track_id]
        birth_date = get_date(germination)
        death_date = get_date(death)
        life_span = death_date - birth_date
        y.append(life_span.days)
    plt.bar(x, y)
    plt.xlabel('Track id')
    plt.ylabel('Life span')
    if show:
        plt.show()
    else:
        plt.savefig("plot_life_span_file.png")


def plot_avg_life_span_specie(specie: Specie, show=True):
    x = []
    y = []
    for tray in specie.trays:
        x.append(tray.file_name.split("/")[1].strip(".json"))
        a = []
        for track_id in tray.track_id_2_plant_ids:
            germination, death = tray.track_id_2_plant_ids[track_id]
            birth_date = get_date(germination)
            death_date = get_date(death)
            life_span = death_date - birth_date
            a.append(life_span.days)
        y.append(sum(a)/len(a))
    plt.bar(x, y)
    plt.xlabel('Tray')
    plt.xticks(rotation=45)
    plt.ylabel('Life span [days]')
    plt.title("Average life span")
    if show:
        plt.show()
    else:
        plt.savefig("avg_life_span_specie.png")


def main():
    zeamx = Specie("ZEAMX")
    sorx = Specie("SORXX")
    alomy = Specie("ALOMY")
    agrre = Specie("AGRRE")
    echcg = Specie("ECHCG")
    poaan = Specie("POAAN")
    list_species = [zeamx, sorx, alomy, agrre, echcg, poaan]

    x = calculate_total_number_of_wrong_plants_across_all_species(list_species)
    print("Total number of wrong plants across all species: " + str(x))

    x = number_of_wrong_plants_per_tray(zeamx)
    print("Number of wrong plants per tray in Zeamx: " + str(x))
    x = number_of_wrong_plants_per_tray(sorx)
    print("Number of wrong plants per tray in Sorx: " + str(x))
    x = number_of_wrong_plants_per_tray(alomy)
    print("Number of wrong plants per tray in Alomy: " + str(x))
    x = number_of_wrong_plants_per_tray(agrre)
    print("Number of wrong plants per tray in Agrre: " + str(x))
    x = number_of_wrong_plants_per_tray(echcg)
    print("Number of wrong plants per tray in Echcg: " + str(x))
    x = number_of_wrong_plants_per_tray(poaan)
    print("Number of wrong plants per tray in poaan: " + str(x))

    x = total_number_of_labelled_plants(list_species)
    print("Total number of labelled plants across all species: " + str(x))

    x = calculate_avg_number_of_labelled_plants_per_tray(zeamx)
    print("Average number of labelled plants per tray in Zeamx: " + str(round(x, 2)))
    x = calculate_avg_number_of_labelled_plants_per_tray(sorx)
    print("Average number of labelled plants per tray in Sorx: " + str(round(x, 2)))
    x = calculate_avg_number_of_labelled_plants_per_tray(alomy)
    print("Average number of labelled plants per tray in Alomy: " + str(round(x, 2)))
    x = calculate_avg_number_of_labelled_plants_per_tray(agrre)
    print("Average number of labelled plants per tray in Agrre: " + str(round(x, 2)))
    x = calculate_avg_number_of_labelled_plants_per_tray(echcg)
    print("Average number of labelled plants per tray in Echcg: " + str(round(x, 2)))
    x = calculate_avg_number_of_labelled_plants_per_tray(poaan)
    print("Average number of labelled plants per tray in Poann: " + str(round(x, 2)))

    plot_average_number_of_wrong_plants_per_tray_per_species(list_species)
    plot_avg_number_of_labelled_plants_per_species(list_species)
    plot_avg_number_of_samples_per_tray_per_species(list_species)
    plot_average_time_annotation_per_tray_per_species("csv_files/annotation_time.csv")
    plot_bbox_area_distribution(zeamx)
    plot_bbox_area_distribution(sorx)
    plot_bbox_area_distribution(alomy)
    plot_bbox_area_distribution(agrre)
    plot_bbox_area_distribution(echcg)
    plot_bbox_area_distribution(poaan)
    plot_avg_life_span_specie(zeamx)
    plot_avg_life_span_specie(sorx)
    plot_avg_life_span_specie(alomy)
    plot_avg_life_span_specie(agrre)
    plot_avg_life_span_specie(echcg)
    plot_avg_life_span_specie(poaan)


if __name__ == "__main__":
    main()



