####################
Extending pyprotobuf
####################

Developing a custom generator
#############################


Create a setup.py
=================

Custom generators can be registered by creating a setup.py with the entry point `pyprotobuf.generators`. pyprotobuf
will detect the generator and make it available as a format.

.. highlight:: python

setup.py::

    setup(
        # ...
        entry_points = '''
        [pyprotobuf.generators]
        custom = custom_generator
        '''
        # ...
     )


Create a generator module
=========================

.. note:: The CodeGenerator api is unstable.


.. highlight:: python

custom_generator.py::


    from pyprotobuf.codegenerator import CodeGenerator

    class Generator(CodeGenerator):
        def generate_file(self, protonode, **kwargs):
            """ Custom ProtoNode generating logic

                :return: The compiled code
                :rtype: str
            """
            pass

    __generator__ = Generator
