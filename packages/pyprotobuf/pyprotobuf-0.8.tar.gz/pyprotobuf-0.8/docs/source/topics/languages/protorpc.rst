########
ProtoRPC
########

pyprotobuf can compile proto files to https://code.google.com/p/google-protorpc/.


Example
#######

.. highlight:: protobuf

example.proto::

    message Item {
      optional string aString = 1;
      optional int32 aNumber = 2;
      required string aRequiredString = 3;
      repeated string aRepeatedString = 4;
    }

.. highlight:: python

Run the command ``protopy --format python example.proto``  to generate::

    from protorpc import messages

    class Item(messages.Message):
        aString = messages.StringField(1)
        aNumber = messages.IntegerField(2)
        aRequiredString = messages.StringField(3, required=True)
        aRepeatedString = messages.StringField(4, repeated=True)

Using the protorpc's DateTimeField
##################################

To use protorpc's DateTimeField, you must ``import "protorpc/message_types.proto"``. This proto file is included with
pyprotobuf.

Then you can define fields with the ``protorpc.DateTimeMessage`` type.

.. highlight:: protobuf

For example::

    import "protorpc/message_types.proto";

    message Test {
        optional protorpc.DateTimeMessage datetime = 1;
    }

.. highlight:: python

Generates::

    from protorpc import messages
    import protorpc.message_types


    class Test(messages.Message):
        datetime = protorpc.message_types.DateTimeField(1)



Defining custom field types
###########################

pyprotobuf supports the option ``python_field_type`` to define the ``protorpc.messages.Message``'s ``protorpc.messages.Field`` type.

This can be used to handle (un)serialization of message types to language native types.


.. highlight:: protobuf

For example::

    message DateTime {
        required int64 microseconds = 1;
        option python_field_type = "example.module.DateTimeField";
    }


    message Test {
        optional DateTime datetime = 1;
    }

.. highlight:: python

Generates::


    from protorpc import messages
    import example.module


    class DateTime(messages.Message):
        microseconds = messages.IntegerField(1)


    class Test(messages.Message):
        datetime = example.module.DateTimeField(1)


In this case, the ``example.module.DateTimeField``` class (not defined) should be customized by converting the
microseconds to return a python datetime and vice-versa.