# -*- coding: utf-8 -*-

"""
Open one image to inspect its labels:
```
python imageview.py data/images/image.jpg
```

Open a folder to browse all its images:
```
python imageview.py data/images/
```

Open a list of images from a txt-file:
```
python imageview.py good_list.txt
```

Browse good/bad detections:
```
python imageview.py good <weights-name> <ground-truths>
python imageview.py bad <weights-name> <ground-truths>
```
"""

import numpy as np
import os
from sys import argv
from PIL import Image
from scipy import ndimage, misc
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, RadioButtons

from converters import from_edges_to_centered, from_fullsize_to_relative
from loaders import load_predicted_boxes, load_list_of_images
from evaluate_detections import from_validation_output

image_width = 448
image_height = 448
pixel_depth = 255

dataset_dir = '../datasets'
valid_dir = '../valid'
output_dir = '../saved_images'


def load_image(image_filename):
    image_filename = image_filename.strip()
    try:
        img_raw = misc.imresize(ndimage.imread(image_filename),
                                (image_height, image_width))
        image_data = (img_raw.astype(float) - pixel_depth / 2) / pixel_depth
    except IOError as e:
        print 'Could not read:', image_filename, ':', e

    return image_data


def load_labels(label_filename):
    labels = np.ndarray(shape=(27, 5), dtype=np.float32)
    labels.fill(-1)

    try:
        if (label_filename == '.DS_Store'):
            return

        with open(label_filename, 'r') as label_file:
            count = 0
            for line in label_file:
                labels[count, :] = line.split()
                count += 1
            count += 1
    except IOError as e:
        print 'Could not read:', label_filename, ':', e

    return labels


patches = []
image_display = None


def show_image_data(image, labels):
    for patch in patches:
        patch.remove()
    del patches[:]

    global image_display
    if image_display:
        image_display.set_data(image[:, :, :] + 0.5)
    else:
        image_display = plt.imshow(image[:, :, :] + 0.5)

    for box in labels:
        if box[0] < 0:
            break  # end of classes for this img

        rectangle = Rectangle((box[1]*image_width - box[3]*image_width*0.5,
                               box[2]*image_height - box[4]*image_height*0.5),
                              box[3]*image_width, box[4]*image_height,
                              ec='red', fill=False, linewidth=3)
        patches.append(rectangle)
        ca.add_patch(rectangle)
    plt.draw()


def show_image(image_filename, labels=None):
    image = load_image(image_filename)

    if not labels:
        label_filename = image_filename.replace('.jpg', '.txt') \
                                       .replace('/images/', '/labels/') \
                                       .replace('/JPEGImages/', '/labels/')
        labels = load_labels(label_filename)
    else:
        im = Image.open(image_filename)
        new_labels = []
        for label in labels:
            box = from_edges_to_centered(label[1:])
            new_labels.append([0] + from_fullsize_to_relative(box, im.size))
        labels = new_labels

    show_image_data(image, labels)

    plt.axes()
    plt.axis('off')
    plt.title(image_filename, fontsize=14)


class Index(object):
    ind = 0

    def __init__(self, image_filenames, labels, radio):
        self.image_filenames = image_filenames
        self.labels = labels
        self.radio = radio

    def save(self, event):
        global image_display, weights_identifier
        image_filename = os.path.normpath(self.image_filenames[self.ind])
        parent_directories = os.path.dirname(image_filename).split(os.sep)
        dataset_name = parent_directories[-2]
        middle_part = (weights_identifier + '_') if weights_identifier else ''
        output_filename = (dataset_name + '_' + middle_part +
                           os.path.basename(image_filename))
        plt.savefig(output_dir + '/' + output_filename)

    def next(self, event):
        self.skip(int(self.radio.value_selected))

    def prev(self, event):
        self.skip(-int(self.radio.value_selected))

    def skip(self, amount):
        self.ind = (self.ind + amount) % len(self.image_filenames)
        plt.suptitle(self.ind, fontsize=14)
        image_filename = self.image_filenames[self.ind]
        image_id, _ = os.path.splitext(os.path.basename(image_filename))
        image_labels = self.labels[image_id] if self.labels else None
        show_image(self.image_filenames[self.ind], image_labels)


def open_path(path, labels):
    global bnext, bprev, bskip, radio
    image_filenames = map(lambda filename: os.path.join(path, filename),
                          filter(lambda filename: filename[0] != '.',
                                 os.listdir(path)))
    print 'Opened path:', path
    open_list(image_filenames, labels)


def open_list(image_filenames, labels):
    global bnext, bprev, bskip, radio, bsave
    image_id, _ = os.path.splitext(os.path.basename(image_filenames[0]))
    image_labels = labels[image_id] if labels else None
    show_image(image_filenames[0], image_labels)
    plt.suptitle(0, fontsize=14)

    rax = plt.axes([0.85, 0.15, 0.1, 0.15])
    radio = RadioButtons(rax, ('1', '5', '10', '100', '500', '1000'), 0)

    callback = Index(image_filenames, labels, radio)
    axsave = plt.axes([0.75, 0.05, 0.05, 0.075])
    axprev = plt.axes([0.85, 0.05, 0.05, 0.075])
    axnext = plt.axes([0.9, 0.05, 0.05, 0.075])

    bsave = Button(axsave, 'Save')
    bsave.on_clicked(callback.save)
    bnext = Button(axnext, '>')
    bnext.on_clicked(callback.next)
    bprev = Button(axprev, '<')
    bprev.on_clicked(callback.prev)


if __name__ == '__main__':
    ca = plt.gca()

    if argv[1]:
        labels = None
        if len(argv) >= 4:
            weights_identifier = argv[2]
            dataset_identifier = argv[3]
            valid_path = (os.getcwd() + '/' +
                          valid_dir + '/valid-' +
                          weights_identifier + '.weights-' +
                          dataset_identifier)
            dataset_path = (os.getcwd() + '/' +
                            dataset_dir + '/' +
                            dataset_identifier + '/files.txt')

            labels = load_predicted_boxes(valid_path)
            threshold = float(argv[4]) if len(argv) >= 5 else 0.2
            for image_id in labels:
                labels[image_id] = filter(lambda label: float(label[0]) > threshold,
                                          labels[image_id])
        if argv[1][-3:] == 'jpg':
            image_filename = argv[1]
            show_image(image_filename, labels)

        elif argv[1][-3:] == 'txt':
            image_filenames = load_list_of_images(argv[1])
            open_list(image_filenames, labels)

        elif argv[1] == 'good' or argv[1] == 'bad':
            good_list, bad_list = from_validation_output(valid_path,
                                                         dataset_path)

            print '%d good images, %s bad images' % (len(good_list),
                                                     len(bad_list))
            if argv[1] == 'good':
                open_list(good_list, labels)
            if argv[1] == 'bad':
                open_list(bad_list, labels)
        else:
            open_path(argv[1], labels)
    else:
        open_path('data/images/')

    plt.show()
