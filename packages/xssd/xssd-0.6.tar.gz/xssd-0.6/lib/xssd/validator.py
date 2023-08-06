#
# Copyright 2012 Martin Owens <doctormo@gmail.com>
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

__version__ = '0.8'
__pkgname__ = 'xssd'

import re
import os
import logging

from datetime import datetime, time, date
from .parse import ParseXML
from .errors import *

"""
Validate complex data structures with an xsd definition.

Based on xsd and xml validation, this is an attempt to provide those functions
without either xml or the hidous errors given out by modules like XPath.

The idea behind the error reporting is that the errors can reflect the structure
of the original structure replacing each variable with an error code and message.

Synopse:

from xsdvalidate import Validator

val = Validator( definition )
err = val.validate( data )

print err or "All is well!"

Definitions:

A definition is a hash containing information like an xml node containing children.

An example definition for registering a user on a website:

definition = {
    'root' : [
      { 'name' : 'input', 'type' : 'newuser' },
      { 'name' : 'foo',   'type' : 'string'  },
    ],

    'simpleTypes' : {
      'confirm'  : { 'base' : 'id',   'match'     : '/input/password' },
      'rname'    : { 'base' : 'name', 'minLength' : 1 },
      'password' : { 'base' : 'id',   'minLength' : 6 },
    },

    'complexTypes' : {
      'newuser' : [
        { 'name : 'username',     'type' : 'token'                                   },
        { 'name : 'password',     'type' : 'password'                                },
        { 'name : 'confirm',      'type' : 'confirm'                                 },
        { 'name : 'firstName',    'type' : 'rname'                                   },
        { 'name : 'familyName',   'type' : 'name',  'minOccurs' : 0                  },
        { 'name : 'nickName',     'type' : 'name',  'minOccurs' : 0                  },
        { 'name : 'emailAddress', 'type' : 'email', 'minOccurs' : 1, 'maxOccurs' : 3 },
    [
      { 'name' : 'aim',    'type' : 'index'  },
      { 'name' : 'msn',    'type' : 'email'  },
      { 'name' : 'jabber', 'type' : 'email'  },
      { 'name' : 'irc',    'type' : 'string' },
    ]
      ],
    },
}


Data:

And this is an example of the data that would validate against it:

data = {
    'input' : {
      'username'     : 'abcdef',
      'password'     : '1234567',
      'confirm'      : '1234567',
      'firstName'    : 'test',
      'familyName'   : 'user',
      'nickName'     : 'foobar',
      'emailAddress' : [ 'foo@bar.com', 'some@other.or', 'great@nice.con' ],
      'msn'          : 'foo@msn.com',
    },
    'foo' : 'extra content',
}


We are asking for a username, a password typed twice, some real names, a nick name,
between 1 and 3 email addresses and at least one instant message account, foo is an
extra string of information to show that the level is arbitary. bellow the definition
and all options are explained.

Errors and Results:

The first result you get is a structure the second is a boolean, the boolean explains the total stuctures pass or fail status.

The structure that is returned is almost a mirror structure of the input:

errors = {
    'input' : {
       'username'     : 0,
       'password'     : 0,
       'confirm'      : 0,
       'firstName'    : 0,
       'familyName'   : 0,
       'nickName'     : 0,
       'emailAddress' : 0,
    }
},


DETAILED DEFINITION:

Definition Root:

  root         - The very first level of all structures, it should contain the first
                 level complex type (see below). The data by default is a hash since
                 all xml have at least one level of xml tags names.

  import       - A list of file names, local to perl that should be loaded to include
                 further and shared simple and complex types. Supported formats are
                 "perl code", xml and yml.

  simpleTypes  - A hash reference containing each simple definition which tests a
                 scalar type (see below for format of each definition)
                

  complexTypes - A hash reference containing each complex definition which tests a
                 structure (see below for definition).


Simple Types:

  A simple type is a definition which will validate data directly, it will never validate
  arrays, hashes or any future wacky structural types. In perl parlance it will only validate
  SCALAR types. These options should match the w3c simple types definition:

  base           - The name of another simple type to first test the value against.
  fixed          - The value should match this exactly.
  pattern        - Should be a regular expresion reference which matchs the value i.e qr/\w/
  minLength      - The minimum length of a string value.
  maxLength      - The maximum length of a string value.
  match          - An XPath link to another data node it should match.
  notMatch       - An XPath link to another data node it should NOT match.
  enumeration    - An array reference of possible values of which value should be one.
  custom         - Should contain a CODE reference which will be called upon to validate the value.
  minInclusive   - The minimum value of a number value inclusive, i.e greater than or eq to (>=).
  maxInclusive   - The maximum value of a number value inclusive, i.e less than of eq to (<=).
  minExclusive   - The minimum value of a number value exlusive, i.e more than (>).
  maxExclusive   - The maximum value of a number value exlusive, i.e less than (<).
  fractionDigits - The maximum number of digits on a fractional number.

Complex Types:

  A complex type is a definition which will validate a hash reference, the very first structure,
  'root' is a complex definition and follows the same syntax as all complex types. each complex
  type is a list of data which should all occur in the hash, when a list entry is a hash it
  equates to one named entry in the hash data and has the following options:

  name      - Required name of the entry in the hash data.
  minOccurs - The minimum number of the named that this data should have in it.
  maxOccurs - The maximum number of the named that this data should have in it.
  type      - The type definition which validates the contents of the data.

  Where the list entry is an array, it will toggle the combine mode and allow further list entries
  With in it this allows for parts of the sturcture to be optional only if different parts of the
  stucture exist.

Inbuilt Types:

  By default these types are available to all definitions as base types.

    string           - /^.*$/
    integer          - /^[\-]{0,1}\d+$/
    index            - /^\d+$/
    double           - /^[0-9\-\.]*$/
    token            - /^\w+$/
    boolean          - /^1|0|true|false$/
    email            - /^.+@.+\..+$/
    date             - /^\d\d\d\d-\d\d-\d\d$/ + datetime
    'time'           - /^\d\d:\d\d$/ + datetime
    datetime         - /^(\d\d\d\d-\d\d-\d\d)?[T ]?(\d\d:\d\d)?$/ + valid_date method
    percentage       - minInclusive == 0 + maxInclusive == 100 + double

"""

def test_datetime(data, stype=None):
    """Test to make sure it's a valid datetime"""
    try:
        if '-' in data and ':' in data:
            datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        elif '-' in data:
            datetime.strptime(data, "%Y-%m-%d")
        elif ':' in data:
            datetime.strptime(data, "%H:%M:%S")
        else:
            return INVALID_DATE_FORMAT
    except:
        return INVALID_DATE
    return NO_ERROR

#Primitive types: [ anyURI, base64Binary, boolean, date,
#  dateTime, decimal, double, duration, float, hexBinary,
#  gDay, gMonth, gMonthDay, gYear, gYearMonth, NOTATION,
#  QName, string, time ]

BASE_CLASSES = {
  'complexTypes': {},
  'simpleTypes': {
   'string'    : { 'pattern' : r'.*' },
   'integer'   : { 'pattern' : r'[\-]{0,1}\d+' },
   'index'     : { 'pattern' : r'\d+' },
   'double'    : { 'pattern' : r'[0-9\-\.]*' },
   'token'     : { 'base'    : r'string', 'pattern' : '\w+' },
   'boolean'   : { 'pattern' : r'1|0|true|false' },
   'email'     : { 'pattern' : r'.+@.+\..+' },
   'date'      : { 'pattern' : r'\d\d\d\d-\d\d-\d\d', 'base' : 'datetime' },
   'time'      : { 'pattern' : r'\d\d:\d\d:\d\d',     'base' : 'datetime' },
   'datetime'  : { 'pattern' : r'(\d\d\d\d-\d\d-\d\d)?[T ]?(\d\d:\d\d:\d\d)?', 'custom' : test_datetime },
   'percentage': { 'base'    : r'double', 'minInclusive' : 0, 'maxInclusive' : 100 },
   }
}


class Validator(object):
    """Validation Machine, parses data and outputs error structures.

    validator = Validator(definition, strict_root, strict_values)

    definition   - Validation structure (see main documentation)
    strict_root  - Don't automatically add a root element dictionary.
    strict_exist - Add errors for elements and attributes not in the schema.

    """
    def __init__(self, definition, strict_root=False, strict_exist=True, debug=False):
       self._strict_root  = strict_root
       self._strict_exist = strict_exist
       self._definition = None
       self._debug = debug
       if isinstance(definition, str):
           definition = self._load_file( definition, True )
       self.setDefinition( definition )

    def validate(self, data):
        """
        Validate a set of data against this validator.
        Returns an errors structure or 0 if there were no errors.
        """
        if isinstance(data, str):
            data = self._load_file( data )
        d = self._definition
        # Save the root data for this validation so it can be
        # used for xpath queries later on in the validation.
        self.current_root_data = data

        # Sometimes we want to be lazy, allow us to be.
        if 'root' not in d and not self._strict_root:
            d = { 'root' : d }
        elif not self._strict_root:
            if data != None:
                return self._validate_elements( d['root'], data )
            else:
                raise NoData()
        else:
            raise NoRootDocument()

    def setDefinition(self, definition):
        """Set the validators definition, will load it (used internally too)"""
        self._definition = self._load_definition( definition )

    def getErrorString(self, err):
        """Return a human readable string for each error code."""
        if err > 0 and err <= len(ERRORS):
            return ERRORS[err]
        return 'Invalid error code'

    def _load_definition(self, definition):
        """Internal method for loading a definition into the validator."""
        # Make sure we have base classes in our definition.
        self._update_types(definition, BASE_CLASSES)

        # Now add any includes (external imports)
        for filename in definition.get('include', []):
            include = None
            if type(filename) in (str, unicode):
                include = self._load_definition_from_file( filename )
            elif type(filename) == dict:
                include = filename
            if include:
                self._update_types(definition, include)
            else:
                raise Exception("Can't load include: %s" % str(filename))
        return definition

    def _update_types(self, definition, source):
        """Update both simple and compelx types."""
        self._update_type(definition, source, 'simpleTypes')
        self._update_type(definition, source, 'complexTypes')

    def _update_type(self, definition, source, ltype):
        """This merges the types together to get a master symbol table."""
        if not definition:
            raise ValueError("Definition not defined!")
        definition[ltype] = definition.get(ltype, {})
        definition[ltype].update(source.get(ltype, {}))

    def _load_definition_from_file(self, filename):
        """Internal method for loading a definition from a file"""
        return self._load_definition( self._load_file( filename ) )

    def _validate_elements(self, definition, data, mode=MODE_AND):
        """Internal method for validating a list of elements"""
        errors = ElementErrors(mode)

        # This should be AND or OR and controls the logic flow of the data varify
        if mode not in (MODE_AND, MODE_OR):
            raise Exception("Invalid mode '%s', should be MODE_AND or MODE_OR." % mode)
  
        if not isinstance(definition, list):
            raise Exception("Definition is not in the correct format: expected list (got %s)." % type(definition))
        
        for element in definition:
            # Element data check
            if isinstance(element, dict):
                name = element.get('name', None)
                # Skip element if it's not defined
                if not name:
                    logging.warn("Skipping element, no name")
                    continue
                # We would pass in only the data field selected, but we need everything.
                errors[name] = self._validate_element( element, data, name )
            elif isinstance(element, list):
                subr = {}
                new_mode = mode == MODE_OR and MODE_AND or MODE_OR
                errors.update(self._validate_elements( element, data, new_mode ))
            else:
                logging.warn("This is a complex type, but isn't element.")

        # These are all the left over names
        if self._strict_exist and mode == MODE_AND:
            for name in data.keys():
                if name not in errors:
                    errors[name] = INVALID_EXIST

        return errors


    def _validate_element(self, definition, all_data, name):
        """Internal method for validating a single element"""
        results = []
        proped  = False

        data = all_data.get(name, None)
        if data != None and not isinstance(data, list):
            proped = True
            data   = [ data ]

        minOccurs = int(definition.get('minOccurs', 1))
        maxOccurs =     definition.get('maxOccurs', 1)
        dataType  =     definition.get('type',      'string')
        fixed     =     definition.get('fixed',     None)
        default   =     definition.get('default',   None)

        # minOccurs checking
        if minOccurs >= 1:
           if data != None:
               if minOccurs > len(data):
                   return INVALID_MIN_OCCURS
           elif default != None:
               data = [ default ]
           else:
               return INVALID_REQUIRED
           if maxOccurs not in [ None, 'unbounded' ] and int(maxOccurs) < minOccurs:
               maxOccurs = minOccurs
        elif data == None:
            # No data and it wasn't required
            return NO_ERROR

        # maxOccurs Checking
        if maxOccurs != 'unbounded':
            if int(maxOccurs) < len(data):
                return INVALID_MAX_OCCURS
    
        for element in data:
            # Fixed checking
            if fixed != None:
                if not isinstance(element, basestring) or element != fixed:
                    results.push(INVALID_VALUE)
                    continue
            # Default checking
            if default != None and element == None:
                element = default

            # Match another node
            match = definition.get('match', None)
            nMatch = definition.get('notMatch', None)
            if match != None:
                if self._find_value( match, all_data ) != element:
                    return INVALID_MATCH
            if nMatch != None:
                if self._find_value( nMatch, all_data ) == element:
                    return INVALID_MATCH

            opts = {}
            for option in ('minLength', 'maxLength', 'complexType'):
                opts[option] = definition.get(option, None)

            # Element type checking
            result = self._validate_type( dataType, element, **opts )
            if result:
               results.append(result)

        if len(results) > 0:
            return proped and results[0] or results
        return NO_ERROR


    def _validate_type(self, typeName, data, **opts):
        """Internal method for validating a single data type"""
        definition = self._definition
        oSimpleType = definition['simpleTypes'].get(typeName, None)
        complexType = definition['complexTypes'].get(typeName,
                        opts.get('complexType', None))

        if isinstance(data, bool):
            data = data and 'true' or 'false'

        if complexType:
            if isinstance(data, dict):
                return self._validate_elements( complexType, data )
            else:
                return INVALID_COMPLEX
        elif oSimpleType:
            simpleType = oSimpleType.copy()
            simpleType.update(opts)
            base    = simpleType.get('base',    None)
            pattern = simpleType.get('pattern', None)
            custom  = simpleType.get('custom',  None)

            # Base type check
            if base:
                err = self._validate_type( base, data )
                if err:
                    return err

            # Pattern type check, assumes edge detection
            if pattern:
                try:
                    if not re.match("^%s$" % pattern, data):
                        return INVALID_PATTERN((pattern, data))
                except TypeError:
                    return INVALID_PATTERN((typeName, type(data)))

            # Custom method check
            if custom:
                if not callable(custom):
                    return INVALID_CUSTOM
                failure = custom(data, simpleType)
                if failure:
                    return failure

            # Maximum Length check
            maxLength = simpleType.get('maxLength', None)
            if maxLength != None and len(data) > int(maxLength):
                return INVALID_MAXLENGTH

            # Minimum Length check
            minLength = simpleType.get('minLength', None)
            if minLength != None and len(data) < int(minLength):
                return INVALID_MINLENGTH

            # Check Enumeration
            enum = simpleType.get('enumeration', None)
            if enum:
                if not isinstance(enum, list):
                    raise Exception("Validator Error: Enumberation not a list")
                if not data in enum:
                    return INVALID_ENUMERATION

            # This over-writes the data, so be careful
            try:
                data = long(data)
            except:
                pass

            for testName in ('minInclusive', 'maxInclusive', 'minExclusive',
                         'maxExclusive', 'fractionDigits'):
                operator = simpleType.get(testName, None)
                if operator != None:
                    if not isinstance(data, long):
                        return INVALID_NUMBER
                    if testName == 'minInclusive' and data < operator:
                        return INVALID_MIN_RANGE
                    if testName == 'maxInclusive' and data > operator:
                        return INVALID_MAX_RANGE
                    if testName == 'minExclusive' and data <= operator:
                        return INVALID_MIN_RANGE
                    if testName == 'maxExclusive' and data >= operator:
                        return INVALID_MAX_RANGE
                    # This is a bit of a hack, but I don't care so much.
                    if testName == 'fractionDigits' and '.' in str(data):
                        if len(str(data).split('.')[1]) > operator:
                            return INVALID_FRACTION
        else:
            raise NoTypeFound("Can't find type '%s'" % typeName)
        return NO_ERROR

    def _find_value(self, path, data):
        """Internal method for finding a value match (basic xpath)"""
        # Remove root path, and stop localisation
        if path[0] == '/':
            data  = self.current_root_data
            paths = path[1:].split('/')
        else:
            paths = path.split('/')

        for segment in paths:
            if isinstance(data, dict):
                try:
                    data = data[segment]
                except KeyError:
                    #logging.warn("Validator Error: Can't find key for '%s'-> %s in %s" % (path, segment, str(paths)))
                    return INVALID_XPATH(path)
            else:
                #logging.warn("Validator Error: Can't find value for '%s'-> %s in %s" % (path, segment, str(paths)))
                INVALID_XPATH(path)
        return data

    def _load_file(self, filename, definition=None):
        """
        Internal method for loading a file, must be valid perl syntax.
        Yep that's right, be bloody careful when loading from files.
        """
        if not os.path.exists(filename):
            raise Exception("file doesn't exist: %s" % filename)
        fh = open( filename, 'r' )
        content = fh.read()
        fh.close()
  
        if content[0] == '<':
            # XML File, parse and load
            parser = ParseXML( filename )
            if definition and 'XMLSchema' in content:
                data = parser.definition
            else:
                data = parser.data
        else:
            # Try and execure the code like python
            data = eval('{ '+content+' }')
        return data

