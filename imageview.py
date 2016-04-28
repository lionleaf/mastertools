import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import ndimage, misc
from matplotlib import pyplot
import matplotlib as mpl
from matplotlib.patches import Rectangle

image_path = 'data/images/'
label_path = 'data/labels/'
image_files = os.listdir(image_path)
label_files = os.listdir(label_path)

image_size = 498
pixel_depth = 255

dataset_size = len(image_files) 
print("Dataset_size = " + str(dataset_size))
i=0
dataset = np.ndarray(shape=(dataset_size, image_size, image_size, 3),
                     dtype=np.float32)
for image_file in image_files:
    try:
        image_file = image_file.strip()
        img_raw = misc.imresize(ndimage.imread(image_path + image_file), (image_size, 
                                                             image_size))
        image_data = (img_raw.astype(float) - 
                        pixel_depth / 2) / pixel_depth
        dataset[i, :, :, :] = image_data
        i+=1
        print(i)
    except IOError as e:
        print('Could not read:', image_path + image_file, ':', e, '- it\'s ok, skipping.')


classes = ["car"]

dataset_size = len(label_files)
i=0
labels = np.ndarray(shape=(dataset_size, 27, 5), dtype=np.float32)
labels.fill(-1)

for label_filename in label_files:
    try:
        if (label_filename == ".DS_Store"):
          continue;
        label_file = open(label_path + label_filename)
        count = 0
        for line in label_file:
            labels[i,count,:] = line.split()
            count+=1
        i += 1
        count += 1
        print(i)
    except IOError as e:
        print('Could not read:', label_path + label_filename, ':', e, '- it\'s ok, skipping.')

print("Labels loaded")



def showImageData(index):

  pyplot.imshow(dataset[index,:,:,:] + 0.5)

  for box in labels[index]:
    if(box[0] < 0):
      break; #end of classes for this img

    print(classes[int(box[0])])
    ca = plt.gca()
    ca.add_patch(Rectangle((box[1]*image_size - box[3]*image_size*0.5 
                            ,box[2]*image_size - box[4]*image_size*0.5 )
                            , box[3]*image_size, box[4]*image_size, ec="red", fill=False))

  pyplot.show()



for i in xrange(10):
  showImageData(i);

print('Done!')
