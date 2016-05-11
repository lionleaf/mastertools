"""
Evaluate detections

Usage:

python evaluate_detections.py recall <recall-output> <ground-truth-list>

or

python evaluate_detections.py valid <predicted-boxes> <ground-truth-list>
"""

from os import path
from sys import argv
from PIL import Image
import re


def parse_detection(box):
    return {
        'xmin': float(box[0]) - float(box[2]) / 2,
        'ymin': float(box[1]) - float(box[3]) / 2,
        'xmax': float(box[0]) + float(box[2]) / 2,
        'ymax': float(box[1]) + float(box[3]) / 2,
    }


def calculate_intersection(a, b):
    left = max(a['xmin'], b['xmin'])
    right = min(a['xmax'], b['xmax'])
    top = max(a['ymin'], b['ymin'])
    bottom = min(a['ymax'], b['ymax'])
    if left < right and top < bottom:
        return (right - left) * (bottom - top)
    else:
        return 0


def calculate_area(rect):
    return (rect['xmax'] - rect['xmin']) * (rect['ymax'] - rect['ymin'])


def from_validation_output(contents, ground_truths):
    detections_per_image = {}
    for line in contents:
        basename, prediction = line.split(' ', 1)
        prediction = prediction.split(' ')
        if basename in detections_per_image:
            detections_per_image[basename].append(prediction)
        else:
            detections_per_image[basename] = [prediction]

    truths = {}

    with open(ground_truths, 'r') as listfile:
        files = map(lambda x: x.strip(), listfile.readlines())
        for file in files:
            basepath, _ = file.rsplit('.', 1)
            labelfile = basepath.replace('images', 'labels') + '.txt'
            _, basename = basepath.rsplit('/', 1)
            with open(labelfile, 'r') as f:
                truths[basename] = []
                boxes = map(lambda x: x.strip(), f.readlines())
                for box in boxes:
                    truths[basename].append(box.split(' ')[1:])

    good_list = []
    bad_list = []

    total_number_of_boxes = 0
    accumulated_detected_objects = 0
    for imagepath in files:
        _, imagefilename = imagepath.rsplit('/', 1)
        image, _ = imagefilename.rsplit('.', 1)
        im = Image.open(imagepath)
        width, height = im.size
        boxes = truths[image]
        total_number_of_boxes += len(boxes)
        detected_objects = 0
        for box in boxes:
            ground_truth = parse_detection(box)
            best_iou = 0
            for detection in detections_per_image[image]:
                if detection[0] < 0.001:
                    continue
                test_result = {
                    'xmin': float(detection[1]) / width,
                    'ymin': float(detection[2]) / height,
                    'xmax': float(detection[3]) / width,
                    'ymax': float(detection[4]) / height,
                }
                intersection = calculate_intersection(ground_truth,
                                                      test_result)
                union = (calculate_area(ground_truth) +
                         calculate_area(test_result) -
                         intersection)
                iou = intersection / float(union)
                if iou > best_iou:
                    best_iou = iou
            if best_iou >= 0.5:
                detected_objects += 1

            # print '### %s: %f' % (image, best_iou)

        if float(detected_objects) / len(boxes) > 0:
            good_list.append(imagepath)
        else:
            bad_list.append(imagepath)

        accumulated_detected_objects += detected_objects
        print ('recall', image,
               float(accumulated_detected_objects) / total_number_of_boxes)
        # print ground_truth
        # print detections_per_image[image]
    write_output(good_list, bad_list)


def from_recall_output(contents, ground_truths):
    r = re.compile('\d+\s+(\d+)\s+(\d+)\s+.+\%')
    detection_info = map(r.match, filter(r.match, contents))

    recall_per_image = []
    for i, info in enumerate(detection_info):
        detections_in_image = int(info.group(1))
        if i != 0:
            detections_in_image -= int(detection_info[i-1].group(1))

        boxes_in_image = int(info.group(2))
        if i != 0:
            boxes_in_image -= int(detection_info[i-1].group(2))

        recall_per_image.append(float(detections_in_image) / boxes_in_image)

    good_list = []
    bad_list = []

    with open(ground_truths, 'r') as f:
        filenames = map(lambda x: x.strip(), f.readlines())

    for i, recall in enumerate(recall_per_image):
        if recall > 0:
            good_list.append(filenames[i])
        else:
            bad_list.append(filenames[i])

    write_output(good_list, bad_list)


def write_output(good_list, bad_list):
    with open('good_list.txt', 'w') as f:
        f.write('\n'.join(good_list))

    with open('bad_list.txt', 'w') as f:
        f.write('\n'.join(bad_list))

if __name__ == '__main__':
    if path.isfile('good_list.txt') or path.isfile('bad_list.txt'):
        print 'good_list.txt and/or bad_list.txt already exists'
        exit(0)
    if argv[1] == 'recall':
        with open(argv[2], 'r') as f:
            contents = map(lambda line: line.strip(), f.readlines())
            from_recall_output(contents, argv[3])
    if argv[1] == 'valid':
        with open(argv[2], 'r') as f:
            contents = map(lambda line: line.strip(), f.readlines())
            from_validation_output(contents, argv[3])
