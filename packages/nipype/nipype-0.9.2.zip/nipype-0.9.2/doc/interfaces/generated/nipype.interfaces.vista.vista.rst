.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.vista.vista
======================


.. _nipype.interfaces.vista.vista.Vnifti2Image:


.. index:: Vnifti2Image

Vnifti2Image
------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/vista/vista.py#L26>`__

Wraps command **vnifti2image**

Convert a nifti file into a vista file.

Example
~~~~~~~

>>> vimage = Vnifti2Image()
>>> vimage.inputs.in_file = 'image.nii'
>>> vimage.cmdline
'vnifti2image -in image.nii -out image.v'
>>> vimage.run()                                       # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                in file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

        [Optional]
        args: (a string)
                Additional parameters to the command
        attributes: (an existing file name)
                attribute file
        environ: (a dictionary with keys which are a value of type 'str' and
                 with values which are a value of type 'str', nipype default value:
                 {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        in_file: (an existing file name)
                in file
        out_file: (a file name)
                output data file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                Output vista file

.. _nipype.interfaces.vista.vista.VtoMat:


.. index:: VtoMat

VtoMat
------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/vista/vista.py#L53>`__

Wraps command **vtomat**

Convert a nifti file into a vista file.

Example
~~~~~~~

>>> vimage = VtoMat()
>>> vimage.inputs.in_file = 'image.v'
>>> vimage.cmdline
'vtomat -in image.v -out image.mat'
>>> vimage.run()                                       # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                in file
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
                in file
        out_file: (a file name)
                output mat file
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored

Outputs::

        out_file: (an existing file name)
                Output mat file
