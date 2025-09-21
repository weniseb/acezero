# Generate input files for nerfacto from ace0 resutls
python -m benchmarks.benchmark_poses --pose_file /home/sebastian/repos/master_thesis/test/trophy/nerf/res_ace0/poses_final.txt --output_dir /home/sebastian/repos/master_thesis/test/trophy/nerf/nerf/ --images_glob_pattern '../test/trophy/nerf/img/*.jpg' --no_run_nerfstudio
python -m benchmarks.benchmark_poses --pose_file /home/sebastian/repos/master_thesis/test/trophy/nerf/res_ace0/poses_final.txt --output_dir /home/sebastian/repos/master_thesis/test/trophy/nerf/nerf/ --images_glob_pattern '../test/trophy/nerf/img/*.jpg' --no_run_nerfstudio --max_resolution 720

# Train nerf model on input data
ns-train nerfacto-big --data /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data \
  --pipeline.model.camera-optimizer.mode off \
  --pipeline.datamanager.images-on-gpu False \
  --method-name nerfacto-big \
  --experiment_name nerf_big_for_eval \
  --output-dir /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data \
  --timestamp run \
  nerfstudio-data \
#  --downscale-factor 4


## RESUME TRAINING
ns-train nerfacto --data /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data \
  --pipeline.datamanager.images-on-gpu True \
  --method-name nerfacto \
  --experiment_name nerf_for_eval_pose_optim_resume \
  --output-dir /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data \
  --timestamp run \
  --load-dir=/home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data/nerf_for_eval_pose_optim/nerfacto/run/nerfstudio_models \
  --max-num-iterations 60000 \
  nerfstudio-data
