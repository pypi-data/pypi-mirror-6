.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.fsl.utils
====================


.. _nipype.interfaces.fsl.utils.AvScale:


.. index:: AvScale

AvScale
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L540>`__

Wraps command **avscale**

Use FSL avscale command to extract info from mat file output of FLIRT

Examples
~~~~~~~~
avscale = AvScale()
avscale.inputs.mat_file = 'flirt.mat'
res = avscale.run()  # doctest: +SKIP

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        mat_file: (an existing file name)
                mat file to read
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        average_scaling
                Average Scaling
        backward_half_transform
                Backwards Half Transform
        determinant
                Determinant
        forward_half_transform
                Forward Half Transform
        left_right_orientation_preserved: (a boolean)
                True if LR orientation preserved
        rotation_translation_matrix
                Rotation and Translation Matrix
        scales
                Scales (x,y,z)
        skews
                Skews

.. _nipype.interfaces.fsl.utils.Complex:


.. index:: Complex

Complex
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1390>`__

Wraps command **fslcomplex**

fslcomplex is a tool for converting complex data
Examples
~~~~~~~~
>>> cplx = Complex()
>>> cplx.inputs.complex_in_file = "complex.nii"
>>> cplx.real_polar = True
>>> res = cplx.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        complex_cartesian: (a boolean)
                mutually_exclusive: real_polar, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        complex_in_file: (an existing file name)
        complex_in_file2: (an existing file name)
        complex_merge: (a boolean)
                mutually_exclusive: real_polar, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge, start_vol, end_vol
        complex_out_file: (a file name)
                mutually_exclusive: complex_out_file, magnitude_out_file,
                 phase_out_file, real_out_file, imaginary_out_file, real_polar,
                 real_cartesian
        complex_polar: (a boolean)
                mutually_exclusive: real_polar, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        complex_split: (a boolean)
                mutually_exclusive: real_polar, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        end_vol: (an integer)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        imaginary_in_file: (an existing file name)
        imaginary_out_file: (a file name)
                mutually_exclusive: complex_out_file, magnitude_out_file,
                 phase_out_file, real_polar, complex_cartesian, complex_polar,
                 complex_split, complex_merge
        magnitude_in_file: (an existing file name)
        magnitude_out_file: (a file name)
                mutually_exclusive: complex_out_file, real_out_file,
                 imaginary_out_file, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        phase_in_file: (an existing file name)
        phase_out_file: (a file name)
                mutually_exclusive: complex_out_file, real_out_file,
                 imaginary_out_file, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        real_cartesian: (a boolean)
                mutually_exclusive: real_polar, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        real_in_file: (an existing file name)
        real_out_file: (a file name)
                mutually_exclusive: complex_out_file, magnitude_out_file,
                 phase_out_file, real_polar, complex_cartesian, complex_polar,
                 complex_split, complex_merge
        real_polar: (a boolean)
                mutually_exclusive: real_polar, real_cartesian, complex_cartesian,
                 complex_polar, complex_split, complex_merge
        start_vol: (an integer)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        complex_out_file: (a file name)
        imaginary_out_file: (a file name)
        magnitude_out_file: (a file name)
        phase_out_file: (a file name)
        real_out_file: (a file name)

.. _nipype.interfaces.fsl.utils.ConvertXFM:


.. index:: ConvertXFM

ConvertXFM
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1021>`__

Wraps command **convert_xfm**

Use the FSL utility convert_xfm to modify FLIRT transformation matrices.

Examples
~~~~~~~~
>>> import nipype.interfaces.fsl as fsl
>>> invt = fsl.ConvertXFM()
>>> invt.inputs.in_file = "flirt.mat"
>>> invt.inputs.invert_xfm = True
>>> invt.inputs.out_file = 'flirt_inv.mat'
>>> invt.cmdline
'convert_xfm -omat flirt_inv.mat -inverse flirt.mat'

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input transformation matrix
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        concat_xfm: (a boolean)
                write joint transformation of two input matrices
                mutually_exclusive: invert_xfm, concat_xfm, fix_scale_skew
                requires: in_file2
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        fix_scale_skew: (a boolean)
                use secondary matrix to fix scale and skew
                mutually_exclusive: invert_xfm, concat_xfm, fix_scale_skew
                requires: in_file2
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input transformation matrix
        in_file2: (an existing file name)
                second input matrix (for use with fix_scale_skew or concat_xfm
        invert_xfm: (a boolean)
                invert input transformation
                mutually_exclusive: invert_xfm, concat_xfm, fix_scale_skew
        out_file: (a file name)
                final transformation matrix
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output transformation matrix

.. _nipype.interfaces.fsl.utils.ExtractROI:


.. index:: ExtractROI

ExtractROI
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L213>`__

Wraps command **fslroi**

Uses FSL Fslroi command to extract region of interest (ROI)
from an image.

You can a) take a 3D ROI from a 3D data set (or if it is 4D, the
same ROI is taken from each time point and a new 4D data set is
created), b) extract just some time points from a 4D data set, or
c) control time and space limits to the ROI.  Note that the
arguments are minimum index and size (not maximum index).  So to
extract voxels 10 to 12 inclusive you would specify 10 and 3 (not
10 and 12).

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import ExtractROI
>>> from nipype.testing import anatfile
>>> fslroi = ExtractROI(in_file=anatfile, roi_file='bar.nii', t_min=0,
...                     t_size=1)
>>> fslroi.cmdline == 'fslroi %s bar.nii 0 1' % anatfile
True

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        crop_list: (a list of items which are a tuple of the form: (an
                 integer, an integer))
                list of two tuples specifying crop options
                mutually_exclusive: x_min, x_size, y_min, y_size, z_min, z_size,
                 t_min, t_size
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        roi_file: (a file name)
                output file
        t_min: (an integer)
        t_size: (an integer)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        x_min: (an integer)
        x_size: (an integer)
        y_min: (an integer)
        y_size: (an integer)
        z_min: (an integer)
        z_size: (an integer)

Outputs::

        roi_file: (an existing file name)

.. _nipype.interfaces.fsl.utils.FilterRegressor:


.. index:: FilterRegressor

FilterRegressor
---------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L410>`__

Wraps command **fsl_regfilt**

Data de-noising by regressing out part of a design matrix

Uses simple OLS regression on 4D images

Inputs::

        [Mandatory]
        design_file: (an existing file name)
                name of the matrix with time courses (e.g. GLM design or MELODIC
                mixing matrix)
        filter_all: (a boolean)
                use all columns in the design file in denoising
                mutually_exclusive: filter_columns
        filter_columns: (a list of items which are an integer)
                (1-based) column indices to filter out of the data
                mutually_exclusive: filter_all
        in_file: (an existing file name)
                input file name (4D image)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        design_file: (an existing file name)
                name of the matrix with time courses (e.g. GLM design or MELODIC
                mixing matrix)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        filter_all: (a boolean)
                use all columns in the design file in denoising
                mutually_exclusive: filter_columns
        filter_columns: (a list of items which are an integer)
                (1-based) column indices to filter out of the data
                mutually_exclusive: filter_all
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file name (4D image)
        mask: (an existing file name)
                mask image file name
        out_file: (a file name)
                output file name for the filtered data
        out_vnscales: (a boolean)
                output scaling factors for variance normalization
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        var_norm: (a boolean)
                perform variance-normalization on data

Outputs::

        out_file: (an existing file name)
                output file name for the filtered data

.. _nipype.interfaces.fsl.utils.ImageMaths:


.. index:: ImageMaths

ImageMaths
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L338>`__

Wraps command **fslmaths**

Use FSL fslmaths command to allow mathematical manipulation of images

`FSL info <http://www.fmrib.ox.ac.uk/fslcourse/lectures/practicals/intro/index.htm#fslutils>`_

Examples
~~~~~~~~

>>> from nipype import fsl
>>> from nipype.testing import anatfile
>>> maths = fsl.ImageMaths(in_file=anatfile, op_string= '-add 5',
...                        out_file='foo_maths.nii')
>>> maths.cmdline == 'fslmaths %s -add 5 foo_maths.nii' % anatfile
True

Inputs::

        [Mandatory]
        in_file: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
        in_file2: (an existing file name)
        op_string: (a string)
                string defining the operation, i. e. -add
        out_data_type: ('char' or 'short' or 'int' or 'float' or 'double' or
                 'input')
                output datatype, one of (char, short, int, float, double, input)
        out_file: (a file name)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        suffix: (a string)
                out_file suffix
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)

.. _nipype.interfaces.fsl.utils.ImageMeants:


.. index:: ImageMeants

ImageMeants
-----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L63>`__

Wraps command **fslmeants**

Use fslmeants for printing the average timeseries (intensities) to
the screen (or saves to a file). The average is taken over all voxels in
the mask (or all voxels in the image if no mask is specified)

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file for computing the average timeseries
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        eig: (a boolean)
                calculate Eigenvariate(s) instead of mean (output will have 0 mean)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file for computing the average timeseries
        mask: (an existing file name)
                input 3D mask
        nobin: (a boolean)
                do not binarise the mask for calculation of Eigenvariates
        order: (an integer, nipype default value: 1)
                select number of Eigenvariates
        out_file: (a file name)
                name of output text matrix
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        show_all: (a boolean)
                show all voxel time series (within mask) instead of averaging
        spatial_coord: (a list of items which are an integer)
                <x y z> requested spatial coordinate (instead of mask)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        transpose: (a boolean)
                output results in transpose format (one row per voxel/mean)
        use_mm: (a boolean)
                use mm instead of voxel coordinates (for -c option)

Outputs::

        out_file: (an existing file name)
                path/name of output text matrix

.. _nipype.interfaces.fsl.utils.ImageStats:


.. index:: ImageStats

ImageStats
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L465>`__

Wraps command **fslstats**

Use FSL fslstats command to calculate stats from images

`FSL info <http://www.fmrib.ox.ac.uk/fslcourse/lectures/practicals/intro/index.htm#fslutils>`_

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import ImageStats
>>> from nipype.testing import funcfile
>>> stats = ImageStats(in_file=funcfile, op_string= '-M')
>>> stats.cmdline == 'fslstats %s -M'%funcfile
True

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to generate stats of
        op_string: (a string)
                string defining the operation, options are applied in order, e.g. -M
                -l 10 -M will report the non-zero mean, apply a threshold and then
                report the new nonzero mean
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to generate stats of
        mask_file: (an existing file name)
                mask file used for option -k %s
        op_string: (a string)
                string defining the operation, options are applied in order, e.g. -M
                -l 10 -M will report the non-zero mean, apply a threshold and then
                report the new nonzero mean
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        split_4d: (a boolean)
                give a separate output line for each 3D volume of a 4D timeseries
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_stat
                stats output

.. _nipype.interfaces.fsl.utils.InvWarp:


.. index:: InvWarp

InvWarp
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1311>`__

Wraps command **invwarp**

Use FSL Invwarp to inverse a FNIRT warp

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import InvWarp
>>> invwarp = InvWarp()
>>> invwarp.inputs.warp = "struct2mni.nii"
>>> invwarp.inputs.reference = "anatomical.nii"
>>> invwarp.cmdline
'invwarp --out=struct2mni_inverse.nii.gz --ref=anatomical.nii --warp=struct2mni.nii'
>>> res = invwarp.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        reference: (an existing file name)
                Name of a file in target space. Note that the target space is now
                different from the target space that was used to create the --warp
                file. It would typically be the file that was specified with the
                --in argument when running fnirt.
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        warp: (an existing file name)
                Name of file containing warp-coefficients/fields. This would
                typically be the output from the --cout switch of fnirt (but can
                also use fields, like the output from --fout).

        [Optional]
        absolute: (a boolean)
                If set it indicates that the warps in --warp should be interpreted
                as absolute, provided that it is not created by fnirt (which always
                uses relative warps). If set it also indicates that the output --out
                should be absolute.
                mutually_exclusive: relative
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        inverse_warp: (a file name)
                Name of output file, containing warps that are the "reverse" of
                those in --warp. This will be a field-file (rather than a file of
                spline coefficients), and it will have any affine component included
                as part of the displacements.
        jacobian_max: (a float)
                Maximum acceptable Jacobian value for constraint (default 100.0)
        jacobian_min: (a float)
                Minimum acceptable Jacobian value for constraint (default 0.01)
        niter: (an integer)
                Determines how many iterations of the gradient-descent search that
                should be run.
        noconstraint: (a boolean)
                Do not apply Jacobian constraint
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        reference: (an existing file name)
                Name of a file in target space. Note that the target space is now
                different from the target space that was used to create the --warp
                file. It would typically be the file that was specified with the
                --in argument when running fnirt.
        regularise: (a float)
                Regularisation strength (deafult=1.0).
        relative: (a boolean)
                If set it indicates that the warps in --warp should be interpreted
                as relative. I.e. the values in --warp are displacements from the
                coordinates in the --ref space. If set it also indicates that the
                output --out should be relative.
                mutually_exclusive: absolute
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        warp: (an existing file name)
                Name of file containing warp-coefficients/fields. This would
                typically be the output from the --cout switch of fnirt (but can
                also use fields, like the output from --fout).

Outputs::

        inverse_warp: (an existing file name)
                Name of output file, containing warps that are the "reverse" of
                those in --warp.

.. _nipype.interfaces.fsl.utils.Merge:


.. index:: Merge

Merge
-----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L149>`__

Wraps command **fslmerge**

Use fslmerge to concatenate images

Images can be concatenated across time, x, y, or z dimensions. Across the
time (t) dimension the TR is set by default to 1 sec.

Note: to set the TR to a different value, specify 't' for dimension and
specify the TR value in seconds for the tr input. The dimension will be
automatically updated to 'tr'.

Examples
~~~~~~~~
>>> from nipype.interfaces.fsl import Merge
>>> merger = Merge()
>>> merger.inputs.in_files = ['functional2.nii', 'functional3.nii']
>>> merger.inputs.dimension = 't'
>>> merger.inputs.output_type = 'NIFTI_GZ'
>>> merger.cmdline
'fslmerge -t functional2_merged.nii.gz functional2.nii functional3.nii'
>>> merger.inputs.tr = 2.25
>>> merger.cmdline
'fslmerge -tr functional2_merged.nii.gz functional2.nii functional3.nii 2.25'

Inputs::

        [Mandatory]
        dimension: ('t' or 'x' or 'y' or 'z' or 'a')
                dimension along which to merge, optionally set tr input when
                dimension is t
        in_files: (a list of items which are an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        dimension: ('t' or 'x' or 'y' or 'z' or 'a')
                dimension along which to merge, optionally set tr input when
                dimension is t
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_files: (a list of items which are an existing file name)
        merged_file: (a file name)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        tr: (a float)
                use to specify TR in seconds (default is 1.00 sec), overrides
                dimension and sets it to tr

Outputs::

        merged_file: (an existing file name)

.. _nipype.interfaces.fsl.utils.Overlay:


.. index:: Overlay

Overlay
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L632>`__

Wraps command **overlay**

Use FSL's overlay command to combine background and statistical images
    into one volume

Examples
~~~~~~~~
>>> from nipype.interfaces import fsl
>>> combine = fsl.Overlay()
>>> combine.inputs.background_image = 'mean_func.nii.gz'
>>> combine.inputs.auto_thresh_bg = True
>>> combine.inputs.stat_image = 'zstat1.nii.gz'
>>> combine.inputs.stat_thresh = (3.5, 10)
>>> combine.inputs.show_negative_stats = True
>>> res = combine.run() #doctest: +SKIP

Inputs::

        [Mandatory]
        auto_thresh_bg: (a boolean)
                automatically threhsold the background image
                mutually_exclusive: auto_thresh_bg, full_bg_range, bg_thresh
        background_image: (an existing file name)
                image to use as background
        bg_thresh: (a tuple of the form: (a float, a float))
                min and max values for background intensity
                mutually_exclusive: auto_thresh_bg, full_bg_range, bg_thresh
        full_bg_range: (a boolean)
                use full range of background image
                mutually_exclusive: auto_thresh_bg, full_bg_range, bg_thresh
        stat_image: (an existing file name)
                statistical image to overlay in color
        stat_thresh: (a tuple of the form: (a float, a float))
                min and max values for the statistical overlay
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        auto_thresh_bg: (a boolean)
                automatically threhsold the background image
                mutually_exclusive: auto_thresh_bg, full_bg_range, bg_thresh
        background_image: (an existing file name)
                image to use as background
        bg_thresh: (a tuple of the form: (a float, a float))
                min and max values for background intensity
                mutually_exclusive: auto_thresh_bg, full_bg_range, bg_thresh
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        full_bg_range: (a boolean)
                use full range of background image
                mutually_exclusive: auto_thresh_bg, full_bg_range, bg_thresh
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        out_file: (a file name)
                combined image volume
        out_type: ('float' or 'int', nipype default value: float)
                write output with float or int
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        show_negative_stats: (a boolean)
                display negative statistics in overlay
                mutually_exclusive: stat_image2
        stat_image: (an existing file name)
                statistical image to overlay in color
        stat_image2: (an existing file name)
                second statistical image to overlay in color
                mutually_exclusive: show_negative_stats
        stat_thresh: (a tuple of the form: (a float, a float))
                min and max values for the statistical overlay
        stat_thresh2: (a tuple of the form: (a float, a float))
                min and max values for second statistical overlay
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        transparency: (a boolean, nipype default value: True)
                make overlay colors semi-transparent
        use_checkerboard: (a boolean)
                use checkerboard mask for overlay

Outputs::

        out_file: (an existing file name)
                combined image volume

.. _nipype.interfaces.fsl.utils.PlotMotionParams:


.. index:: PlotMotionParams

PlotMotionParams
----------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L913>`__

Wraps command **fsl_tsplot**

Use fsl_tsplot to plot the estimated motion parameters from a realignment
program.

Examples
~~~~~~~~
>>> import nipype.interfaces.fsl as fsl
>>> plotter = fsl.PlotMotionParams()
>>> plotter.inputs.in_file = 'functional.par'
>>> plotter.inputs.in_source = 'fsl'
>>> plotter.inputs.plot_type = 'rotations'
>>> res = plotter.run() #doctest: +SKIP

Notes
~~~~~
The 'in_source' attribute determines the order of columns that are expected
in the source file.  FSL prints motion parameters in the order rotations,
translations, while SPM prints them in the opposite order.  This interface
should be able to plot timecourses of motion parameters generated from other
sources as long as they fall under one of these two patterns.  For more
flexibilty, see the :class:`fsl.PlotTimeSeries` interface.

Inputs::

        [Mandatory]
        in_file: (an existing file name or a list of items which are an
                 existing file name)
                file with motion parameters
        in_source: ('spm' or 'fsl')
                which program generated the motion parameter file - fsl, spm
        plot_type: ('rotations' or 'translations' or 'displacement')
                which motion type to plot - rotations, translations, displacement
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name or a list of items which are an
                 existing file name)
                file with motion parameters
        in_source: ('spm' or 'fsl')
                which program generated the motion parameter file - fsl, spm
        out_file: (a file name)
                image to write
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        plot_size: (a tuple of the form: (an integer, an integer))
                plot image height and width
        plot_type: ('rotations' or 'translations' or 'displacement')
                which motion type to plot - rotations, translations, displacement
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image to write

.. _nipype.interfaces.fsl.utils.PlotTimeSeries:


.. index:: PlotTimeSeries

PlotTimeSeries
--------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L832>`__

Wraps command **fsl_tsplot**

Use fsl_tsplot to create images of time course plots.

Examples
~~~~~~~~
>>> import nipype.interfaces.fsl as fsl
>>> plotter = fsl.PlotTimeSeries()
>>> plotter.inputs.in_file = 'functional.par'
>>> plotter.inputs.title = 'Functional timeseries'
>>> plotter.inputs.labels = ['run1', 'run2']
>>> plotter.run() #doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name or a list of items which are an
                 existing file name)
                file or list of files with columns of timecourse information
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name or a list of items which are an
                 existing file name)
                file or list of files with columns of timecourse information
        labels: (a string or a list of items which are a string)
                label or list of labels
        legend_file: (an existing file name)
                legend file
        out_file: (a file name)
                image to write
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        plot_finish: (an integer)
                final column from in-file to plot
                mutually_exclusive: plot_range
        plot_range: (a tuple of the form: (an integer, an integer))
                first and last columns from the in-file to plot
                mutually_exclusive: plot_start, plot_finish
        plot_size: (a tuple of the form: (an integer, an integer))
                plot image height and width
        plot_start: (an integer)
                first column from in-file to plot
                mutually_exclusive: plot_range
        sci_notation: (a boolean)
                switch on scientific notation
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        title: (a string)
                plot title
        x_precision: (an integer)
                precision of x-axis labels
        x_units: (an integer, nipype default value: 1)
                scaling units for x-axis (between 1 and length of in file)
        y_max: (a float)
                maximum y value
                mutually_exclusive: y_range
        y_min: (a float)
                minumum y value
                mutually_exclusive: y_range
        y_range: (a tuple of the form: (a float, a float))
                min and max y axis values
                mutually_exclusive: y_min, y_max

Outputs::

        out_file: (an existing file name)
                image to write

.. _nipype.interfaces.fsl.utils.PowerSpectrum:


.. index:: PowerSpectrum

PowerSpectrum
-------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1131>`__

Wraps command **fslpspec**

Use FSL PowerSpectrum command for power spectrum estimation.

Examples
~~~~~~~~
>>> from nipype.interfaces import fsl
>>> pspec = fsl.PowerSpectrum()
>>> pspec.inputs.in_file = 'functional.nii'
>>> res = pspec.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input 4D file to estimate the power spectrum
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input 4D file to estimate the power spectrum
        out_file: (a file name)
                name of output 4D file for power spectrum
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                path/name of the output 4D power spectrum file

.. _nipype.interfaces.fsl.utils.Reorient2Std:


.. index:: Reorient2Std

Reorient2Std
------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1224>`__

Wraps command **fslreorient2std**

fslreorient2std is a tool for reorienting the image to match the
approximate orientation of the standard template images (MNI152).

Examples
~~~~~~~~
>>> reorient = Reorient2Std()
>>> reorient.inputs.in_file = "functional.nii"
>>> res = reorient.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
        out_file: (a file name)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)

.. _nipype.interfaces.fsl.utils.SigLoss:


.. index:: SigLoss

SigLoss
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1186>`__

Wraps command **sigloss**

Estimates signal loss from a field map (in rad/s)

Examples
~~~~~~~~
>>> sigloss = SigLoss()
>>> sigloss.inputs.in_file = "phase.nii"
>>> sigloss.inputs.echo_time = 0.03
>>> res = sigloss.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                b0 fieldmap file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        echo_time: (a float)
                echo time in seconds
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                b0 fieldmap file
        mask_file: (an existing file name)
                brain mask file
        out_file: (a file name)
                output signal loss estimate file
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        slice_direction: ('x' or 'y' or 'z')
                slicing direction
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                signal loss estimate file

.. _nipype.interfaces.fsl.utils.Slicer:


.. index:: Slicer

Slicer
------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L744>`__

Wraps command **slicer**

Use FSL's slicer command to output a png image from a volume.

Examples
~~~~~~~~
>>> from nipype.interfaces import fsl
>>> from nipype.testing import example_data
>>> slice = fsl.Slicer()
>>> slice.inputs.in_file = example_data('functional.nii')
>>> slice.inputs.all_axial = True
>>> slice.inputs.image_width = 750
>>> res = slice.run() #doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input volume
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        all_axial: (a boolean)
                output all axial slices into one picture
                mutually_exclusive: single_slice, middle_slices, all_axial,
                 sample_axial
                requires: image_width
        args: (a string)
                Additional parameters to the command
        colour_map: (an existing file name)
                use different colour map from that stored in nifti header
        dither_edges: (a boolean)
                produce semi-transparaent (dithered) edges
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        image_edges: (an existing file name)
                volume to display edge overlay for (useful for checking registration
        image_width: (an integer)
                max picture width
        in_file: (an existing file name)
                input volume
        intensity_range: (a tuple of the form: (a float, a float))
                min and max intensities to display
        label_slices: (a boolean, nipype default value: True)
                display slice number
        middle_slices: (a boolean)
                output picture of mid-sagital, axial, and coronal slices
                mutually_exclusive: single_slice, middle_slices, all_axial,
                 sample_axial
        nearest_neighbour: (a boolean)
                use nearest neighbour interpolation for output
        out_file: (a file name)
                picture to write
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        sample_axial: (an integer)
                output every n axial slices into one picture
                mutually_exclusive: single_slice, middle_slices, all_axial,
                 sample_axial
                requires: image_width
        scaling: (a float)
                image scale
        show_orientation: (a boolean, nipype default value: True)
                label left-right orientation
        single_slice: ('x' or 'y' or 'z')
                output picture of single slice in the x, y, or z plane
                mutually_exclusive: single_slice, middle_slices, all_axial,
                 sample_axial
                requires: slice_number
        slice_number: (an integer)
                slice number to save in picture
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        threshold_edges: (a float)
                use threshold for edges

Outputs::

        out_file: (an existing file name)
                picture to write

.. _nipype.interfaces.fsl.utils.Smooth:


.. index:: Smooth

Smooth
------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L102>`__

Wraps command **fslmaths**

Use fslmaths to smooth the image

Inputs::

        [Mandatory]
        fwhm: (a float)
        in_file: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        fwhm: (a float)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        smoothed_file: (a file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        smoothed_file: (an existing file name)

.. _nipype.interfaces.fsl.utils.Split:


.. index:: Split

Split
-----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L288>`__

Wraps command **fslsplit**

Uses FSL Fslsplit command to separate a volume into images in
time, x, y or z dimension.

Inputs::

        [Mandatory]
        dimension: ('t' or 'x' or 'y' or 'z')
                dimension along which the file will be split
        in_file: (an existing file name)
                input filename
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        dimension: ('t' or 'x' or 'y' or 'z')
                dimension along which the file will be split
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input filename
        out_base_name: (a string)
                outputs prefix
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_files: (an existing file name)

.. _nipype.interfaces.fsl.utils.SwapDimensions:


.. index:: SwapDimensions

SwapDimensions
--------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/utils.py#L1089>`__

Wraps command **fslswapdim**

Use fslswapdim to alter the orientation of an image.

This interface accepts a three-tuple corresponding to the new
orientation.  You may either provide dimension ids in the form of
(-)x, (-)y, or (-z), or nifti-syle dimension codes (RL, LR, AP, PA, IS, SI).

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input image
        new_dims: (a tuple of the form: ('x' or '-x' or 'y' or '-y' or 'z' or
                 '-z' or 'RL' or 'LR' or 'AP' or 'PA' or 'IS' or 'SI', 'x' or '-x'
                 or 'y' or '-y' or 'z' or '-z' or 'RL' or 'LR' or 'AP' or 'PA' or
                 'IS' or 'SI', 'x' or '-x' or 'y' or '-y' or 'z' or '-z' or 'RL' or
                 'LR' or 'AP' or 'PA' or 'IS' or 'SI'))
                3-tuple of new dimension order
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input image
        new_dims: (a tuple of the form: ('x' or '-x' or 'y' or '-y' or 'z' or
                 '-z' or 'RL' or 'LR' or 'AP' or 'PA' or 'IS' or 'SI', 'x' or '-x'
                 or 'y' or '-y' or 'z' or '-z' or 'RL' or 'LR' or 'AP' or 'PA' or
                 'IS' or 'SI', 'x' or '-x' or 'y' or '-y' or 'z' or '-z' or 'RL' or
                 'LR' or 'AP' or 'PA' or 'IS' or 'SI'))
                3-tuple of new dimension order
        out_file: (a file name)
                image to write
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image with new dimensions
