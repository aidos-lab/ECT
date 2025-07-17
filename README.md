# Companion Repository for "Topology meets Machine Learning: An Introduction using the Euler Characteristic Transform"

This is a small list of additional resources for the Euler
Characteristic Transform. Please also check out the
[repository](https://github.com/aidos-lab/ECT) for some sample code.
Notice that the examples have been provided with a primary focus on
being *instructive* as opposed to being highly optimized.

## Examples

- [`ect.py`](./ect.py): A script for calculating the ECT of *meshes*,
  i.e., two-dimensional simplicial complexes. This file was used to
  create all visualizations in the paper.

- [`ect_image.py`](./ect_image.py): Renders the output of the script
  above as an image.

The two scripts are supposed to work in tandem like this:

```bash
# Create the ECT of a given mesh (not supplied for licencing reasons)
# using multiple directions and visualize it.
$ python ect.py /tmp/ncc-1701-d.stl > /tmp/ECT.txt
$ python ect_image.py --normalize /tmp/ECT.txt
```
The `ect.py` also affords several other creation strategies:

```bash
# Create the ECT of a given mesh (not supplied for licencing reasons)
# using a specific direction (x-axis).
$ python ect.py /tmp/ncc-1701-d.stl -d "1,0,0" -e /tmp/x.ply > /tmp/x.txt
```

## Papers

The ECT or its variants has been used in a variety of different
applications. Here are some examples (feel free to add more by opening
a [PR](https://github.com/aidos-lab/ECT/pulls) or [issue](https://github.com/aidos-lab/ECT/issues) in this repository):

- [*An Invitation to the Euler Characteristic Transform*](https://www.tandfonline.com/doi/full/10.1080/00029890.2024.2409616)
- [*Differentiable Euler Characteristic Transforms for Shape Classification*](https://openreview.net/forum?id=MO632iPq3I)
- [*Diss-l-ECT: Dissecting Graph Data with Local Euler Characteristic Transforms*](https://arxiv.org/abs/2410.02622)
- [*Predicting Clinical Outcomes in Glioblastoma: An Application of Topological and Functional Data Analysis*](https://www.tandfonline.com/doi/abs/10.1080/01621459.2019.1671198)

## Software

- [`ect`](https://github.com/MunchLab/ect)
- [`DECT`](https://github.com/aidos-lab/DECT)
