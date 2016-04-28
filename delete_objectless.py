
from os import listdir, remove

for file in listdir('data/labels'):
    with open('data/labels/' + file, 'r') as f:
        if f.read().strip() == '':
            print 'deleting', file
            remove('data/labels/' + file)
            basename, _ = file.rsplit('.', 1)
            remove('data/images/' + basename + '.jpg')
