#Given one folder of datasets and one folder of weight, it runs every weight on every dataset
import os
import subprocess

datasets_path = '../datasets'
weights_path = '../weights'
yolo_path = '../darknet'

output_dir = os.getcwd() + '/output'

#Generates the files.txt file required for yolo to read the dataset for all datasets in the folder
def generateFilelists(nr_of_files = 0):
  print 'generating file lists. nr_of_files=' + str(nr_of_files)
  for dataset in os.listdir(datasets_path):
    nr = 0
    cpath = os.getcwd() + '/' + datasets_path + '/' + dataset
    try:
      filelist = open(cpath + '/files.txt', 'w')
    except:
      continue
    for filen in os.listdir(cpath+'/images'):
      if filen.endswith('.jpg'):
        nr += 1
        filelist.write(cpath+'/images/'+filen+'\n')
        if nr_of_files and nr >= nr_of_files:
          break
    filelist.close()

def testWeight(redo, weight_file):
  for dataset in os.listdir(datasets_path):
    if dataset == '.DS_Store':
      continue
    dataset_path = os.getcwd() + '/' + datasets_path+'/'+dataset+"/files.txt"
    outfile_name = output_dir+'/'+weight_file.split("/")[-1]+"-"+dataset
    if(os.path.isfile(outfile_name)):
      print '\nresult file already exists. Skipping: ' + outfile_name
      continue
    outfile = open(outfile_name,'a')

    print '\nStarting ' + outfile_name

    yolo_process = subprocess.Popen(["./darknet", 'yolo', 'recall', 'cfg/singleclass.cfg', weight_file, dataset_path], cwd=yolo_path, stderr=outfile)

    if yolo_process.wait() != 0:
      print "YOLO fail"
    else:
      print "\nCompleted " + outfile_name

    outfile.close()


def testAll(redo):
  print 'Testing all files! Redo = ' + str(redo)
  for weight in os.listdir(weights_path):
    testWeight(redo, os.getcwd() + '/' + weights_path + "/" + weight)



def generateMatrix(outfile):
  print '\ngenerating matrix'
  output = open(outfile, 'a')

  for weight in os.listdir(weights_path):
    output.write("\t"+weight)
  output.write('\n')
  for dataset in os.listdir(datasets_path):
    if dataset == ".DS_Store":
      continue
    output.write(dataset)
    for weight in os.listdir(weights_path):
      outfile_name = output_dir+'/'+weight+"-"+dataset
      try:
        outfile = open(outfile_name,'r')
        #ugly oneliner: Read all lines into memory, get the last one, split by ":" and get last
        #should give final %-age
        output.write("\t"+outfile.readlines()[-1].split(":")[-1].strip()) #ugly
      except:
        output.write("\t" + "N/A")
    output.write('\n')
  output.write('\n\n\n')
  output.close()

generateFilelists()
testAll(False)
generateMatrix(output_dir+"/matrix.txt")

