#!/usr/bin/env python

import unittest

import decimal

from pprint import pprint

from datetime import datetime
from lxml import etree

from spyne.const import MAX_STRING_FIELD_LENGTH

from spyne.decorator import srpc
from spyne.application import Application

from spyne.model.complex import XmlAttribute
from spyne.model.complex import ComplexModel
from spyne.model.complex import Iterable
from spyne.model.complex import Array
from spyne.model.primitive import Decimal
from spyne.model.primitive import DateTime
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode

from spyne.service import ServiceBase

from spyne.util.protocol import deserialize_request_string

from spyne.util.dictdoc import get_dict_as_object
from spyne.util.dictdoc import get_object_as_dict

from spyne.util.xml import get_object_as_xml
from spyne.util.xml import get_xml_as_object
from spyne.util.xml import get_schema_documents
from spyne.util.xml import get_validation_schema


class TestXml(unittest.TestCase):
    def test_serialize(self):

        class C(ComplexModel):
            __namespace__ = "tns"
            i = Integer
            s = Unicode

        c = C(i=5, s="x")

        ret = get_object_as_xml(c, C)
        print etree.tostring(ret)
        assert ret.tag == "{tns}C"

        ret = get_object_as_xml(c, C, "X")
        print etree.tostring(ret)
        assert ret.tag == "{tns}X"

        ret = get_object_as_xml(c, C, "X", no_namespace=True)
        print etree.tostring(ret)
        assert ret.tag == "X"

        ret = get_object_as_xml(c, C, no_namespace=True)
        print etree.tostring(ret)
        assert ret.tag == "C"

    def test_deserialize(self):
        class Punk(ComplexModel):
            __namespace__ = 'some_namespace'

            a = Unicode
            b = Integer
            c = Decimal
            d = DateTime

        class Foo(ComplexModel):
            __namespace__ = 'some_other_namespace'

            a = Unicode
            b = Integer
            c = Decimal
            d = DateTime
            e = XmlAttribute(Integer)

            def __eq__(self, other):
                # remember that this is a test object
                assert (
                    self.a == other.a and
                    self.b == other.b and
                    self.c == other.c and
                    self.d == other.d and
                    self.e == other.e
                )

                return (
                    self.a == other.a and
                    self.b == other.b and
                    self.c == other.c and
                    self.d == other.d and
                    self.e == other.e
                )

        docs = get_schema_documents([Punk, Foo])
        pprint(docs)
        assert docs['s0'].tag == '{http://www.w3.org/2001/XMLSchema}schema'
        assert docs['tns'].tag == '{http://www.w3.org/2001/XMLSchema}schema'
        print()

        print("the other namespace %r:" % docs['tns'].attrib['targetNamespace'])
        assert docs['tns'].attrib['targetNamespace'] == 'some_namespace'
        print(etree.tostring(docs['tns'], pretty_print=True))
        print()

        print("the other namespace %r:" % docs['s0'].attrib['targetNamespace'])
        assert docs['s0'].attrib['targetNamespace'] == 'some_other_namespace'
        print(etree.tostring(docs['s0'], pretty_print=True))
        print()

        foo = Foo(a=u'a', b=1, c=decimal.Decimal('3.4'), d=datetime(2011,02,20), e=5)
        doc = get_object_as_xml(foo, Foo)
        print(etree.tostring(doc, pretty_print=True))
        foo_back = get_xml_as_object(doc, Foo)

        assert foo_back == foo

        # as long as it doesn't fail, it's ok.
        get_validation_schema([Punk, Foo])


class TestCDict(unittest.TestCase):
    def test_cdict(self):
        from spyne.util.cdict import cdict

        class A(object):
            pass

        class B(A):
            pass

        class C(object):
            pass

        class D:
            pass

        d = cdict({A: "fun", object: "base"})

        assert d[A] == 'fun'
        assert d[B] == 'fun'
        assert d[C] == 'base'
        try:
            d[D]
        except KeyError:
            pass
        else:
            raise Exception("Must fail.")


class TestSafeRepr(unittest.TestCase):
    def test_log_repr(self):
        from spyne.model.complex import ComplexModel
        from spyne.model.primitive import Integer
        from spyne.model.primitive import String
        from spyne.model.complex import log_repr

        class Z(ComplexModel):
            z=String

        assert 128 > MAX_STRING_FIELD_LENGTH
        assert log_repr(Z(z="a"*128)) == "Z(z='%s'(...))" % ('a' * MAX_STRING_FIELD_LENGTH)


class TestDeserialize(unittest.TestCase):
    def test_deserialize(self):
        from spyne.protocol.soap import Soap11

        class SomeService(ServiceBase):
            @srpc(Integer, _returns=Iterable(Integer))
            def some_call(yo):
                return range(yo)

        app = Application([SomeService], 'tns', in_protocol=Soap11(),
                                                out_protocol=Soap11())

        meat = 30

        string = """
            <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/">
                <x:Body>
                    <tns:some_call xmlns:tns="tns">
                        <tns:yo>%s</tns:yo>
                    </tns:some_call>
                </x:Body>
            </x:Envelope>
        """ % meat

        obj = deserialize_request_string(string, app)

        assert obj.yo == meat


class TestEtreeDict(unittest.TestCase):
    def test_simple(self):
        from lxml.etree import tostring
        from spyne.util.etreeconv import root_dict_to_etree

        assert tostring(root_dict_to_etree({'a':{'b':'c'}})) == '<a><b>c</b></a>'

class TestDictDoc(unittest.TestCase):
    def test_the(self):
        class C(ComplexModel):
            __namespace__ = "tns"
            i = Integer
            s = Unicode
            a = Array(DateTime)

            def __eq__(self, other):
                print "Yaaay!"
                return  self.i == other.i and \
                        self.s == other.s and \
                        self.a == other.a

        c = C(i=5, s="x", a=[datetime(2011,12,22)])

        for iw, ca in ((False,dict), (True,dict), (False,list), (True, list)):
            print
            print 'complex_as:', ca
            d = get_object_as_dict(c, C, complex_as=ca)
            print d
            o = get_dict_as_object(d, C, complex_as=ca)
            print o
            print c
            assert o == c


if __name__ == '__main__':
    unittest.main()
