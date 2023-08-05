import os, sys
import argparse
import numpy
import bob
import errno
#import matplotlib.pyplot

def create_feature_set(db, dbname, indir, basedir, ext, ftdir, objects, r, iod, w, lbp, nb, lt, ls, f, no):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = []
  face_eyes_norm = bob.ip.FaceEyesNorm(eyes_distance = iod, crop_height = int(w*r), crop_width = w, crop_eyecenter_offset_h = w*r*0.4, crop_eyecenter_offset_w = w*0.5)
  cropped_image = numpy.ndarray((w*r, w), dtype = numpy.float64)
  c = 0
  if dbname == 'morph':
    import csv
    csvfile = open(os.path.join(indir,'MORPH_Album2_EYECOORDS.csv'),'rb')
    csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    csvreader.next()
    annotation = {}
    for row in csvreader:
      annotation[row[0].split(',')[0]] = [int(row[0].split(',')[1]), int(row[0].split(',')[2]), int(row[0].split(',')[3]), int(row[0].split(',')[4])]
    annotation['021896_2F64'] = [67,99,117,103]
    annotation['027324_0M64'] = [59,109,112,108]
      
  for obj in objects:
    if dbname == 'banca' or dbname == 'feret' or dbname == 'lfw' or dbname == 'morph' or c%4 == 0:
      obj_path = str(obj.make_path(indir,ext))
      ft_path = os.path.join(ftdir,obj.path.split('/')[-1]+'.hdf5')
      if not os.path.exists(ft_path) or f:
        img = bob.io.load(obj_path)
        if len(img.shape)>2:
          img = bob.ip.rgb_to_gray(img)
        if dbname == 'banca':
          eyes = db.annotations(obj.id)
          face_eyes_norm(img, cropped_image, re_y = eyes['reye'][0], re_x = eyes['reye'][1], le_y = eyes['leye'][0], le_x = eyes['leye'][1])
        elif dbname == 'mobio':
          posdir = '/'.join(indir.split('/')[:-1]+['IMAGE_ANNOTATIONS'])
          eyes = numpy.loadtxt(str(obj.make_path(posdir,'.pos')))
          face_eyes_norm(img, cropped_image, re_y = eyes[1], re_x = eyes[0], le_y = eyes[3], le_x = eyes[2])
        elif dbname == 'feret':
          pos_path = str(obj.make_path(indir,'.pos'))
          eyes = numpy.loadtxt(pos_path)
          face_eyes_norm(img, cropped_image, re_y = eyes[1], re_x = eyes[0], le_y = eyes[3], le_x = eyes[2])
        elif dbname == 'lfw':
          pos_path = str(obj.make_path(basedir+'/databases/lfw_eyec','.pos'))
          eyes = numpy.genfromtxt(pos_path,dtype='double')[:,1:]
          face_eyes_norm(img, cropped_image, re_y = eyes[0][1], re_x = eyes[0][0], le_y = eyes[1][1], le_x = eyes[1][0])
        elif dbname == 'morph':
          eyes = annotation[obj.path.split('.')[0].split('/')[2]]
          face_eyes_norm(img, cropped_image, re_y = eyes[1], re_x = eyes[0], le_y = eyes[3], le_x = eyes[2])
        #matplotlib.pyplot.imshow(cropped_image, cmap = matplotlib.cm.Greys_r)
        #matplotlib.pyplot.show()
        if lbp:
          # LBP histograms
          ft = lbphist(cropped_image,lbptype=lt,numblock=nb,lbpscale=ls)
        else:
          # Raw pixel values
          ft = cropped_image.flatten()
        if not no:
          file_hdf5 = bob.io.HDF5File(str(ft_path), "w")
          file_hdf5.set('LBP_Feature', ft)
          del file_hdf5
      else:
        file_hdf5 = bob.io.HDF5File(str(ft_path))
        ft = file_hdf5.read('LBP_Feature')
      dataset.append(ft)
    c = c+1      
  return dataset
  
def divideframe(frame,numblock):
  blockslist = []
  width_y = int(frame.shape[0]/numblock)
  width_x = int(frame.shape[1]/numblock)
  start_y = [width_y*r for r in range(0,numblock)]
  start_x = [width_x*r for r in range(0,numblock)]
  for x in range(0,len(start_x)):
    for y in range(0,len(start_y)):
      sx = start_x[x]
      sy = start_y[y]
      nextblock = frame[sy:sy+width_y, sx:sx+width_x]
      blockslist.append(nextblock)
  return blockslist # list of subblocks as frames
  
def lbphist(img,lbptype='reg',numblock = 1, lbpscale=None, norm=False):
  num_points = int(str(lbpscale[0]).replace("'","").replace(",","").replace("(","").replace(")","").replace(" ",""))
  radius = int(lbpscale[1][0])
  elbptype = {'reg':bob.ip.ELBPType.REGULAR, 'tra':bob.ip.ELBPType.TRANSITIONAL, 'dir':bob.ip.ELBPType.DIRECTION_CODED}
  finalhist = numpy.array([])
  if lbptype != 'mod':
    lbp = bob.ip.LBP(num_points,radius,radius,uniform=True,elbp_type=elbptype[lbptype]) 
  else:
    lbp = bob.ip.LBP(num_points,radius,radius,uniform=True,to_average=True)
  
  lbpimage = numpy.ndarray(lbp.get_lbp_shape(img), 'uint16') # allocating the image with lbp codes
  lbp(img, lbpimage) # calculating the lbp image
  
  blockslist = divideframe(lbpimage, numblock) # divide the lbp image into non-overlapping blocks
  for bl in blockslist:
    hist = bob.ip.histogram(bl, 0, lbp.max_label-1, lbp.max_label)
    if norm:
      hist = hist / sum(hist) # histogram normalization
    finalhist = numpy.append(finalhist, hist) # concatenate the subblocks' already normalized histograms
  return finalhist.astype(numpy.float)

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
  MACHINE_DIR = os.path.join(basedir, 'output','machine')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--inputdir', dest='inputdir', default=INPUT_DIR, metavar='DIR', type=str, help='Base directory containing the data files to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('-o', '--outputdir', dest="outputdir", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-db', '--database', dest="database", default='banca', choices=('banca', 'mobio','feret','lfw','morph'), help="Database to be utilized (defaults to '%(default)s')")
  parser.add_argument('-d', '--iod', dest="iod", default=30, type=float, help="Inter-occular distance (defaults to '%(default)s')")
  parser.add_argument('-w', '--width', dest="width", default=90, type=int, help="Width of the cropped image (defaults to '%(default)s')")
  parser.add_argument('-r', '--ratio', dest="ratio", default=1, type=float, help="Ratio height/width (defaults to '%(default)s')")
  parser.add_argument('-l', '--lbp', dest='lbp', default=False, action='store_true', help='If set, LBP histograms will be extracted instead of using raw pixel values.')
  parser.add_argument('-nb', '--numblock', dest="numblock", default=1, type=int, help="Number of blocks for LBP histogram calculations (defaults to '%(default)s')")
  parser.add_argument('-lt', '--lbptype', dest="lbptype", default='reg', choices=('reg', 'tra', 'dir', 'mod'), help="LBP types to be used in feature extraction (defaults to '%(default)s')")
  parser.add_argument('-ls', '--lbpscale', dest="lbpscale", default=[8,1], type=tuple, nargs=2, help="LBP scale to be used in feature extraction ([number of points] [radius]) (defaults to '%(default)s')")
  parser.add_argument('-c', '--classifier', dest="classifier", default='lda', choices=('lda', 'chi2', 'svm'), help="LBP types to be used in feature extraction (defaults to '%(default)s')")
  parser.add_argument('-md', '--machinedir', dest="machinedir", default=MACHINE_DIR, help="This directory for the machine files to be used/saved by this procedure (defaults to '%(default)s')")
  parser.add_argument('-f', dest='force', default=False, action='store_true', help='If set, the extracted features are over-written.')
  parser.add_argument('-no', dest='nooutput', default=False, action='store_true', help='If set, the extracted features are not saved.')
  parser.add_argument('-gb', dest='genderbalance', default=False, action='store_true', help='If set, the number of samples for each gender in the training set will be made equal.')
  parser.add_argument('-sm', dest='savemachine', default=False, action='store_true', help='If set, the trained machines will be saved in the output directory.')
  parser.add_argument('-lm', dest='loadmachine', default=False, action='store_true', help='If set, the trained machines will be loaded from the given machine directory.')
  parser.add_argument('-td', '--training_database', dest="training_database", default=None, choices=('banca', 'mobio','feret','lfw','morph'), help="Training database of which saved machines will be loaded. If not specified, the same database will be used.(defaults to '%(default)s')")  
  parser.add_argument('-tf', '--training_fold', dest="training_fold", default=None, type=int, help="Fold number for the training database of which saved machines will be loaded. If not specified, the same fold will be used. (defaults to '%(default)s')")
  parser.add_argument('-g', dest='grid', default=False, action='store_true', help='If set, the grid will be used.')

  args = parser.parse_args()
  
  ftdir = args.outputdir+'/LBP/'+args.database
  if args.training_database is None:
    args.training_database = args.database
  
  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")

  make_sure_path_exists(args.outputdir)
  make_sure_path_exists(args.machinedir)
  make_sure_path_exists(ftdir)
  
  if args.genderbalance:
    machine_suffix = '_balanced'
  else:
    machine_suffix = ''
    
  if args.lbp:
    lbp_string = 'and LBP parameters type:%s scale:%s %s number of blocks:%d' %(args.lbptype,str(args.lbpscale[0]).replace("'","").replace(",","").replace("(","").replace(")","").replace(" ",""),int(args.lbpscale[1][0]),args.numblock)
  else:
    lbp_string = ''
  if args.genderbalance:
    gb_string = ' after the gender distribution is made uniform'
  else:
    gb_string = ''
  if args.training_fold is None:
    fold_string = 'regular folds'
  else:
    fold_string = 'fold:'+str(args.training_fold)
    
  print "Running gender estimation tests on evaluation partition of %s database with cropping parameters IOD:%d W:%d H:%d %s using training partition of %s database (%s) for training %s%s." %(args.database,args.iod, args.width, int(args.width*args.ratio),lbp_string,args.training_database,fold_string,args.classifier,gb_string)    
  train_files_F = []
  train_files_M = []
  eval_files_F = []
  eval_files_M = []
  
  if args.grid:
    sge_task_id = os.getenv('SGE_TASK_ID')
    if sge_task_id is None:
      raise Exception("not in the grid")
    folds = [int(sge_task_id)-1]
  else:
    folds = range(0,5)
  
  if (args.database == 'banca'):
    import xbob.db.banca as db 
    database = db.Database()
    id_F = [c.id for c in database.clients(genders='f')]
    id_M = [c.id for c in database.clients(genders='m')]
    train_files_F.append(database.objects(protocol='G',model_ids=id_F,groups=['world','dev']))
    train_files_M.append(database.objects(protocol='G',model_ids=id_M,groups=['world','dev']))
    eval_files_F.append(database.objects(protocol='G',model_ids=id_F,groups='eval'))
    eval_files_M.append(database.objects(protocol='G',model_ids=id_M,groups='eval'))
    extension = '.ppm'
  elif (args.database == 'mobio'):
    import xbob.db.mobio as db
    database = db.Database()
    train_files_F.append(database.objects(gender='female',groups=['world','dev']))
    train_files_M.append(database.objects(gender='male',groups=['world','dev']))
    eval_files_F.append(database.objects(gender='female',groups='eval'))
    eval_files_M.append(database.objects(gender='male',groups='eval'))
    extension = '.png'
  elif (args.database == 'feret'):
    import xbob.db.verification.filelist
    protocol_dir = basedir+'/protocols/%s' %args.database
    database = xbob.db.verification.filelist.Database(protocol_dir)
    train_files = database.objects(groups='world')
    train_files_F.append([k for k in train_files if k.client_id == 'female'])
    train_files_M.append([k for k in train_files if k.client_id == 'male'])
    eval_files = database.objects(groups='dev', purposes='probe')
    eval_files_F.append([k for k in eval_files if k.client_id == 'female'])
    eval_files_M.append([k for k in eval_files if k.client_id == 'male'])
    extension = '.png'
  elif (args.database == 'lfw'):
    import xbob.db.verification.filelist
    for fold in folds:
      protocol_dir = basedir+'/protocols/%s/fold%d' %(args.database,fold)
      database = xbob.db.verification.filelist.Database(protocol_dir)
      train_files = database.objects(groups='world')
      eval_files = database.objects(groups='dev', purposes='probe')
      train_files_F.append([k for k in train_files if k.client_id == 'female'])
      eval_files_F.append([k for k in eval_files if k.client_id == 'female'])
      if not args.genderbalance:
        train_files_M.append([k for k in train_files if k.client_id == 'male'])
        eval_files_M.append([k for k in eval_files if k.client_id == 'male'])
      else:
        train_files_M.append([k for k in train_files if k.client_id == 'male'][0:len(train_files_F[fold])])
        eval_files_M.append([k for k in eval_files if k.client_id == 'male'][0:len(train_files_F[fold])])
    extension = '.jpg'
  elif (args.database == 'morph'):
    import xbob.db.verification.filelist
    for fold in folds:
      protocol_dir = basedir+'/protocols/%s/fold%d' %(args.database,fold)
      database = xbob.db.verification.filelist.Database(protocol_dir)
      train_files = database.objects(groups='world')
      eval_files = database.objects(groups='dev', purposes='probe')
      train_files_F.append([k for k in train_files if k.client_id == 'female'])
      eval_files_F.append([k for k in eval_files if k.client_id == 'female'])
      if not args.genderbalance:
        train_files_M.append([k for k in train_files if k.client_id == 'male'])
        eval_files_M.append([k for k in eval_files if k.client_id == 'male'])
      else:
        train_files_M.append([k for k in train_files if k.client_id == 'male'][0:len(train_files_F[0])])
        eval_files_M.append([k for k in eval_files if k.client_id == 'male'][0:len(train_files_F[0])])
    extension = '.JPG'
  
  for fold in range(0,len(train_files_F)):
    train_files_F[fold].sort()
    train_files_M[fold].sort()
    eval_files_F[fold].sort()
    eval_files_M[fold].sort()
    
    if args.training_fold is None:
      if len(train_files_F)==1: training_fold = folds[0]
      else: training_fold = fold
    else: training_fold = args.training_fold
    
    need_train = True  
    if args.classifier == 'lda' or args.classifier == 'svm':
      pca_file_name = '%s/pca_machine_%s_%d%s.hdf5' %(args.machinedir,args.training_database,training_fold,machine_suffix)
      lda_svm_file_name = '%s/%s_machine_%s_%d%s.hdf5' %(args.machinedir,args.classifier,args.training_database,training_fold,machine_suffix)
      thres_file_name = '%s/thres_%s_%s_%d%s.hdf5' %(args.machinedir,args.classifier,args.training_database,training_fold,machine_suffix)
      if args.loadmachine and os.path.exists(pca_file_name) and os.path.exists(lda_svm_file_name) and os.path.exists(thres_file_name):
        need_train = False
    elif args.classifier == 'chi2':
      chi2_file_name = '%s/chi2_models_%s_%d%s.hdf5' %(args.machinedir,args.training_database,training_fold,machine_suffix)
      thres_file_name = '%s/thres_%s_%s_%d%s.hdf5' %(args.machinedir,args.classifier,args.training_database,training_fold,machine_suffix)
      if args.loadmachine and os.path.exists(chi2_file_name) and os.path.exists(thres_file_name):
        need_train = False
    
    if need_train:
      print ".. Loading training files for fold %d.."%fold
      train_F = create_feature_set(database,args.database,args.inputdir,basedir,extension,ftdir,train_files_F[fold],args.ratio,args.iod,args.width,args.lbp,args.numblock,args.lbptype,args.lbpscale,args.force,args.nooutput)
      train_M = create_feature_set(database,args.database,args.inputdir,basedir,extension,ftdir,train_files_M[fold],args.ratio,args.iod,args.width,args.lbp,args.numblock,args.lbptype,args.lbpscale,args.force,args.nooutput)   
    print ".. Loading evaluation files for fold %d.."%fold
    eval_F = create_feature_set(database,args.database,args.inputdir,basedir,extension,ftdir,eval_files_F[fold],args.ratio,args.iod,args.width,args.lbp,args.numblock,args.lbptype,args.lbpscale,args.force,args.nooutput)
    eval_M = create_feature_set(database,args.database,args.inputdir,basedir,extension,ftdir,eval_files_M[fold],args.ratio,args.iod,args.width,args.lbp,args.numblock,args.lbptype,args.lbpscale,args.force,args.nooutput)   

    if args.classifier == 'lda' or args.classifier == 'svm':
      if args.loadmachine and os.path.exists(pca_file_name):
        print ".. Loading PCA machine: %s.." %pca_file_name
        pca_file = bob.io.HDF5File(pca_file_name)
        pca_machine = bob.machine.LinearMachine(pca_file)
        del pca_file
      else:
        print ".. Training PCA machine (keeping 99% of the energy).."
        train_all = numpy.append(train_M, train_F, axis=0)
        T = bob.trainer.PCATrainer()
        [pca_machine, eigvalues] = T.train(train_all)
        cumEnergy = numpy.array([sum(eigvalues[0:eigvalues.size-i]) / sum(eigvalues) for i in range(0, eigvalues.size+1)])
        numeigvalues = len(cumEnergy)-sum(cumEnergy>0.99)
        pca_machine.resize(pca_machine.shape[0], int(numeigvalues))
        if args.savemachine:
          pca_file = bob.io.HDF5File(pca_file_name, 'w')
          pca_machine.save(pca_file)
          del pca_file
      if need_train:
        print ".. Applying PCA projection for training feature set.."
        train_F_pca = numpy.vstack([pca_machine(d) for d in train_F])
        train_M_pca = numpy.vstack([pca_machine(d) for d in train_M])
      print ".. Applying PCA projection for evaluation feature set.."
      eval_F_pca = numpy.vstack([pca_machine(d) for d in eval_F])
      eval_M_pca = numpy.vstack([pca_machine(d) for d in eval_M])
    
    if args.classifier == 'lda':
      if args.loadmachine and os.path.exists(lda_svm_file_name):
        print ".. Loading LDA machine: %s.." %lda_svm_file_name
        lda_file = bob.io.HDF5File(lda_svm_file_name)
        lda_machine = bob.machine.LinearMachine(lda_file)
        del lda_file
      else:                
        print ".. Training LDA machine.."
        T = bob.trainer.FisherLDATrainer()
        [lda_machine, eigvalues] = T.train((train_M_pca, train_F_pca)) 
        lda_machine.shape = (lda_machine.shape[0], 1) #only use first component
        if args.savemachine:
          lda_file = bob.io.HDF5File(lda_svm_file_name, 'w')
          lda_machine.save(lda_file)
          del lda_file
      if need_train:
        print ".. Calculating LDA scores for training set.."
        train_F_scores = numpy.vstack([lda_machine(d) for d in train_F_pca])[:,0]
        train_M_scores = numpy.vstack([lda_machine(d) for d in train_M_pca])[:,0]
      print ".. Calculating LDA scores for evaluation set.."
      eval_F_scores = numpy.vstack([lda_machine(d) for d in eval_F_pca])[:,0]
      eval_M_scores = numpy.vstack([lda_machine(d) for d in eval_M_pca])[:,0]
    
    elif args.classifier == 'svm':
      if args.loadmachine and os.path.exists(lda_svm_file_name):
        print ".. Loading SVM machine: %s.." %lda_svm_file_name
        svm_file = bob.io.HDF5File(lda_svm_file_name)
        svm_machine = bob.machine.SupportVector(svm_file)
        del svm_file
      else:
        print ".. Training SVM machine.."
        svm_trainer = bob.trainer.SVMTrainer(kernel_type = bob.machine._machine.svm_kernel_type.RBF, gamma=1e-5)
        svm_trainer.probability = True
        svm_machine = svm_trainer.train([train_M_pca, train_F_pca])
        if args.savemachine:
          svm_file = bob.io.HDF5File(lda_svm_file_name, 'w')
          svm_machine.save(svm_file)
          del svm_file
      if need_train:
        print ".. Calculating SVM scores for training set.."
        train_F_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in train_F_pca])
        train_M_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in train_M_pca])
      print ".. Calculating SVM scores for evaluation set.."
      eval_F_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in eval_F_pca])
      eval_M_scores = numpy.array([svm_machine.predict_class_and_scores(x)[1][0] for x in eval_M_pca])
    
    elif args.classifier == 'chi2':
      if args.loadmachine and os.path.exists(chi2_file_name):
        print ".. Loading Chi2 models: %s.." %chi2_file_name
        chi2_file = bob.io.HDF5File(chi2_file_name)
        model_F = chi2_file.read('model_F')
        model_M = chi2_file.read('model_M')
        del chi2_file
      else:
        print ".. Computing female and male models.. (average histogram).."
        model_F = numpy.mean(train_F,axis=0)
        model_M = numpy.mean(train_M,axis=0)
        if args.savemachine:
          chi2_file = bob.io.HDF5File(chi2_file_name, 'w')
          chi2_file.set('model_F', model_F)
          chi2_file.set('model_M', model_M)
          del chi2_file
      if need_train:
        print ".. Calculating Chi-2 scores for training set.."
        train_F_scores = numpy.array([bob.math.chi_square(x,model_M) - bob.math.chi_square(x,model_F) for x in train_F])
        train_M_scores = numpy.array([bob.math.chi_square(x,model_M) - bob.math.chi_square(x,model_F) for x in train_M])
      print ".. Calculating Chi-2 scores for evaluation set.."
      eval_F_scores = numpy.array([bob.math.chi_square(x,model_M) - bob.math.chi_square(x,model_F) for x in eval_F])
      eval_M_scores = numpy.array([bob.math.chi_square(x,model_M) - bob.math.chi_square(x,model_F) for x in eval_M])
    
    if (eval_M_scores.mean() > eval_F_scores.mean()):
      eval_F_scores = -1*eval_F_scores
      eval_M_scores = -1*eval_M_scores
    
    if need_train:
      if (train_M_scores.mean() > train_F_scores.mean()):
        train_F_scores = -1*train_F_scores
        train_M_scores = -1*train_M_scores    
      if (args.database == 'banca' or args.database == 'mobio'):
        thres_F_scores = eval_F_scores
        thres_M_scores = eval_M_scores
      else:
        thres_F_scores = train_F_scores
        thres_M_scores = train_M_scores
    
    if args.loadmachine and os.path.exists(thres_file_name):
      print ".. Loading thresholds: %s.." %thres_file_name
      thres_file = bob.io.HDF5File(thres_file_name)
      thres_1 = thres_file.read('thres_1')
      thres_2 = thres_file.read('thres_2')
      thres_3 = thres_file.read('thres_3')
      del thres_file
    else:
      print ".. Calculating thresholds.."
      thres_rate_max = 0
      minScore = numpy.floor(min([thres_M_scores.min(),thres_F_scores.min()]))
      maxScore = numpy.ceil(max([thres_M_scores.max(),thres_F_scores.max()]))
      step = (maxScore-minScore)/100000
      for thres in numpy.arange(minScore,maxScore,step):
        thres_far, thres_frr = bob.measure.farfrr(thres_M_scores, thres_F_scores, thres)
        thres_rate = 100-((thres_far*len(thres_M_scores))+(thres_frr*len(thres_F_scores)))/(len(thres_M_scores)+len(thres_F_scores))*100
        if thres_rate>thres_rate_max:
          thres_rate_max = thres_rate
          thres_1 = thres
      thres_2 = bob.measure.eer_threshold(thres_M_scores, thres_F_scores)
      thres_3 = bob.measure.min_hter_threshold(thres_M_scores, thres_F_scores)
      if args.savemachine:
        thres_file = bob.io.HDF5File(thres_file_name, 'w')
        thres_file.set('thres_1', thres_1)
        thres_file.set('thres_2', thres_2)
        thres_file.set('thres_3', thres_3)
        del thres_file
    thres_4 = 0
    
    eval_far_1, eval_frr_1 = bob.measure.farfrr(eval_M_scores, eval_F_scores, thres_1)
    eval_rate_1 = 100-((eval_far_1*len(eval_M_scores))+(eval_frr_1*len(eval_F_scores)))/(len(eval_M_scores)+len(eval_F_scores))*100
    eval_far_2, eval_frr_2 = bob.measure.farfrr(eval_M_scores, eval_F_scores, thres_2)
    eval_rate_2 = 100-((eval_far_2*len(eval_M_scores))+(eval_frr_2*len(eval_F_scores)))/(len(eval_M_scores)+len(eval_F_scores))*100
    eval_far_3, eval_frr_3 = bob.measure.farfrr(eval_M_scores, eval_F_scores, thres_3)
    eval_rate_3 = 100-((eval_far_3*len(eval_M_scores))+(eval_frr_3*len(eval_F_scores)))/(len(eval_M_scores)+len(eval_F_scores))*100
    eval_far_4, eval_frr_4 = bob.measure.farfrr(eval_M_scores, eval_F_scores, thres_4)
    eval_rate_4 = 100-((eval_far_4*len(eval_M_scores))+(eval_frr_4*len(eval_F_scores)))/(len(eval_M_scores)+len(eval_F_scores))*100
    
    print 100-eval_far_1*100.0, 100-eval_frr_1*100.0, eval_rate_1
    print 100-eval_far_2*100.0, 100-eval_frr_2*100.0, eval_rate_2
    print 100-eval_far_3*100.0, 100-eval_frr_3*100.0, eval_rate_3
    print 100-eval_far_4*100.0, 100-eval_frr_4*100.0, eval_rate_4
    
    #Uncomment to view the score distribution
    '''minscore = min(numpy.concatenate((eval_F_scores,eval_M_scores)))
    maxscore = max(numpy.concatenate((eval_F_scores,eval_M_scores)))
    scorebins = numpy.linspace(minscore,maxscore,30)
    fig = matplotlib.pyplot.figure()
    title =  'Score Distribution'
    matplotlib.pyplot.title(title, fontsize=15)
    matplotlib.pyplot.xlabel('Score bins', fontsize=20)
    matplotlib.pyplot.ylabel('Number of Attempts', fontsize=20)
    p1 = matplotlib.pyplot.hist(eval_F_scores, bins=scorebins, normed=True, alpha=0.4, color='g', label='Male Scores')
    p2 = matplotlib.pyplot.hist(eval_M_scores, bins=scorebins, normed=True, alpha=0.4, color='r', label='Female Scores')
    matplotlib.pyplot.legend(prop={'size':17})
    matplotlib.pyplot.grid()
    matplotlib.pyplot.show()'''
   
  return 0

if __name__ == "__main__":
  main()
