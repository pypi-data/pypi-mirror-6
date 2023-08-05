.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.dipy.tracks
======================


.. _nipype.interfaces.dipy.tracks.TrackDensityMap:


.. index:: TrackDensityMap

TrackDensityMap
---------------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/dipy/tracks.py#L34>`__

Creates a tract density image from a TrackVis track file using functions from dipy

Example
~~~~~~~

>>> import nipype.interfaces.dipy as dipy
>>> trk2tdi = dipy.TrackDensityMap()
>>> trk2tdi.inputs.in_file = 'converted.trk'
>>> trk2tdi.run()                                   # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                The input TrackVis track file

        [Optional]
        data_dims: (a list of from 3 to 3 items which are an integer)
                The size of the image in voxels.
        in_file: (an existing file name)
                The input TrackVis track file
        out_filename: (a file name, nipype default value: tdi.nii)
                The output filename for the tracks in TrackVis (.trk) format
        voxel_dims: (a list of from 3 to 3 items which are a float)
                The size of each voxel in mm.

Outputs::

        out_file: (an existing file name)
