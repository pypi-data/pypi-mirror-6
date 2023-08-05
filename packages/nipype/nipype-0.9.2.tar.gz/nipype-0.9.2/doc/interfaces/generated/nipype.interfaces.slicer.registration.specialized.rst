.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.registration.specialized
==========================================


.. _nipype.interfaces.slicer.registration.specialized.ACPCTransform:


.. index:: ACPCTransform

ACPCTransform
-------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/slicer/registration/specialized.py#L20>`__

Wraps command **ACPCTransform **

title: ACPC Transform

category: Registration.Specialized

description: <p>Calculate a transformation from two lists of fiducial points.</p><p>ACPC line is two fiducial points, one at the anterior commissure and one at the posterior commissure. The resulting transform will bring the line connecting them to horizontal to the AP axis.</p><p>The midline is a series of points defining the division between the hemispheres of the brain (the mid sagittal plane). The resulting transform will put the output volume with the mid sagittal plane lined up with the AS plane.</p><p>Use the Filtering module<b>Resample Scalar/Vector/DWI Volume</b>to apply the transformation to a volume.</p>

version: 1.0

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/ACPCTransform

license: slicer3

contributor: Nicole Aucoin (SPL, BWH), Ron Kikinis (SPL, BWH)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        acpc: (a list of from 3 to 3 items which are a float)
                ACPC line, two fiducial points, one at the anterior commissure and
                one at the posterior commissure.
        args: (a string)
                Additional parameters to the command
        debugSwitch: (a boolean)
                Click if wish to see debugging output
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        midline: (a list of from 3 to 3 items which are a float)
                The midline is a series of points defining the division between the
                hemispheres of the brain (the mid sagittal plane).
        outputTransform: (a boolean or a file name)
                A transform filled in from the ACPC and Midline registration
                calculation
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        outputTransform: (an existing file name)
                A transform filled in from the ACPC and Midline registration
                calculation

.. _nipype.interfaces.slicer.registration.specialized.BRAINSDemonWarp:


.. index:: BRAINSDemonWarp

BRAINSDemonWarp
---------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/slicer/registration/specialized.py#L208>`__

Wraps command **BRAINSDemonWarp **

title: Demon Registration (BRAINS)

category: Registration.Specialized

description:
    This program finds a deformation field to warp a moving image onto a fixed image.  The images must be of the same signal kind, and contain an image of the same kind of object.  This program uses the Thirion Demons warp software in ITK, the Insight Toolkit.  Additional information is available at: http://www.nitrc.org/projects/brainsdemonwarp.



version: 3.0.0

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Modules:BRAINSDemonWarp

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: This tool was developed by Hans J. Johnson and Greg Harris.

acknowledgements: The development of this tool was supported by funding from grants NS050568 and NS40068 from the National Institute of Neurological Disorders and Stroke and grants MH31593, MH40856, from the National Institute of Mental Health.

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        arrayOfPyramidLevelIterations: (an integer)
                The number of iterations for each pyramid level
        backgroundFillValue: (an integer)
                Replacement value to overwrite background when performing BOBF
        checkerboardPatternSubdivisions: (an integer)
                Number of Checkerboard subdivisions in all 3 directions
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        fixedBinaryVolume: (an existing file name)
                Mask filename for desired region of interest in the Fixed image.
        fixedVolume: (an existing file name)
                Required: input fixed (target) image
        gradient_type: ('0' or '1' or '2')
                Type of gradient used for computing the demons force (0 is
                symmetrized, 1 is fixed image, 2 is moving image)
        gui: (a boolean)
                Display intermediate image volumes for debugging
        histogramMatch: (a boolean)
                Histogram Match the input images. This is suitable for images of the
                same modality that may have different absolute scales, but the same
                overall intensity profile.
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        initializeWithDisplacementField: (an existing file name)
                Initial deformation field vector image file name
        initializeWithTransform: (an existing file name)
                Initial Transform filename
        inputPixelType: ('float' or 'short' or 'ushort' or 'int' or 'uchar')
                Input volumes will be typecast to this format:
                float|short|ushort|int|uchar
        interpolationMode: ('NearestNeighbor' or 'Linear' or
                 'ResampleInPlace' or 'BSpline' or 'WindowedSinc' or 'Hamming' or
                 'Cosine' or 'Welch' or 'Lanczos' or 'Blackman')
                Type of interpolation to be used when applying transform to moving
                volume. Options are Linear, ResampleInPlace, NearestNeighbor,
                BSpline, or WindowedSinc
        lowerThresholdForBOBF: (an integer)
                Lower threshold for performing BOBF
        maskProcessingMode: ('NOMASK' or 'ROIAUTO' or 'ROI' or 'BOBF')
                What mode to use for using the masks: NOMASK|ROIAUTO|ROI|BOBF. If
                ROIAUTO is choosen, then the mask is implicitly defined using a otsu
                forground and hole filling algorithm. Where the Region Of Interest
                mode uses the masks to define what parts of the image should be used
                for computing the deformation field. Brain Only Background Fill uses
                the masks to pre-process the input images by clipping and filling in
                the background with a predefined value.
        max_step_length: (a float)
                Maximum length of an update vector (0: no restriction)
        medianFilterSize: (an integer)
                Median filter radius in all 3 directions. When images have a lot of
                salt and pepper noise, this step can improve the registration.
        minimumFixedPyramid: (an integer)
                The shrink factor for the first level of the fixed image pyramid.
                (i.e. start at 1/16 scale, then 1/8, then 1/4, then 1/2, and finally
                full scale)
        minimumMovingPyramid: (an integer)
                The shrink factor for the first level of the moving image pyramid.
                (i.e. start at 1/16 scale, then 1/8, then 1/4, then 1/2, and finally
                full scale)
        movingBinaryVolume: (an existing file name)
                Mask filename for desired region of interest in the Moving image.
        movingVolume: (an existing file name)
                Required: input moving image
        neighborhoodForBOBF: (an integer)
                neighborhood in all 3 directions to be included when performing BOBF
        numberOfBCHApproximationTerms: (an integer)
                Number of terms in the BCH expansion
        numberOfHistogramBins: (an integer)
                The number of histogram levels
        numberOfMatchPoints: (an integer)
                The number of match points for histrogramMatch
        numberOfPyramidLevels: (an integer)
                Number of image pyramid levels to use in the multi-resolution
                registration.
        numberOfThreads: (an integer)
                Explicitly specify the maximum number of threads to use.
        outputCheckerboardVolume: (a boolean or a file name)
                Genete a checkerboard image volume between the fixedVolume and the
                deformed movingVolume.
        outputDebug: (a boolean)
                Flag to write debugging images after each step.
        outputDisplacementFieldPrefix: (a string)
                Displacement field filename prefix for writing separate x, y, and z
                component images
        outputDisplacementFieldVolume: (a boolean or a file name)
                Output deformation field vector image (will have the same physical
                space as the fixedVolume).
        outputNormalized: (a boolean)
                Flag to warp and write the normalized images to output. In
                normalized images the image values are fit-scaled to be between 0
                and the maximum storage type value.
        outputPixelType: ('float' or 'short' or 'ushort' or 'int' or 'uchar')
                outputVolume will be typecast to this format:
                float|short|ushort|int|uchar
        outputVolume: (a boolean or a file name)
                Required: output resampled moving image (will have the same physical
                space as the fixedVolume).
        promptUser: (a boolean)
                Prompt the user to hit enter each time an image is sent to the
                DebugImageViewer
        registrationFilterType: ('Demons' or 'FastSymmetricForces' or
                 'Diffeomorphic')
                Registration Filter Type: Demons|FastSymmetricForces|Diffeomorphic
        seedForBOBF: (an integer)
                coordinates in all 3 directions for Seed when performing BOBF
        smoothDisplacementFieldSigma: (a float)
                A gaussian smoothing value to be applied to the deformation feild at
                each iteration.
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        upFieldSmoothing: (a float)
                Smoothing sigma for the update field at each iteration
        upperThresholdForBOBF: (an integer)
                Upper threshold for performing BOBF
        use_vanilla_dem: (a boolean)
                Run vanilla demons algorithm

Outputs::

        outputCheckerboardVolume: (an existing file name)
                Genete a checkerboard image volume between the fixedVolume and the
                deformed movingVolume.
        outputDisplacementFieldVolume: (an existing file name)
                Output deformation field vector image (will have the same physical
                space as the fixedVolume).
        outputVolume: (an existing file name)
                Required: output resampled moving image (will have the same physical
                space as the fixedVolume).

.. _nipype.interfaces.slicer.registration.specialized.FiducialRegistration:


.. index:: FiducialRegistration

FiducialRegistration
--------------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/slicer/registration/specialized.py#L58>`__

Wraps command **FiducialRegistration **

title: Fiducial Registration

category: Registration.Specialized

description: Computes a rigid, similarity or affine transform from a matched list of fiducials

version: 0.1.0.$Revision$

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/TransformFromFiducials

contributor: Casey B Goodlett (Kitware), Dominik Meier (SPL, BWH)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

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
        fixedLandmarks: (a list of from 3 to 3 items which are a float)
                Ordered list of landmarks in the fixed image
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        movingLandmarks: (a list of from 3 to 3 items which are a float)
                Ordered list of landmarks in the moving image
        outputMessage: (a string)
                Provides more information on the output
        rms: (a float)
                Display RMS Error.
        saveTransform: (a boolean or a file name)
                Save the transform that results from registration
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        transformType: ('Translation' or 'Rigid' or 'Similarity')
                Type of transform to produce

Outputs::

        saveTransform: (an existing file name)
                Save the transform that results from registration

.. _nipype.interfaces.slicer.registration.specialized.VBRAINSDemonWarp:


.. index:: VBRAINSDemonWarp

VBRAINSDemonWarp
----------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/slicer/registration/specialized.py#L131>`__

Wraps command **VBRAINSDemonWarp **

title: Vector Demon Registration (BRAINS)

category: Registration.Specialized

description:
    This program finds a deformation field to warp a moving image onto a fixed image.  The images must be of the same signal kind, and contain an image of the same kind of object.  This program uses the Thirion Demons warp software in ITK, the Insight Toolkit.  Additional information is available at: http://www.nitrc.org/projects/brainsdemonwarp.



version: 3.0.0

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Modules:BRAINSDemonWarp

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: This tool was developed by Hans J. Johnson and Greg Harris.

acknowledgements: The development of this tool was supported by funding from grants NS050568 and NS40068 from the National Institute of Neurological Disorders and Stroke and grants MH31593, MH40856, from the National Institute of Mental Health.

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        arrayOfPyramidLevelIterations: (an integer)
                The number of iterations for each pyramid level
        backgroundFillValue: (an integer)
                Replacement value to overwrite background when performing BOBF
        checkerboardPatternSubdivisions: (an integer)
                Number of Checkerboard subdivisions in all 3 directions
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        fixedBinaryVolume: (an existing file name)
                Mask filename for desired region of interest in the Fixed image.
        fixedVolume: (an existing file name)
                Required: input fixed (target) image
        gradient_type: ('0' or '1' or '2')
                Type of gradient used for computing the demons force (0 is
                symmetrized, 1 is fixed image, 2 is moving image)
        gui: (a boolean)
                Display intermediate image volumes for debugging
        histogramMatch: (a boolean)
                Histogram Match the input images. This is suitable for images of the
                same modality that may have different absolute scales, but the same
                overall intensity profile.
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        initializeWithDisplacementField: (an existing file name)
                Initial deformation field vector image file name
        initializeWithTransform: (an existing file name)
                Initial Transform filename
        inputPixelType: ('float' or 'short' or 'ushort' or 'int' or 'uchar')
                Input volumes will be typecast to this format:
                float|short|ushort|int|uchar
        interpolationMode: ('NearestNeighbor' or 'Linear' or
                 'ResampleInPlace' or 'BSpline' or 'WindowedSinc' or 'Hamming' or
                 'Cosine' or 'Welch' or 'Lanczos' or 'Blackman')
                Type of interpolation to be used when applying transform to moving
                volume. Options are Linear, ResampleInPlace, NearestNeighbor,
                BSpline, or WindowedSinc
        lowerThresholdForBOBF: (an integer)
                Lower threshold for performing BOBF
        makeBOBF: (a boolean)
                Flag to make Brain-Only Background-Filled versions of the input and
                target volumes.
        max_step_length: (a float)
                Maximum length of an update vector (0: no restriction)
        medianFilterSize: (an integer)
                Median filter radius in all 3 directions. When images have a lot of
                salt and pepper noise, this step can improve the registration.
        minimumFixedPyramid: (an integer)
                The shrink factor for the first level of the fixed image pyramid.
                (i.e. start at 1/16 scale, then 1/8, then 1/4, then 1/2, and finally
                full scale)
        minimumMovingPyramid: (an integer)
                The shrink factor for the first level of the moving image pyramid.
                (i.e. start at 1/16 scale, then 1/8, then 1/4, then 1/2, and finally
                full scale)
        movingBinaryVolume: (an existing file name)
                Mask filename for desired region of interest in the Moving image.
        movingVolume: (an existing file name)
                Required: input moving image
        neighborhoodForBOBF: (an integer)
                neighborhood in all 3 directions to be included when performing BOBF
        numberOfBCHApproximationTerms: (an integer)
                Number of terms in the BCH expansion
        numberOfHistogramBins: (an integer)
                The number of histogram levels
        numberOfMatchPoints: (an integer)
                The number of match points for histrogramMatch
        numberOfPyramidLevels: (an integer)
                Number of image pyramid levels to use in the multi-resolution
                registration.
        numberOfThreads: (an integer)
                Explicitly specify the maximum number of threads to use.
        outputCheckerboardVolume: (a boolean or a file name)
                Genete a checkerboard image volume between the fixedVolume and the
                deformed movingVolume.
        outputDebug: (a boolean)
                Flag to write debugging images after each step.
        outputDisplacementFieldPrefix: (a string)
                Displacement field filename prefix for writing separate x, y, and z
                component images
        outputDisplacementFieldVolume: (a boolean or a file name)
                Output deformation field vector image (will have the same physical
                space as the fixedVolume).
        outputNormalized: (a boolean)
                Flag to warp and write the normalized images to output. In
                normalized images the image values are fit-scaled to be between 0
                and the maximum storage type value.
        outputPixelType: ('float' or 'short' or 'ushort' or 'int' or 'uchar')
                outputVolume will be typecast to this format:
                float|short|ushort|int|uchar
        outputVolume: (a boolean or a file name)
                Required: output resampled moving image (will have the same physical
                space as the fixedVolume).
        promptUser: (a boolean)
                Prompt the user to hit enter each time an image is sent to the
                DebugImageViewer
        registrationFilterType: ('Demons' or 'FastSymmetricForces' or
                 'Diffeomorphic' or 'LogDemons' or 'SymmetricLogDemons')
                Registration Filter Type: Demons|FastSymmetricForces|Diffeomorphic|L
                ogDemons|SymmetricLogDemons
        seedForBOBF: (an integer)
                coordinates in all 3 directions for Seed when performing BOBF
        smoothDisplacementFieldSigma: (a float)
                A gaussian smoothing value to be applied to the deformation feild at
                each iteration.
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        upFieldSmoothing: (a float)
                Smoothing sigma for the update field at each iteration
        upperThresholdForBOBF: (an integer)
                Upper threshold for performing BOBF
        use_vanilla_dem: (a boolean)
                Run vanilla demons algorithm
        weightFactors: (a float)
                Weight fatctors for each input images

Outputs::

        outputCheckerboardVolume: (an existing file name)
                Genete a checkerboard image volume between the fixedVolume and the
                deformed movingVolume.
        outputDisplacementFieldVolume: (an existing file name)
                Output deformation field vector image (will have the same physical
                space as the fixedVolume).
        outputVolume: (an existing file name)
                Required: output resampled moving image (will have the same physical
                space as the fixedVolume).
