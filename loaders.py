def load_predicted_boxes(filename):
    with open(filename, 'r') as f:
        contents = map(lambda line: line.strip(), f.readlines())
        detections_per_image = {}
        for line in contents:
            basename, prediction = line.split(' ', 1)
            prediction = prediction.split(' ')
            if basename in detections_per_image:
                detections_per_image[basename].append(prediction)
            else:
                detections_per_image[basename] = [prediction]
        return detections_per_image


def load_ground_truth(filename):
    with open(filename, 'r') as listfile:
        files = map(lambda x: x.strip(), listfile.readlines())
        truths = {}
        for file in files:
            basepath, _ = file.rsplit('.', 1)
            labelfile = basepath.replace('images', 'labels') + '.txt'
            _, basename = basepath.rsplit('/', 1)
            with open(labelfile, 'r') as f:
                truths[basename] = []
                boxes = map(lambda x: x.strip(), f.readlines())
                for box in boxes:
                    truths[basename].append(box.split(' ')[1:])
        return truths


def load_list_of_images(filename):
    with open(filename, 'r') as f:
        filenames = filter(lambda filename: filename[0] != '#',
                           map(lambda filename: filename.strip(),
                               f.readlines()))
        return filenames
