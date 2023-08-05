.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.afni.preprocess
==========================


.. _nipype.interfaces.afni.preprocess.Allineate:


.. index:: Allineate

Allineate
---------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1080>`__

Wraps command **3dAllineate**

Program to align one dataset (the 'source') to a base dataset

For complete details, see the `3dAllineate Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dAllineate.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> allineate = afni.Allineate()
>>> allineate.inputs.in_file = 'functional.nii'
>>> allineate.inputs.out_file= 'functional_allineate.nii'
>>> allineate.inputs.in_matrix= 'cmatrix.mat'
>>> res = allineate.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dAllineate
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        autobox: (a boolean)
                Expand the -automask function to enclose a rectangular
                 box that holds the irregular mask.
        automask: (an integer)
                Compute a mask function, set a value for dilation or 0.
        autoweight: (a string)
                Compute a weight function using the 3dAutomask
                 algorithm plus some blurring of the base image.
        center_of_mass: (a string)
                Use the center-of-mass calculation to bracket the shifts.
        check: (a list of items which are 'leastsq' or 'ls' or 'mutualinfo'
                 or 'mi' or 'corratio_mul' or 'crM' or 'norm_mutualinfo' or 'nmi' or
                 'hellinger' or 'hel' or 'corratio_add' or 'crA' or 'corratio_uns'
                 or 'crU')
                After cost functional optimization is done, start at the
                 final parameters and RE-optimize using this new cost functions.
                 If the results are too different, a warning message will be
                 printed. However, the final parameters from the original
                 optimization will be used to create the output dataset.
        convergence: (a float)
                Convergence test in millimeters (default 0.05mm).
        cost: ('leastsq' or 'ls' or 'mutualinfo' or 'mi' or 'corratio_mul' or
                 'crM' or 'norm_mutualinfo' or 'nmi' or 'hellinger' or 'hel' or
                 'corratio_add' or 'crA' or 'corratio_uns' or 'crU')
                Defines the 'cost' function that defines the matching
                 between the source and the base
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        epi: (a boolean)
                Treat the source dataset as being composed of warped
                 EPI slices, and the base as comprising anatomically
                 'true' images. Only phase-encoding direction image
                 shearing and scaling will be allowed with this option.
        final_interpolation: ('nearestneighbour' or 'linear' or 'cubic' or
                 'quintic' or 'wsinc5')
                Defines interpolation method used to create the output dataset
        fine_blur: (a float)
                Set the blurring radius to use in the fine resolution
                 pass to 'x' mm. A small amount (1-2 mm?) of blurring at
                 the fine step may help with convergence, if there is
                 some problem, especially if the base volume is very noisy.
                 [Default == 0 mm = no blurring at the final alignment pass]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dAllineate
        in_matrix: (a file name)
                matrix to align input file
        in_param_file: (an existing file name)
                Read warp parameters from file and apply them to
                 the source dataset, and produce a new dataset
        interpolation: ('nearestneighbour' or 'linear' or 'cubic' or
                 'quintic')
                Defines interpolation method to use during matching
        master: (an existing file name)
                Write the output dataset on the same grid as this file
        newgrid: (a float)
                Write the output dataset using isotropic grid spacing in mm
        nmatch: (an integer)
                Use at most n scattered points to match the datasets.
        no_pad: (a boolean)
                Do not use zero-padding on the base image.
        nomask: (a boolean)
                Don't compute the autoweight/mask; if -weight is not
                 also used, then every voxel will be counted equally.
        nwarp: ('bilinear' or 'cubic' or 'quintic' or 'heptic' or 'nonic' or
                 'poly3' or 'poly5' or 'poly7' or 'poly9')
                Experimental nonlinear warping: bilinear or legendre poly.
        nwarp_fixdep: (a list of items which are 'X' or 'Y' or 'Z' or 'I' or
                 'J' or 'K')
                To fix non-linear warp dependency along directions.
        nwarp_fixmot: (a list of items which are 'X' or 'Y' or 'Z' or 'I' or
                 'J' or 'K')
                To fix motion along directions.
        one_pass: (a boolean)
                Use only the refining pass -- do not try a coarse
                 resolution pass first. Useful if you know that only
                 small amounts of image alignment are needed.
        out_file: (a file name)
                output file from 3dAllineate
        out_matrix: (a file name)
                Save the transformation matrix for each volume.
        out_param_file: (a file name)
                Save the warp parameters in ASCII (.1D) format.
        out_weight_file: (a file name)
                Write the weight volume to disk as a dataset
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        reference: (an existing file name)
                file to be used as reference, the first volume will be used
                if not given the reference will be the first volume of in_file.
        replacebase: (a boolean)
                If the source has more than one volume, then after the first
                 volume is aligned to the base
        replacemeth: ('leastsq' or 'ls' or 'mutualinfo' or 'mi' or
                 'corratio_mul' or 'crM' or 'norm_mutualinfo' or 'nmi' or
                 'hellinger' or 'hel' or 'corratio_add' or 'crA' or 'corratio_uns'
                 or 'crU')
                After first volume is aligned, switch method for later volumes.
                 For use with '-replacebase'.
        source_automask: (an integer)
                Automatically mask the source dataset with dilation or 0.
        source_mask: (an existing file name)
                mask the input dataset
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        two_best: (an integer)
                In the coarse pass, use the best 'bb' set of initial
                 points to search for the starting point for the fine
                 pass. If bb==0, then no search is made for the best
                 starting point, and the identity transformation is
                 used as the starting point. [Default=5; min=0 max=11]
        two_blur: (a float)
                Set the blurring radius for the first pass in mm.
        two_first: (a boolean)
                Use -twopass on the first image to be registered, and
                 then on all subsequent images from the source dataset,
                 use results from the first image's coarse pass to start
                 the fine pass.
        two_pass: (a boolean)
                Use a two pass alignment strategy for all volumes, searching
                 for a large rotation+shift and then refining the alignment.
        usetemp: (a boolean)
                temporary file use
        warp_type: ('shift_only' or 'shift_rotate' or 'shift_rotate_scale' or
                 'affine_general')
                Set the warp type.
        warpfreeze: (a boolean)
                Freeze the non-rigid body parameters after first volume.
        weight_file: (an existing file name)
                Set the weighting for each voxel in the base dataset;
                 larger weights mean that voxel count more in the cost function.
                 Must be defined on the same grid as the base dataset
        zclip: (a boolean)
                Replace negative values in the input datasets (source & base) with
                zero.

Outputs::

        matrix: (a file name)
                matrix to align input file
        out_file: (a file name)
                output image file name

.. _nipype.interfaces.afni.preprocess.AutoTcorrelate:


.. index:: AutoTcorrelate

AutoTcorrelate
--------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L347>`__

Wraps command **3dAutoTcorrelate**

Computes the correlation coefficient between the time series of each
pair of voxels in the input dataset, and stores the output into a
new anatomical bucket dataset [scaled to shorts to save memory space].

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> corr = afni.AutoTcorrelate()
>>> corr.inputs.in_file = 'functional.nii'
>>> corr.inputs.polort = -1
>>> corr.inputs.eta2 = True
>>> corr.inputs.mask = 'mask.nii'
>>> corr.inputs.mask_only_targets = True
>>> corr.cmdline # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
'3dAutoTcorrelate -eta2 -mask mask.nii -mask_only_targets -prefix functional_similarity_matrix.1D -polort -1 functional.nii'
>>> res = corr.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                timeseries x space (volume or surface) file
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
        eta2: (a boolean)
                eta^2 similarity
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                timeseries x space (volume or surface) file
        mask: (an existing file name)
                mask of voxels
        mask_only_targets: (a boolean)
                use mask only on targets voxels
                mutually_exclusive: mask_source
        mask_source: (an existing file name)
                mask for source voxels
                mutually_exclusive: mask_only_targets
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        polort: (an integer)
                Remove polynomical trend of order m or -1 for no detrending
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Autobox:


.. index:: Autobox

Autobox
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1785>`__

Wraps command **3dAutobox**

Computes size of a box that fits around the volume.
Also can be used to crop the volume to that box.

For complete details, see the `3dAutobox Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dAutobox.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> abox = afni.Autobox()
>>> abox.inputs.in_file = 'structural.nii'
>>> abox.inputs.padding = 5
>>> res = abox.run()   # doctest: +SKIP

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
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file
        no_clustering: (a boolean)
                Don't do any clustering to find box. Any non-zero
                 voxel will be preserved in the cropped volume.
                 The default method uses some clustering to find the
                 cropping box, and will clip off small isolated blobs.
        out_file: (a file name)
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        padding: (an integer)
                Number of extra voxels to pad on each side of box
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (a file name)
                output file
        x_max: (an integer)
        x_min: (an integer)
        y_max: (an integer)
        y_min: (an integer)
        z_max: (an integer)
        z_min: (an integer)

.. _nipype.interfaces.afni.preprocess.Automask:


.. index:: Automask

Automask
--------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L528>`__

Wraps command **3dAutomask**

Create a brain-only mask of the image using AFNI 3dAutomask command

For complete details, see the `3dAutomask Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dAutomask.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> automask = afni.Automask()
>>> automask.inputs.in_file = 'functional.nii'
>>> automask.inputs.dilate = 1
>>> automask.inputs.outputtype = "NIFTI"
>>> automask.cmdline #doctest: +ELLIPSIS
'3dAutomask -apply_prefix functional_masked.nii -dilate 1 -prefix functional_mask.nii functional.nii'
>>> res = automask.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dAutomask
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        brain_file: (a file name)
                output file from 3dAutomask
        clfrac: (a float)
                sets the clip level fraction (must be 0.1-0.9). A small value will
                tend to make the mask larger [default = 0.5].
        dilate: (an integer)
                dilate the mask outwards
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        erode: (an integer)
                erode the mask inwards
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dAutomask
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        brain_file: (an existing file name)
                brain file (skull stripped)
        out_file: (an existing file name)
                mask file

.. _nipype.interfaces.afni.preprocess.Bandpass:


.. index:: Bandpass

Bandpass
--------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L822>`__

Wraps command **3dBandpass**

Program to lowpass and/or highpass each voxel time series in a
dataset, offering more/different options than Fourier

For complete details, see the `3dBandpass Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dbandpass.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> from nipype.testing import  example_data
>>> bandpass = afni.Bandpass()
>>> bandpass.inputs.in_file = example_data('functional.nii')
>>> bandpass.inputs.highpass = 0.005
>>> bandpass.inputs.lowpass = 0.1
>>> res = bandpass.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        highpass: (a float)
                highpass
        in_file: (an existing file name)
                input file to 3dBandpass
        lowpass: (a float)
                lowpass
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        automask: (a boolean)
                Create a mask from the input dataset
        blur: (a float)
                Blur (inside the mask only) with a filter
                 width (FWHM) of 'fff' millimeters.
        despike: (a boolean)
                Despike each time series before other processing.
                 ++ Hopefully, you don't actually need to do this,
                 which is why it is optional.
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        highpass: (a float)
                highpass
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dBandpass
        localPV: (a float)
                Replace each vector by the local Principal Vector
                 (AKA first singular vector) from a neighborhood
                 of radius 'rrr' millimiters.
                 ++ Note that the PV time series is L2 normalized.
                 ++ This option is mostly for Bob Cox to have fun with.
        lowpass: (a float)
                lowpass
        mask: (an existing file name)
                mask file
        nfft: (an integer)
                set the FFT length [must be a legal value]
        no_detrend: (a boolean)
                Skip the quadratic detrending of the input that
                 occurs before the FFT-based bandpassing.
                 ++ You would only want to do this if the dataset
                 had been detrended already in some other program.
        normalize: (a boolean)
                Make all output time series have L2 norm = 1
                 ++ i.e., sum of squares = 1
        notrans: (a boolean)
                Don't check for initial positive transients in the data:
                 ++ The test is a little slow, so skipping it is OK,
                 if you KNOW the data time series are transient-free.
        orthogonalize_dset: (an existing file name)
                Orthogonalize each voxel to the corresponding
                 voxel time series in dataset 'fset', which must
                 have the same spatial and temporal grid structure
                 as the main input dataset.
                 ++ At present, only one '-dsort' option is allowed.
        orthogonalize_file: (an existing file name)
                Also orthogonalize input to columns in f.1D
                 ++ Multiple '-ort' options are allowed.
        out_file: (a file name)
                output file from 3dBandpass
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        tr: (a float)
                set time step (TR) in sec [default=from dataset header]

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.BlurInMask:


.. index:: BlurInMask

BlurInMask
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1628>`__

Wraps command **3dBlurInMask**

Blurs a dataset spatially inside a mask.  That's all.  Experimental.

For complete details, see the `3dBlurInMask Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dBlurInMask.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> bim = afni.BlurInMask()
>>> bim.inputs.in_file = 'functional.nii'
>>> bim.inputs.mask = 'mask.nii'
>>> bim.inputs.fwhm = 5.0
>>> bim.cmdline #doctest: +ELLIPSIS
'3dBlurInMask -input functional.nii -FWHM 5.000000 -mask mask.nii -prefix functional_blur'
>>> res = bim.run()   # doctest: +SKIP

Inputs::

        [Mandatory]
        fwhm: (a float)
                fwhm kernel size
        in_file: (an existing file name)
                input file to 3dSkullStrip
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        automask: (a boolean)
                Create an automask from the input dataset.
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        float_out: (a boolean)
                Save dataset as floats, no matter what the input data type is.
        fwhm: (a float)
                fwhm kernel size
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dSkullStrip
        mask: (a file name)
                Mask dataset, if desired. Blurring will occur only within the mask.
                Voxels NOT in the mask will be set to zero in the output.
        multimask: (a file name)
                Multi-mask dataset -- each distinct nonzero value in dataset will be
                treated as a separate mask for blurring purposes.
        options: (a string)
                options
        out_file: (a file name)
                output to the file
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        preserve: (a boolean)
                Normally, voxels not in the mask will be set to zero in the output.
                If you want the original values in the dataset to be preserved in
                the output, use this option.
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.BrickStat:


.. index:: BrickStat

BrickStat
---------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1419>`__

Wraps command **3dBrickStat**

Compute maximum and/or minimum voxel values of an input dataset

For complete details, see the `3dBrickStat Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dBrickStat.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> brickstat = afni.BrickStat()
>>> brickstat.inputs.in_file = 'functional.nii'
>>> brickstat.inputs.mask = 'skeleton_mask.nii.gz'
>>> brickstat.inputs.min = True
>>> res = brickstat.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dmaskave
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
                input file to 3dmaskave
        mask: (an existing file name)
                -mask dset = use dset as mask to include/exclude voxels
        min: (a boolean)
                print the minimum value in dataset
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        min_val: (a float)
                output

.. _nipype.interfaces.afni.preprocess.Calc:


.. index:: Calc

Calc
----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1553>`__

Wraps command **3dcalc**

This program does voxel-by-voxel arithmetic on 3D datasets

For complete details, see the `3dcalc Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dcalc.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> calc = afni.Calc()
>>> calc.inputs.in_file_a = 'functional.nii'
>>> calc.inputs.in_file_b = 'functional2.nii'
>>> calc.inputs.expr='a*b'
>>> calc.inputs.out_file =  'functional_calc.nii.gz'
>>> calc.inputs.outputtype = "NIFTI"
>>> calc.cmdline #doctest: +ELLIPSIS
'3dcalc -a functional.nii  -b functional2.nii -expr "a*b" -prefix functional_calc.nii.gz'

Inputs::

        [Mandatory]
        expr: (a string)
                expr
        in_file_a: (an existing file name)
                input file to 3dcalc
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
        expr: (a string)
                expr
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file_a: (an existing file name)
                input file to 3dcalc
        in_file_b: (an existing file name)
                operand file to 3dcalc
        in_file_c: (an existing file name)
                operand file to 3dcalc
        other: (a file name)
                other options
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        single_idx: (an integer)
                volume index for in_file_a
        start_idx: (an integer)
                start index for in_file_a
                requires: stop_idx
        stop_idx: (an integer)
                stop index for in_file_a
                requires: start_idx
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Copy:


.. index:: Copy

Copy
----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L670>`__

Wraps command **3dcopy**

Copies an image of one type to an image of the same
or different type using 3dcopy command

For complete details, see the `3dcopy Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dcopy.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> copy = afni.Copy()
>>> copy.inputs.in_file = 'functional.nii'
>>> copy.inputs.out_file = 'new_func.nii'
>>> res = copy.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dcopy
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
                input file to 3dcopy
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Despike:


.. index:: Despike

Despike
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L470>`__

Wraps command **3dDespike**

Removes 'spikes' from the 3D+time input dataset

For complete details, see the `3dDespike Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dDespike.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> despike = afni.Despike()
>>> despike.inputs.in_file = 'functional.nii'
>>> despike.cmdline
'3dDespike -prefix functional_despike functional.nii'
>>> res = despike.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dDespike
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
                input file to 3dDespike
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Detrend:


.. index:: Detrend

Detrend
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L432>`__

Wraps command **3dDetrend**

This program removes components from voxel time series using
linear least squares

For complete details, see the `3dDetrend Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dDetrend.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> detrend = afni.Detrend()
>>> detrend.inputs.in_file = 'functional.nii'
>>> detrend.inputs.args = '-polort 2'
>>> detrend.inputs.outputtype = "AFNI"
>>> detrend.cmdline
'3dDetrend -polort 2 -prefix functional_detrend functional.nii'
>>> res = detrend.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dDetrend
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
                input file to 3dDetrend
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Fim:


.. index:: Fim

Fim
---

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1257>`__

Wraps command **3dfim+**

Program to calculate the cross-correlation of
an ideal reference waveform with the measured FMRI
time series for each voxel

For complete details, see the `3dfim+ Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dfim+.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> fim = afni.Fim()
>>> fim.inputs.in_file = 'functional.nii'
>>> fim.inputs.ideal_file= 'seed.1D'
>>> fim.inputs.out_file = 'functional_corr.nii'
>>> fim.inputs.out = 'Correlation'
>>> fim.inputs.fim_thr = 0.0009
>>> res = fim.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        ideal_file: (an existing file name)
                ideal time series file name
        in_file: (an existing file name)
                input file to 3dfim+
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
        fim_thr: (a float)
                fim internal mask threshold value
        ideal_file: (an existing file name)
                ideal time series file name
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dfim+
        out: (a string)
                Flag to output the specified parameter
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Fourier:


.. index:: Fourier

Fourier
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L712>`__

Wraps command **3dFourier**

Program to lowpass and/or highpass each voxel time series in a
dataset, via the FFT

For complete details, see the `3dFourier Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dfourier.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> fourier = afni.Fourier()
>>> fourier.inputs.in_file = 'functional.nii'
>>> fourier.inputs.args = '-retrend'
>>> fourier.inputs.highpass = 0.005
>>> fourier.inputs.lowpass = 0.1
>>> res = fourier.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        highpass: (a float)
                highpass
        in_file: (an existing file name)
                input file to 3dFourier
        lowpass: (a float)
                lowpass
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
        highpass: (a float)
                highpass
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dFourier
        lowpass: (a float)
                lowpass
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Maskave:


.. index:: Maskave

Maskave
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1141>`__

Wraps command **3dmaskave**

Computes average of all voxels in the input dataset
which satisfy the criterion in the options list

For complete details, see the `3dmaskave Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dmaskave.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> maskave = afni.Maskave()
>>> maskave.inputs.in_file = 'functional.nii'
>>> maskave.inputs.mask= 'seed_mask.nii'
>>> maskave.inputs.quiet= True
>>> maskave.cmdline #doctest: +ELLIPSIS
'3dmaskave -mask seed_mask.nii -quiet functional.nii > functional_maskave.1D'
>>> res = maskave.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dmaskave
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
                input file to 3dmaskave
        mask: (an existing file name)
                matrix to align input file
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        quiet: (a boolean)
                matrix to align input file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Merge:


.. index:: Merge

Merge
-----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L635>`__

Wraps command **3dmerge**

Merge or edit volumes using AFNI 3dmerge command

For complete details, see the `3dmerge Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dmerge.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> merge = afni.Merge()
>>> merge.inputs.in_files = ['functional.nii', 'functional2.nii']
>>> merge.inputs.blurfwhm = 4
>>> merge.inputs.doall = True
>>> merge.inputs.out_file = 'e7.nii'
>>> res = merge.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        blurfwhm: (an integer)
                FWHM blur value (mm)
        doall: (a boolean)
                apply options to all sub-bricks in dataset
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_files: (an existing file name)
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.ROIStats:


.. index:: ROIStats

ROIStats
--------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1502>`__

Wraps command **3dROIstats**

Display statistics over masked regions

For complete details, see the `3dROIstats Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dROIstats.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> roistats = afni.ROIStats()
>>> roistats.inputs.in_file = 'functional.nii'
>>> roistats.inputs.mask = 'skeleton_mask.nii.gz'
>>> roistats.inputs.quiet=True
>>> res = roistats.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dROIstats
        terminal_output: ('allatonce', nipype default value: allatonce)
                Control terminal output:`allatonce` - waits till command is finished
                to display output

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
                input file to 3dROIstats
        mask: (an existing file name)
                input mask
        mask_f2short: (a boolean)
                Tells the program to convert a float mask to short integers, by
                simple rounding.
        quiet: (a boolean)
                execute quietly
        terminal_output: ('allatonce', nipype default value: allatonce)
                Control terminal output:`allatonce` - waits till command is finished
                to display output

Outputs::

        stats: (an existing file name)
                output tab separated values file

.. _nipype.interfaces.afni.preprocess.Refit:


.. index:: Refit

Refit
-----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L176>`__

Wraps command **3drefit**

Changes some of the information inside a 3D dataset's header

For complete details, see the `3drefit Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3drefit.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> refit = afni.Refit()
>>> refit.inputs.in_file = 'structural.nii'
>>> refit.inputs.deoblique = True
>>> refit.cmdline
'3drefit -deoblique structural.nii'
>>> res = refit.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3drefit
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        deoblique: (a boolean)
                replace current transformation matrix with cardinal matrix
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3drefit
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        xorigin: (a string)
                x distance for edge voxel offset
        yorigin: (a string)
                y distance for edge voxel offset
        zorigin: (a string)
                z distance for edge voxel offset

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Resample:


.. index:: Resample

Resample
--------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L295>`__

Wraps command **3dresample**

Resample or reorient an image using AFNI 3dresample command

For complete details, see the `3dresample Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dresample.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> resample = afni.Resample()
>>> resample.inputs.in_file = 'functional.nii'
>>> resample.inputs.orientation= 'RPI'
>>> resample.inputs.outputtype = "NIFTI"
>>> resample.cmdline
'3dresample -orient RPI -prefix functional_resample.nii -inset functional.nii'
>>> res = resample.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dresample
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
                input file to 3dresample
        master: (a file name)
                align dataset grid to a reference file
        orientation: (a string)
                new orientation code
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        resample_mode: ('NN' or 'Li' or 'Cu' or 'Bk')
                resampling method from set {'NN', 'Li', 'Cu', 'Bk'}. These are for
                'Nearest Neighbor', 'Linear', 'Cubic' and 'Blocky' interpolation,
                respectively. Default is NN.
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        voxel_size: (a tuple of the form: (a float, a float, a float))
                resample to new dx, dy and dz

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Retroicor:


.. index:: Retroicor

Retroicor
---------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1858>`__

Wraps command **3dretroicor**

Performs Retrospective Image Correction for physiological
motion effects, using a slightly modified version of the
RETROICOR algorithm

The durations of the physiological inputs are assumed to equal
the duration of the dataset. Any constant sampling rate may be
used, but 40 Hz seems to be acceptable. This program's cardiac
peak detection algorithm is rather simplistic, so you might try
using the scanner's cardiac gating output (transform it to a
spike wave if necessary).

This program uses slice timing information embedded in the
dataset to estimate the proper cardiac/respiratory phase for
each slice. It makes sense to run this program before any
program that may destroy the slice timings (e.g. 3dvolreg for
motion correction).

For complete details, see the `3dretroicor Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dretroicor.html>`_

Examples
~~~~~~~~
>>> from nipype.interfaces import afni as afni
>>> ret = afni.Retroicor()
>>> ret.inputs.in_file = 'functional.nii'
>>> ret.inputs.card = 'mask.1D'
>>> ret.inputs.resp = 'resp.1D'
>>> res = ret.run()   # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dretroicor
        out_file: (a file name)
                output image file name
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        card: (an existing file name)
                1D cardiac data file for cardiac correction
        cardphase: (a file name)
                Filename for 1D cardiac phase output
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dretroicor
        order: (an integer)
                The order of the correction (2 is typical)
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        resp: (an existing file name)
                1D respiratory waveform data for correction
        respphase: (a file name)
                Filename for 1D resp phase output
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        threshold: (an integer)
                Threshold for detection of R-wave peaks in input (Make sure it is
                above the background noise level, Try 3/4 or 4/5 times range plus
                minimum)

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.SkullStrip:


.. index:: SkullStrip

SkullStrip
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1178>`__

Wraps command **3dSkullStrip**

A program to extract the brain from surrounding
tissue from MRI T1-weighted images

For complete details, see the `3dSkullStrip Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dSkullStrip.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> skullstrip = afni.SkullStrip()
>>> skullstrip.inputs.in_file = 'functional.nii'
>>> skullstrip.inputs.args = '-o_ply'
>>> res = skullstrip.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dSkullStrip
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
                input file to 3dSkullStrip
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TCat:


.. index:: TCat

TCat
----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1213>`__

Wraps command **3dTcat**

Concatenate sub-bricks from input datasets into
one big 3D+time dataset

For complete details, see the `3dTcat Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTcat.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tcat = afni.TCat()
>>> tcat.inputs.in_files = ['functional.nii', 'functional2.nii']
>>> tcat.inputs.out_file= 'functional_tcat.nii'
>>> tcat.inputs.rlt = '+'
>>> res = tcat.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
                input file to 3dTcat
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
        in_files: (an existing file name)
                input file to 3dTcat
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        rlt: (a string)
                options
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TCorr1D:


.. index:: TCorr1D

TCorr1D
-------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1378>`__

Wraps command **3dTcorr1D**

Computes the correlation coefficient between each voxel time series
in the input 3D+time dataset.
For complete details, see the `3dTcorr1D Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTcorr1D.html>`_

>>> from nipype.interfaces import afni as afni
>>> tcorr1D = afni.TCorr1D()
>>> tcorr1D.inputs.xset= 'u_rc1s1_Template.nii'
>>> tcorr1D.inputs.y_1d = 'seed.1D'
>>> tcorr1D.cmdline
'3dTcorr1D -prefix u_rc1s1_Template_correlation.nii.gz  u_rc1s1_Template.nii  seed.1D'
>>> res = tcorr1D.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        xset: (an existing file name)
                3d+time dataset input
        y_1d: (an existing file name)
                1D time series file input

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
        ktaub: (a boolean)
                Correlation is the Kendall's tau_b correlation coefficient
                mutually_exclusive: pearson, spearman, quadrant
        out_file: (a file name)
                output filename prefix
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        pearson: (a boolean)
                Correlation is the normal Pearson correlation coefficient
                mutually_exclusive: spearman, quadrant, ktaub
        quadrant: (a boolean)
                Correlation is the quadrant correlation coefficient
                mutually_exclusive: pearson, spearman, ktaub
        spearman: (a boolean)
                Correlation is the Spearman (rank) correlation coefficient
                mutually_exclusive: pearson, quadrant, ktaub
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        xset: (an existing file name)
                3d+time dataset input
        y_1d: (an existing file name)
                1D time series file input

Outputs::

        out_file: (an existing file name)
                output file containing correlations

.. _nipype.interfaces.afni.preprocess.TCorrMap:


.. index:: TCorrMap

TCorrMap
--------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1723>`__

Wraps command **3dTcorrMap**

For each voxel time series, computes the correlation between it
and all other voxels, and combines this set of values into the
output dataset(s) in some way.

For complete details, see the `3dTcorrMap Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTcorrMap.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tcm = afni.TCorrMap()
>>> tcm.inputs.in_file = 'functional.nii'
>>> tcm.inputs.mask = 'mask.nii'
>>> tcm.mean_file = '%s_meancorr.nii'
>>> res = tcm.run()   # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        absolute_threshold: (a file name)
                mutually_exclusive: absolute_threshold, var_absolute_threshold,
                 var_absolute_threshold_normalize
        args: (a string)
                Additional parameters to the command
        automask: (a boolean)
        average_expr: (a file name)
                mutually_exclusive: average_expr, average_expr_nonzero, sum_expr
        average_expr_nonzero: (a file name)
                mutually_exclusive: average_expr, average_expr_nonzero, sum_expr
        bandpass: (a tuple of the form: (a float, a float))
        blur_fwhm: (a float)
        correlation_maps: (a file name)
        correlation_maps_masked: (a file name)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        expr: (a string)
        histogram: (a file name)
        histogram_bin_numbers: (an integer)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
        mask: (an existing file name)
        mean_file: (a file name)
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        pmean: (a file name)
        polort: (an integer)
        qmean: (a file name)
        regress_out_timeseries: (a file name)
        seeds: (an existing file name)
                mutually_exclusive: s, e, e, d, s, _, w, i, d, t, h
        seeds_width: (a float)
                mutually_exclusive: s, e, e, d, s
        sum_expr: (a file name)
                mutually_exclusive: average_expr, average_expr_nonzero, sum_expr
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        thresholds: (a list of items which are an integer)
        var_absolute_threshold: (a file name)
                mutually_exclusive: absolute_threshold, var_absolute_threshold,
                 var_absolute_threshold_normalize
        var_absolute_threshold_normalize: (a file name)
                mutually_exclusive: absolute_threshold, var_absolute_threshold,
                 var_absolute_threshold_normalize
        zmean: (a file name)

Outputs::

        absolute_threshold: (a file name)
        average_expr: (a file name)
        average_expr_nonzero: (a file name)
        correlation_maps: (a file name)
        correlation_maps_masked: (a file name)
        histogram: (a file name)
        mean_file: (a file name)
        pmean: (a file name)
        qmean: (a file name)
        sum_expr: (a file name)
        var_absolute_threshold: (a file name)
        var_absolute_threshold_normalize: (a file name)
        zmean: (a file name)

.. _nipype.interfaces.afni.preprocess.TCorrelate:


.. index:: TCorrelate

TCorrelate
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L1307>`__

Wraps command **3dTcorrelate**

Computes the correlation coefficient between corresponding voxel
time series in two input 3D+time datasets 'xset' and 'yset'

For complete details, see the `3dTcorrelate Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTcorrelate.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tcorrelate = afni.TCorrelate()
>>> tcorrelate.inputs.xset= 'u_rc1s1_Template.nii'
>>> tcorrelate.inputs.yset = 'u_rc1s2_Template.nii'
>>> tcorrelate.inputs.out_file = 'functional_tcorrelate.nii.gz'
>>> tcorrelate.inputs.polort = -1
>>> tcorrelate.inputs.pearson = True
>>> res = tcarrelate.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        xset: (an existing file name)
                input xset
        yset: (an existing file name)
                input yset

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
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        pearson: (a boolean)
                Correlation is the normal Pearson correlation coefficient
        polort: (an integer)
                Remove polynomical trend of order m
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        xset: (an existing file name)
                input xset
        yset: (an existing file name)
                input yset

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TShift:


.. index:: TShift

TShift
------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L128>`__

Wraps command **3dTshift**

Shifts voxel time series from input
so that seperate slices are aligned to the same
temporal origin

For complete details, see the `3dTshift Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTshift.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tshift = afni.TShift()
>>> tshift.inputs.in_file = 'functional.nii'
>>> tshift.inputs.tpattern = 'alt+z'
>>> tshift.inputs.tzero = 0.0
>>> tshift.cmdline #doctest:
'3dTshift -prefix functional_tshift -tpattern alt+z -tzero 0.0 functional.nii'
>>> res = tshift.run()   # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dTShift
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
        ignore: (an integer)
                ignore the first set of points specified
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dTShift
        interp: ('Fourier' or 'linear' or 'cubic' or 'quintic' or 'heptic')
                different interpolation methods (see 3dTShift for details) default =
                Fourier
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        rlt: (a boolean)
                Before shifting, remove the mean and linear trend
        rltplus: (a boolean)
                Before shifting, remove the mean and linear trend and later put back
                the mean
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        tpattern: ('alt+z' or 'alt+z2' or 'alt-z' or 'alt-z2' or 'seq+z' or
                 'seq-z')
                use specified slice time pattern rather than one in header
        tr: (a string)
                manually set the TRYou can attach suffix "s" for seconds or "ms" for
                milliseconds.
        tslice: (an integer)
                align each slice to time offset of given slice
                mutually_exclusive: tzero
        tzero: (a float)
                align each slice to given time offset
                mutually_exclusive: tslice

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TStat:


.. index:: TStat

TStat
-----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L395>`__

Wraps command **3dTstat**

Compute voxel-wise statistics using AFNI 3dTstat command

For complete details, see the `3dTstat Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTstat.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tstat = afni.TStat()
>>> tstat.inputs.in_file = 'functional.nii'
>>> tstat.inputs.args= '-mean'
>>> tstat.inputs.out_file = "stats"
>>> tstat.cmdline
'3dTstat -mean -prefix stats functional.nii'
>>> res = tstat.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dTstat
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
                input file to 3dTstat
        mask: (an existing file name)
                mask file
        options: (a string)
                selected statistical output
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.To3D:


.. index:: To3D

To3D
----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L58>`__

Wraps command **to3d**

Create a 3D dataset from 2D image files using AFNI to3d command

For complete details, see the `to3d Documentation
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/to3d.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni
>>> To3D = afni.To3D()
>>> To3D.inputs.datatype = 'float'
>>> To3D.inputs.in_folder = '.'
>>> To3D.inputs.out_file = 'dicomdir.nii'
>>> To3D.inputs.filetype = "anat"
>>> To3D.cmdline #doctest: +ELLIPSIS
'to3d -datum float -anat -prefix dicomdir.nii ./*.dcm'
>>> res = To3D.run() #doctest: +SKIP

Inputs::

        [Mandatory]
        in_folder: (an existing directory name)
                folder with DICOM images to convert
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        assumemosaic: (a boolean)
                assume that Siemens image is mosaic
        datatype: ('short' or 'float' or 'byte' or 'complex')
                set output file datatype
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        filetype: ('spgr' or 'fse' or 'epan' or 'anat' or 'ct' or 'spct' or
                 'pet' or 'mra' or 'bmap' or 'diff' or 'omri' or 'abuc' or 'fim' or
                 'fith' or 'fico' or 'fitt' or 'fift' or 'fizt' or 'fict' or 'fibt'
                 or 'fibn' or 'figt' or 'fipt' or 'fbuc')
                type of datafile being converted
        funcparams: (a string)
                parameters for functional data
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_folder: (an existing directory name)
                folder with DICOM images to convert
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        skipoutliers: (a boolean)
                skip the outliers check
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Volreg:


.. index:: Volreg

Volreg
------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L593>`__

Wraps command **3dvolreg**

Register input volumes to a base volume using AFNI 3dvolreg command

For complete details, see the `3dvolreg Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dvolreg.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> volreg = afni.Volreg()
>>> volreg.inputs.in_file = 'functional.nii'
>>> volreg.inputs.args = '-Fourier -twopass'
>>> volreg.inputs.zpad = 4
>>> volreg.inputs.outputtype = "NIFTI"
>>> volreg.cmdline #doctest: +ELLIPSIS
'3dvolreg -Fourier -twopass -1Dfile functional.1D -prefix functional_volreg.nii -zpad 4 -maxdisp1D functional_md.1D functional.nii'
>>> res = volreg.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dvolreg
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        basefile: (an existing file name)
                base file for registration
        copyorigin: (a boolean)
                copy base file origin coords to output
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dvolreg
        md1d_file: (a file name)
                max displacement output file
        oned_file: (a file name)
                1D movement parameters output file
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        timeshift: (a boolean)
                time shift to mean slice time offset
        verbose: (a boolean)
                more detailed description of the process
        zpad: (an integer)
                Zeropad around the edges by 'n' voxels during rotations

Outputs::

        md1d_file: (an existing file name)
                max displacement info file
        oned_file: (an existing file name)
                movement parameters info file
        out_file: (an existing file name)
                registered file

.. _nipype.interfaces.afni.preprocess.Warp:


.. index:: Warp

Warp
----

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L243>`__

Wraps command **3dWarp**

Use 3dWarp for spatially transforming a dataset

For complete details, see the `3dWarp Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dWarp.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> warp = afni.Warp()
>>> warp.inputs.in_file = 'structural.nii'
>>> warp.inputs.deoblique = True
>>> warp.inputs.out_file = "trans.nii.gz"
>>> warp.cmdline
'3dWarp -deoblique -prefix trans.nii.gz structural.nii'
>>> res = warp.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dWarp
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        deoblique: (a boolean)
                transform dataset from oblique to cardinal
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        gridset: (an existing file name)
                copy grid of specified dataset
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input file to 3dWarp
        interp: ('linear' or 'cubic' or 'NN' or 'quintic')
                spatial interpolation methods [default = linear]
        matparent: (an existing file name)
                apply transformation from 3dWarpDrive
        mni2tta: (a boolean)
                transform dataset from MNI152 to Talaraich
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        tta2mni: (a boolean)
                transform dataset from Talairach to MNI152
        zpad: (an integer)
                pad input dataset with N planes of zero on all sides.

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.ZCutUp:


.. index:: ZCutUp

ZCutUp
------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/afni/preprocess.py#L860>`__

Wraps command **3dZcutup**

Cut z-slices from a volume using AFNI 3dZcutup command

For complete details, see the `3dZcutup Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dZcutup.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> zcutup = afni.ZCutUp()
>>> zcutup.inputs.in_file = 'functional.nii'
>>> zcutup.inputs.out_file = 'functional_zcutup.nii'
>>> zcutup.inputs.keep= '0 10'
>>> res = zcutup.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dZcutup
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
                input file to 3dZcutup
        keep: (a string)
                slice range to keep in output
        out_file: (a file name)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file
