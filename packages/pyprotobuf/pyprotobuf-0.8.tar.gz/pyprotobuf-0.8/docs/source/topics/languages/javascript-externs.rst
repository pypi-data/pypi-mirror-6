##################
Javascript Externs
##################




Example
#######

.. highlight:: protobuf

Input file (test.proto)::

    option javascript_package = "com.example";

    message Item {
      optional string aString = 1;
      optional int32 aNumber = 2;
      required string aRequiredString = 3;
      repeated string aRepeatedString = 4;
    }

.. highlight:: javascript

Generated javascript externs(``protopy --format externs test.proto``)::

    /** @constructor */
    com.example.Item = function(){};

    /** @type {string} */
    com.example.Item.prototype.aString;

    /** @type {number} */
    com.example.Item.prototype.aNumber;

    /** @type {string} */
    com.example.Item.prototype.aRequiredString;

    /** @type {[string]} */
    com.example.Item.prototype.aRepeatedString;



