# Copyright (C) 2012-2014 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import sys
import pywbem

from LMIBaseObject import LMIWrapperBaseObject
from LMIUtil import lmi_wrap_cim_instance
from LMIUtil import lmi_wrap_cim_instance_name

class LMIInstanceName(LMIWrapperBaseObject):
    """
    LMI wrapper class representing :py:class:`CIMInstanceName`.

    :param LMIConnection conn: connection object
    :param CIMInstanceName cim_instance_name: wrapped object
    """
    def __init__(self, conn, cim_instance_name):
        if isinstance(cim_instance_name, LMIInstanceName):
            cim_instance_name = cim_instance_name.wrapped_object
        # We use __dict__ to avoid recursion potentially caused by
        # combo __setattr__ and __getattr__
        self.__dict__["_cim_instance_name"] = cim_instance_name
        super(LMIInstanceName, self).__init__(conn)

    def __cmp__(self, other):
        """
        :param LMIInstanceName other: :py:class:`LMIInstanceName` object to compare
        :returns: negative number, if self < other; 0 if self == other or positive
            number, if self > other
        :rtype: int
        """
        if not isinstance(other, LMIInstanceName):
            return -1
        return cmp(self._cim_instance_name, other._cim_instance_name)

    def __contains__(self, key):
        """
        :param string key: key name, which will be tested for presence in keybindings
        :returns: True, if the specified key is present in keybindings, False otherwise
        """
        return key in self._cim_instance_name

    def __getattr__(self, name):
        """
        Returns class member or key property.

        :param string name: class member or key property name
        :returns: class member or key property
        :raises: :py:exc:`AttributeError`
        """
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self._cim_instance_name.keys():
            member = self._cim_instance_name[name]
            if isinstance(member, pywbem.CIMInstanceName):
                member = lmi_wrap_cim_instance_name(self._conn, member)
            return member
        raise AttributeError(name)

    def __setattr__(self, name, value):
        """
        Assigns a new value to class member or key property.

        :param string name: class member or key property name
        :param value: new value to assign
        """
        if name in self._cim_instance_name.keys():
            # Convert string value into unicode
            if isinstance(value, str):
                value = unicode(value, "utf-8")
            self._cim_instance_name[name] = value
        else:
            self.__dict__[name] =  value

    def __str__(self):
        """
        :returns: string containing object path
        """
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        """
        :returns: unicode string containing object path
        """
        return unicode(self._cim_instance_name)

    def __repr__(self):
        """
        :returns: pretty string for the object
        """
        return "%s(classname=\"%s\"...)" % ( \
            self.__class__.__name__, \
            self.classname \
        )

    def associator_names(self, **kwargs):
        """
        Returns a list of associated :py:class:`LMIInstanceName` with this object.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of names by mandating that each returned name identify an
            object that shall be associated to the source object through an instance of
            this class or one of its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of names by mandating that each returned name identify an object
            that shall be either an instance of this class (or one of its subclasses) or
            be this class (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of names by mandating that each returned name identify an object that shall be
            associated to the source object through an association in which the source
            object plays the specified role. That is, the name of the property in the
            association class that refers to the source object shall match the value of
            this parameter. Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of names by mandating that each returned name identify an object that
            shall be associated to the source object through an association in which the
            named returned object plays the specified role. That is, the name of the
            property in the association class that refers to the returned object shall
            match the value of this parameter. Default value is None.
        :returns: list of associated :py:class:`LMIInstanceName` objects

        **Usage:** :ref:`associators_instance_names`.
        """
        assoc_names_list = self._conn._client._get_associator_names(
            self._cim_instance_name, **kwargs)
        return [
            lmi_wrap_cim_instance_name(self._conn, assoc_name) \
            for assoc_name in assoc_names_list
        ]

    def first_associator_name(self, **kwargs):
        """
        Returns the first associated :py:class:`LMIInstanceName` with this object.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of names by mandating that each returned name identify an
            object that shall be associated to the source object through an instance of
            this class or one of its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of names by mandating that each returned name identify an object
            that shall be either an instance of this class (or one of its subclasses) or
            be this class (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of names by mandating that each returned name identify an object that shall be
            associated to the source object through an association in which the source
            object plays the specified role. That is, the name of the property in the
            association class that refers to the source object shall match the value of
            this parameter. Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of names by mandating that each returned name identify an object that
            shall be associated to the source object through an association in which the
            named returned object plays the specified role. That is, the name of the
            property in the association class that refers to the returned object shall
            match the value of this parameter. Default value is None.
        :returns: first associated :py:class:`LMIInstanceName` object

        **Usage:** :ref:`associators_instance_names`.
        """
        result = self.associator_names(**kwargs)
        return result[0] if result else None

    def associators(self, **kwargs):
        """
        Returns a list of associated :py:class:`LMIInstance` objects with this instance.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of objects by mandating that each returned object shall be
            associated to the source object through an instance of this class or one of
            its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be either
            an instance of this class (or one of its subclasses) or be this class (or one
            of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall be associated with the
            source object through an association in which the source object plays the
            specified role. That is, the name of the property in the association class
            that refers to the source object shall match the value of this parameter.
            Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of objects by mandating that each returned object shall be associated to
            the source object through an association in which the returned object plays
            the specified role. That is, the name of the property in the association class
            that refers to the returned object shall match the value of this parameter.
            Default value is None.
        :param bool IncludeQualifiers: bool flag indicating, if all qualifiers for each
            object (including qualifiers on the object and on any returned properties)
            shall be included as ``<QUALIFIER>`` elements in the response. Default value
            is False.
        :param bool IncludeClassOrigin: bool flag indicating, if the ``CLASSORIGIN``
            attribute shall be present on all appropriate elements in each returned
            object. Default value is False.
        :param list PropertyList: if not None, the members of the array define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If *PropertyList* is an empty list, no
            properties are included in each returned object. If it is None, no additional
            filtering is defined. Default value is None.
        :returns: list of associated :py:class:`LMIInstance` objects

        **Usage:** :ref:`associators_instances`.
        """
        associators_list = self._conn._client._get_associators(
            self._cim_instance_name, **kwargs)
        return [
            lmi_wrap_cim_instance(
                self._conn, assoc, assoc.classname, assoc.path.namespace) \
            for assoc in associators_list
        ]

    def first_associator(self, **kwargs):
        """
        Returns the first associated :py:class:`LMIInstance` with this object.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of objects by mandating that each returned object shall be
            associated to the source object through an instance of this class or one of
            its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be either
            an instance of this class (or one of its subclasses) or be this class (or one
            of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall be associated with the
            source object through an association in which the source object plays the
            specified role. That is, the name of the property in the association class
            that refers to the source object shall match the value of this parameter.
            Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of objects by mandating that each returned object shall be associated to
            the source object through an association in which the returned object plays
            the specified role. That is, the name of the property in the association class
            that refers to the returned object shall match the value of this parameter.
            Default value is None.
        :param bool IncludeQualifiers: bool flag indicating, if all qualifiers for each
            object (including qualifiers on the object and on any returned properties)
            shall be included as ``<QUALIFIER>`` elements in the response. Default value
            is False.
        :param bool IncludeClassOrigin: bool flag indicating, if the ``CLASSORIGIN``
            attribute shall be present on all appropriate elements in each returned
            object. Default value is False.
        :param list PropertyList: if not None, the members of the array define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If it is None, no additional
            filtering is defined. Default value is None.
        :returns: first associated :py:class:`LMIInstance`

        **Usage:** :ref:`associators_instances`.
        """
        result = self.associators(**kwargs)
        return result[0] if result else None

    def reference_names(self, **kwargs):
        """
        Returns a list of association :py:class:`LMIInstanceName` objects with this
        object.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of object names by mandating that each returned Object Name
            identify an instance of this class (or one of its subclasses) or this class
            (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of object names by mandating that each returned object name shall identify an
            object that refers to the target instance through a property with a name that
            matches the value of this parameter. Default value is None.
        :returns: list of association :py:class:`LMIInstanceName` objects

        **Usage:** :ref:`references_instance_names`.
        """
        reference_names_list = self._conn._client._get_reference_names(
            self._cim_instance_name, **kwargs)
        return [
            lmi_wrap_cim_instance_name(self._conn, ref_name) \
            for ref_name in reference_names_list
        ]

    def first_reference_name(self, **kwargs):
        """
        Returns the first association :py:class:`LMIInstanceName` with this object.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of object names by mandating that each returned Object Name
            identify an instance of this class (or one of its subclasses) or this class
            (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of object names by mandating that each returned object name shall identify an
            object that refers to the target instance through a property with a name that
            matches the value of this parameter. Default value is None.
        :returns: first association :py:class:`LMIInstanceName` object

        **Usage:** :ref:`references_instance_names`.
        """
        result = self.reference_names(**kwargs)
        return result[0] if result else None

    def references(self, **kwargs):
        """
        Returns a list of association :py:class:`LMIInstance` objects with this object.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be an
            instance of this class (or one of its subclasses) or this class (or one of its
            subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall refer to the target
            object through a property with a name that matches the value of this
            parameter. Default value is None.
        :param bool IncludeQualifiers: flag indicating, if all qualifiers for each object
            (including qualifiers on the object and on any returned properties) shall be
            included as ``<QUALIFIER>`` elements in the response. Default value is False.
        :param bool IncludeClassOrigin: flag indicating, if the ``CLASSORIGIN`` attribute
            shall be present on all appropriate elements in each returned object. Default
            value is False.
        :param list PropertyList: if not None, the members of the list define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If PropertyList is None, no
            additional filtering is defined. Default value is None.
        :returns: list of association :py:class:`LMIInstance` objects

        **Usage:** :ref:`references_instances`.
        """
        references_list = self._conn._client._get_references(
            self._cim_instance_name, **kwargs)
        return [
            lmi_wrap_cim_instance(
                self._conn, ref, ref.classname, ref.path.namespace) \
            for ref in references_list
        ]

    def first_reference(self, **kwargs):
        """
        Returns the first association :py:class:`LMIInstance` with this object.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be an
            instance of this class (or one of its subclasses) or this class (or one of its
            subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall refer to the target
            object through a property with a name that matches the value of this
            parameter. Default value is None.
        :param bool IncludeQualifiers: flag indicating, if all qualifiers for each object
            (including qualifiers on the object and on any returned properties) shall be
            included as ``<QUALIFIER>`` elements in the response. Default value is False.
        :param bool IncludeClassOrigin: flag indicating, if the ``CLASSORIGIN`` attribute
            shall be present on all appropriate elements in each returned object. Default
            value is False.
        :param list PropertyList: if not None, the members of the list define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If PropertyList is None, no
            additional filtering is defined. Default value is None.
        :returns: first association :py:class:`LMIInstance` object

        **Usage:** :ref:`references_instances`.
        """
        result = self.references(**kwargs)
        return result[0] if result else None

    def copy(self):
        """
        :returns: copy of itself
        """
        return lmi_wrap_cim_instance_name(
                self._conn, self._cim_instance_name.copy())

    def to_instance(self):
        """
        Creates a new :py:class:`LMIInstance` object from :py:class:`LMIInstanceName`.

        :returns: :py:class:`LMIInstance` object if the object was retrieved successfully;
            None otherwise.

        **Usage:** :ref:`instance_names_conversion`.
        """
        (cim_instance, _, errorstr) = self._conn._client._get_instance(
            self._cim_instance_name, LocalOnly=False)
        if not cim_instance:
            return None
        return lmi_wrap_cim_instance(self._conn, cim_instance,
            self._cim_instance_name.classname,
            self._cim_instance_name.namespace
        )

    def key_properties(self):
        """
        :returns: list of strings of key properties

        **Usage:** :ref:`instance_names_key_properties`.
        """
        return self._cim_instance_name.keys()

    def print_key_properties(self):
        """
        Prints out the list of key properties.

        **Usage:** :ref:`instance_names_key_properties`.
        """
        for name in self._cim_instance_name.keys():
            sys.stdout.write("%s\n" % name)

    def key_properties_dict(self):
        """
        :returns: dictionary with key properties and corresponding values
        """
        return self._cim_instance_name.keybindings.copy()

    def key_property_value(self, prop_name):
        """
        :param string prop_name: key property name
        :returns: key property value
        """
        return getattr(self, prop_name)

    @property
    def classname(self):
        """
        :returns: class name
        :rtype: string
        """
        return self._cim_instance_name.classname

    @property
    def namespace(self):
        """
        :returns: namespace name
        :rtype: string
        """
        return self._cim_instance_name.namespace

    @property
    def hostname(self):
        """
        :returns: host name
        :rtype: string
        """
        return self._cim_instance_name.host

    @property
    def wrapped_object(self):
        """
        :returns: wrapped :py:class:`CIMInstanceName` object
        """
        return self._cim_instance_name
