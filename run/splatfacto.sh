# Generate input files for splatfacto from ace0 results
# --images_glob_pattern must be relative to the current working directory!! => Must be same as in "poses_final.txt"!!!!
python -m benchmarks.benchmark_poses --pose_file /home/sebastian/repos/master_thesis/test/globe/1/res_ace0/poses_final.txt --output_dir /home/sebastian/repos/master_thesis/test/globe/1/nerf/ --images_glob_pattern '../test/globe/1/img/*.jpg' --method splatfacto --no_run_nerfstudio
python -m benchmarks.benchmark_poses --pose_file /home/sebastian/repos/master_thesis/test/globe/1/res_ace0/poses_final.txt --output_dir /home/sebastian/repos/master_thesis/test/globe/1/nerf/ --images_glob_pattern '../test/globe/1/img/*.jpg' --method splatfacto --no_run_nerfstudio --max_resolution 720

# Generate input files from COLMAP
ns-process-data images --data ./img --output-dir ./out --skip-colmap --colmap-model-path ./sparse


# train gaussian splatting model on input
ns-train splatfacto --data /home/sebastian/repos/master_thesis/test/doll/colmap/nerf/nerf_data \
  --pipeline.model.camera-optimizer.mode off \
  --pipeline.datamanager.images-on-gpu True \
  --method-name splatfacto \
  --experiment_name nerf_for_eval \
  --output-dir /home/sebastian/repos/master_thesis/test/doll/colmap/nerf/nerf_data \
  --timestamp run \
  nerfstudio-data \
  --downscale-factor 4

ns-train splatfacto-big --data /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data \
  --pipeline.model.camera-optimizer.mode off \
  --pipeline.datamanager.images-on-gpu True \
  --method-name splatfacto-big \
  --experiment_name nerf_big_for_eval \
  --output-dir /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data \
  --timestamp run \
  nerfstudio-data \
  --downscale-factor 4


# EXPORT SPLATS
ns-export gaussian-splat --load-config /home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data/nerf_big_for_eval/splatfacto/run/config.yml --output-dir ../test/trophy/wo_cal/nerf/