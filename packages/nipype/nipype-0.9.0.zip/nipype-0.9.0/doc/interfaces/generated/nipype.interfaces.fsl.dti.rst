.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.fsl.dti
==================


.. _nipype.interfaces.fsl.dti.BEDPOSTX:


.. index:: BEDPOSTX

BEDPOSTX
--------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L147>`__

Wraps command **bedpostx**

Deprecated! Please use create_bedpostx_pipeline instead

Example
~~~~~~~

>>> from nipype.interfaces import fsl
>>> bedp = fsl.BEDPOSTX(bpx_directory='subjdir', bvecs='bvecs', bvals='bvals', dwi='diffusion.nii',     mask='mask.nii', fibres=1)
>>> bedp.cmdline
'bedpostx subjdir -n 1'

Inputs::

        [Mandatory]
        bvals: (an existing file name)
                b values file
        bvecs: (an existing file name)
                b vectors file
        dwi: (an existing file name)
                diffusion weighted image data file
        mask: (an existing file name)
                bet binary mask file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        bpx_directory: (a directory name, nipype default value: bedpostx)
                the name for this subjects bedpostx folder
        burn_period: (an integer)
                burnin period
        bvals: (an existing file name)
                b values file
        bvecs: (an existing file name)
                b vectors file
        dwi: (an existing file name)
                diffusion weighted image data file
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        fibres: (an integer)
                number of fibres per voxel
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        jumps: (an integer)
                number of jumps
        mask: (an existing file name)
                bet binary mask file
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        sampling: (an integer)
                sample every
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        weight: (a float)
                ARD weight, more weight means less secondary fibres per voxel

Outputs::

        bpx_out_directory: (an existing directory name)
                path/name of directory with all bedpostx output files for this
                subject
        dyads: (a list of items which are an existing file name)
                a list of path/name of mean of PDD distribution in vector form
        mean_fsamples: (a list of items which are an existing file name)
                a list of path/name of 3D volume with mean of distribution on f
                anisotropy
        mean_phsamples: (a list of items which are an existing file name)
                a list of path/name of 3D volume with mean of distribution on phi
        mean_thsamples: (a list of items which are an existing file name)
                a list of path/name of 3D volume with mean of distribution on theta
        merged_fsamples: (a list of items which are an existing file name)
                a list of path/name of 4D volume with samples from the distribution
                on anisotropic volume fraction
        merged_phsamples: (a list of items which are an existing file name)
                a list of path/name of file with samples from the distribution on
                phi
        merged_thsamples: (a list of items which are an existing file name)
                a list of path/name of 4D volume with samples from the distribution
                on theta
        xfms_directory: (an existing directory name)
                path/name of directory with the tranformation matrices

.. _nipype.interfaces.fsl.dti.DTIFit:


.. index:: DTIFit

DTIFit
------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L70>`__

Wraps command **dtifit**

Use FSL  dtifit command for fitting a diffusion tensor model at each
voxel

Example
~~~~~~~

>>> from nipype.interfaces import fsl
>>> dti = fsl.DTIFit()
>>> dti.inputs.dwi = 'diffusion.nii'
>>> dti.inputs.bvecs = 'bvecs'
>>> dti.inputs.bvals = 'bvals'
>>> dti.inputs.base_name = 'TP'
>>> dti.inputs.mask = 'mask.nii'
>>> dti.cmdline
'dtifit -k diffusion.nii -o TP -m mask.nii -r bvecs -b bvals'

Inputs::

        [Mandatory]
        bvals: (an existing file name)
                b values file
        bvecs: (an existing file name)
                b vectors file
        dwi: (an existing file name)
                diffusion weighted image data file
        mask: (an existing file name)
                bet binary mask file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        base_name: (a string, nipype default value: dtifit_)
                base_name that all output files will start with
        bvals: (an existing file name)
                b values file
        bvecs: (an existing file name)
                b vectors file
        cni: (an existing file name)
                input counfound regressors
        dwi: (an existing file name)
                diffusion weighted image data file
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        little_bit: (a boolean)
                only process small area of brain
        mask: (an existing file name)
                bet binary mask file
        max_x: (an integer)
                max x
        max_y: (an integer)
                max y
        max_z: (an integer)
                max z
        min_x: (an integer)
                min x
        min_y: (an integer)
                min y
        min_z: (an integer)
                min z
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        save_tensor: (a boolean)
                save the elements of the tensor
        sse: (a boolean)
                output sum of squared errors
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        FA: (an existing file name)
                path/name of file with the fractional anisotropy
        L1: (an existing file name)
                path/name of file with the 1st eigenvalue
        L2: (an existing file name)
                path/name of file with the 2nd eigenvalue
        L3: (an existing file name)
                path/name of file with the 3rd eigenvalue
        MD: (an existing file name)
                path/name of file with the mean diffusivity
        MO: (an existing file name)
                path/name of file with the mode of anisotropy
        S0: (an existing file name)
                path/name of file with the raw T2 signal with no diffusion weighting
        V1: (an existing file name)
                path/name of file with the 1st eigenvector
        V2: (an existing file name)
                path/name of file with the 2nd eigenvector
        V3: (an existing file name)
                path/name of file with the 3rd eigenvector
        tensor: (an existing file name)
                path/name of file with the 4D tensor volume

.. _nipype.interfaces.fsl.dti.DistanceMap:


.. index:: DistanceMap

DistanceMap
-----------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L727>`__

Wraps command **distancemap**

Use FSL's distancemap to generate a map of the distance to the nearest nonzero voxel.

Example
~~~~~~~

>>> import nipype.interfaces.fsl as fsl
>>> mapper = fsl.DistanceMap()
>>> mapper.inputs.in_file = "skeleton_mask.nii.gz"
>>> mapper.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to calculate distance values for
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        distance_map: (a file name)
                distance map to write
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                image to calculate distance values for
        invert_input: (a boolean)
                invert input image
        local_max_file: (a boolean or a file name)
                write an image of the local maxima
        mask_file: (an existing file name)
                binary mask to contrain calculations
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        distance_map: (an existing file name)
                value is distance to nearest nonzero voxels
        local_max_file: (a file name)
                image of local maxima

.. _nipype.interfaces.fsl.dti.FindTheBiggest:


.. index:: FindTheBiggest

FindTheBiggest
--------------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L571>`__

Wraps command **find_the_biggest**

Use FSL find_the_biggest for performing hard segmentation on
the outputs of connectivity-based thresholding in probtrack.
For complete details, see the `FDT
Documentation. <http://www.fmrib.ox.ac.uk/fsl/fdt/fdt_biggest.html>`_

Example
~~~~~~~

>>> from nipype.interfaces import fsl
>>> ldir = ['seeds_to_M1.nii', 'seeds_to_M2.nii']
>>> fBig = fsl.FindTheBiggest(in_files=ldir, out_file='biggestSegmentation')
>>> fBig.cmdline
'find_the_biggest seeds_to_M1.nii seeds_to_M2.nii biggestSegmentation'

Inputs::

        [Mandatory]
        in_files: (a list of items which are an existing file name)
                a list of input volumes or a singleMatrixFile
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
        in_files: (a list of items which are an existing file name)
                a list of input volumes or a singleMatrixFile
        out_file: (a file name)
                file with the resulting segmentation
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                output file indexed in order of input files

.. _nipype.interfaces.fsl.dti.MakeDyadicVectors:


.. index:: MakeDyadicVectors

MakeDyadicVectors
-----------------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L874>`__

Wraps command **make_dyadic_vectors**

Create vector volume representing mean principal diffusion direction
and its uncertainty (dispersion)

Inputs::

        [Mandatory]
        phi_vol: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        theta_vol: (an existing file name)

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
        mask: (an existing file name)
        output: (a file name, nipype default value: dyads)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        perc: (a float)
                the {perc}% angle of the output cone of uncertainty (output will be
                in degrees)
        phi_vol: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        theta_vol: (an existing file name)

Outputs::

        dispersion: (an existing file name)
        dyads: (an existing file name)

.. _nipype.interfaces.fsl.dti.ProbTrackX:


.. index:: ProbTrackX

ProbTrackX
----------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L324>`__

Wraps command **probtrackx**

Use FSL  probtrackx for tractography on bedpostx results

Examples
~~~~~~~~

>>> from nipype.interfaces import fsl
>>> pbx = fsl.ProbTrackX(samples_base_name='merged', mask='mask.nii',     seed='MASK_average_thal_right.nii', mode='seedmask',     xfm='trans.mat', n_samples=3, n_steps=10, force_dir=True, opd=True, os2t=True,     target_masks = ['targets_MASK1.nii', 'targets_MASK2.nii'],     thsamples='merged_thsamples.nii', fsamples='merged_fsamples.nii', phsamples='merged_phsamples.nii',     out_dir='.')
>>> pbx.cmdline
'probtrackx --forcedir -m mask.nii --mode=seedmask --nsamples=3 --nsteps=10 --opd --os2t --dir=. --samples=merged --seed=MASK_average_thal_right.nii --targetmasks=targets.txt --xfm=trans.mat'

Inputs::

        [Mandatory]
        fsamples: (an existing file name)
        mask: (an existing file name)
                bet binary mask file in diffusion space
        phsamples: (an existing file name)
        seed: (an existing file name or a list of items which are an existing
                 file name or a list of items which are a list of from 3 to 3 items
                 which are an integer)
                seed volume(s), or voxel(s)or freesurfer label file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        thsamples: (an existing file name)

        [Optional]
        args: (a string)
                Additional parameters to the command
        avoid_mp: (an existing file name)
                reject pathways passing through locations given by this mask
        c_thresh: (a float)
                curvature threshold - default=0.2
        correct_path_distribution: (a boolean)
                correct path distribution for the length of the pathways
        dist_thresh: (a float)
                discards samples shorter than this threshold (in mm - default=0)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        fibst: (an integer)
                force a starting fibre for tracking - default=1, i.e. first fibre
                orientation. Only works if randfib==0
        force_dir: (a boolean, nipype default value: True)
                use the actual directory name given - i.e. do not add + to make a
                new directory
        fsamples: (an existing file name)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        inv_xfm: (a file name)
                transformation matrix taking DTI space to seed space (compulsory
                when using a warp_field for seeds_to_dti)
        loop_check: (a boolean)
                perform loop_checks on paths - slower, but allows lower curvature
                threshold
        mask: (an existing file name)
                bet binary mask file in diffusion space
        mask2: (an existing file name)
                second bet binary mask (in diffusion space) in twomask_symm mode
        mesh: (an existing file name)
                Freesurfer-type surface descriptor (in ascii format)
        mod_euler: (a boolean)
                use modified euler streamlining
        mode: ('simple' or 'two_mask_symm' or 'seedmask')
                options: simple (single seed voxel), seedmask (mask of seed voxels),
                twomask_symm (two bet binary masks)
        n_samples: (an integer, nipype default value: 5000)
                number of samples - default=5000
        n_steps: (an integer)
                number of steps per sample - default=2000
        network: (a boolean)
                activate network mode - only keep paths going through at least one
                seed mask (required if multiple seed masks)
        opd: (a boolean, nipype default value: True)
                outputs path distributions
        os2t: (a boolean)
                Outputs seeds to targets
        out_dir: (an existing directory name)
                directory to put the final volumes in
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        phsamples: (an existing file name)
        rand_fib: (0 or 1 or 2 or 3)
                options: 0 - default, 1 - to randomly sample initial fibres (with f
                > fibthresh), 2 - to sample in proportion fibres (with f>fibthresh)
                to f, 3 - to sample ALL populations at random (even if f<fibthresh)
        random_seed: (a boolean)
                random seed
        s2tastext: (a boolean)
                output seed-to-target counts as a text file (useful when seeding
                from a mesh)
        sample_random_points: (a boolean)
                sample random points within seed voxels
        samples_base_name: (a string, nipype default value: merged)
                the rootname/base_name for samples files
        seed: (an existing file name or a list of items which are an existing
                 file name or a list of items which are a list of from 3 to 3 items
                 which are an integer)
                seed volume(s), or voxel(s)or freesurfer label file
        seed_ref: (an existing file name)
                reference vol to define seed space in simple mode - diffusion space
                assumed if absent
        step_length: (a float)
                step_length in mm - default=0.5
        stop_mask: (an existing file name)
                stop tracking at locations given by this mask file
        target_masks: (a file name)
                list of target masks - required for seeds_to_targets classification
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        thsamples: (an existing file name)
        use_anisotropy: (a boolean)
                use anisotropy to constrain tracking
        verbose: (0 or 1 or 2)
                Verbose level, [0-2].Level 2 is required to output particle files.
        waypoints: (an existing file name)
                waypoint mask or ascii list of waypoint masks - only keep paths
                going through ALL the masks
        xfm: (an existing file name)
                transformation matrix taking seed space to DTI space (either FLIRT
                matrix or FNIRT warp_field) - default is identity

Outputs::

        fdt_paths: (an existing file name)
                path/name of a 3D image file containing the output connectivity
                distribution to the seed mask
        log: (an existing file name)
                path/name of a text record of the command that was run
        particle_files: (a list of items which are an existing file name)
                Files describing all of the tract samples. Generated only if verbose
                is set to 2
        targets: (a list of items which are an existing file name)
                a list with all generated seeds_to_target files
        way_total: (an existing file name)
                path/name of a text file containing a single number corresponding to
                the total number of generated tracts that have not been rejected by
                inclusion/exclusion mask criteria

.. _nipype.interfaces.fsl.dti.ProjThresh:


.. index:: ProjThresh

ProjThresh
----------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L528>`__

Wraps command **proj_thresh**

Use FSL proj_thresh for thresholding some outputs of probtrack
For complete details, see the FDT Documentation
<http://www.fmrib.ox.ac.uk/fsl/fdt/fdt_thresh.html>

Example
~~~~~~~

>>> from nipype.interfaces import fsl
>>> ldir = ['seeds_to_M1.nii', 'seeds_to_M2.nii']
>>> pThresh = fsl.ProjThresh(in_files=ldir, threshold=3)
>>> pThresh.cmdline
'proj_thresh seeds_to_M1.nii seeds_to_M2.nii 3'

Inputs::

        [Mandatory]
        in_files: (a list of items which are an existing file name)
                a list of input volumes
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        threshold: (an integer)
                threshold indicating minimum number of seed voxels entering this
                mask region

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
        in_files: (a list of items which are an existing file name)
                a list of input volumes
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        threshold: (an integer)
                threshold indicating minimum number of seed voxels entering this
                mask region

Outputs::

        out_files: (a list of items which are an existing file name)
                path/name of output volume after thresholding

.. _nipype.interfaces.fsl.dti.TractSkeleton:


.. index:: TractSkeleton

TractSkeleton
-------------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L639>`__

Wraps command **tbss_skeleton**

Use FSL's tbss_skeleton to skeletonise an FA image or project arbitrary values onto a skeleton.

There are two ways to use this interface.  To create a skeleton from an FA image, just
supply the ``in_file`` and set ``skeleton_file`` to True (or specify a skeleton filename.
To project values onto a skeleton, you must set ``project_data`` to True, and then also
supply values for ``threshold``, ``distance_map``, and ``data_file``. The ``search_mask_file``
and ``use_cingulum_mask`` inputs are also used in data projection, but ``use_cingulum_mask``
is set to True by default.  This mask controls where the projection algorithm searches
within a circular space around a tract, rather than in a single perpindicular direction.

Example
~~~~~~~

>>> import nipype.interfaces.fsl as fsl
>>> skeletor = fsl.TractSkeleton()
>>> skeletor.inputs.in_file = "all_FA.nii.gz"
>>> skeletor.inputs.skeleton_file = True
>>> skeletor.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input image (typcially mean FA volume)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        alt_data_file: (an existing file name)
                4D non-FA data to project onto skeleton
        alt_skeleton: (an existing file name)
                alternate skeleton to use
        args: (a string)
                Additional parameters to the command
        data_file: (an existing file name)
                4D data to project onto skeleton (usually FA)
        distance_map: (an existing file name)
                distance map image
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                input image (typcially mean FA volume)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        project_data: (a boolean)
                project data onto skeleton
                requires: threshold, distance_map, data_file
        projected_data: (a file name)
                input data projected onto skeleton
        search_mask_file: (an existing file name)
                mask in which to use alternate search rule
                mutually_exclusive: use_cingulum_mask
        skeleton_file: (a boolean or a file name)
                write out skeleton image
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        threshold: (a float)
                skeleton threshold value
        use_cingulum_mask: (a boolean, nipype default value: True)
                perform alternate search using built-in cingulum mask
                mutually_exclusive: search_mask_file

Outputs::

        projected_data: (a file name)
                input data projected onto skeleton
        skeleton_file: (a file name)
                tract skeleton image

.. _nipype.interfaces.fsl.dti.VecReg:


.. index:: VecReg

VecReg
------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L469>`__

Wraps command **vecreg**

Use FSL vecreg for registering vector data
For complete details, see the FDT Documentation
<http://www.fmrib.ox.ac.uk/fsl/fdt/fdt_vecreg.html>

Example
~~~~~~~

>>> from nipype.interfaces import fsl
>>> vreg = fsl.VecReg(in_file='diffusion.nii',                  affine_mat='trans.mat',                  ref_vol='mni.nii',                  out_file='diffusion_vreg.nii')
>>> vreg.cmdline
'vecreg -t trans.mat -i diffusion.nii -o diffusion_vreg.nii -r mni.nii'

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                filename for input vector or tensor field
        ref_vol: (an existing file name)
                filename for reference (target) volume
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        affine_mat: (an existing file name)
                filename for affine transformation matrix
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
                filename for input vector or tensor field
        interpolation: ('nearestneighbour' or 'trilinear' or 'sinc' or
                 'spline')
                interpolation method : nearestneighbour, trilinear (default), sinc
                or spline
        mask: (an existing file name)
                brain mask in input space
        out_file: (a file name)
                filename for output registered vector or tensor field
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        ref_mask: (an existing file name)
                brain mask in output space (useful for speed up of nonlinear reg)
        ref_vol: (an existing file name)
                filename for reference (target) volume
        rotation_mat: (an existing file name)
                filename for secondary affine matrixif set, this will be used for
                the rotation of the vector/tensor field
        rotation_warp: (an existing file name)
                filename for secondary warp fieldif set, this will be used for the
                rotation of the vector/tensor field
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        warp_field: (an existing file name)
                filename for 4D warp field for nonlinear registration

Outputs::

        out_file: (an existing file name)
                path/name of filename for the registered vector or tensor field

.. _nipype.interfaces.fsl.dti.XFibres:


.. index:: XFibres

XFibres
-------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/dti.py#L824>`__

Wraps command **xfibres**

Perform model parameters estimation for local (voxelwise) diffusion parameters

Inputs::

        [Mandatory]
        bvals: (an existing file name)
        bvecs: (an existing file name)
        dwi: (an existing file name)
        mask: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        all_ard: (a boolean)
                Turn ARD on on all fibres
                mutually_exclusive: no_ard, all_ard
        args: (a string)
                Additional parameters to the command
        burn_in: (an integer >= 0)
                Total num of jumps at start of MCMC to be discarded
        burn_in_no_ard: (an integer >= 0)
                num of burnin jumps before the ard is imposed
        bvals: (an existing file name)
        bvecs: (an existing file name)
        dwi: (an existing file name)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        force_dir: (a boolean, nipype default value: True)
                use the actual directory name given - i.e. do not add + to make a
                new directory
        fudge: (an integer)
                ARD fudge factor
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        logdir: (a directory name, nipype default value: logdir)
        mask: (an existing file name)
        model: (an integer)
                Which model to use. 1=mono-exponential (default and required for
                single shell). 2=continous exponential (for multi-shell experiments)
        n_fibres: (an integer >= 1)
                Maximum nukmber of fibres to fit in each voxel
        n_jumps: (an integer >= 1)
                Num of jumps to be made by MCMC
        no_ard: (a boolean)
                Turn ARD off on all fibres
                mutually_exclusive: no_ard, all_ard
        no_spat: (a boolean)
                Initialise with tensor, not spatially
                mutually_exclusive: no_spat, non_linear
        non_linear: (a boolean)
                Initialise with nonlinear fitting
                mutually_exclusive: no_spat, non_linear
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        sample_every: (an integer >= 0)
                Num of jumps for each sample (MCMC)
        seed: (an integer)
                seed for pseudo random number generator
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        update_proposal_every: (an integer >= 1)
                Num of jumps for each update to the proposal density std (MCMC)

Outputs::

        dyads: (an existing file name)
                Mean of PDD distribution in vector form.
        fsamples: (an existing file name)
                Samples from the distribution on anisotropic volume fraction
        mean_S0samples: (an existing file name)
                Samples from S0 distribution
        mean_dsamples: (an existing file name)
                Mean of distribution on diffusivity d
        mean_fsamples: (an existing file name)
                Mean of distribution on f anisotropy
        phsamples: (an existing file name)
                Samples from the distribution on phi
        thsamples: (an existing file name)
                Samples from the distribution on theta
