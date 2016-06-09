"""
Calculate and plot precision/recall curves
"""

from sys import argv
from PIL import Image
import math
import os
import json
import numpy as np
from sklearn import metrics
from evaluate_detections import detected_objects_in_image
from loaders import load_ground_truth, load_predicted_boxes

weights_dir = '../weights'
dataset_dir = '../datasets'
valid_dir = '../valid'
prerec_dir = '../prerec'
latex_dir = '../latex'


def identifier_from_path(imagepath):
    _, imagefilename = imagepath.rsplit('/', 1)
    image, _ = imagefilename.rsplit('.', 1)
    return image


def calculate_f_measure(precision_list, recall_list):
    max_f_measure = 0
    max_i = None
    for i in range(len(precision_list)):
        precision = precision_list[i]
        recall = recall_list[i]
        if precision == 0 and recall == 0:
            continue
        f = 2.0 * precision * recall / (precision + recall)
        if f >= max_f_measure:
            max_f_measure = f
            max_i = i
    return {
        'value': max_f_measure,
        'precision': precision_list[max_i],
        'recall': recall_list[max_i],
    }


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

    recall_list = []
    precision_list = []
    for i in map(math.log10, np.arange(1, 10.02, 0.02)):
        total_number_of_boxes = 0
        accumulated_true_positives = 0
        accumulated_false_positives = 0
        accumulated_false_negatives = 0
        for image in predicted_boxes:
            boxes = ground_truth[image]
            detected_objects = detected_objects_in_image(
                boxes,
                predicted_boxes[image],
                thresh=i
            )
            false_positives = (len(filter(lambda x: x['prob'] > i,
                                          predicted_boxes[image]))
                               - detected_objects)

            total_number_of_boxes += len(boxes)
            accumulated_true_positives += detected_objects
            accumulated_false_positives += false_positives
            accumulated_false_negatives += len(boxes) - detected_objects

        if accumulated_true_positives + accumulated_true_positives == 0:
            break

        recall = float(accumulated_true_positives) / total_number_of_boxes
        precision = (float(accumulated_true_positives) /
                     (accumulated_true_positives +
                      accumulated_false_positives))
        recall_list.append(recall)
        precision_list.append(precision)
        print '[%g] Precision-Recall:' % i, precision, recall

    recall_list.append(0.)
    precision_list.append(1.)

    try:
        average_precision = metrics.auc(recall_list, precision_list)
    except:
        average_precision = 0.0

    f_measure = calculate_f_measure(precision_list, recall_list)

    return recall_list, precision_list, average_precision, f_measure


def plot_graph(recall_list, precision_list):
    import matplotlib.pyplot as plt

    plt.clf()
    plt.plot(recall_list, precision_list, label='Precision-Recall curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall')
    plt.legend(loc='upper right')
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
            if 'f_measure' not in data:
                data['f_measure'] = calculate_f_measure(data['precision_list'],
                                                        data['recall_list'])
                with open(prerec_path, 'w') as f:
                    f.write(json.dumps(data))
            return (data['recall_list'],
                    data['precision_list'],
                    data['average_precision'],
                    data['f_measure'])
    valid_path = (os.getcwd() + '/' +
                  valid_dir + '/valid-' +
                  weights_identifier + '.weights-' +
                  dataset_identifier)
    dataset_path = (os.getcwd() + '/' +
                    dataset_dir + '/' +
                    dataset_identifier + '/files.txt')
    predicted_boxes = load_predicted_boxes(valid_path)
    ground_truth = load_ground_truth(dataset_path)
    with open(dataset_path, 'r') as f:
        files = map(lambda x: x.strip(), f.readlines())

    (recall_list,
     precision_list,
     average_precision,
     f_measure) = calculate_precision_recall(ground_truth,
                                             predicted_boxes,
                                             files)
    with open(prerec_path, 'w') as f:
        f.write(json.dumps({
            'recall_list': recall_list,
            'precision_list': precision_list,
            'average_precision': average_precision,
            'f_measure': f_measure,
        }))
    return recall_list, precision_list, average_precision, f_measure


def dump_row(output, dataset):
    if dataset == '.DS_Store':
        return
    output.write(dataset)
    for weight in weight_files:
        if not weight.endswith('.weights'):
            continue
        outfile_name = prerec_dir + '/prerec-' + weight + '-' + dataset
        try:
            outfile = open(outfile_name, 'r')
            data = json.loads(outfile.read())
            output.write(',{0:.2%}'.format(data['average_precision']))
        except:
            output.write(',N/A')
    output.write('\n')


if __name__ == '__main__':
    if len(argv) > 2:
        (recall_list,
         precision_list,
         average_precision,
         f_measure) = load_and_calculate_precision_recall(argv[1],
                                                          argv[2])

        print 'AP: {0:.2%}'.format(average_precision)
        plot_graph(recall_list, precision_list)
    elif len(argv) == 2 and argv[1] == 'latex':
        weight_files = sorted(os.listdir(weights_dir))
        dataset_files = sorted(os.listdir(dataset_dir))

        for weight in weight_files:
            if not weight.endswith('.weights'):
                continue
            weights_identifier, _ = weight.split('.', 1)

            for dataset in dataset_files:
                try:
                    (
                        recall_list, precision_list, average_precision,
                        f_measure
                    ) = load_and_calculate_precision_recall(weights_identifier,
                                                            dataset)
                except IOError as e:
                    print e
                    continue

                filename = weights_identifier + '-' + dataset + '.txt'
                with open(latex_dir + '/' + filename, 'w') as f:
                    f.write('Precision Recall\n')
                    data = zip(precision_list, recall_list)
                    for precision, recall in data:
                        f.write('%f %f\n' % (precision, recall))

                filename = weights_identifier + '-' + dataset + '_ap.txt'
                with open(latex_dir + '/' + filename, 'w') as f:
                    f.write('{0:.2%}\n'.format(average_precision))

                filename = weights_identifier + '-' + dataset + '_f.txt'
                with open(latex_dir + '/' + filename, 'w') as f:
                    f.write('%f\n' % f_measure['value'])

                filename = weights_identifier + '-' + dataset + '_f_pos.txt'
                with open(latex_dir + '/' + filename, 'w') as f:
                    f.write('Precision Recall\n')
                    f.write('%f %f\n' % (f_measure['precision'],
                                         f_measure['recall']))

    elif len(argv) == 2 and argv[1] == 'matrix':
        weight_files = sorted(os.listdir(weights_dir))
        dataset_files = sorted(os.listdir(dataset_dir))

        with open(prerec_dir + '/matrix.txt', 'a') as output:
            for weight in weight_files:
                if not weight.endswith('.weights'):
                    continue
                output.write(',' + weight)
            output.write('\n')

            for dataset in dataset_files:
                dump_row(output, dataset)

            output.write('\n\n\n')
    else:
        weight_files = sorted(os.listdir(weights_dir))
        dataset_files = sorted(os.listdir(dataset_dir))
        for weight in weight_files:
            if not weight.endswith('.weights'):
                continue
            weight, _ = weight.split('.', 1)
            for dataset in dataset_files:
                print '### %s - %s ###' % (weight, dataset)
                try:
                    load_and_calculate_precision_recall(weight, dataset)
                except IOError as e:
                    print e
