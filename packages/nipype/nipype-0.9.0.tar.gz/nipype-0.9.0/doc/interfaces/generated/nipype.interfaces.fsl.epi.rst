.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.fsl.epi
==================


.. _nipype.interfaces.fsl.epi.ApplyTOPUP:


.. index:: ApplyTOPUP

ApplyTOPUP
----------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L251>`__

Wraps command **applytopup**

Interface for FSL topup, a tool for estimating and correcting susceptibility induced distortions.
`General reference <http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup/ApplytopupUsersGuide>`_
and `use example <http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup/ExampleTopupFollowedByApplytopup>`_.


Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import ApplyTOPUP
>>> applytopup = ApplyTOPUP()
>>> applytopup.inputs.in_files = [ "epi.nii", "epi_rev.nii" ]
>>> applytopup.inputs.encoding_file = "topup_encoding.txt"
>>> applytopup.inputs.in_index = [ 1,2 ]
>>> applytopup.inputs.in_topup = "my_topup_results"
>>> applytopup.cmdline #doctest: +ELLIPSIS
'applytopup --datain=topup_encoding.txt --imain=epi.nii,epi_rev.nii --inindex=1,2 --topup=my_topup_results --out=.../nipypeatu'
>>> res = applytopup.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        encoding_file: (an existing file name)
                name of text file with PE directions/times
        in_files: (an existing file name)
                name of 4D file with images
        in_index: (a list of items which are any value)
                comma separated list of indicies into --datain of the input image
                (to be corrected)
        in_topup: (a file name)
                basename of field/movements (from topup)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        datatype: ('char' or 'short' or 'int' or 'float' or 'double')
                force output data type
        encoding_file: (an existing file name)
                name of text file with PE directions/times
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_files: (an existing file name)
                name of 4D file with images
        in_index: (a list of items which are any value)
                comma separated list of indicies into --datain of the input image
                (to be corrected)
        in_topup: (a file name)
                basename of field/movements (from topup)
        interp: ('trilinear' or 'spline')
                interpolation method
        method: ('jac' or 'lsr')
                use jacobian modulation (jac) or least-squares resampling (lsr)
        out_base: (a file name)
                basename for output (warped) image
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_corrected: (an existing file name)
                name of 4D image file with unwarped images

.. _nipype.interfaces.fsl.epi.EPIDeWarp:


.. index:: EPIDeWarp

EPIDeWarp
---------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L415>`__

Wraps command **epidewarp.fsl**

Wraps fieldmap unwarping script from Freesurfer's epidewarp.fsl_

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import EPIDeWarp
>>> dewarp = EPIDeWarp()
>>> dewarp.inputs.epi_file = "functional.nii"
>>> dewarp.inputs.mag_file = "magnitude.nii"
>>> dewarp.inputs.dph_file = "phase.nii"
>>> dewarp.inputs.output_type = "NIFTI_GZ"
>>> dewarp.cmdline #doctest: +ELLIPSIS
'epidewarp.fsl --mag magnitude.nii --dph phase.nii --epi functional.nii --esp 0.58 --exfdw .../exfdw.nii.gz --nocleanup --sigma 2 --tediff 2.46 --tmpdir .../temp --vsm .../vsm.nii.gz'
>>> res = dewarp.run() # doctest: +SKIP

References
~~~~~~~~~~
_epidewarp.fsl: http://surfer.nmr.mgh.harvard.edu/fswiki/epidewarp.fsl

Inputs::

        [Mandatory]
        dph_file: (an existing file name)
                Phase file assumed to be scaled from 0 to 4095
        mag_file: (an existing file name)
                Magnitude file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        cleanup: (a boolean)
                cleanup
        dph_file: (an existing file name)
                Phase file assumed to be scaled from 0 to 4095
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        epi_file: (an existing file name)
                EPI volume to unwarp
        epidw: (a string)
                dewarped epi volume
        esp: (a float, nipype default value: 0.58)
                EPI echo spacing
        exf_file: (an existing file name)
                example func volume (or use epi)
        exfdw: (a string)
                dewarped example func volume
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        mag_file: (an existing file name)
                Magnitude file
        nocleanup: (a boolean, nipype default value: True)
                no cleanup
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        sigma: (an integer, nipype default value: 2)
                2D spatial gaussing smoothing stdev (default = 2mm)
        tediff: (a float, nipype default value: 2.46)
                difference in B0 field map TEs
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        tmpdir: (a string)
                tmpdir
        vsm: (a string)
                voxel shift map

Outputs::

        exf_mask: (a file name)
                Mask from example functional volume
        exfdw: (a file name)
                dewarped functional volume example
        unwarped_file: (a file name)
                unwarped epi file
        vsm_file: (a file name)
                voxel shift map

.. _nipype.interfaces.fsl.epi.Eddy:


.. index:: Eddy

Eddy
----

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L330>`__

Wraps command **eddy**

Interface for FSL eddy, a tool for estimating and correcting eddy currents induced distortions.
`User guide <http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Eddy/UsersGuide>`_ and
`more info regarding acqp file <http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/Faq#How_do_I_know_what_to_put_into_my_--acqp_file>`_.

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import Eddy
>>> eddy = Eddy()
>>> eddy.inputs.in_file = 'epi.nii'
>>> eddy.inputs.in_mask  = 'epi_mask.nii'
>>> eddy.inputs.in_index = 'epi_index.txt'
>>> eddy.inputs.in_acqp  = 'epi_acqp.txt'
>>> eddy.inputs.in_bvec  = 'bvecs.scheme'
>>> eddy.inputs.in_bval  = 'bvals.scheme'
>>> eddy.cmdline #doctest: +ELLIPSIS
'eddy --acqp=epi_acqp.txt --bvals=bvals.scheme --bvecs=bvecs.scheme --imain=epi.nii --index=epi_index.txt --mask=epi_mask.nii --out=.../eddy_corrected'
>>> res = eddy.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_acqp: (an existing file name)
                File containing acquisition parameters
        in_bval: (an existing file name)
                File containing the b-values for all volumes in --imain
        in_bvec: (an existing file name)
                File containing the b-vectors for all volumes in --imain
        in_file: (an existing file name)
                File containing all the images to estimate distortions for
        in_index: (an existing file name)
                File containing indices for all volumes in --imain into --acqp and
                --topup
        in_mask: (an existing file name)
                Mask to indicate brain
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
        flm: ('linear' or 'quadratic' or 'cubic')
                First level EC model
        fwhm: (a float)
                FWHM for conditioning filter when estimating the parameters
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_acqp: (an existing file name)
                File containing acquisition parameters
        in_bval: (an existing file name)
                File containing the b-values for all volumes in --imain
        in_bvec: (an existing file name)
                File containing the b-vectors for all volumes in --imain
        in_file: (an existing file name)
                File containing all the images to estimate distortions for
        in_index: (an existing file name)
                File containing indices for all volumes in --imain into --acqp and
                --topup
        in_mask: (an existing file name)
                Mask to indicate brain
        in_topup: (an existing file name)
                Base name for output files from topup
        method: ('jac' or 'lsr')
                Final resampling method (jacobian/least squeares)
        niter: (an integer)
                Number of iterations
        out_base: (a file name)
                basename for output (warped) image
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        repol: (a boolean)
                Detect and replace outlier slices
        session: (an existing file name)
                File containing session indices for all volumes in --imain
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_corrected: (an existing file name)
                4D image file containing all the corrected volumes
        out_parameter: (an existing file name)
                text file with parameters definining the field and movement for each
                scan

.. _nipype.interfaces.fsl.epi.EddyCorrect:


.. index:: EddyCorrect

EddyCorrect
-----------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L546>`__

Wraps command **eddy_correct**

Deprecated! Please use create_eddy_correct_pipeline instead

Example
~~~~~~~

>>> from nipype.interfaces.fsl import EddyCorrect
>>> eddyc = EddyCorrect(in_file='diffusion.nii', out_file="diffusion_edc.nii", ref_num=0)
>>> eddyc.cmdline
'eddy_correct diffusion.nii diffusion_edc.nii 0'

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                4D input file
        ref_num: (an integer)
                reference number
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
                4D input file
        out_file: (a file name)
                4D output file
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        ref_num: (an integer)
                reference number
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        eddy_corrected: (an existing file name)
                path/name of 4D eddy corrected output file

.. _nipype.interfaces.fsl.epi.PrepareFieldmap:


.. index:: PrepareFieldmap

PrepareFieldmap
---------------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L49>`__

Wraps command **fsl_prepare_fieldmap**

Interface for the fsl_prepare_fieldmap script (FSL 5.0)

Prepares a fieldmap suitable for FEAT from SIEMENS data - saves output in rad/s format
e.g. fsl_prepare_fieldmap SIEMENS images_3_gre_field_mapping images_4_gre_field_mapping fmap_rads 2.65


Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import PrepareFieldmap
>>> prepare = PrepareFieldmap()
>>> prepare.inputs.in_phase = "phase.nii"
>>> prepare.inputs.in_magnitude = "magnitude.nii"
>>> prepare.inputs.output_type = "NIFTI_GZ"
>>> prepare.cmdline #doctest: +ELLIPSIS
'fsl_prepare_fieldmap SIEMENS phase.nii magnitude.nii .../phase_fslprepared.nii.gz 2.460000'
>>> res = prepare.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        delta_TE: (a float, nipype default value: 2.46)
                echo time difference of the fielmap sequence in ms. (usually 2.46ms
                in Siemens)
        in_magnitude: (an existing file name)
                Magnitude difference map, brain extracted
        in_phase: (an existing file name)
                Phase difference map, in SIEMENS format range from 0-4096 or 0-8192
                ~
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        delta_TE: (a float, nipype default value: 2.46)
                echo time difference of the fielmap sequence in ms. (usually 2.46ms
                in Siemens)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_magnitude: (an existing file name)
                Magnitude difference map, brain extracted
        in_phase: (an existing file name)
                Phase difference map, in SIEMENS format range from 0-4096 or 0-8192
                ~
        nocheck: (a boolean, nipype default value: False)
                do not perform sanity checks for image size/range/dimensions
        out_fieldmap: (a file name)
                output name for prepared fieldmap
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        scanner: (a string, nipype default value: SIEMENS)
                must be SIEMENS
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_fieldmap: (an existing file name)
                output name for prepared fieldmap

.. _nipype.interfaces.fsl.epi.SigLoss:


.. index:: SigLoss

SigLoss
-------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L504>`__

Wraps command **sigloss**

Estimates signal loss from a field map (in rad/s)

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import SigLoss
>>> sigloss = SigLoss()
>>> sigloss.inputs.in_file = "phase.nii"
>>> sigloss.inputs.echo_time = 0.03
>>> sigloss.inputs.output_type = "NIFTI_GZ"
>>> sigloss.cmdline #doctest: +ELLIPSIS
'sigloss --te=0.030000 -i phase.nii -s .../phase_sigloss.nii.gz'
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

.. _nipype.interfaces.fsl.epi.TOPUP:


.. index:: TOPUP

TOPUP
-----

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/fsl/epi.py#L143>`__

Wraps command **topup**

Interface for FSL topup, a tool for estimating and correcting susceptibility induced distortions
Reference: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TOPUP
Example: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup/ExampleTopupFollowedByApplytopup

topup --imain=<some 4D image> --datain=<text file> --config=<text file with parameters> --coutname=my_field


Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import TOPUP
>>> topup = TOPUP()
>>> topup.inputs.in_file = "b0_b0rev.nii"
>>> topup.inputs.encoding_file = "topup_encoding.txt"
>>> topup.cmdline #doctest: +ELLIPSIS
'topup --config=b02b0.cnf --datain=topup_encoding.txt --imain=b0_b0rev.nii --out=.../nipypetu'
>>> res = topup.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                name of 4D file with images
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        config: (a string, nipype default value: b02b0.cnf)
                Name of config file specifying command line arguments
        encoding_direction: ('y' or 'x' or 'z' or 'x-' or 'y-' or 'z-')
                encoding direction for automatic generation of encoding_file
        encoding_file: (an existing file name)
                name of text file with PE directions/times
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        estmov: (1 or 0)
                estimate movements if set
        fwhm: (a float)
                FWHM (in mm) of gaussian smoothing kernel
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                name of 4D file with images
        interp: ('spline' or 'linear')
                Image interpolation model, linear or spline.
        max_iter: (an integer)
                max # of non-linear iterations
        minmet: (0 or 1)
                Minimisation method 0=Levenberg-Marquardt, 1=Scaled Conjugate
                Gradient
        numprec: ('double' or 'float')
                Precision for representing Hessian, double or float.
        out_base: (a file name)
                base-name of output files (spline coefficients (Hz) and movement
                parameters)
        out_corrected: (a file name)
                name of 4D image file with unwarped images
        out_field: (a file name)
                name of image file with field (Hz)
        out_logfile: (a file name)
                name of log-file
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        readout_times: (a list of items which are a float)
                readout times (dwell times by # phase-encode steps minus 1)
        regrid: (1 or 0)
                If set (=1), the calculations are done in a different grid
        scale: (0 or 1)
                If set (=1), the images are individually scaled to a common mean
        splineorder: (an integer)
                order of spline, 2->Qadratic spline, 3->Cubic spline
        subsamp: (an integer)
                sub-sampling scheme, default 1
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        warp_res: (a float)
                (approximate) resolution (in mm) of warp basis for the different
                sub-sampling levels

Outputs::

        out_corrected: (a file name)
                name of 4D image file with unwarped images
        out_enc_file: (a file name)
                encoding directions file output for applytopup
        out_field: (a file name)
                name of image file with field (Hz)
        out_fieldcoef: (an existing file name)
                file containing the field coefficients
        out_logfile: (a file name)
                name of log-file
        out_movpar: (an existing file name)
                movpar.txt output file
        out_topup: (a file name)
                basename for the <out_base>_fieldcoef.nii.gz and
                <out_base>_movpar.txt files
