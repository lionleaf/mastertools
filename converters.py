def from_fullsize_to_relative(raw, image_size):
    width, height = image_size
    return [
        float(raw[0]) / width,
        float(raw[1]) / height,
        float(raw[2]) / width,
        float(raw[3]) / height
    ]


def from_centered_to_edges(raw):
    return [
        float(raw[0]) - float(raw[2]) / 2,
        float(raw[1]) - float(raw[3]) / 2,
        float(raw[0]) + float(raw[2]) / 2,
        float(raw[1]) + float(raw[3]) / 2,
    ]


def from_edges_to_centered(raw):
    width = float(raw[2]) - float(raw[0])
    height = float(raw[3]) - float(raw[1])
    return [
        float(raw[0]) + width / 2,
        float(raw[1]) + height / 2,
        width,
        height
    ]
