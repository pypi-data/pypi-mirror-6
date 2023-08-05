import os
import argparse
import bob
import numpy
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def main():
  IOD = [10, 20, 30]
  W_IOD_RATIO = [1.5, 2, 2.5, 3, 3.5]
  H_W_RATIO = [1/2.0, 1/1.5, 1, 1.5, 2]
      
  LBP_SCALE = ['8 1', '8 2', '16 2']
  NUM_BLOCK = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
  LBP_TYPE = ['reg', 'mod']

  databases = ['feret']
  ALL = numpy.zeros((2,4950,9))
  ranks_acc = numpy.empty((2,4950), int)
  ranks_hter = numpy.empty((2,4950), int)
  ranks_eer = numpy.empty((2,4950), int)

  for d in range(0,len(databases)):
    database = databases[d]
    for conf in range(0,4950):  
      iod = conf/(5*5*3*11*2)
      w_iod_ratio = conf%(5*5*3*11*2)/(5*3*11*2)
      h_w_ratio = conf%(5*5*3*11*2)%(5*3*11*2)/(3*11*2)
      lbp_scale = conf%(5*5*3*11*2)%(5*3*11*2)%(3*11*2)/(11*2)
      num_block = conf%(5*5*3*11*2)%(5*3*11*2)%(3*11*2)%(11*2)/(2)
      lbp_type = conf%(5*5*3*11*2)%(5*3*11*2)%(3*11*2)%(11*2)%(2)
      w = int(iod*w_iod_ratio)    
      file_name = os.path.join('output','test_all',database,str(IOD[iod])+'_'+str(W_IOD_RATIO[w_iod_ratio])+'_'+str(H_W_RATIO[h_w_ratio])+'_'+LBP_SCALE[lbp_scale]+'_'+str(NUM_BLOCK[num_block])+'_'+LBP_TYPE[lbp_type]+'.hdf5')
      if os.path.exists(file_name):
        file_hdf5 = bob.io.HDF5File(file_name)
        acc = file_hdf5.read('ACC')
        hter = file_hdf5.read('HTER')
        eer = file_hdf5.read('EER')
        ALL[d,conf,0] = iod
        ALL[d,conf,1] = w_iod_ratio
        ALL[d,conf,2] = h_w_ratio
        ALL[d,conf,3] = lbp_scale
        ALL[d,conf,4] = num_block
        ALL[d,conf,5] = lbp_type
        ALL[d,conf,6] = acc[2]
        ALL[d,conf,7] = hter[2]
        ALL[d,conf,8] = eer[2]
    ranks_acc[d,ALL[d,:,6].argsort()] = numpy.arange(4950)
    ranks_hter[d,ALL[d,:,7].argsort()] = numpy.arange(4950)
    ranks_eer[d,ALL[d,:,8].argsort()] = numpy.arange(4950)

  best_conf = sum(ranks_acc).argmax()
  print 'Best configuration for ACC is: IOD:%d W_IOD:%2.1f H_W:%2.1f LS:%s NB:%d LT:%s with ACC:%f HTER:%f EER:%f for BANCA and ACC:%f HTER:%f EER:%f for MOBIO' %(IOD[int(ALL[0,best_conf,0])], W_IOD_RATIO[int(ALL[0,best_conf,1])], H_W_RATIO[int(ALL[0,best_conf,2])],LBP_SCALE[int(ALL[0,best_conf,3])],NUM_BLOCK[int(ALL[0,best_conf,4])],LBP_TYPE[int(ALL[0,best_conf,5])],ALL[0,best_conf,6],ALL[0,best_conf,7],ALL[0,best_conf,8],ALL[1,best_conf,6],ALL[1,best_conf,7],ALL[1,best_conf,8])
  best_conf = sum(ranks_hter).argmax()
  print 'Best configuration for HTER is: IOD:%d W_IOD:%2.1f H_W:%2.1f LS:%s NB:%d LT:%s with ACC:%f HTER:%f EER:%f for BANCA and ACC:%f HTER:%f EER:%f for MOBIO' %(IOD[int(ALL[0,best_conf,0])], W_IOD_RATIO[int(ALL[0,best_conf,1])], H_W_RATIO[int(ALL[0,best_conf,2])],LBP_SCALE[int(ALL[0,best_conf,3])],NUM_BLOCK[int(ALL[0,best_conf,4])],LBP_TYPE[int(ALL[0,best_conf,5])],ALL[0,best_conf,6],ALL[0,best_conf,7],ALL[0,best_conf,8],ALL[1,best_conf,6],ALL[1,best_conf,7],ALL[1,best_conf,8])
  best_conf = sum(ranks_eer).argmax()
  print 'Best configuration for EER is: IOD:%d W_IOD:%2.1f H_W:%2.1f LS:%s NB:%d LT:%s with ACC:%f HTER:%f EER:%f for BANCA and ACC:%f HTER:%f EER:%f for MOBIO' %(IOD[int(ALL[0,best_conf,0])], W_IOD_RATIO[int(ALL[0,best_conf,1])], H_W_RATIO[int(ALL[0,best_conf,2])],LBP_SCALE[int(ALL[0,best_conf,3])],NUM_BLOCK[int(ALL[0,best_conf,4])],LBP_TYPE[int(ALL[0,best_conf,5])],ALL[0,best_conf,6],ALL[0,best_conf,7],ALL[0,best_conf,8],ALL[1,best_conf,6],ALL[1,best_conf,7],ALL[1,best_conf,8])
  
  
  print '\nFirst 10 configurations with respect to ACC:'
  best_10 = sum(ranks_acc).argsort()[-10:]
  for i in range(0,10):
    print 'RANK:%d IOD:%d W_IOD:%2.1f H_W:%2.1f LS:%s NB:%d LT:%s with ACC:%f HTER:%f EER:%f for BANCA and ACC:%f HTER:%f EER:%f for MOBIO' %(4949*len(databases)-sum(ranks_acc)[best_10[i]],IOD[int(ALL[0,best_10[i],0])], W_IOD_RATIO[int(ALL[0,best_10[i],1])], H_W_RATIO[int(ALL[0,best_10[i],2])],LBP_SCALE[int(ALL[0,best_10[i],3])],NUM_BLOCK[int(ALL[0,best_10[i],4])],LBP_TYPE[int(ALL[0,best_10[i],5])],ALL[0,best_10[i],6],ALL[0,best_10[i],7],ALL[0,best_10[i],8],ALL[1,best_10[i],6],ALL[1,best_10[i],7],ALL[1,best_10[i],8])
  
  return 0

if __name__ == "__main__":
  main()
    
