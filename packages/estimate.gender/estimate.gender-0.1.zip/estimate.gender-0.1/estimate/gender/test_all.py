import os, sys
import argparse
import subprocess
import numpy
import bob
import errno
import socket

def make_sure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def main():
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUT_DIR = os.path.join(basedir, 'database')
  OUTPUT_DIR = os.path.join(basedir, 'output')
  
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-db', '--database', dest="database", default='banca', choices=('banca','mobio'), help="Database to be utilized (defaults to '%(default)s')")
  parser.add_argument('-c', '--classifier', dest="classifier", default='lda', choices=('lda', 'chi2', 'svm'), help="Classifier to be utilized (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')
  args = parser.parse_args()
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")
  
  make_sure_path_exists(os.path.join(args.outputdir,'test_all',args.database))
  
  IOD = [10, 20, 30]
  W_IOD_RATIO = [1.5, 2, 2.5, 3, 3.5]
  H_W_RATIO = [1/2.0, 1/1.5, 1, 1.5, 2]
    
  LBP_SCALE = ['8 1', '8 2', '16 2']
  NUM_BLOCK = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
  LBP_TYPE = ['reg', 'mod']
  
  if args.grid:
    sge_task_id = os.getenv('SGE_TASK_ID')
    if sge_task_id is None:
      raise Exception("not in the grid")
    CONF = [int(sge_task_id)-1]
  else:
    CONF = range(0,4950)
  
  for conf in CONF:
    print conf, socket.gethostname()
    iod = IOD[conf/(5*5*3*11*2)]
    w_iod_ratio = W_IOD_RATIO[conf%(5*5*3*11*2)/(5*3*11*2)]
    h_w_ratio = H_W_RATIO[conf%(5*5*3*11*2)%(5*3*11*2)/(3*11*2)]
    lbp_scale = LBP_SCALE[conf%(5*5*3*11*2)%(5*3*11*2)%(3*11*2)/(11*2)]
    num_block = NUM_BLOCK[conf%(5*5*3*11*2)%(5*3*11*2)%(3*11*2)%(11*2)/(2)]
    lbp_type = LBP_TYPE[conf%(5*5*3*11*2)%(5*3*11*2)%(3*11*2)%(11*2)%(2)]
    w = int(iod*w_iod_ratio)    
    print iod, w_iod_ratio, h_w_ratio, lbp_scale, num_block, lbp_type
    file_name = os.path.join(args.outputdir,'test_all',args.database,str(iod)+'_'+str(w_iod_ratio)+'_'+str(h_w_ratio)+'_'+lbp_scale+'_'+str(num_block)+'_'+lbp_type+'.hdf5')
    if os.path.exists(file_name):
      print 'File %s exists. Exiting..' %file_name
    else:
      command = "bin/estimateGender.py -db "+args.database+" -i "+args.inputdir+" -d "+str(iod)+" -w "+str(w)+" -r "+str(h_w_ratio)+" -nb "+str(num_block)+" -lt "+lbp_type+" -ls "+lbp_scale+" -c "+args.classifier+" -l -f -no"
      print command
      p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)  
      completed = False
      while not completed:
        if p.poll() is not None:
          completed = True
      out, err = p.communicate()
      print out
      acc = [float(s) for s in out.split('\n')[-5].split(' ')]
      eer = [float(s) for s in out.split('\n')[-4].split(' ')]
      hter = [float(s) for s in out.split('\n')[-3].split(' ')]
      zero = [float(s) for s in out.split('\n')[-2].split(' ')]
      file_hdf5 = bob.io.HDF5File(file_name, "w")
      file_hdf5.set('ACC', acc)
      file_hdf5.set('EER', eer)
      file_hdf5.set('HTER', hter)
      file_hdf5.set('ZERO', zero)
      del file_hdf5
  
  return 0

if __name__ == "__main__":
  main()
