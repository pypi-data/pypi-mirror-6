"""Python 3 compatible AMQP Data Encoder

Functions for encoding data of various types including field tables and arrays

"""
import calendar
import decimal as _decimal
import datetime
import struct
import time


def bit(value, byte, position):
    """Encode a bit value

    :param int value: Value to decode
    :param int byte: The byte to apply the value to
    :param int position: The position in the byte to set the bit on
    :rtype: tuple of bytes used and a bool value

    """
    return byte | (value << position)


def boolean(value):
    """Encode a boolean value.

    :param bool value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, bool):
        raise ValueError("bool type required")
    return struct.pack('>B', int(value))


def decimal(value):
    """Encode a decimal.Decimal value.

    :param decimal.Decimal value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, _decimal.Decimal):
        raise ValueError("decimal.Decimal type required")
    tmp = '%s' % value
    if '.' in tmp:
        decimals = len(tmp.split('.')[-1])
        value = value.normalize()
        raw = int(value * (_decimal.Decimal(10) ** decimals))
        return struct.pack('>Bi', decimals, raw)
    return struct.pack('>Bi', 0, int(value))


def double(value):
    """Encode a floating point value as a double

    :param float value: Value to encode
    :rtype: str

    """
    if not isinstance(value, float):
        raise ValueError("float type required")
    return struct.pack('>d', value)


def floating_point(value):
    """Encode a floating point value.

    :param float value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, float):
        raise ValueError("float type required")
    return struct.pack('>f', value)


def long_int(value):
    """Encode a long integer.

    :param int value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, int):
        raise ValueError("int type required")
    if value < -2147483648 or value > 2147483647:
        raise ValueError("Long integer range: -2147483648 to 2147483647")
    return struct.pack('>l', value)


def long_long_int(value):
    """Encode a long-long int.

    :param long or int value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, int):
        raise ValueError("int type required")
    if value < -9223372036854775808 or value > 9223372036854775807:
        raise ValueError("long-long integer range: "
                         "-9223372036854775808 to 9223372036854775807")
    return struct.pack('>q', value)


def long_string(value):
    """Encode a string.

    :param str value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, str):
        raise ValueError("str type required")
    return struct.pack('>I', len(value)) + bytes(value, 'utf-8')


def octet(value):
    """Encode an octet value.

    :param value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, int):
        raise ValueError("int type required")
    return struct.pack('B', value)


def short_int(value):
    """Encode a short integer.

    :param int value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, int):
        raise ValueError("int type required")
    if value < -32768 or value > 32767:
        raise ValueError("Short range: -32768 to 32767")
    return struct.pack('>H', value)


def short_string(value):
    """ Encode a string.

    :param str value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, str):
        raise ValueError("str type required, received %s:%r" % (type(value),
                                                                value))
    return struct.pack('B', len(value)) + bytes(value, 'utf-8')


def timestamp(value):
    """Encode a datetime.datetime object or time.struct_time.

    :param datetime.datetime or time.struct_time value value: Value to encode
    :rtype: bytes

    """
    if isinstance(value, datetime.datetime):
        value = value.timetuple()
    if isinstance(value, time.struct_time):
        return struct.pack('>Q', calendar.timegm(value))
    raise ValueError("datetime.datetime or time.struct_time type required")


def field_array(value):
    """Encode a field array from a dictionary.

    :param list value: Value to encode
    :rtype: bytes

    """
    if not isinstance(value, list):
        raise ValueError("list type required")

    data = list()
    for item in value:
        data.append(encode_table_value(item))

    output = b''.join(data)
    return struct.pack('>I', len(output)) + output


def field_table(value):
    """Encode a field table from a dictionary.

    :param dict value: Value to encode
    :rtype: bytes

    """
    # If there is no value, return a standard 4 null bytes
    if not value:
        return struct.pack('>I', 0)

    if not isinstance(value, dict):
        raise ValueError("dict type required, got %s" % type(value))

    # Iterate through all of the keys and encode the data into a table
    data = list()
    for key in sorted(value.keys()):
        # Append the field header / delimiter
        data.append(struct.pack('B', len(key)))
        data.append(bytes(key, 'utf-8'))
        try:
            data.append(encode_table_value(value[key]))
        except ValueError as err:
            raise ValueError("%s error: %s" % (key, err))

    # Join all of the data together as a string
    output = b''.join(data)
    return struct.pack('>I', len(output)) + output


def table_integer(value):
    """Determines the best type of numeric type to encode value as, preferring
    the smallest data size first.

    :param int value: Value to encode
    :rtype: bytes

    """
    # Send the appropriately sized data value
    if -32768 < value < 32767:
        return b's' + short_int(value)
    elif -2147483648 < value < 2147483647:
        return b'I' + long_int(value)
    elif -9223372036854775808 < value < 9223372036854775807:
        return b'L' + long_long_int(value)

    raise ValueError("Numeric value exceeds long-long-int max: %r" % value)


def encode_table_value(value):
    """Takes a value of any type and tries to encode it with the proper encoder

    :param any value: Value to encode
    :rtype: bytes

    """
    # Determine the field type and encode it
    if isinstance(value, bool):
        result = b't' + boolean(value)
    elif isinstance(value, int):
        result = table_integer(value)
    elif isinstance(value, _decimal.Decimal):
        result = b'D' + decimal(value)
    elif isinstance(value, float):
        result = b'f' + floating_point(value)
    elif isinstance(value, str):
        result = b'S' + long_string(value)
    elif (isinstance(value, datetime.datetime) or
          isinstance(value, time.struct_time)):
        result = b'T' + timestamp(value)
    elif isinstance(value, dict):
        result = b'F' + field_table(value)
    elif isinstance(value, list):
        result = b'A' + field_array(value)
    elif value is None:
        result = b'V'
    else:
        raise ValueError("Unknown type: %s (%r)"% (type(value), value))

    # Return the encoded value
    return result


def by_type(value, data_type):
    """Takes a value of any type and tries to encode it with the specified
    encoder.

    :param any value: Value to encode
    :param str data_type: type of data to encode
    :rtype: bytes

    """
    # Determine the field type and encode it
    if data_type == 'field_array':
        return field_array(value)
    elif data_type == 'double':
        return double(value)
    elif data_type == 'long':
        return long_int(value)
    elif data_type == 'longlong':
        return long_long_int(value)
    elif data_type == 'longstr':
        return long_string(value)
    elif data_type == 'octet':
        return octet(value)
    elif data_type == 'short':
        return short_int(value)
    elif data_type == 'shortstr':
        return short_string(value)
    elif data_type == 'table':
        return field_table(value)
    elif data_type == 'timestamp':
        return timestamp(value)
    elif data_type == 'void':
        return None
    else:
        raise ValueError("Unknown type: %s" % value)
