#!/usr/bin/env python3
import subprocess
import time
import json
import os
import shlex
from datetime import datetime
from typing import List


class NerfTrainingLogger:
    def __init__(self):
        self.conda_env = "nerfstudio"
        self.conda_path = "/home/sebastian/miniconda3/bin/conda"

    def check_conda_environment(self):
        """Check if we're in the correct conda environment"""
        try:
            current_env = os.environ.get('CONDA_DEFAULT_ENV', '')
            if current_env == self.conda_env:
                print(f"Already in {self.conda_env} environment")
                return True
            else:
                print(f"Current environment: {current_env}, need to switch to {self.conda_env}")
                return False
        except Exception as e:
            print(f"Error checking conda environment: {e}")
            return False

    def get_conda_command_prefix(self):
        """Get the command prefix to run commands in conda environment"""
        if self.check_conda_environment():
            return []
        else:
            print("PANIC! You are not in the nerfstudio conda environment!")
            exit(-1)
            return [self.conda_path, 'run', '-n', self.conda_env]
            # return ["source /home/sebastian/miniconda3/etc/profile.d/conda.sh;", "conda activate nerfstudio;"]

    def export_gaussian_splat(self, config_path: str, output_dir: str) -> bool:
        """Export gaussian splat from trained splatfacto model"""

        # Validate config file exists
        if not os.path.exists(config_path):
            print(f"Config file not found: {config_path}")
            return False

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Build ns-export command
        export_cmd = [
            "ns-export", "gaussian-splat",
            "--load-config", config_path,
            "--output-dir", output_dir
        ]

        # Get conda command prefix if needed
        conda_prefix = self.get_conda_command_prefix()
        if conda_prefix:
            cmd = conda_prefix + export_cmd
        else:
            cmd = export_cmd

        # Create log file for export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_dir, f"gaussian_export_{timestamp}.log")

        print(f"Starting gaussian splat export...")
        print(f"Config: {config_path}")
        print(f"Output directory: {output_dir}")
        print(f"Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            with open(log_file, 'w') as f:
                f.write(f"=== GAUSSIAN SPLAT EXPORT START ===\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Config: {config_path}\n")
                f.write(f"Output Directory: {output_dir}\n")
                f.write(f"Conda Environment: {self.conda_env}\n")
                f.write(f"{'=' * 50}\n\n")

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable="/bin/bash", shell=True,
                                           universal_newlines=True, bufsize=1)

                for line in process.stdout:
                    print(line, end='')
                    f.write(line)
                    f.flush()

            process.wait()
            end_time = time.time()
            duration = end_time - start_time

            with open(log_file, 'a') as f:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"Duration: {duration:.2f}s\n")
                f.write(f"Return code: {process.returncode}\n")

            print(f"\nGaussian splat export completed in {duration:.2f}s")
            print(f"Export logs saved to: {log_file}")

            if process.returncode == 0:
                print(f"Gaussian splat successfully exported to: {output_dir}")
                # Look for common output files
                ply_files = [f for f in os.listdir(output_dir) if f.endswith('.ply')]
                if ply_files:
                    print(f"Generated PLY files: {ply_files}")

            return process.returncode == 0

        except Exception as e:
            print(f"Gaussian splat export failed: {e}")
            with open(log_file, 'a') as f:
                f.write(f"\nEXCEPTION: {e}\n")
            return False

    def export_pointcloud(self, config_path: str, output_dir: str, num_points: int = 1000000,
                          remove_outliers: bool = True, normal_method: str = "open3d",
                          save_world_frame: bool = False) -> bool:
        """Export pointcloud from trained nerfacto model"""

        # Validate config file exists
        if not os.path.exists(config_path):
            print(f"Config file not found: {config_path}")
            return False

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Build ns-export command
        export_cmd = [
            "ns-export", "pointcloud",
            "--load-config", config_path,
            "--output-dir", output_dir,
            "--num-points", str(num_points),
            "--remove-outliers", str(remove_outliers),
            "--normal-method", normal_method,
            "--save-world-frame", str(save_world_frame)
        ]

        # Get conda command prefix if needed
        conda_prefix = self.get_conda_command_prefix()
        if conda_prefix:
            cmd = conda_prefix + export_cmd
        else:
            cmd = export_cmd

        # Create log file for export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_dir, f"pointcloud_export_{timestamp}.log")

        print(f"Starting pointcloud export...")
        print(f"Config: {config_path}")
        print(f"Output directory: {output_dir}")
        print(f"Number of points: {num_points}")
        print(f"Remove outliers: {remove_outliers}")
        print(f"Normal method: {normal_method}")
        print(f"Save world frame: {save_world_frame}")
        print(f"Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            with open(log_file, 'w') as f:
                f.write(f"=== POINTCLOUD EXPORT START ===\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Config: {config_path}\n")
                f.write(f"Output Directory: {output_dir}\n")
                f.write(f"Number of points: {num_points}\n")
                f.write(f"Remove outliers: {remove_outliers}\n")
                f.write(f"Normal method: {normal_method}\n")
                f.write(f"Save world frame: {save_world_frame}\n")
                f.write(f"Conda Environment: {self.conda_env}\n")
                f.write(f"{'=' * 50}\n\n")

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, bufsize=1)

                for line in process.stdout:
                    print(line, end='')
                    f.write(line)
                    f.flush()

            process.wait()
            end_time = time.time()
            duration = end_time - start_time

            with open(log_file, 'a') as f:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"Duration: {duration:.2f}s\n")
                f.write(f"Return code: {process.returncode}\n")

            print(f"\nPointcloud export completed in {duration:.2f}s")
            print(f"Export logs saved to: {log_file}")

            if process.returncode == 0:
                print(f"Pointcloud successfully exported to: {output_dir}")
                # Look for common output files
                ply_files = [f for f in os.listdir(output_dir) if f.endswith('.ply')]
                if ply_files:
                    print(f"Generated PLY files: {ply_files}")

            return process.returncode == 0

        except Exception as e:
            print(f"Pointcloud export failed: {e}")
            with open(log_file, 'a') as f:
                f.write(f"\nEXCEPTION: {e}\n")
            return False

    def train_simple(self, method: str, base_dir: str, experiment_name: str, config: List[str],
                     dataparser: str = "nerfstudio-data", export_geometry: bool = True, quit_viewer: bool = False):
        """Simple training using conda run with optional gaussian splat export"""

        # Construct data path
        data_path = os.path.join(base_dir, "nerf/nerf_data")

        # Separate dataparser-specific parameters from general config
        dataparser_params = []
        general_config = []

        for param in config:
            if param.startswith("--downscale-factor"):
                dataparser_params.extend(param.split())
            else:
                general_config.extend(param.split())

        # Build ns-train command
        ns_cmd = [
            "ns-train", method,
            "--data", data_path,
            "--method-name", method,
            "--experiment_name", experiment_name,
            "--output-dir", data_path,
            "--viewer.quit-on-train-completion", str(quit_viewer),
            "--logging.steps-per-log", "100",
            "--logging.local-writer.max-log-size", "0"
        ]

        # Add general config parameters
        ns_cmd.extend(general_config)

        # Add dataparser
        ns_cmd.append(dataparser)

        # Add dataparser-specific parameters after dataparser
        ns_cmd.extend(dataparser_params)

        # Create experiment log directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_log_dir = os.path.join(data_path, experiment_name, method)
        os.makedirs(experiment_log_dir, exist_ok=True)

        # Create log files
        log_file = os.path.join(experiment_log_dir, f"training_{timestamp}.log")
        params_file = os.path.join(experiment_log_dir, f"params_{timestamp}.json")

        # Use conda run method
        training_success = self._try_conda_run(ns_cmd, log_file, params_file, method, base_dir,
                                               experiment_name, config, timestamp)

        # If training succeeded and export is enabled, export appropriate geometry
        if training_success and export_geometry:
            print("\n" + "=" * 60)
            print("Training completed successfully! Starting geometry export...")
            print("=" * 60)

            # Look for the config.yml file in the experiment directory
            config_path = os.path.join(experiment_log_dir, "run" ,"config.yml")

            if os.path.exists(config_path):
                if method == "splatfacto":
                    print("📊 Exporting Gaussian Splat for splatfacto model...")
                    export_success = self.export_gaussian_splat(config_path, experiment_log_dir)
                    if export_success:
                        print("✅ Gaussian splat export completed successfully!")
                    else:
                        print("❌ Gaussian splat export failed. Check the export logs.")

                elif method == "nerfacto":
                    print("🔵 Exporting Pointcloud for nerfacto model...")
                    export_success = self.export_pointcloud(
                        config_path,
                        experiment_log_dir,
                        num_points=pointcloud_params["num_points"],
                        remove_outliers=pointcloud_params["remove_outliers"],
                        normal_method=pointcloud_params["normal_method"],
                        save_world_frame=pointcloud_params["save_world_frame"]
                    )
                    if export_success:
                        print("✅ Pointcloud export completed successfully!")
                    else:
                        print("❌ Pointcloud export failed. Check the export logs.")

                else:
                    print(f"ℹ️  No automatic export configured for method: {method}")
                    print("   Supported methods for automatic export: splatfacto, nerfacto")

            else:
                print(f"❌ Config file not found at: {config_path}")
                print("Cannot proceed with geometry export.")

        return training_success

    def _try_conda_run(self, ns_cmd: List[str], log_file: str, params_file: str,
                       method: str, base_dir: str, experiment_name: str,
                       config: List[str], timestamp: str) -> bool:
        """Try using conda run command"""
        conda_prefix = self.get_conda_command_prefix()

        if not conda_prefix:  # Already in correct environment
            cmd = ns_cmd
        else:
            # Use conda run to execute in nerfstudio environment
            cmd = conda_prefix + ns_cmd

        return self._execute_training(cmd, log_file, params_file, method, base_dir,
                                      experiment_name, config, timestamp)

    def _execute_training(self, cmd: List[str], log_file: str, params_file: str,
                          method: str, base_dir: str, experiment_name: str,
                          config: List[str], timestamp: str) -> bool:
        """Execute the training command and handle logging"""

        # Log parameters
        params_data = {
            "timestamp": timestamp,
            "method": method,
            "base_dir": base_dir,
            "experiment_name": experiment_name,
            "config": config,
            "conda_environment": self.conda_env,
            "command": " ".join(cmd)
        }

        with open(params_file, 'w') as f:
            json.dump(params_data, f, indent=2)

        print(f"Starting training: {method}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Logs will be saved to: {os.path.dirname(log_file)}")

        start_time = time.time()

        try:
            with open(log_file, 'w') as f:
                f.write(f"=== TRAINING START ===\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Conda Environment: {self.conda_env}\n")
                f.write(f"{'=' * 50}\n\n")

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, bufsize=1)

                for line in process.stdout:
                    print(line, end='')
                    f.write(line)
                    f.flush()

            process.wait()
            end_time = time.time()
            duration = end_time - start_time

            with open(log_file, 'a') as f:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"Duration: {duration:.2f}s ({duration / 60:.2f} minutes)\n")
                f.write(f"Return code: {process.returncode}\n")

            params_data["duration_seconds"] = duration
            params_data["return_code"] = process.returncode

            with open(params_file, 'w') as f:
                json.dump(params_data, f, indent=2)

            print(f"\nCompleted in {duration:.2f}s")
            print(f"Logs saved to: {os.path.dirname(log_file)}")

            return process.returncode == 0

        except Exception as e:
            print(f"Training execution failed: {e}")
            return False



pointcloud_params = {
    "num_points": 1000000,
    "remove_outliers": True,
    "normal_method": "open3d",
    "save_world_frame": False
}

# Usage
if __name__ == "__main__":
    logger = NerfTrainingLogger()

    # Example usage with automatic gaussian splat export for splatfacto
    method = "splatfacto"
    base_dir = "/home/sebastian/repos/master_thesis/test/shelf/0"
    experiment = "nerf_for_eval"
    config = [
        "--pipeline.model.camera-optimizer.mode off",
        "--pipeline.datamanager.images-on-gpu True",
        "--timestamp run",
        "--downscale-factor 4"
    ]

    # Train with automatic gaussian splat export (default behavior for splatfacto)
    # success = logger.train_simple(method, base_dir, experiment, config, export_geometry=True, quit_viewer=True)

    # if success:
    #     print("Training and export completed successfully!")
    # else:
    #     print("Training or export failed. Check the logs for details.")

    data_path = os.path.join(base_dir, "nerf/nerf_data")
    experiment_log_dir = os.path.join(data_path, experiment, method)
    config_path = os.path.join(experiment_log_dir, "run", "config.yml")
    print("📊 Exporting Gaussian Splat for splatfacto model...")
    export_success = logger.export_gaussian_splat(config_path, experiment_log_dir)
    if export_success:
        print("✅ Gaussian splat export completed successfully!")
    else:
        print("❌ Gaussian splat export failed. Check the export logs.")

    # You can also manually export gaussian splats from an existing model:
    # config_path = "/home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data/nerf_big_for_eval/splatfacto/run/config.yml"
    # output_dir = "/home/sebastian/repos/master_thesis/test/doll/2/nerf/nerf_data/nerf_big_for_eval/splatfacto/run"
    # logger.export_gaussian_splat(config_path, output_dir)