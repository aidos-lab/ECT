"""Euler Characteristic Transform for Meshes"""

import argparse
import trimesh

import numpy as np


def sample_from_unit_sphere(num_directions, dimension, seed=None):
    """Sample directions from unit sphere.

    Parameters
    ----------
    num_directions : int
        Number of directions

    dimension : int
        Dimension of the resulting vectors. For generating points on the
        2-sphere, you have to specify 3 here.

    seed : int (optional)
        Seed for the random number generator.

    Returns
    -------
    np.array of shape (num_directions, dimension)
        The directions
    """
    rng = np.random.default_rng(seed)

    directions = rng.standard_normal(size=(num_directions, dimension))
    directions = directions / np.sqrt(np.sum(directions**2, axis=1)[:, None])

    return directions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("FILE", type=str, help="Input file (mesh)")

    parser.add_argument(
        "--decimate",
        type=float,
        default=0.0,
        help="If set, decimate mesh by the specified amount in [0, 1]",
    )

    parser.add_argument(
        "-d",
        "--direction",
        type=str,
        default=None,
        help="Fixed direction; if set, will ignore number of directions",
    )

    parser.add_argument(
        "-N",
        "--normalize",
        action="store_true",
        help="If set, normalize model to unit sphere",
    )

    parser.add_argument(
        "-n",
        "--num-directions",
        type=int,
        default=8,
        help="Number of directions",
    )

    parser.add_argument(
        "-e",
        "--export",
        type=str,
        help="Filename for exporting the mesh with the filtration values as "
        "quality attributes. This only applies a *single* direction is "
        "used.",
    )

    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        help="Sets optional seed for reproducible number generation",
    )

    args = parser.parse_args()

    mesh = trimesh.load(args.FILE, force="mesh")

    if args.decimate > 0.0:
        mesh = mesh.simplify_quadric_decimation(args.decimate)

    if args.direction is not None:
        directions = np.asarray(list(map(float, args.direction.split(","))))
        directions = directions.reshape(1, -1)
    else:
        directions = sample_from_unit_sphere(
            args.num_directions, 3, seed=args.seed
        )

    # Since we are also permitted to use a single fixed direction, we
    # cannot rely on the value of `args.num_directions`.
    num_directions = directions.shape[0]

    vertices = np.asarray(mesh.vertices)

    if args.normalize:
        vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)

    filtration_values = vertices @ directions.T

    for direction in range(num_directions):
        filtration_values_ = filtration_values[:, direction]

        # In case there are duplicates, this will ensure that our count
        # routine works as expected.
        vertex_values = np.sort(filtration_values_)

        # We can sort the values directly since we only care about their
        # counts anyway.
        edge_values = np.sort(
            np.max(filtration_values_[mesh.edges_unique], axis=1)
        )
        face_values = np.sort(np.max(filtration_values_[mesh.faces], axis=1))

        for value in vertex_values:

            # This gives us the right (see what I did here?) index for
            # the insertion, which is also the count are interested in.
            num_vertices = np.searchsorted(vertex_values, value, side="right")
            num_edges = np.searchsorted(edge_values, value, side="right")
            num_faces = np.searchsorted(face_values, value, side="right")

            print(value, num_vertices - num_edges + num_faces)

        print("\n")

    if num_directions == 1 and args.export is not None:
        # Take the last filtration; since we only specified a single
        # direction, this is sufficient. As usual, filtration values
        # will be extended to faces. `trimesh` does not support edge
        # quality data.

        mesh.vertex_attributes["quality"] = filtration_values_

        mesh.face_attributes["quality"] = np.max(
            filtration_values_[mesh.faces], axis=1
        )

        mesh.export(args.export)
