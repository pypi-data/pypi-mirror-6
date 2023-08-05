.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.c3
=============


.. _nipype.interfaces.c3.C3dAffineTool:


.. index:: C3dAffineTool

C3dAffineTool
-------------

`Link to code <http://github.com/nipy/nipype/tree/b1b78251dfd6f3b60c6bc63f79f86b356a8fe9cc/nipype/interfaces/c3.py#L27>`__

Wraps command **c3d_affine_tool**

Converts fsl-style Affine registration into ANTS compatible itk format

Example
~~~~~~~

>>> from nipype.interfaces.c3 import C3dAffineTool
>>> c3 = C3dAffineTool()
>>> c3.inputs.source_file = 'cmatrix.mat'
>>> c3.inputs.itk_transform = 'affine.txt'
>>> c3.inputs.fsl2ras = True
>>> c3.cmdline
'c3d_affine_tool -src cmatrix.mat -fsl2ras -oitk affine.txt'

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
        fsl2ras: (a boolean)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the
                interface fails to run
        itk_transform: (a boolean or a file name)
                Export ITK transform.
        reference_file: (an existing file name)
        source_file: (an existing file name)
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output: `stream` - displays to terminal
                immediately, `allatonce` - waits till command is finished to display
                output, `file` - writes output to file, `none` - output is ignored
        transform_file: (an existing file name)

Outputs::

        itk_transform: (an existing file name)
