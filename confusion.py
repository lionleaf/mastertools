#Given one folder of datasets and one folder of weight, it runs every weight on every dataset
import os
import sys
import argparse
import subprocess

datasets_path = '../datasets'
weights_path = '../weights'
yolo_path = '/home/stiaje/darknet'

output_dir = '../recall'

weight_files = os.listdir(weights_path)
weight_files.sort()

print weight_files

dataset_files = os.listdir(datasets_path)
dataset_files.sort()

print dataset_files

#Generates the files.txt file required for yolo to read the dataset for all datasets in the folder
def generateFilelists(nr_of_files = 0):
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
  dataset_path = os.getcwd() + '/' + datasets_path+'/'+dataset+"/files.txt"
  weight_path = os.getcwd() + '/' + weights_path+'/'+weight_file
  outfile_name = output_dir+'/'+weight_file.split("/")[-1]+"-"+dataset
  if(os.path.isfile(outfile_name)):
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


def kittiAll(redo):
  print 'Kitti on all files! Redo = ' + str(redo)
  for weight in weight_files:
    runRecall(redo, 'kitti', weight)


def dumpRow(output, dataset):
  if dataset == ".DS_Store":
    return
  output.write(dataset)
  for weight in weight_files:
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
parser.add_argument('action', help='Calculate a matrix of all results')
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
else:
  print "invalid action!"

