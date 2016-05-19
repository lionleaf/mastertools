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


def load_list_of_images(filename):
    with open(filename, 'r') as f:
        filenames = filter(lambda filename: filename[0] != '#',
                           map(lambda filename: filename.strip(),
                               f.readlines()))
        return filenames
