#Grid search for algorithm parameters and find the optimal configuration on MOBIO and BANCA databases
bin/test_all.py -db mobio -i /databases/mobio/IMAGES_PNG
bin/test_all.py -db banca -i /databases/banca/english/images/images
bin/rank_all.py

# Run experiments on Feret, LFW and Morph databses and save PCA and SVM machines (with  and without balanced training sets for LFW and Morph)
./bin/estimateGender.py -db feret -i ./databases/feret                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -sm
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -sm
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -sm -gb
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -sm
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -sm -gb

# Run cross-database experiments
# Experiments on Feret using training partitions of LFW
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 0
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 1
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 2
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 3
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 4
# Experiments on Feret using training partitions of LFW (with balanced training set)
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 0 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 1 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 2 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 3 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 4 -gb
# Experiments on Feret using training partitions of Morph
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 0
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 1
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 2
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 3
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 4
# Experiments on Feret using training partitions of Morph (with balanced training set)
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 0 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 1 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 2 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 3 -gb
./bin/estimateGender.py -db feret -i ./databases/feret      -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 4 -gb

# Experiments on LFW using training partition of Feret
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td feret -tf 0
# Experiments on LFW using training partitions of Morph
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 0
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 1
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 2
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 3
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 4
# Experiments on LFW using training partitions of Morph (with balanced training set)
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 0 -gb
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 1 -gb
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 2 -gb
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 3 -gb
./bin/estimateGender.py -db lfw   -i <lfw directory>/all_images_aligned_with_funneling -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td morph -tf 4 -gb

# Experiments on Morph using training partition of Feret
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td feret -tf 0
# Experiments on Morph using training partitions of LFW
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 0
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 1
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 2
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 3
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 4
# Experiments on Morph using training partitions of LFW (with balanced training set)
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 0 -gb
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 1 -gb
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 2 -gb
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 3 -gb
./bin/estimateGender.py -db morph -i <morph directory>                                 -d 30 -w 105 -r 0.6666666666666666 -l -nb 12 -lt mod -ls 8 2 -c svm -f -no -lm -td lfw   -tf 4 -gb
