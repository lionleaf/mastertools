"""
Calculate and plot precision/recall curves
"""

from sys import argv
from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt
from evaluate_detections import detected_objects_in_image
from loaders import load_ground_truth, load_predicted_boxes

dataset_dir = '../datasets'
valid_dir = '../valid'


def identifier_from_path(imagepath):
    _, imagefilename = imagepath.rsplit('/', 1)
    image, _ = imagefilename.rsplit('.', 1)
    return image


def calculate_precision_recall(ground_truth, predicted_boxes, files):
    for imagepath in files:
        im = Image.open(imagepath)
        width, height = im.size
        image = identifier_from_path(imagepath)
        for i, detection in enumerate(predicted_boxes[image]):
            predicted_boxes[image][i] = {
                'prob': float(detection[0]),
                'xmin': float(detection[1]) / width,
                'ymin': float(detection[2]) / height,
                'xmax': float(detection[3]) / width,
                'ymax': float(detection[4]) / height,
            }

    total_number_of_boxes = 0
    accumulated_true_positives = 0
    accumulated_false_positives = 0
    accumulated_false_negatives = 0
    recall_list = []
    precision_list = []
    for i in np.arange(0, 1, 0.005):
        for image in predicted_boxes:
            image = identifier_from_path(imagepath)
            boxes = ground_truth[image]
            detected_objects = detected_objects_in_image(
                boxes,
                predicted_boxes[image],
                thresh=i
            )

            total_number_of_boxes += len(boxes)
            accumulated_true_positives += detected_objects
            accumulated_false_positives += (len(predicted_boxes[image])
                                            - len(boxes))
            accumulated_false_negatives += len(boxes) - detected_objects

        recall = float(accumulated_true_positives) / total_number_of_boxes
        precision = (float(accumulated_true_positives) /
                     (accumulated_true_positives +
                      accumulated_false_positives))
        recall_list.append(recall)
        precision_list.append(precision)
        print '[%g] Precision-Recall:' % i, precision, recall

    recall_list.append(0.)
    precision_list.append(1.)

    plt.clf()
    plt.plot(recall_list, precision_list, label='Precision-Recall curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall')
    plt.legend(loc='lower left')
    plt.show()


if __name__ == '__main__':
    weights_identifier = argv[1]
    dataset_identifier = argv[2]
    valid_path = (os.getcwd() + '/' +
                  valid_dir + '/valid-' +
                  weights_identifier + '.weights-' +
                  dataset_identifier)
    dataset_path = (os.getcwd() + '/' +
                    dataset_dir + '/' +
                    dataset_identifier + '/files.txt')
    ground_truth = load_ground_truth(dataset_path)
    predicted_boxes = load_predicted_boxes(valid_path)
    with open(dataset_path, 'r') as f:
        files = map(lambda x: x.strip(), f.readlines())
    calculate_precision_recall(ground_truth, predicted_boxes, files)
