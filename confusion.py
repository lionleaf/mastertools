#Given one folder of datasets and one folder of weight, it runs every weight on every dataset
import os
import sys
import argparse
import subprocess

datasets_path = '../datasets'
weights_path = '../weights'
yolo_path = '../darknet'

output_dir = '../recall'
valid_output_dir = '../valid'

weight_files = os.listdir(weights_path)
weight_files.sort()

print weight_files

dataset_files = os.listdir(datasets_path)
dataset_files.sort()

print dataset_files

#Generates the files.txt file required for yolo to read the dataset for all datasets in the folder
def generateFilelists(nr_of_files=None):
  print 'generating file lists. nr_of_files=' + str(nr_of_files)
  for dataset in dataset_files:
    nr = 0
    cpath = os.getcwd() + '/' + datasets_path + '/' + dataset
    print 'generating file.txt for ', dataset, cpath
    try:
      filelist = open(cpath + '/files.txt', 'w+')
    except:
      print 'Exception opening new file!!'
      continue
    for filen in os.listdir(cpath+'/images'):
      if filen.endswith('.jpg'):
        nr += 1
        filelist.write(cpath+'/images/'+filen+'\n')
        if nr_of_files and nr >= nr_of_files:
          break
    filelist.close()

def testWeight(redo, weight_file):
  for dataset in dataset_files:
    runRecall(redo, dataset, weight_file)

def runRecall(redo, dataset, weight_file):
  if dataset == '.DS_Store':
    return
  if not weight_file.endswith(".weights"):
    return  #folder?!
  dataset_path = os.getcwd() + '/' + datasets_path+'/' + dataset + '/files.txt'
  weight_path = os.getcwd() + '/' + weights_path + '/' + weight_file
  outfile_name = output_dir + '/' + weight_file + '-' + dataset
  new_directory = os.path.dirname(output_dir + '/' + weight_file)
  if not os.path.exists(new_directory):
    os.makedirs(new_directory)
  if os.path.isfile(outfile_name):
    print '\nresult file already exists. Skipping: ' + outfile_name
    return
  outfile = open(outfile_name,'a')

  print '\nStarting ' + outfile_name

  yolo_process = subprocess.Popen(["./darknet", 'yolo', 'recall', 'cfg/singleclass.cfg', weight_path, dataset_path], cwd=yolo_path, stderr=outfile)

  if yolo_process.wait() != 0:
    print "YOLO fail"
  else:
    print "\nCompleted " + outfile_name

  outfile.close()

def testAll(redo):
  print 'Testing all files! Redo = ' + str(redo)
  for weight in weight_files:
    testWeight(redo, weight)
    #testWeight(redo, weights_path + "/" + weight)

def runValid(redo, dataset, weight_file):
  if dataset == '.DS_Store':
    return
  if not weight_file.endswith(".weights"):
    return  #folder?!
  dataset_path = os.getcwd() + '/' + datasets_path+'/'+dataset+"/files.txt"
  weight_path = os.getcwd() + '/' + weights_path+'/'+weight_file
  outfile_name = os.getcwd() + '/' + valid_output_dir+'/valid-'+weight_file.split("/")[-1]+"-"+dataset
  tempfile = os.getcwd() + '/' + yolo_path + '/kitti/validated_car.txt'
  if(os.path.isfile(outfile_name)):
    print '\nresult file already exists. Skipping: ' + outfile_name
    return

  with open(dataset_path) as f:
    if len(f.readlines()) == 0:
      print '\nEmpty files.txt. Skipping: ' + outfile_name
      return

  print '\nStarting valid' + outfile_name

  cfg_file = 'cfg/singleclass.cfg'
  if weight_file.endswith('_large.weights'):
    cfg_file = 'cfg/singleclass_large.cfg'

  yolo_process = subprocess.Popen(["./darknet", 'yolo', 'valid', cfg_file, weight_path, dataset_path], cwd=yolo_path, stdout=open(os.devnull, 'wb'))

  if yolo_process.wait() != 0:
    print "YOLO fail"
  else:
    print "\nCompleted valid " + outfile_name
    os.rename(tempfile, outfile_name)


def validAll(redo):
  print 'Valid all files! Redo = ' + str(redo)
  for weight in weight_files:
    for dataset in dataset_files:
      runValid(redo, dataset, weight)


def kittiAll(redo):
  print 'Kitti on all files! Redo = ' + str(redo)
  for weight in weight_files:
    runRecall(redo, 'kitti', weight)


def weightsOverTime(redo, weight_folder):
  print 'Kitti on all files! Redo = ' + str(redo)
  weight_files_over_time = sorted(os.listdir(weights_path + '/' + weight_folder))
  for weight in weight_files_over_time:
    runRecall(redo, 'kitti', weight_folder + '/' + weight)


def dumpRow(output, dataset, custom_weight_files=None):
  if dataset == ".DS_Store":
    return
  output.write(dataset)
  for weight in (custom_weight_files or weight_files):
    if not weight.endswith(".weights"):
      continue
    outfile_name = output_dir+'/'+weight+"-"+dataset
    try:
      outfile = open(outfile_name,'r')
      #ugly oneliner: Read all lines into memory, get the last one, split by ":" and get last
      #should give final %-age
      output.write(","+outfile.readlines()[-1].split(":")[-1].strip()) #ugly
    except:
      output.write("," + "N/A")
  output.write('\n')


def customMatrix(weights_folder):

  print '\ngenerating custom matrix'
  output = open(output_dir + '/' + weights_folder + '/matrix.txt', 'a')

  weight_files_over_time = sorted(os.listdir(weights_path + '/' + weights_folder))
  for weight in weight_files_over_time:
    output.write(',' + weight)
  output.write('\n')
  dumpRow(output, 'kitti',
          map(lambda x: weights_folder + '/' + x, weight_files_over_time))
  output.write('\n\n\n')
  output.close()


def kittiMatrix():

  print '\ngenerating kitti matrix'
  output = open(output_dir + "/kitti.txt", 'a')

  for weight in weight_files:
    output.write(","+weight)
  output.write('\n')
  dumpRow(output, 'kitti')
  output.write('\n\n\n')
  output.close()

def generateMatrix(outfile):
  print '\ngenerating matrix'
  output = open(outfile, 'a')

  for weight in weight_files:
    if not weight.endswith(".weights"):
      continue
    output.write(","+weight)
  output.write('\n')
  for dataset in dataset_files:
    dumpRow(output, dataset)
  output.write('\n\n\n')
  output.close()


parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('action', help='matrix for the matrix, kitti for only kitti, kittiplot for plotting kitti performance over training time')
parser.add_argument('weights_folder', nargs='?', help='name of weights folder')
parser.add_argument('-n','--nocalc', help='Skip the calculation and just compile the result file', action='store_true', required=False)
args = vars(parser.parse_args())

if args['action'] == 'matrix':
  print "matrix!!"
  if not args['nocalc']:
    print "matrix!!"
    generateFilelists()
    testAll(False)
  generateMatrix(output_dir+"/matrix.txt")
elif args['action'] == 'kitti':
  print "kitti!!"
  if not args['nocalc']:
    generateFilelists()
    kittiAll(False)
  kittiMatrix()
elif args['action'] == 'weightsovertime':
  print "weightsovertime!!"
  if not args['nocalc']:
    generateFilelists()
    weightsOverTime(False, args['weights_folder'])
  customMatrix(args['weights_folder'])
elif args['action'] == 'valid':
  print "valid!!"
  generateFilelists()
  validAll(False)
else:
  print "invalid action!"

