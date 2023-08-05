.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.fsl.maths
====================


.. _nipype.interfaces.fsl.maths.ApplyMask:


.. index:: ApplyMask

ApplyMask
---------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L171>`__

Wraps command **fslmaths**

Use fslmaths to apply a binary mask to another image.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        mask_file: (an existing file name)
                binary image defining mask space
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        mask_file: (an existing file name)
                binary image defining mask space
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.BinaryMaths:


.. index:: BinaryMaths

BinaryMaths
-----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L272>`__

Wraps command **fslmaths**

Use fslmaths to perform mathematical operations using a second image or a numeric value.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        operand_file: (an existing file name)
                second image to perform operation with
                mutually_exclusive: operand_value
        operand_value: (a float)
                value to perform operation with
                mutually_exclusive: operand_file
        operation: ('add' or 'sub' or 'mul' or 'div' or 'rem' or 'max' or
                 'min')
                operation to perform
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        operand_file: (an existing file name)
                second image to perform operation with
                mutually_exclusive: operand_value
        operand_value: (a float)
                value to perform operation with
                mutually_exclusive: operand_file
        operation: ('add' or 'sub' or 'mul' or 'div' or 'rem' or 'max' or
                 'min')
                operation to perform
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.ChangeDataType:


.. index:: ChangeDataType

ChangeDataType
--------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L64>`__

Wraps command **fslmaths**

Use fslmaths to change the datatype of an image.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                output data type
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                output data type
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.DilateImage:


.. index:: DilateImage

DilateImage
-----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L195>`__

Wraps command **fslmaths**

Use fslmaths to perform a spatial dilation of an image.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        operation: ('mean' or 'modal' or 'max')
                filtering operation to perfoem in dilation
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        kernel_file: (an existing file name)
                use external file for kernel
                mutually_exclusive: kernel_size
        kernel_shape: ('3D' or '2D' or 'box' or 'boxv' or 'gauss' or 'sphere'
                 or 'file')
                kernel shape to use
        kernel_size: (a float)
                kernel size - voxels for box/boxv, mm for sphere, mm sigma for gauss
                mutually_exclusive: kernel_file
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        operation: ('mean' or 'modal' or 'max')
                filtering operation to perfoem in dilation
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.ErodeImage:


.. index:: ErodeImage

ErodeImage
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L214>`__

Wraps command **fslmaths**

Use fslmaths to perform a spatial erosion of an image.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        kernel_file: (an existing file name)
                use external file for kernel
                mutually_exclusive: kernel_size
        kernel_shape: ('3D' or '2D' or 'box' or 'boxv' or 'gauss' or 'sphere'
                 or 'file')
                kernel shape to use
        kernel_size: (a float)
                kernel size - voxels for box/boxv, mm for sphere, mm sigma for gauss
                mutually_exclusive: kernel_file
        minimum_filter: (a boolean, nipype default value: False)
                if true, minimum filter rather than erosion by zeroing-out
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.IsotropicSmooth:


.. index:: IsotropicSmooth

IsotropicSmooth
---------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L151>`__

Wraps command **fslmaths**

Use fslmaths to spatially smooth an image with a gaussian kernel.

Inputs::

        [Mandatory]
        fwhm: (a float)
                fwhm of smoothing kernel [mm]
                mutually_exclusive: sigma
        in_file: (an existing file name)
                image to operate on
        sigma: (a float)
                sigma of smoothing kernel [mm]
                mutually_exclusive: fwhm
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
                fwhm of smoothing kernel [mm]
                mutually_exclusive: sigma
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        sigma: (a float)
                sigma of smoothing kernel [mm]
                mutually_exclusive: fwhm
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.MathsCommand:


.. index:: MathsCommand

MathsCommand
------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L35>`__

Wraps command **fslmaths**


Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.MaxImage:


.. index:: MaxImage

MaxImage
--------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L126>`__

Wraps command **fslmaths**

Use fslmaths to generate a max image across a given dimension.

Examples
~~~~~~~~
from nipype.interfaces.fsl.maths import MaxImage
maxer = MaxImage()
maxer.inputs.in_file = "functional.nii"
maxer.dimension = "T"
maths.cmdline
fslmaths functional.nii -Tmax functional_max.nii

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        dimension: ('T' or 'X' or 'Y' or 'Z', nipype default value: T)
                dimension to max across
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.MeanImage:


.. index:: MeanImage

MeanImage
---------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L113>`__

Wraps command **fslmaths**

Use fslmaths to generate a mean image across a given dimension.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        dimension: ('T' or 'X' or 'Y' or 'Z', nipype default value: T)
                dimension to mean across
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.MultiImageMaths:


.. index:: MultiImageMaths

MultiImageMaths
---------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L287>`__

Wraps command **fslmaths**

Use fslmaths to perform a sequence of mathematical operations.

Examples
~~~~~~~~
from nipype.interfaces.fsl import MultiImageMaths
maths = MultiImageMaths()
maths.inputs.in_file = "functional.nii"
maths.inputs.op_string = "-add %s -mul -1 -div %s"
maths.inputs.operand_files = ["functional2.nii", "functional3.nii"]
maths.inputs.out_file = functional4.nii
maths.cmdline
fslmaths functional1.nii -add functional2.nii -mul -1 -div functional3.nii functional4.nii

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        op_string: (a string)
                python formatted string of operations to perform
        operand_files: (an existing file name)
                list of file names to plug into op string
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        op_string: (a string)
                python formatted string of operations to perform
        operand_files: (an existing file name)
                list of file names to plug into op string
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.SpatialFilter:


.. index:: SpatialFilter

SpatialFilter
-------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L235>`__

Wraps command **fslmaths**

Use fslmaths to spatially filter an image.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        operation: ('mean' or 'median' or 'meanu')
                operation to filter with
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        kernel_file: (an existing file name)
                use external file for kernel
                mutually_exclusive: kernel_size
        kernel_shape: ('3D' or '2D' or 'box' or 'boxv' or 'gauss' or 'sphere'
                 or 'file')
                kernel shape to use
        kernel_size: (a float)
                kernel size - voxels for box/boxv, mm for sphere, mm sigma for gauss
                mutually_exclusive: kernel_file
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        operation: ('mean' or 'median' or 'meanu')
                operation to filter with
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.TemporalFilter:


.. index:: TemporalFilter

TemporalFilter
--------------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L318>`__

Wraps command **fslmaths**

Use fslmaths to apply a low, high, or bandpass temporal filter to a timeseries.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
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
        highpass_sigma: (a float, nipype default value: -1)
                highpass filter sigma (in volumes)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        lowpass_sigma: (a float, nipype default value: -1)
                lowpass filter sigma (in volumes)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.Threshold:


.. index:: Threshold

Threshold
---------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L83>`__

Wraps command **fslmaths**

Use fslmaths to apply a threshold to an image in a variety of ways.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        thresh: (a float)
                threshold value

        [Optional]
        args: (a string)
                Additional parameters to the command
        direction: ('below' or 'above', nipype default value: below)
                zero-out either below or above thresh value
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        thresh: (a float)
                threshold value
        use_nonzero_voxels: (a boolean)
                use nonzero voxels to caluclate robust range
                requires: use_robust_range
        use_robust_range: (a boolean)
                inteperet thresh as percentage (0-100) of robust range

Outputs::

        out_file: (an existing file name)
                image written after calculations

.. _nipype.interfaces.fsl.maths.UnaryMaths:


.. index:: UnaryMaths

UnaryMaths
----------

`Link to code <http://github.com/nipy/nipype/tree/083918710085dcc1ce0a4427b490267bef42316a/nipype/interfaces/fsl/maths.py#L250>`__

Wraps command **fslmaths**

Use fslmaths to perorm a variety of mathematical operations on an image.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                image to operate on
        operation: ('exp' or 'log' or 'sin' or 'cos' or 'sqr' or 'sqrt' or
                 'recip' or 'abs' or 'bin' or 'index')
                operation to perform
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
                image to operate on
        internal_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for calculations (default is float)
        nan2zeros: (a boolean)
                change NaNs to zeros before doing anything
        operation: ('exp' or 'log' or 'sin' or 'cos' or 'sqr' or 'sqrt' or
                 'recip' or 'abs' or 'bin' or 'index')
                operation to perform
        out_file: (a file name)
                image to write
        output_datatype: ('float' or 'char' or 'int' or 'short' or 'double'
                 or 'input')
                datatype to use for output (default uses input type)
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or
                 'NIFTI')
                FSL output type
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                image written after calculations
