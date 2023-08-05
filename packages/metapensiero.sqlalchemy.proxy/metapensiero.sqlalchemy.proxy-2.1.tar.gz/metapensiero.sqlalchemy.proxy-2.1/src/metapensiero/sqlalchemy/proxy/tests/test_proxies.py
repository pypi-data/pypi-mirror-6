# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy
# :Creato:    dom 19 ott 2008 00:04:34 CEST
# :Autore:    Lele Gaifax <lele@nautilus.homeip.net>
# :Licenza:   GNU General Public License version 3 or later
#

from datetime import date, datetime

from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey,
                        Integer, MetaData, Numeric, String, Text,
                        Table, create_engine, func, orm, select)
from sqlalchemy.exc import SAWarning, StatementError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator

from nose.tools import assert_equal, assert_greater, assert_in, assert_not_in

from metapensiero.sqlalchemy.proxy import (
    ProxiedEntity, ProxiedQuery, compare_field,
    extract_raw_conditions)


class Title(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return value and value.title()


def birthdate_info(name):
    return {
        'min': date(1980, 1, 1),
        'max': lambda fname, iname: date.today()
    }

metadata = MetaData()

persons = Table('persons', metadata,
                Column('id', Integer, primary_key=True),
                Column('firstname', String),
                Column('lastname', String),
                Column('birthdate', Date, info=birthdate_info),
                Column('timestamp', DateTime),
                Column('smart', Boolean),
                Column('somevalue', Integer),
                Column('title', Title),
                )

class Person(object):
    def __init__(self, firstname, lastname, birthdate, timestamp, smart, title):
        self.firstname = firstname
        self.lastname = lastname
        self.birthdate = birthdate
        self.timestamp = timestamp
        self.smart = smart
        self.somevalue = 0
        self.title = title

orm.mapper(Person, persons)


class Pet(declarative_base(metadata=metadata)):
    __tablename__ = 'pets'

    id = Column(Integer, primary_key=True,
                info=dict(label='id', hint='the pet id'))
    name = Column(String)
    person_id = Column(Integer, ForeignKey('persons.id'))
    birthdate = Column(Date, info=birthdate_info)
    weight = Column(Numeric(5,2),
                    info=dict(label='weight', hint='the weight'))
    notes = Column(Text, info=dict(label='notes', hint='random notes'))

    person = orm.relation(Person, backref=orm.backref('pets', order_by=id))


class Complex(declarative_base(metadata=metadata)):
    __tablename__ = 'complex'

    id1 = Column(Integer, primary_key=True,
                 info=dict(label='id1', hint='the first part of id'))
    id2 = Column(Integer, primary_key=True,
                 info=dict(label='id2', hint='the second part of id'))
    name = Column(String)


# Note: the echoed statements will be visible with "nosetests -s"
engine = create_engine('sqlite:///:memory:', echo=True)
Session = orm.sessionmaker(bind=engine)


def setup():
    import warnings

    # Silence the warning about Decimal usage with sqlite
    warnings.filterwarnings(
        action='ignore', category=SAWarning,
        message=r'.*sqlite\+pysqlite does \*not\* support Decimal objects.*')

    metadata.create_all(engine)

    session = Session()

    me = Person('Lele', 'Gaifas', date(1968, 3, 18),
                datetime(2009, 12, 7, 19, 0, 0), False,
                "perito industriale")
    session.add(me)

    bro = Person('Lallo', 'Gaifas', date(1955, 9, 21),
                 datetime(2009, 12, 7, 20, 0, 0), True,
                 "ingegnere")
    session.add(bro)

    yaku = Pet(name='Yacu')
    yaku.person = me
    session.add(yaku)

    laika = Pet(name='Laika')
    laika.person = me
    session.add(laika)

    session.commit()


def teardown():
    metadata.drop_all(engine)


def test_extract_raw_conditions():
    erc = extract_raw_conditions

    rc = erc(dict(filter_col='foo', filter_value='bar'))
    assert_equal(rc, [('foo', 'bar')])

    rc = erc(dict(filter_col='foo'))
    assert_equal(rc, [])

    rc = erc(dict(filter=[dict(property='foo', value='bar', operator='<')]))
    assert_equal(rc, [('foo', '<bar')])

    rc = erc(dict(filter=[dict(property='foo', value=1, operator='<')]))
    assert_equal(rc, [('foo', '<1')])

    rc = erc(dict(filter=[dict(property='foo', operator='<')]))
    assert_equal(rc, [])

    rc = erc(dict(filter='[{"property": "foo", "value": "bar", "operator": "<"}]'))
    assert_equal(rc, [('foo', '<bar')])

    rc = erc(dict(filter_foo='bar'))
    assert_equal(rc, [('foo', 'bar')])


def test_compare_field():
    cf = compare_field

    expr = cf(persons.c.firstname, u'>=foo')
    s = str(expr)
    assert_in(' >= ', s)

    expr = cf(persons.c.firstname, u'>foo')
    s = str(expr)
    assert_in(' > ', s)

    expr = cf(persons.c.firstname, u'<=foo')
    s = str(expr)
    assert_in(' <= ', s)

    expr = cf(persons.c.firstname, u'<foo')
    s = str(expr)
    assert_in(' < ', s)

    expr = cf(persons.c.firstname, u'=foo')
    s = str(expr)
    assert_in(' = ', s)

    expr = cf(persons.c.firstname, u'<>foo')
    s = str(expr)
    assert_in(' != ', s)

    expr = cf(persons.c.firstname, u'~=foo')
    s = str(expr)
    assert_in('LIKE ', s)

    expr = cf(persons.c.firstname, u'foo')
    s = str(expr)
    assert_in('LIKE ', s)

    expr = cf(persons.c.firstname, u'~foo')
    s = str(expr)
    assert_in('LIKE ', s)

    expr = cf(persons.c.firstname, u'NULL')
    s = str(expr)
    assert_in(' IS NULL', s)

    expr = cf(persons.c.firstname, u'!NULL')
    s = str(expr)
    assert_in(' IS NOT NULL', s)

    expr = cf(persons.c.firstname, u'<>NULL')
    s = str(expr)
    assert_in(' IS NOT NULL', s)

    expr = cf(persons.c.firstname, u'foo,bar')
    s = str(expr)
    assert_in(' IN (', s)

    expr = cf(persons.c.firstname, u'<>foo,bar')
    s = str(expr)
    assert_in(' NOT IN (', s)

    expr = cf(persons.c.id, (1, 2))
    s = str(expr)
    assert_in(' IN (', s)

    expr = cf(persons.c.id, '1,2')
    s = str(expr)
    assert_in(' IN (', s)

    expr = cf(persons.c.id, dict(start=1, end=2))
    s = str(expr)
    assert_in(' BETWEEN ', s)

    expr = cf(persons.c.id, dict(start=None, end=2))
    s = str(expr)
    assert_in(' <= ', s)

    expr = cf(persons.c.id, dict(end=2))
    s = str(expr)
    assert_in(' <= ', s)

    expr = cf(persons.c.id, dict(start=1, end=None))
    s = str(expr)
    assert_in(' >= ', s)

    expr = cf(persons.c.id, dict(start=1))
    s = str(expr)
    assert_in(' >= ', s)

    try:
        expr = cf(persons.c.id, dict(start=None, end=None))
    except UserWarning:
        pass

    expr = cf(persons.c.id, '<>0')
    s = str(expr)
    # sqlite uses !=, others use <> ...
    assert (' <> ' in s) or (' != ' in s)
    assert 'NULL' not in s

    expr = cf(persons.c.birthdate, dict(start=date.today()))
    s = str(expr)
    assert_in(' >= ', s)

    expr = cf(persons.c.birthdate, dict(start=datetime.now()))
    s = str(expr)
    assert_in(' >= ', s)

    expr = cf(persons.c.birthdate, dict(end=date.today()))
    s = str(expr)
    assert_in(' <= ', s)

    expr = cf(persons.c.birthdate, dict(start=date.today(),
                                        end=date.today()))
    s = str(expr)
    assert_in(' BETWEEN ', s)

    expr = cf(persons.c.id, (1, 2, 3))
    s = str(expr)
    assert_in(' IN (', s)

    expr = cf(persons.c.id, u'1,2,3')
    s = str(expr)
    assert_in(' IN (', s)

    expr = cf(persons.c.id, u'<>1,2,3')
    s = str(expr)
    assert_in(' NOT IN (', s)

    expr = cf(persons.c.timestamp, dict(start=None, end=datetime.now()))
    s = str(expr)
    assert_in(' <= ', s)

    expr = cf(persons.c.timestamp, dict(start="2008-08-01",
                                        end=datetime.now()))
    s = str(expr)
    assert_in(' BETWEEN ', s)

    expr = cf(persons.c.timestamp, "2008-08-01T10:10:10,2009-07-01T12:12:12")
    s = str(expr)
    assert_in(' IN (', s)

    expr = cf(persons.c.timestamp, "2008-08-01T10:10:10><2009-07-01T12:12:12")
    s = str(expr)
    assert_in(' BETWEEN ', s)

    expr = cf(persons.c.id, "2><9")
    s = str(expr)
    assert_in(' BETWEEN ', s)

    expr = cf(persons.c.id, "><7")
    s = str(expr)
    assert_in(' <= ', s)

    expr = cf(persons.c.id, "2><")
    s = str(expr)
    assert_in(' >= ', s)

    expr = cf(persons.c.id, ">0")
    s = str(expr)
    assert_in(' > ', s)

    expr = cf(persons.c.smart, None)
    s = str(expr)
    assert_in(' IS NULL', s)

    expr = cf(persons.c.smart, True)
    s = str(expr)
    assert_in('smart', s)

    expr = cf(persons.c.somevalue, 1)
    s = str(expr)
    assert_in('somevalue', s)


def test_basic():
    proxy = ProxiedEntity(Person, 'id,firstname,title'.split(','))

    sas = Session()

    res = proxy(sas, result='root', count='count',
                filter_col='lastname', filter_value='foo')
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], 0)

    res = proxy(sas, result='root', count="count",
                filter_col='firstname', filter_value='Lele')
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], len(res['root']))
    assert_equal(res['root'][0].title, "Perito Industriale")


def test_boolean():
    proxy = ProxiedEntity(Person, 'id,firstname'.split(','))

    sas = Session()

    res = proxy(sas, result='root', count='count', filter_smart='true')
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], 1)

    res = proxy(sas, result='root', count="count", filter_smart='false')
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], len(res['root']))
    assert_equal(res['root'][0].firstname, u'Lele')

    res = proxy(sas, result=False, only_cols='["firstname","lastname"]')
    assert_equal(res['message'], 'Ok')


def test_basic_decl():
    proxy = ProxiedEntity(Pet)

    sas = Session()

    res = proxy(sas, result='root', count='count',
                filter_col='name', filter_value='Yacu')
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], 1)


def test_metadata():
    proxy = ProxiedEntity(Person, 'id,smart,title'.split(','),
                          dict(smart=dict(label='Some value',
                                          hint='A value from a set',
                                          dictionary=((0, 'low'),
                                                      (1, 'medium'),
                                                      (2, 'high')))))

    sas = Session()

    res = proxy(sas, success='success', result=None, metadata='metadata')
    assert_equal(res['success'], True)
    assert_equal(res['metadata'].get('root_slot', 'foo'), 'foo')
    assert_equal(len(res['metadata']['fields']), 3)
    assert_equal(res['metadata']['fields'][1]['dictionary'],
                 [[0, 'low'], [1, 'medium'], [2, 'high']])
    assert_equal(res['metadata']['fields'][2]['type'], 'string')

    proxy = ProxiedEntity(
        Person,
        'id,firstname,lastname,birthdate,somevalue'.split(','),
        dict(firstname=dict(label='First name',
                            hint='First name of the person'),
                            lastname=lambda fname: dict(label='Foo'),
             somevalue=dict(label='Some value',
                            hint='A value from a set',
                            dictionary={0: 'low',
                                        1: 'medium',
                                        2: 'high'})))
    proxy.translate = lambda msg: msg.upper()

    res = proxy(sas, success='success', result='root', count='count',
                metadata='metadata', filter_firstname='Lele', asdict=True)
    assert_equal(res['success'], True)
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], 1)
    assert_equal(len(res['metadata']['fields']), 5)
    assert_equal(res['metadata']['fields'][1]['label'], 'FIRST NAME')
    assert_equal(res['metadata']['fields'][2]['label'], 'FOO')
    assert_equal(res['metadata']['fields'][3]['min'], date(1980, 1, 1))
    assert_equal(res['metadata']['fields'][3]['max'], date.today())
    assert_equal(res['metadata']['fields'][4]['dictionary'],
                 {0: 'LOW', 1: 'MEDIUM', 2: 'HIGH'})
    assert_equal(res['metadata']['count_slot'], 'count')
    assert_equal(res['metadata']['root_slot'], 'root')
    assert_equal(res['metadata']['success_slot'], 'success')
    assert_equal(type(res['root'][0]), type({}))

    proxy = ProxiedEntity(Pet, 'id,name,birthdate,weight,notes'.split(','),
                          dict(name=dict(label='Pet name',
                                         hint='The name of this pet')))

    res = proxy(sas, result=False, metadata='metadata')
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['metadata']['fields']), 5)
    assert_equal(res['metadata']['fields'][0]['label'], 'id')
    assert_equal(res['metadata']['fields'][0]['hint'], 'the pet id')
    assert_equal(res['metadata']['fields'][1]['label'], 'Pet name')
    assert_equal(res['metadata']['fields'][1]['hint'], 'The name of this pet')
    assert_equal(res['metadata']['fields'][2]['min'], date(1980, 1, 1))
    assert_equal(res['metadata']['fields'][2]['max'], date.today())
    assert_equal(res['metadata']['fields'][3]['decimals'], 2)
    assert_equal(res['metadata']['primary_key'], 'id')

    proxy = ProxiedEntity(Complex)
    res = proxy(sas, result=False, metadata='metadata')
    assert_equal(res['metadata']['primary_key'], ['id1', 'id2'])


def test_query_metadata():
    proxy = ProxiedQuery(persons.select())

    sas = Session()

    res = proxy(sas, result=False, metadata='metadata')
    assert_equal(res['metadata']['primary_key'], 'id')

    proxy = ProxiedQuery(Complex.__table__.select())
    res = proxy(sas, result=False, metadata='metadata')
    assert_equal(res['metadata']['primary_key'], ['id1', 'id2'])

    proxy = ProxiedQuery(persons.select(), dict(id=False))
    res = proxy(sas, result=False, metadata='metadata')
    assert_not_in('id', res['metadata']['fields'])


def test_query():
    proxy = ProxiedEntity(Person)

    sas = Session()

    res = proxy(sas, query=u"Lele", fields="firstname,lastname,nickname")
    assert len(res)==1

    res = proxy(sas, query=u"perito")
    assert len(res)==1

    res = proxy(sas, query=u"aifa", fields="firstname,lastname,nickname")
    assert len(res)>1


def test_filters():
    proxy = ProxiedEntity(Person)

    sas = Session()

    res = proxy(sas, filters=[dict(property='firstname', value=u"=Lele")])
    assert_equal(len(res), 1)

    res = proxy(sas, filters=[dict(property='firstname')])
    assert_greater(len(res), 1)

    res = proxy(sas, filters=[dict(value=u'=Lele')])
    assert_greater(len(res), 1)

    res = proxy(sas, filters=[dict(property='firstname', value=u"Lele",
                                   operator='=')])
    assert_equal(len(res), 1)

    res = proxy(sas, filters=[dict(property='lastname', value=u"aifa")])
    assert_greater(len(res), 1)

    res = proxy(sas, filters=[dict(property='lastname', value=u"aifa",
                                   operator='~')])
    assert_greater(len(res), 1)


def test_dict():
    proxy = ProxiedEntity(Person, 'id,firstname,lastname'.split(','))

    sas = Session()

    res = proxy(sas, limit=1, asdict=True)
    assert len(res)==1
    p = res[0]
    for f in ('id', 'firstname', 'lastname'):
        assert_in(f, p)
    assert 'birthdate' not in p


def test_plain_entities():
    proxy = ProxiedEntity(Person)

    sas = Session()

    res = proxy(sas, filter_firstname='Lele')
    assert_equal(len(res), 1)
    p = res[0]
    assert_equal(p.firstname, 'Lele')
    assert isinstance(p, Person)


def test_sort():
    proxy = ProxiedEntity(Person)

    sas = Session()

    res = proxy(sas, sort="firstname")
    assert res[0].firstname < res[1].firstname

    res = proxy(sas, sort="firstname", dir="DESC")
    assert res[0].firstname > res[1].firstname

    res = proxy(sas, sort='[{"property":"firstname","direction":"DESC"}]')
    assert res[0].firstname > res[1].firstname


def test_sort_multiple():
    proxy = ProxiedEntity(Person)

    sas = Session()

    res = proxy(sas, sort=[dict(property="firstname", direction="ASC")])
    assert res[0].firstname < res[1].firstname

    res = proxy(sas, sort=[dict(property="firstname", direction="DESC")])
    assert res[0].firstname > res[1].firstname

    res = proxy(sas, sort=[dict(property="somevalue"),
                           dict(property="birthdate", direction="DESC")])
    assert res[0].birthdate > res[1].birthdate


def test_simple_select():
    proxy = ProxiedQuery(persons.select())

    assert_in('SELECT ', str(proxy))

    sas = Session()

    res = proxy(sas, result='root',
                filter_col='lastname', filter_value="foo")
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 0)

    res = proxy(sas, result='result',
                filter_col='lastname', filter_value="=foo")
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['result']), 0)

    res = proxy(sas, result='result',
                filter_col='firstname', filter_value="Lele")
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['result']), 1)

    res = proxy(sas, result='result', count='count',
                filter_firstname="Lele")
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['result']), res['count'])

    for none in (None, 'None', 'False', 'false'):
        res = proxy(sas, result=none, count='count')
        assert_equal(res['message'], 'Ok')
        assert_not_in(none, res)
        assert_not_in('result', res)
        assert_greater(res['count'], 1)

    res = proxy(sas, result='result', count='count', start=1, limit=1)
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['result']), 1)
    assert_greater(res['count'], 1)

    res = proxy(sas, result=True, asdict=True)
    assert_equal(len(res), 2)

    res = proxy(sas, result=None, metadata='metadata')
    assert_equal(res['message'], 'Ok')
    assert res['metadata']['fields']

    res = proxy(sas, result='True', sort="firstname")
    assert_greater(res[1].firstname, res[0].firstname)

    res = proxy(sas, sort="firstname", dir="DESC")
    assert_greater(res[0].firstname, res[1].firstname)


def test_simple_select_decl():
    proxy = ProxiedQuery(Pet.__table__.select())

    sas = Session()

    res = proxy(sas, result='root', filter_col='name', filter_value="foo")
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 0)

    res = proxy(sas, filter_name='Yacu')
    assert_equal(len(res), 1)

    res = proxy(sas, filter_='Yacu')
    assert_greater(len(res), 1)

    res = proxy(sas, filter_timestamp="2009-12-07T19:00:00,2009-12-07T19:00:00",
                result=False, count='count', format=None)
    assert_equal(res['count'], 2)

    proxy = ProxiedQuery(persons.select())

    res = proxy(sas, filter_timestamp="2009-12-07T19:00:00,2009-12-07T19:00:00",
                result=False, count='count', format=None)
    assert_equal(res['count'], 1)


def test_with_join():
    pets = Pet.__table__
    proxy = ProxiedQuery(
        select([persons.c.firstname, func.count(pets.c.id).label('number')],
               from_obj=persons.outerjoin(pets)).group_by(persons.c.firstname),
        dict(number=dict(label='Number',
                         hint='Number of pets')))

    sas = Session()

    res = proxy(sas, result='root', metadata='metadata')
    assert_equal(len(res['root']), 2)
    assert_equal(res['metadata']['fields'][1]['label'], 'Number')

    res = proxy(sas, sort="number")
    assert_equal(res[0].firstname, 'Lallo')

    res = proxy(sas, sort="number", dir="DESC")
    assert_equal(res[0].firstname, 'Lele')

    res = proxy(sas, sort='[{"property":"number","direction":"DESC"},{"property":"non-existing","direction":"ASC"}]')
    assert_equal(res[0].firstname, 'Lele')

    proxy = ProxiedQuery(
        select([persons.c.id, persons.c.birthdate, pets.c.birthdate],
               from_obj=persons.outerjoin(pets)))

    res = proxy(sas, result=False, count='count', filter_birthdate=None)
    assert_equal(res['count'], 0)

    proxy = ProxiedQuery(
        select([persons.c.firstname],
               from_obj=persons.outerjoin(pets)))

    res = proxy(sas, result=False, count='count', filter_persons_id=-1)
    assert_equal(res['count'], 0)

    res = proxy(sas, result=False, count='count', filter_weight=1)
    assert_equal(res['count'], 0)

    proxy = ProxiedQuery(
        select([persons.c.firstname, pets.c.name],
               from_obj=persons.outerjoin(pets)))

    res = proxy(sas, result=False, count='count', filter_birthdate=None)
    assert_equal(res['count'], 0)


def test_select_with_bindparams():
    from sqlalchemy.sql import bindparam

    query = select([persons.c.firstname],
                   persons.c.birthdate == bindparam('birth', type_=Date,
                                                    value=date(1955, 9, 21)))
    proxy = ProxiedQuery(query)

    sas = Session()

    res = proxy(sas, result='root')
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 1)
    assert_equal(res['root'][0][0], 'Lallo')

    res = proxy(sas, result=False, count='count')
    assert_equal(res['count'], 1)

    res = proxy(sas, result=False, count='count',
                params=dict(birth=date(2000, 1, 1)))
    assert_equal(res['count'], 0)

    res = proxy(sas, result='root',
                params=dict(birth=date(1968, 3, 18)))
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 1)
    assert_equal(res['root'][0][0], 'Lele')

    res = proxy(sas, result='root',
                params=dict(birth=date(2000, 1, 1), foo=1))
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 0)

    res = proxy(sas, result='root', params=dict(birth="1968-03-18"))
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 1)
    assert_equal(res['root'][0][0], 'Lele')


def test_select_with_typeless_bindparams():
    from sqlalchemy.sql import bindparam

    query = select([persons.c.firstname],
                   persons.c.birthdate == bindparam('birth'))
    proxy = ProxiedQuery(query)

    sas = Session()

    res = proxy(sas, result='root', params=dict(birth=None))
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 0)

    res = proxy(sas, result=False, count='count', params=dict(birth=None))
    assert_equal(res['count'], 0)

    res = proxy(sas, result='root', params=dict(birth=date(1968, 3, 18)))
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 1)
    assert_equal(res['root'][0][0], 'Lele')

    res = proxy(sas, result='root', params=dict(birth="1968-03-18"))
    assert_equal(res['message'], 'Ok')
    assert_equal(len(res['root']), 1)
    assert_equal(res['root'][0][0], 'Lele')

    res = proxy(sas, result=False, count='count',
                params=dict(birth="1968-03-18"))
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], 1)

    res = proxy(sas, result=False, count='count',
                params=dict(birth="1968-03-18",
                            foo="bar"))
    assert_equal(res['message'], 'Ok')
    assert_equal(res['count'], 1)

    try:
        proxy(sas, result=False, count='count')
    except StatementError:
        pass
    else:
        assert False, "Should raise a StatementError"


def test_orm_queries():
    from sqlalchemy.orm import Query

    sas = Session()

    query = Query([Pet])
    proxy = ProxiedEntity(query)

    res = proxy(sas, sort="name")
    assert res[0].name < res[1].name

    query = Query([Pet])
    proxy = ProxiedEntity(query, fields=['name', 'birthdate'])
    res = proxy(sas, success='success', result=None, metadata='metadata')
    assert_equal(res['success'], True)
    assert_equal(res['metadata'].get('root_slot', 'foo'), 'foo')
    assert_equal(len(res['metadata']['fields']), 2)
    assert_equal(res['metadata']['fields'][0]['label'], "Name")
