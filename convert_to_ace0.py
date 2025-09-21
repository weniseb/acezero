import cv2
import os
import numpy as np
import struct
from pathlib import Path


def read_cameras_binary(path_to_model_file):
    """Read COLMAP cameras.bin file"""
    cameras = {}
    with open(path_to_model_file, "rb") as fid:
        num_cameras = struct.unpack("<Q", fid.read(8))[0]
        for _ in range(num_cameras):
            camera_properties = struct.unpack("<iiQQ", fid.read(24))
            camera_id = camera_properties[0]
            model_id = camera_properties[1]
            width = camera_properties[2]
            height = camera_properties[3]
            num_params = struct.unpack("<Q", fid.read(8))[0]
            params = struct.unpack(f"<{'d' * num_params}", fid.read(8 * num_params))
            cameras[camera_id] = {
                'model_id': model_id,
                'width': width,
                'height': height,
                'params': params
            }
    return cameras


def read_cameras_text(path_to_model_file):
    """Read COLMAP cameras.txt file"""
    cameras = {}
    with open(path_to_model_file, "r") as fid:
        for line in fid:
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue

            parts = line.split()
            camera_id = int(parts[0])
            model = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            params = [float(p) for p in parts[4:]]

            # Convert model name to model_id (simplified mapping)
            model_map = {"PINHOLE": 1, "RADIAL": 2, "OPENCV": 3, "SIMPLE_PINHOLE": 0}
            model_id = model_map.get(model, 1)

            cameras[camera_id] = {
                'model_id': model_id,
                'width': width,
                'height': height,
                'params': params
            }
    return cameras


def read_images_binary(path_to_model_file):
    """Read COLMAP images.bin file"""
    images = {}
    with open(path_to_model_file, "rb") as fid:
        num_reg_images = struct.unpack("<Q", fid.read(8))[0]
        for _ in range(num_reg_images):
            binary_image_properties = struct.unpack("<idddddddi", fid.read(64))
            image_id = binary_image_properties[0]
            qvec = binary_image_properties[1:5]
            tvec = binary_image_properties[5:8]
            camera_id = binary_image_properties[8]

            current_char = struct.unpack("<c", fid.read(1))[0]
            name = b""
            while current_char != b"\x00":
                name += current_char
                current_char = struct.unpack("<c", fid.read(1))[0]
            name = name.decode("utf-8")

            num_points2D = struct.unpack("<Q", fid.read(8))[0]
            x_y_id_s = struct.unpack(f"<{'ddq' * num_points2D}", fid.read(24 * num_points2D))

            images[image_id] = {
                'qvec': qvec,
                'tvec': tvec,
                'camera_id': camera_id,
                'name': name,
                'points2D': x_y_id_s
            }
    return images


def read_images_text(path_to_model_file):
    """Read COLMAP images.txt file"""
    images = {}
    with open(path_to_model_file, "r") as fid:
        lines = fid.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#") or len(line) == 0:
            i += 1
            continue

        parts = line.split()
        image_id = int(parts[0])
        qvec = [float(parts[j]) for j in range(1, 5)]
        tvec = [float(parts[j]) for j in range(5, 8)]
        camera_id = int(parts[8])
        name = parts[9]

        # Skip the points2D line (next line)
        i += 2

        images[image_id] = {
            'qvec': qvec,
            'tvec': tvec,
            'camera_id': camera_id,
            'name': name,
            'points2D': []  # We don't need points2D for ACE0 conversion
        }

    return images


def read_points3D_binary(path_to_model_file):
    """Read COLMAP points3D.bin file"""
    points3D = {}
    with open(path_to_model_file, "rb") as fid:
        num_points = struct.unpack("<Q", fid.read(8))[0]
        for _ in range(num_points):
            binary_point_line_properties = struct.unpack("<QdddBBBd", fid.read(43))
            point3D_id = binary_point_line_properties[0]
            xyz = binary_point_line_properties[1:4]
            rgb = binary_point_line_properties[4:7]
            error = binary_point_line_properties[7]

            track_length = struct.unpack("<Q", fid.read(8))[0]
            track_elems = struct.unpack(f"<{'ii' * track_length}", fid.read(8 * track_length))

            points3D[point3D_id] = {
                'xyz': xyz,
                'rgb': rgb,
                'error': error,
                'track': track_elems
            }
    return points3D


def read_points3D_text(path_to_model_file):
    """Read COLMAP points3D.txt file"""
    points3D = {}
    with open(path_to_model_file, "r") as fid:
        for line in fid:
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue

            parts = line.split()
            point3D_id = int(parts[0])
            xyz = [float(parts[j]) for j in range(1, 4)]
            rgb = [int(parts[j]) for j in range(4, 7)]
            error = float(parts[7]) if len(parts) > 7 else 0.0

            # Track information (if present) - we don't need it for ACE0
            track_elems = []
            if len(parts) > 8:
                track_data = parts[8:]
                track_elems = [int(x) for x in track_data]

            points3D[point3D_id] = {
                'xyz': xyz,
                'rgb': rgb,
                'error': error,
                'track': track_elems
            }
    return points3D


def save_ace0_poses(images, cameras, output_dir):
    """Convert COLMAP data to ACE0 poses_final.txt format"""
    poses_file = os.path.join(output_dir, 'poses_final.txt')

    with open(poses_file, 'w') as f:
        for image_id, image_data in images.items():
            # Image name
            name = Path(image_data['name']).stem

            # Quaternion (qw, qx, qy, qz)
            qvec = image_data['qvec']
            qw, qx, qy, qz = qvec[0], qvec[1], qvec[2], qvec[3]

            # Translation
            tvec = image_data['tvec']
            tx, ty, tz = tvec[0], tvec[1], tvec[2]

            # Get focal length from camera
            camera_id = image_data['camera_id']
            camera = cameras[camera_id]
            focal_length = camera['params'][0]  # Assuming PINHOLE model

            # Confidence (default to 1000.0 since COLMAP doesn't store this)
            confidence = 1000.0

            f.write(f"{name}.png {qw} {qx} {qy} {qz} {tx} {ty} {tz} {focal_length} {confidence}\n")


def save_ace0_pointcloud(points3D, output_dir):
    """Convert COLMAP points3D to ACE0 point_cloud.ply format"""
    pointcloud_file = os.path.join(output_dir, 'point_cloud.ply')

    # Collect all points and colors
    vertices = []
    colors = []

    for point_id, point_data in points3D.items():
        xyz = point_data['xyz']
        rgb = point_data['rgb']

        vertices.append([xyz[0], xyz[1], xyz[2]])
        colors.append([int(rgb[0]), int(rgb[1]), int(rgb[2])])

    vertices = np.array(vertices)
    colors = np.array(colors)

    # Create normals (default to [0, 1, 0] as in your original script)
    normals = np.tile([0, 1, 0], (vertices.shape[0], 1))

    # Create PLY header
    header = """ply
format ascii 1.0
element vertex {}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
property float nx
property float ny
property float nz
end_header
""".format(len(vertices))

    # Write PLY file
    with open(pointcloud_file, 'w') as f:
        f.write(header)
        for vertex, color, normal in zip(vertices, colors, normals):
            f.write(
                f"{vertex[0]} {vertex[1]} {vertex[2]} {int(color[0])} {int(color[1])} {int(color[2])} {normal[0]} {normal[1]} {normal[2]}\n")


def detect_colmap_format(colmap_dir):
    """Detect whether COLMAP files are in binary or text format"""
    bin_files = ['cameras.bin', 'images.bin', 'points3D.bin']
    txt_files = ['cameras.txt', 'images.txt', 'points3D.txt']

    bin_exists = all(os.path.exists(os.path.join(colmap_dir, f)) for f in bin_files)
    txt_exists = all(os.path.exists(os.path.join(colmap_dir, f)) for f in txt_files)

    if bin_exists and not txt_exists:
        return 'binary'
    elif txt_exists and not bin_exists:
        return 'text'
    elif bin_exists and txt_exists:
        print("Both binary and text files found. Using binary format.")
        return 'binary'
    else:
        raise FileNotFoundError("No complete set of COLMAP files found (cameras, images, points3D)")


def convert_colmap_to_ace0(colmap_dir, output_dir):
    """Main function to convert COLMAP binary or text format to ACE0 format"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Detect format and set file paths
    format_type = detect_colmap_format(colmap_dir)

    if format_type == 'binary':
        cameras_file = os.path.join(colmap_dir, 'cameras.bin')
        images_file = os.path.join(colmap_dir, 'images.bin')
        points3D_file = os.path.join(colmap_dir, 'points3D.bin')

        cameras = read_cameras_binary(cameras_file)
        images = read_images_binary(images_file)
        points3D = read_points3D_binary(points3D_file)
        print("Reading COLMAP binary format files...")
    else:  # text format
        cameras_file = os.path.join(colmap_dir, 'cameras.txt')
        images_file = os.path.join(colmap_dir, 'images.txt')
        points3D_file = os.path.join(colmap_dir, 'points3D.txt')

        cameras = read_cameras_text(cameras_file)
        images = read_images_text(images_file)
        points3D = read_points3D_text(points3D_file)
        print("Reading COLMAP text format files...")

    # Convert to ACE0 format
    save_ace0_poses(images, cameras, output_dir)
    save_ace0_pointcloud(points3D, output_dir)

    print(f"Conversion complete. ACE0 files saved to {output_dir}")
    print(f"Converted {len(images)} images and {len(points3D)} 3D points from {format_type} format")


if __name__ == '__main__':
    colmap_sparse_dir = '/home/sebastian/repos/master_thesis/acezero/datasets/mip360/bonsai/sparse'
    ace0_output_dir = '/home/sebastian/repos/master_thesis/acezero/datasets/mip360/bonsai/sparse/ace0'

    convert_colmap_to_ace0(colmap_sparse_dir, ace0_output_dir)