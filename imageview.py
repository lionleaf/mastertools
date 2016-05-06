# -*- coding: utf-8 -*-

import numpy as np
import os
from sys import argv
from scipy import ndimage, misc
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, RadioButtons

image_width = 896
image_height = 896
pixel_depth = 255


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
                              ec='red', fill=False)
        patches.append(rectangle)
        ca.add_patch(rectangle)
    plt.draw()


def show_image(image_filename, label_filename=None):
    if not label_filename:
        label_filename = image_filename.replace('.jpg', '.txt') \
                                       .replace('/images/', '/labels/')
    image = load_image(image_filename)
    labels = load_labels(label_filename)
    show_image_data(image, labels)

    plt.axes()
    plt.title(image_filename, fontsize=14)


class Index(object):
    ind = 0

    def __init__(self, image_filenames, radio):
        self.image_filenames = image_filenames
        self.radio = radio

    def next(self, event):
        self.skip(int(self.radio.value_selected))

    def prev(self, event):
        self.skip(-int(self.radio.value_selected))

    def skip(self, amount):
        self.ind = (self.ind + amount) % len(self.image_filenames)
        plt.suptitle(self.ind, fontsize=14)
        show_image(self.image_filenames[self.ind])


def open_path(path):
    global bnext, bprev, bskip, radio
    image_filenames = map(lambda filename: os.path.join(path, filename),
                          filter(lambda filename: filename[0] != '.',
                                 os.listdir(path)))
    print 'Opened path:', path

    show_image(image_filenames[0])
    plt.suptitle(0, fontsize=14)

    rax = plt.axes([0.85, 0.15, 0.1, 0.15])
    radio = RadioButtons(rax, ('1', '5', '10', '100', '500', '1000'), 0)

    callback = Index(image_filenames, radio)
    axprev = plt.axes([0.85, 0.05, 0.05, 0.075])
    axnext = plt.axes([0.9, 0.05, 0.05, 0.075])
    bnext = Button(axnext, '>')
    bnext.on_clicked(callback.next)
    bprev = Button(axprev, '<')
    bprev.on_clicked(callback.prev)


if __name__ == '__main__':
    ca = plt.gca()

    if argv[1]:
        if argv[1][-3:] == 'jpg':
            image_filename = argv[1]
            show_image(image_filename)
        else:
            open_path(argv[1])
    else:
        open_path('data/images/')

    plt.show()
