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
from loaders import load_predicted_boxes, load_ground_truth
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


def detected_objects_in_image(boxes, detections_for_image,
                              thresh=0.001, iou_thresh=0.5):
    detected_objects = 0
    for box in boxes:
        ground_truth = parse_detection(box)
        best_iou = 0
        for detection in detections_for_image:
            if detection['prob'] < thresh:
                continue
            intersection = calculate_intersection(ground_truth,
                                                  detection)
            union = (calculate_area(ground_truth) +
                     calculate_area(detection) -
                     intersection)
            iou = intersection / float(union)
            if iou > best_iou:
                best_iou = iou
        if best_iou >= iou_thresh:
            detected_objects += 1
    return detected_objects


def from_validation_output(predictions, ground_truths):
    detections_per_image = load_predicted_boxes(predictions)

    truths = load_ground_truth(ground_truths)

    with open(ground_truths, 'r') as listfile:
        files = map(lambda x: x.strip(), listfile.readlines())

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
        detections = {
            'prob': float(detections_per_image[image][0]),
            'xmin': float(detections_per_image[image][1]) / width,
            'ymin': float(detections_per_image[image][2]) / height,
            'xmax': float(detections_per_image[image][3]) / width,
            'ymax': float(detections_per_image[image][4]) / height,
        }
        detected_objects = detected_objects_in_image(
            boxes,
            detections
        )

        if len(boxes) > 0 and float(detected_objects) / len(boxes) > 0:
            good_list.append(imagepath)
        else:
            bad_list.append(imagepath)

        accumulated_detected_objects += detected_objects

        # print ('recall', image,
        #        float(accumulated_detected_objects) / total_number_of_boxes)
        # print ground_truth
        # print detections_per_image[image]
    return (good_list, bad_list)


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

        if boxes_in_image > 0:
            recall_per_image.append(float(detections_in_image) /
                                    boxes_in_image)
        else:
            recall_per_image.append(0)

    good_list = []
    bad_list = []

    with open(ground_truths, 'r') as f:
        filenames = map(lambda x: x.strip(), f.readlines())

    for i, recall in enumerate(recall_per_image):
        if recall > 0:
            good_list.append(filenames[i])
        else:
            bad_list.append(filenames[i])

    return (good_list, bad_list)


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
            write_output(from_recall_output(contents, argv[3]))
    elif argv[1] == 'valid':
        write_output(from_validation_output(argv[2], argv[3]))
    else:
        print 'Unkown command'
        print 'Try \'recall\' or \'valid\''
