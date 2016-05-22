"""
Calculate and plot precision/recall curves
"""

from sys import argv
from PIL import Image
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from evaluate_detections import detected_objects_in_image
from loaders import load_ground_truth, load_predicted_boxes

weights_dir = '../weights'
dataset_dir = '../datasets'
valid_dir = '../valid'
prerec_dir = '../prerec'


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

    average_precision = metrics.auc(recall_list, precision_list)
    print 'AP:', average_precision

    return recall_list, precision_list, average_precision


def plot_graph(recall_list, precision_list):
    plt.clf()
    plt.plot(recall_list, precision_list, label='Precision-Recall curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall')
    plt.legend(loc='lower left')
    plt.show()


def load_and_calculate_precision_recall(weights_identifier,
                                        dataset_identifier):
    prerec_path = (os.getcwd() + '/' +
                   prerec_dir + '/prerec-' +
                   weights_identifier + '.weights-' +
                   dataset_identifier)
    if os.path.isfile(prerec_path):
        with open(prerec_path, 'r') as f:
            data = json.loads(f.read())
            return (data['recall_list'],
                    data['precision_list'],
                    data['average_precision'])
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

    (recall_list,
     precision_list,
     average_precision) = calculate_precision_recall(ground_truth,
                                                     predicted_boxes,
                                                     files)
    with open(prerec_path, 'w') as f:
        f.write(json.dumps({
            'recall_list': recall_list,
            'precision_list': precision_list,
            'average_precision': average_precision,
        }))
    return recall_list, precision_list, average_precision


if __name__ == '__main__':
    if len(argv) > 2:
        (recall_list,
         precision_list,
         _) = load_and_calculate_precision_recall(argv[1], argv[2])

        plot_graph(recall_list, precision_list)
    else:
        weight_files = sorted(os.listdir(weights_dir))
        dataset_files = sorted(os.listdir(dataset_dir))
        for weight in weight_files:
            if not weight.endswith('.weights'):
                continue
            weight, _ = weight.split('.', 1)
            for dataset in dataset_files:
                print '### %s - %s ###' % (weight, dataset)
                load_and_calculate_precision_recall(weight, dataset)