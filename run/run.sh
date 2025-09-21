# img path should be relative!
python ace_zero.py "../test/globe/1/img/*.jpg" "/home/sebastian/repos/master_thesis/test/globe/1/res_ace0/" --export_point_cloud True --dense_point_cloud True

# GALAXY S23
python ace_zero.py "../test/globe/1/img/*.jpg" "/home/sebastian/repos/master_thesis/test/globe/1/res_ace0/" --export_point_cloud True --dense_point_cloud True --use_external_focal_length 1990.5

# DJI TELLO
python ace_zero.py "../test/doll/img/*.jpg" "/home/sebastian/repos/master_thesis/test/doll/1/res_ace0/" --export_point_cloud True --dense_point_cloud True --try_seeds 8 --seed_iterations 20000 --ransac_iterations 64 --ransac_threshold 5 --use_external_focal_length 620.0
python ace_zero.py "../test/doll/img/*.png" "/home/sebastian/repos/master_thesis/test/doll/1/res_ace0_w_calib/" --export_point_cloud True --dense_point_cloud True --try_seeds 8 --seed_iterations 20000 --ransac_iterations 64 --ransac_threshold 5 --use_external_focal_length 921.15 --refine_calibration False


python ace_zero.py "../test/doll/img/*.jpg" "/home/sebastian/repos/master_thesis/test/06_08/small/res_ace0/" --export_point_cloud True --try_seeds 8 --seed_iterations 20000 --ransac_iterations 64 --ransac_threshold 5

python ace_zero.py "../test/06_08/small/images/*.png" "/home/sebastian/repos/master_thesis/test/06_08/small/res_ace0/" --export_point_cloud True --use_external_focal_length 921.15

#python3 ace_zero.py \
#    "$scene_dir/images/*.jpeg" \
#    "$scene_output_path" \
#    --try_seeds 8 \
#    --seed_parallel_workers -1 \
#    --seed_iterations 20000 \
#    --ransac_iterations 64 \
#    --ransac_threshold 5 \
#    --export_point_cloud True