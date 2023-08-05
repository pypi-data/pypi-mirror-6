.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.ants.segmentation
============================


.. _nipype.interfaces.ants.segmentation.Atropos:


.. index:: Atropos

Atropos
-------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/ants/segmentation.py#L57>`__

Wraps command **Atropos**

A finite mixture modeling (FMM) segmentation approach with possibilities for
specifying prior constraints. These prior constraints include the specification
of a prior label image, prior probability images (one for each class), and/or an
MRF prior to enforce spatial smoothing of the labels. Similar algorithms include
FAST and SPM.

Examples
~~~~~~~~

>>> from nipype.interfaces.ants import Atropos
>>> at = Atropos()
>>> at.inputs.dimension = 3
>>> at.inputs.intensity_images = 'structural.nii'
>>> at.inputs.mask_image = 'mask.nii'
>>> at.inputs.initialization = 'PriorProbabilityImages'
>>> at.inputs.prior_probability_images = ['rc1s1.nii', 'rc1s2.nii']
>>> at.inputs.number_of_tissue_classes = 2
>>> at.inputs.prior_weighting = 0.8
>>> at.inputs.prior_probability_threshold = 0.0000001
>>> at.inputs.likelihood_model = 'Gaussian'
>>> at.inputs.mrf_smoothing_factor = 0.2
>>> at.inputs.mrf_radius = [1, 1, 1]
>>> at.inputs.icm_use_synchronous_update = True
>>> at.inputs.maximum_number_of_icm_terations = 1
>>> at.inputs.n_iterations = 5
>>> at.inputs.convergence_threshold = 0.000001
>>> at.inputs.posterior_formulation = 'Socrates'
>>> at.inputs.use_mixture_model_proportions = True
>>> at.inputs.save_posteriors = True
>>> at.cmdline
'Atropos --image-dimensionality 3 --icm [1,1] --initialization PriorProbabilityImages[2,priors/priorProbImages%02d.nii,0.8,1e-07] --intensity-image structural.nii --likelihood-model Gaussian --mask-image mask.nii --mrf [0.2,1x1x1] --convergence [5,1e-06] --output [structural_labeled.nii,POSTERIOR_%02d.nii.gz] --posterior-formulation Socrates[1]'

Inputs::

        [Mandatory]
        initialization: ('Random' or 'Otsu' or 'KMeans' or
                 'PriorProbabilityImages' or 'PriorLabelImage')
                requires: number_of_tissue_classes
        intensity_images: (an existing file name)
        mask_image: (an existing file name)
        number_of_tissue_classes: (an integer)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        convergence_threshold: (a float)
                requires: n_iterations
        dimension: (3 or 2 or 4, nipype default value: 3)
                image dimension (2, 3, or 4)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        icm_use_synchronous_update: (a boolean)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        initialization: ('Random' or 'Otsu' or 'KMeans' or
                 'PriorProbabilityImages' or 'PriorLabelImage')
                requires: number_of_tissue_classes
        intensity_images: (an existing file name)
        likelihood_model: (a string)
        mask_image: (an existing file name)
        maximum_number_of_icm_terations: (an integer)
                requires: icm_use_synchronous_update
        mrf_radius: (a list of items which are an integer)
                requires: mrf_smoothing_factor
        mrf_smoothing_factor: (a float)
        n_iterations: (an integer)
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        number_of_tissue_classes: (an integer)
        out_classified_image_name: (a file name)
        output_posteriors_name_template: (a string, nipype default value:
                 POSTERIOR_%02d.nii.gz)
        posterior_formulation: (a string)
        prior_probability_images: (an existing file name)
        prior_probability_threshold: (a float)
                requires: prior_weighting
        prior_weighting: (a float)
        save_posteriors: (a boolean)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        use_mixture_model_proportions: (a boolean)
                requires: posterior_formulation

Outputs::

        classified_image: (an existing file name)
        posteriors: (a file name)

.. _nipype.interfaces.ants.segmentation.N4BiasFieldCorrection:


.. index:: N4BiasFieldCorrection

N4BiasFieldCorrection
---------------------

`Link to code <http://github.com/nipy/nipype/tree/49d76df8df526ae0790ff6079642565548bc4434/nipype/interfaces/ants/segmentation.py#L188>`__

Wraps command **N4BiasFieldCorrection**

N4 is a variant of the popular N3 (nonparameteric nonuniform normalization)
retrospective bias correction algorithm. Based on the assumption that the
corruption of the low frequency bias field can be modeled as a convolution of
the intensity histogram by a Gaussian, the basic algorithmic protocol is to
iterate between deconvolving the intensity histogram by a Gaussian, remapping
the intensities, and then spatially smoothing this result by a B-spline modeling
of the bias field itself. The modifications from and improvements obtained over
the original N3 algorithm are described in the following paper: N. Tustison et
al., N4ITK: Improved N3 Bias Correction, IEEE Transactions on Medical Imaging,
29(6):1310-1320, June 2010.

Examples
~~~~~~~~

>>> from nipype.interfaces.ants import N4BiasFieldCorrection
>>> n4 = N4BiasFieldCorrection()
>>> n4.inputs.dimension = 3
>>> n4.inputs.input_image = 'structural.nii'
>>> n4.inputs.bspline_fitting_distance = 300
>>> n4.inputs.shrink_factor = 3
>>> n4.inputs.n_iterations = [50,50,30,20]
>>> n4.inputs.convergence_threshold = 1e-6
>>> n4.cmdline
'N4BiasFieldCorrection --convergence [ 50x50x30x20 ,1e-06] --bsline-fitting [300] --image-dimension 3 --input-image structural.nii --output structural_corrected.nii --shrink-factor 3'

Inputs::

        [Mandatory]
        input_image: (a file name)
                image to apply transformation to (generally a coregistered
                functional)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        bspline_fitting_distance: (a float)
        convergence_threshold: (a float)
                requires: n_iterations
        dimension: (3 or 2, nipype default value: 3)
                image dimension (2 or 3)
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        input_image: (a file name)
                image to apply transformation to (generally a coregistered
                functional)
        mask_image: (a file name)
        n_iterations: (a list of items which are an integer)
                requires: convergence_threshold
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        output_image: (a string)
                output file name
        shrink_factor: (an integer)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        output_image: (an existing file name)
                Warped image
