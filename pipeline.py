"""
Author: Patrick Mühr Araúz  (patrick.muehr@tum.de)

Provide classes for the Datumaro dataset created with CVAT (Computer Vision Annotation Tool).
The annotations are made in CVAT and saved as JSON files. This module implements functions to read these files.

The classes are:
    * Bbox: Bounding box of a crop
    * Frame: Single image of a crop tray, containing 0 or many Bboxes
    * Tray: Collection of many frames of a fixed tray over a period of time
    * Specie: Encapsulates all of the trays where a specie has been sembrada
"""


import json
import os


class Bbox:
    def __init__(self, track_id: int, label_id: int, coordinates: list):
        """Initializes a CVAT bounding box

        Parameters:
            track_id: the ID of the Bbox, IDs are unique within a Tray and within a frame
            label_id: it is set to 0 if the crop inside this Bbox matches the main specie in the tray (aka correct plant), otherwise it is set to 1 (different plant).
            coordinates: [x-upper left corner, y-upper left corner, width, height]
        """

        self.track_id = track_id + 1  # +1 so track_id in json file equals track_id in CVAT
        self.coordinates = coordinates
        self.label_id = label_id

    def __str__(self):
        """Return an oneline str with the parameters of Bbox class"""
        y = "Bbox(track_id={}, label_id {}, coordinates={})".format(self.track_id, self.label_id, self.coordinates)
        return y


class Frame:  # Information about: plant id, frame number and bboxes (track_id, label_id, coordinates)
    def __init__(self, plant_id: str, frame_number: int, bboxes: list):
        """Initializes a CVAT Frame

        Parameters:
            plant_id: id of the frame (image) with time stamp. e.g.: POAAN/113804/POAAN_113804_2021Y07M22D_13H26M19S_img
            frame_number: number of the frame
            bboxes: a list of instances of the Bbox class
        """

        self.plant_id = plant_id
        self.frame_number = frame_number
        self.bboxes = bboxes

    def __str__(self):
        """Return a str with the parameter of the Frame class"""
        y = "Frame(plant_id={}, frame_number={}, bboxes=\n".format(self.plant_id, self.frame_number)
        for line in self.bboxes:
            y += "\t\t{},\n".format(line)
        return y[:-2] + ")\n"

    def count_samples(self):
        """This function counts the number of samples (number of annotated bboxes in each frame)"""
        return len(self.bboxes)


class Tray:
    def __init__(self, file_name: str):
        """Initializes a CVAT Tray

        Parameters:
            file_name: name of the file to be parsed
        """

        self.file_name = file_name
        self.frames = []  # list of Frame instances
        self.track_id_2_plant_ids = {}  # dictionary with track_id and corresponding germination/death of the plant
        self.populate_frames()
        self.__populate_track_id_2_plant_ids()

    def count_type_plant(self):
        """Count the number of different plants and correct plants
        returns a list with [number of correct plants, number of different plants]
        """

        number_of_zeros = 0
        number_of_ones = 0
        visited_track_ids = []
        for frame in self.frames:
            for bbox in frame.bboxes:
                if bbox.track_id in visited_track_ids:
                    continue
                visited_track_ids.append(bbox.track_id)

                if bbox.label_id == 0 or bbox.label_id == "0":
                    number_of_zeros += 1
                else:
                    number_of_ones += 1
        return [number_of_zeros, number_of_ones]


    def number_plants(self):
        """Count the number of plants present in this Tray"""

        maximum = 0
        for frame in self.frames:  # iterate in list self.frame (line 50)
            for bbox in frame.bboxes:  # iterate in list bboxes where the track_id, label_id and coordinates of the bboxes are. NOTE: this method is working because an instance of the class Bbox has been created before (line 60)
                if bbox.track_id > maximum:  # search for the max value.
                    maximum = bbox.track_id
        return maximum + 1  # track id begins at 0 therefore +1


    def __str__(self):
        """Return a str with the file name and all its frames"""

        x = "Tray(file_name={}, frames=\n".format(self.file_name)
        for t in self.frames:
            x += "\t{}\n".format(t)
        return x[:-1] + ")"

    def count_samples(self):
        """Count the number of samples (annotated bboxes) in this Tray"""

        samples = 0
        for frame in self.frames:
            samples += frame.count_samples()
        return samples

    def populate_frames(self):
        """Create the Frame instances and add them to self.frames"""

        try:
            with open(self.file_name) as f:  # open file as f
                data = json.load(f)  # json.load: load a json file and save it as a Dictionary in Data variable.
        except Exception:  # Note: items is one of the main keys in this dictionary (categories, info, items)
            print(self.file_name)
            raise Exception
        for element in data[
            "items"]:  # Note: items contains a list with a lot of dictionaries. Iterate through its keys.
            annotations = element[
                "annotations"]  # "annotations": is a key inside items that contains another dictionary with the key "bbox":
            bboxes_info = []  # create an empty list for the bboxes
            for element2 in annotations:  # iterate through the variable annotations that contains the following keys: "attr":, "bbox":, and "group":
                track_id_bbox = int(element2["attributes"][
                                        "track_id"])  # track_id is a key inside the attr dictionary. Save the corresponding value (id of the bbox) as a int.
                label_id = element2[
                    "label_id"]  # saves the corresponding value (correct plant = 0, different plant = 1) of the label_id key
                bbox = Bbox(track_id_bbox, label_id, element2[
                    "bbox"])  # create an instance of a Bbox class with the attr. track id, label_id (correct plant = 0, different plant = 1) and values of the key bbox (coordinates)
                bboxes_info.append(bbox)  # append instance bbox to the empty list bboxes

            frame = Frame(element["id"], int(element["attr"]["frame"]),
                          bboxes_info)  # create an instance of the Frame class with the plant id, frames number and bboxes list(track_id, label_id, coordinates)
            self.frames.append(frame)  # append this instance to empty self.frame

    def __populate_track_id_2_plant_ids(self,
                                        discriminate=True):
        """populate the dictionary self.track_id_2_plant_ids

        Parameters:
            discriminate: if True populate the self.track_id_2_plant_ids dictionary only with the correct plants
        """

        track_id_list = []  # populate track_id_list with bbox track_ids
        for frame in self.frames:
            for bbox in frame.bboxes:
                if bbox.track_id not in track_id_list:
                    if discriminate:
                        if bbox.label_id == 0:
                            track_id_list.append(bbox.track_id)
                    else:
                        track_id_list.append(bbox.track_id)
        death = {}  # dictionary with {bbox track_id:plant_id} where the bbox is last seen
        for track_id in track_id_list:
            for frame in self.frames:
                for bbox in frame.bboxes:
                    if bbox.track_id == track_id:
                        death[track_id] = frame.plant_id
        germination = {}  # dictionary with {bbox track_id:plant_id} where the bbox is first seen
        for track_id in track_id_list:
            stop = False
            for frame in self.frames:
                if stop:
                    break
                for bbox in frame.bboxes:
                    if bbox.track_id == track_id:
                        germination[track_id] = frame.plant_id
                        stop = True
                        break
        for track_id in track_id_list:  # populating self.track_id_2_plant_ids dictionary with germination and death dates.
            self.track_id_2_plant_ids[track_id] = (germination[track_id], death[track_id])


class Specie:  # input: directory with all the files of the same species, output: all the information needed (plant id, frame#, bboxes list(track_id, label_id, coordinates) for all the files inside this dictionary
    def __init__(self, directory: str):
        """Initializes an abstract representation of a collection of Tray instances that belongs to a certain specie

        Parameters:
            directory: name of a directory that contains JSON files of one specie
        """

        self.directory = directory
        self.trays = []  # list of Tray instances
        for element in os.listdir(
                directory):  # returns a list containing the names of the entries in the directory given. Iterate through this list
            full_file_name = directory + "/" + element  # construct/obtain the complete path of the file
            x = Tray(
                full_file_name)  # Create an instance of the class Tray tanking the complete path of the file as an argument
            self.trays.append(x)  # append this (x) to the empty list self.trays

    def __str__(self):
        """Return a str with all the names of the JSON file inside self.trays"""

        x = "Plant(directory={}".format(self.directory)
        for tray in self.trays:
            x += "\t{}\n".format(tray)
        return x[:-1] + ")"

    def total_number_plants(self):
        """Count the number of plants in this Specie"""

        summ = 0
        for element in self.trays:
            summ += element.number_plants()
        return summ

    def count_type_plant(self):
        """Count the number of different plants and correct plants in this Specie
        return a list with the number of [correct plants, wrong plants]"""

        number_of_zeros = 0
        number_of_ones = 0
        for tray in self.trays:
            zeros_and_ones = tray.count_type_plant()
            zeros = zeros_and_ones[0]
            ones = zeros_and_ones[1]
            number_of_zeros += zeros
            number_of_ones += ones
        return [number_of_zeros, number_of_ones]

    def count_samples(self):
        """Count the number of labeled bboxes in this Specie"""

        samples = 0
        for tray in self.trays:
            samples += tray.count_samples()
        return samples

    def get_list_bboxes(self):
        """Return a generator of all the bboxes in this Specie instance"""

        for tray in self.trays:
            for frame in tray.frames:
                for bbox in frame.bboxes:
                    yield bbox
