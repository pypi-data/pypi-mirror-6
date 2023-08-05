Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: **********************************************************
        marshmallow: simplified object serialization for REST APIs
        **********************************************************
        
        .. image:: https://badge.fury.io/py/marshmallow.png
            :target: http://badge.fury.io/py/marshmallow
            :alt: Latest version
        
        .. image:: https://travis-ci.org/sloria/marshmallow.png?branch=master
            :target: https://travis-ci.org/sloria/marshmallow
            :alt: Travis-CI
        
        Homepage: http://marshmallow.rtfd.org/
        
        
        **marshmallow** is an ORM/ODM/framework-agnostic library for converting complex datatypes, such as objects, into native Python datatypes. The serialized objects can then be rendered to standard formats such as JSON for use in a REST API.
        
        .. code-block:: python
        
            from datetime import datetime
            from marshmallow import Serializer, fields, pprint
        
            # A "model"
            class Person(object):
                def __init__(self, name):
                    self.name = name
                    self.date_born = datetime.now()
        
            # A serializer
            class PersonSerializer(Serializer):
                name = fields.String()
                date_born = fields.DateTime()
        
            person = Person("Guido van Rossum")
            serialized = PersonSerializer(person)
            pprint(serialized.data)
            # {"name": "Guido van Rossum", "date_born": "Sun, 10 Nov 2013 14:24:50 -0000"}
        
        
        Get It Now
        ==========
        
        ::
        
            $ pip install -U marshmallow
        
        
        Documentation
        =============
        
        Full documentation is available at http://marshmallow.rtfd.org/ .
        
        
        Requirements
        ============
        
        - Python >= 2.6 or >= 3.3
        
        
        License
        =======
        
        MIT licensed. See the bundled `LICENSE <https://github.com/sloria/marshmallow/blob/master/LICENSE>`_ file for more details.
        
        
        Changelog
        ---------
        
        0.4.1 (2013-12-01)
        ++++++++++++++++++
        
        * An object's ``__marshallable__`` method, if defined, takes precedence over ``__getitem__``.
        * Generator expressions can be passed to a serializer.
        * Better support for serializing list-like collections (e.g. ORM querysets).
        * Other minor bugfixes.
        
        0.4.0 (2013-11-24)
        ++++++++++++++++++
        
        * Add ``additional`` `clas Meta` option.
        * Add ``dateformat`` `class Meta` option.
        * Support for serializing UUID, date, time, and timedelta objects.
        * Remove ``Serializer.to_data`` method. Just use ``Serialize.data`` property.
        * String field defaults to empty string instead of ``None``.
        * *Backwards-incompatible*: ``isoformat`` and ``rfcformat`` functions moved to utils.py.
        * *Backwards-incompatible*: Validation functions moved to validate.py.
        * *Backwards-incompatible*: Remove types.py.
        * Reorder parameters to ``DateTime`` field (first parameter is dateformat).
        * Ensure that ``to_json`` returns bytestrings.
        * Fix bug with including an object property in ``fields`` Meta option.
        * Fix bug with passing ``None`` to a serializer.
        
        0.3.1 (2013-11-16)
        ++++++++++++++++++
        
        * Fix bug with serializing dictionaries.
        * Fix error raised when serializing empty list.
        * Add ``only`` and ``exclude`` parameters to Serializer constructor.
        * Add ``strict`` parameter and option: causes Serializer to raise an error if invalid data are passed in, rather than storing errors.
        * Updated Flask + SQLA example in docs.
        
        0.3.0 (2013-11-14)
        ++++++++++++++++++
        
        * Declaring Serializers just got easier. The *class Meta* paradigm allows you to specify fields more concisely. Can specify ``fields`` and ``exclude`` options.
        * Allow date formats to be changed by passing ``format`` parameter to ``DateTime`` field constructor. Can either be ``"rfc"`` (default), ``"iso"``, or a date format string.
        * More useful error message when declaring fields as classes (instead of an instance, which is the correct usage).
        * Rename MarshallingException -> MarshallingError.
        * Rename marshmallow.core -> marshmallow.serializer.
        
        0.2.1 (2013-11-12)
        ++++++++++++++++++
        
        * Allow prefixing field names.
        * Fix storing errors on Nested Serializers.
        * Python 2.6 support.
        
        0.2.0 (2013-11-11)
        ++++++++++++++++++
        
        * Field-level validation.
        * Add ``fields.Method``.
        * Add ``fields.Function``.
        * Allow binding of extra data to a serialized object by passing the ``extra`` param when initializing a ``Serializer``.
        * Add ``relative`` paramater to ``fields.Url`` that allows for relative URLs.
        
        0.1.0 (2013-11-10)
        ++++++++++++++++++
        
        * First release.
        
Keywords: serialization,rest,json,api
Platform: UNKNOWN
Classifier: Development Status :: 3 - Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
