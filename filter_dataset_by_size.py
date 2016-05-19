# -*- coding: utf-8 -*-

"""
Filter Dataset by Size

Usage:

python filter_dataset_by_size.py list_of_files.txt

or

python filter_dataset_by_size.py folder_with_labels

Outputs a new folder called filtered_labels/ alongside the labels/ folder,
containing new label files.
It also outputs a file alongside the labels/ folder called filtered_labels.txt
It contains the filenames of all label files with one or more remaining
bounding boxes.
"""

import os
from sys import argv


def parse_detection(box):
    return {
        'xmin': float(box[0]) - float(box[2]) / 2,
        'ymin': float(box[1]) - float(box[3]) / 2,
        'xmax': float(box[0]) + float(box[2]) / 2,
        'ymax': float(box[1]) + float(box[3]) / 2,
    }


def calculate_area(rect):
    return (rect['xmax'] - rect['xmin']) * (rect['ymax'] - rect['ymin'])


def open_path(path):
    filenames = map(lambda filename: os.path.join(path, filename),
                    filter(lambda filename: filename[0] != '.',
                           os.listdir(path)))
    print 'Opened path:', path
    open_list(filenames)


def open_list(filenames):
    files_with_boxes = []
    for filename in filenames:
        boxes = []
        with open(filename, 'r') as f:
            lines = map(lambda x: x.strip(), f.readlines())
            for line in lines:
                box = parse_detection(line.split(' ')[1:])
                if calculate_area(box) > 0.03:
                    boxes.append(line)
        if len(boxes) > 0:
            files_with_boxes.append(filename)
        new_filename = filename.replace('labels/', 'filtered_labels/')
        new_directory = os.path.dirname(new_filename)
        if not os.path.exists(new_directory):
            os.makedirs(new_directory)
        with open(new_filename, 'w') as f:
            f.write('\n'.join(boxes) + '\n')

    parent_dir, _ = os.path.split(os.path.dirname(filenames[0]))
    list_filename = parent_dir + '/filtered_labels.txt'
    with open(list_filename, 'w') as f:
        f.write('\n'.join(files_with_boxes) + '\n')


if __name__ == '__main__':
    if argv[1]:
        if argv[1][-3:] == 'txt':
            with open(argv[1], 'r') as f:
                filenames = map(lambda filename: filename.strip(),
                                f.readlines())
                open_list(filenames)
        else:
            open_path(argv[1])
    else:
        open_path('data/labels/')
