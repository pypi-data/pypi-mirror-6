.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.filtering.thresholdscalarvolume
=================================================


.. _nipype.interfaces.slicer.filtering.thresholdscalarvolume.ThresholdScalarVolume:


.. index:: ThresholdScalarVolume

ThresholdScalarVolume
---------------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/slicer/filtering/thresholdscalarvolume.py#L23>`__

Wraps command **ThresholdScalarVolume **

title: Threshold Scalar Volume

category: Filtering

description: <p>Threshold an image.</p><p>Set image values to a user-specified outside value if they are below, above, or between simple threshold values.</p><p>ThresholdAbove: The values greater than or equal to the threshold value are set to OutsideValue.</p><p>ThresholdBelow: The values less than or equal to the threshold value are set to OutsideValue.</p><p>ThresholdOutside: The values outside the range Lower-Upper are set to OutsideValue.</p><p>Although all image types are supported on input, only signed types are produced.</p><p>

version: 0.1.0.$Revision: 2104 $(alpha)

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/Threshold

contributor: Nicole Aucoin (SPL, BWH), Ron Kikinis (SPL, BWH)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        InputVolume: (an existing file name)
                Input volume
        OutputVolume: (a boolean or a file name)
                Thresholded input volume
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        lower: (an integer)
                Lower threshold value
        outsidevalue: (an integer)
                Set the voxels to this value if they fall outside the threshold
                range
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        threshold: (an integer)
                Threshold value
        thresholdtype: ('Below' or 'Above' or 'Outside')
                What kind of threshold to perform. If Outside is selected, uses
                Upper and Lower values. If Below is selected, uses the
                ThresholdValue, if Above is selected, uses the ThresholdValue.
        upper: (an integer)
                Upper threshold value

Outputs::

        OutputVolume: (an existing file name)
                Thresholded input volume
