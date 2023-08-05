#
# Copyright CERN, 2010.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

"""A Fudge Field.

These are added to Fudge `Message`s in order to encode
them, and are returned as the contents of decoded Fudge `Message`s

"""
from fudgemsg import codecs
from fudgemsg import prefix
from fudgemsg.registry import DEFAULT_REGISTRY
from fudgemsg import types
from fudgemsg import utils

import fudgemsg # For message.Message

class Field:
    """A Concrete field suitable for including into a Fudge Message"""

    def __init__(self, type_, ordinal, name, value):
        """Create a new Fudge field.

        Arguments:
            type_ : FieldType
            ordinal : short'
            name : unicode string where len(name) < 255
            value : object

        """
        self.type_ = type_
        self.ordinal = ordinal
        self.name = name
        self.value = value

    def size(self, taxonomy=None):
        """Calculate the size that the field will take up in the message.

        Arguments:
             taxonomy: A Taxomomy to be used for replacing names with ordinals.
                 (Default : none)

        Returns:
             The size in bytes required to encode this field

        """
        has_ordinal = self.ordinal is not None
        has_name = self.name is not None

        size = 2 # prefix
        if self.name and taxonomy:
            if taxonomy.get_ordinal(self.name):
                has_ordinal = True
                has_name = False
        if has_ordinal:
            size += 2
        if has_name:
            # one for size prefix
            size += 1 + types.size_unicode(self.name)

        if self.type_.is_variable_sized:
            # We store a variable sized length and then the value itself
            if self.is_type(types.FUDGEMSG_TYPE_ID):
                # sub-message, need to be taxonomy aware
                value_length = self.type_.calc_size(self.value, taxonomy)
            else:
                value_length = self.type_.calc_size(self.value)
            size += bytes_for_value_length(value_length) + value_length
        else:
            size += self.type_.fixed_size
        return size

    def is_type(self, type_id):
        """Return True if this type has ID equal to type_id.

        Arguments:
           type_id : the ID to check against

        Return:
           True if type_id is the type_id of this object, otherwise False"""
        return self.type_.type_id == type_id

    def __repr__(self):
        if self.name and self.ordinal is not None:
            return "Field[%s:%s-'%s']"% (self.name, self.type_, self.value)
        elif self.name and self.ordinal is not None:
            return "Field[%s,%d:%s-'%s']"% (self.name, self.ordinal, \
                    self.type_, self.value)
        else:
            return "Field[%s-'%s']"% (self.type_, self.value)

    def encode(self, writer, taxonomy=None):
        """Encode a Field.

        This encodes Field Prefix, Type, Ordinal, Name, Data

        """
        variable_width = 0
        if self.type_.is_variable_sized:
            if self.is_type(types.FUDGEMSG_TYPE_ID):
                # sub-message, need to be taxonomy aware
                value_length = self.type_.calc_size(self.value, taxonomy)
            else:
                value_length = self.type_.calc_size(self.value)
            variable_width = bytes_for_value_length(value_length)

        ordinal = self.ordinal
        name = self.name
        if taxonomy and self.name:
            tax_ord = taxonomy.get_ordinal(self.name)
            if tax_ord:
                ordinal = tax_ord
                name = None

        prefix_byte = prefix.encode_prefix(not self.type_.is_variable_sized, \
                variable_width, ordinal is not None, name is not None)

        # And write it out
        writer.write(chr(prefix_byte))
        writer.write(codecs.enc_byte(self.type_.type_id))
        if ordinal is not None:
            writer.write(codecs.enc_short(ordinal))
        if name:
            assert len(name) <= utils.MAX_BYTE
            writer.write(codecs.enc_name(name))

        if self.type_.is_variable_sized:
            encode_value_length(value_length, writer)

        if self.is_type(types.FUDGEMSG_TYPE_ID):
            self.value.encode(writer, taxonomy)
        else:
            writer.write(self.type_.encoder(self.value))


    @classmethod
    def decode(cls, encoded, taxonomy=None):
        """Decode a field from a byte array.

        Returns:
            (field, num_read).

            field: the field read from the byte array
            num_read: number of bytes this field took up

        Raises:
            Error: if there is not enough bytes in the array for the field.

        """
        assert len(encoded) >= 2

        # prefix
        pos = 0
        fixedwidth, variablewidth, has_ordinal, has_name = \
                prefix.decode_prefix(ord(encoded[pos]))
        pos += 1
        type_id = ord(encoded[pos])
        # TODO(jamesc) - need to handle user supplied registries
        field_type = DEFAULT_REGISTRY[type_id]
        pos += 1

        # ordinal
        ordinal = None
        if has_ordinal:
            ordinal = codecs.dec_short(encoded[pos:])
            pos += 2

        # name
        name = None
        if has_name:
            name_len = ord(encoded[pos])
            pos += 1 # length encoded as 1 byte
            name = codecs.dec_unicode(encoded[pos:pos+name_len])
            pos += name_len
        elif has_ordinal and taxonomy:
            name = taxonomy.get_name(ordinal)

        # value
        if fixedwidth:
            value = field_type.decoder(encoded[pos:pos+field_type.fixed_size])
            pos += field_type.fixed_size
        else:
            value_length = decode_value_length(encoded[pos:], variablewidth)

            pos += variablewidth
            if type_id == types.FUDGEMSG_TYPE_ID:
                value = fudgemsg.message.Message.decode(encoded[pos:pos+value_length], taxonomy)
            else:
                value = field_type.decoder(encoded[pos:pos+value_length])
            pos += value_length

        field = Field(field_type, ordinal, name, value)
        return field, pos

def bytes_for_value_length(length):
    """For a value length, calculate how many
    bytes are needed to hold the length

    Arguments:
        length : Length of value (0 <= length <= MAX_INT)

    Return:
        number of bytes needed to hold it (1, 2 or 4)

    """
    assert length >= 0 and length <= utils.MAX_INT

    if length <= utils.MAX_BYTE:
        return 1
    elif length <= utils.MAX_SHORT:
        return 2
    else:
        return 4

def encode_value_length(value_length, writer):
    """Enocde the length of a value as a
    var_width length. This will be the smallest of
    a byte, short or int which can hold the length.

    Arguments:
        value_length: the length in buytes of the value object
        writer: the writer object to write the length to

    """
    assert value_length >= 0 and value_length <= utils.MAX_INT

    if value_length <= utils.MAX_BYTE:
        writer.write(codecs.enc_byte(value_length))
    elif value_length <= utils.MAX_SHORT:
        writer.write(codecs.enc_short(value_length))
    else:
        writer.write(codecs.enc_int(value_length))

def decode_value_length(encoded, width):
    """Decode the length of a value from a
    var_width length.

    Arguments:
        encoded: The byte stream to read from
        width:  The number of bytes to read (1, 2, 4)

    Return:
        The decoded value length

    """
    assert width in (0, 1, 2, 4)

    if width == 0:
        return 0
    elif width == 1:
        return codecs.dec_byte(encoded[0])
    elif width == 2:
        return codecs.dec_short(encoded[0:2])
    else:
        return codecs.dec_int(encoded[0:4])
