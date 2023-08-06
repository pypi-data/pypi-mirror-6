#
# Copyright 2010 Martin Owens
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Structural Errors which track complex errors throughout a complex structure.

This includes array and dictonary problems, but errors do not stop the parsing
and validation of the rest of the structure.

These are no python-errors as they are not code errors but data error report codes.
"""

# Logic Modes
MODE_OR  = False
MODE_AND = True

class NoData(ValueError):
    """Report error about there not being any data"""

class NoRootDocument(ValueError):
    """Report error concerning the lack of root"""

class NoTypeFound(KeyError):
    """Reported when there the named type is not found"""

class ElementErrors(dict):
    """Keep track of errors as they're added, true if errors."""
    def __init__(self, mode=MODE_AND):
        self._in_error = 0
        self._added = 0
        self._mode = mode

    def __setitem__(self, key, value):
        if key in self:
            self.remove_error(self[key])
        super(ElementErrors, self).__setitem__(key, value)
        self.add_error(value)

    def __repr__(self):
        if self._added and not self._in_error:
            return "NO_ERROR"
        return super(ElementErrors, self).__repr__()

    def pop(self, key):
        self.remove_error(super(ElementErrors, self).pop(key))

    def update(self, iterable):
        """Merge in errors from a seperate validation process"""
        # Adding a batch of errors is counted as one.
        self.add_error(iterable)
        if isinstance(iterable, ElementErrors) and iterable._mode == MODE_OR:
            if iterable:
                return self.update_ok_only(iterable)
        super(ElementErrors, self).update(iterable)

    def update_ok_only(self, iterable):
        """Merge in but turn errors into OK (used for OR)"""
        for key in iterable.keys():
            if iterable[key]:
                self[key] = iterable[key]
            else:
                self[key] = NO_ERROR(iterable[key])

    def add_error(self, error):
        if error:
            self._in_error += 1
        self._added += 1

    def remove_error(self, error):
        if error:
            self._in_error -= 1
        self._added -= 1

    def __nonzero__(self):
        #print "In ERROR: %s %i:%i" % (str(self._data), self._in_error, self._added)
        if self._mode == MODE_OR:
            if self._added > 0:
                return self._in_error >= self._added
            return False
        return self._in_error != 0

    def __eq__(self, errors):
        if not isinstance(errors, dict):
            return False
            #raise ValueError("Can't compare error dictionary with %s" % type(errors))
        for (key, value) in super(ElementErrors, self).items():
            if key not in errors or errors[key] != value:
                return False
        return True

    def __ne__(self, opt):
        return not self.__eq__(opt)


class ValidateError(object):
    """Control the validation errrors and how they're displayed"""
    def __init__(self, code, msg, desc=None):
        self._code = code
        self._msg  = msg
        self._desc = desc
        self._cont = None

    def __repr__(self):
        return self._msg.upper().replace(' ','_')
        # Used for debugging, maybe enable it in a future version
        if self._cont:
            return "%s (%s)\n" % (self._msg, str(self._cont))
        return "#%d %s (%s)\n" % (self._code, self._msg, self._desc)

    def __call__(self, context):
        """When an error is called, it adds context to it"""
        if not self._cont:
            self._cont = context
        return self

    def __int__(self):
        return self._code

    def __str__(self):
        result = [ self._msg ]
        if self._desc:
            result.append( self._desc )
        return ' '.join(result)

    def __unicode__(self):
        return unicode(str(elf._msg))

    def __nonzero__(self):
        return self._code > 0

    def __eq__(self, opt):
        if isinstance(opt, ValidateError):
            opt = opt._code
        return self._code == opt

    def __ne__(self, opt):
        return not self.__eq__(opt)



# Validation Error codes
NO_ERROR            = ValidateError(0x00, 'No Error')
INVALID_TYPE        = ValidateError(0x01, 'Invalid Node Type')
INVALID_PATTERN     = ValidateError(0x02, 'Invalid Pattern', 'Regex Pattern failed')
INVALID_MINLENGTH   = ValidateError(0x03, 'Invalid MinLength', 'Not enough nodes present')
INVALID_MAXLENGTH   = ValidateError(0x04, 'Invalid MaxLength', 'Too many nodes present')
INVALID_MATCH       = ValidateError(0x05, 'Invalid Match', 'Node to Node match failed')
INVALID_VALUE       = ValidateError(0x06, 'Invalid Value', 'Fixed string did not match')
INVALID_NODE        = ValidateError(0x07, 'Invalid Node', 'Required data does not exist for this node')
INVALID_ENUMERATION = ValidateError(0x08, 'Invalid Enum', 'Data not equal to any values supplied')
INVALID_MIN_RANGE   = ValidateError(0x09, 'Invalid Min Range', 'Less than allowable range')
INVALID_MAX_RANGE   = ValidateError(0x0A, 'Invalid Max Range', 'Greater than allowable range')
INVALID_NUMBER      = ValidateError(0x0B, 'Invalid Number', 'Data is not a real number')
INVALID_COMPLEX     = ValidateError(0x0C, 'Invalid Complex', 'Failed to validate Complex Type')
INVALID_REQUIRED    = ValidateError(0x0D, 'Invalid Required', 'Data is required, but missing.')
INVALID_EXIST       = ValidateError(0x0E, 'Invalid Exist', 'This data shouldn\'t exist.')
INVALID_MIN_OCCURS  = ValidateError(0x0F, 'Invalid Occurs', 'Minium number of occurances not met')
INVALID_MAX_OCCURS  = ValidateError(0x10, 'Invalid Occurs', 'Maxium number of occurances exceeded')
INVALID_XPATH       = ValidateError(0x11, 'Invalid XPath', 'The path given doesn\'t exist.')

# When python goes wrong
CRITICAL = ValidateError(0x30, 'Critical Problem')

# Custom internal methods for checking values
INVALID_CUSTOM = ValidateError(0x40, 'Invalid Custom', 'Custom filter method returned false')

# Extra Error codes
INVALID_DATE_FORMAT = ValidateError(0x50, 'Invalid Date Format', 'Format of date can\'t be parsed')
INVALID_DATE        = ValidateError(0x51, 'Invalid Date', 'Date is out of range or otherwise not valid')

