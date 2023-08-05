import re
import time
import datetime

from nose.tools import with_setup, assert_raises

from billy.core import db
from billy.importers import utils


def drop_everything():
    db.metadata.drop()
    db.legislators.drop()
    db.bills.drop()
    db.committees.drop()


def test_insert_with_id_duplicate_id():
    obj = {'_id': 'whatever'}
    assert_raises(ValueError, utils.insert_with_id, obj)


@with_setup(drop_everything)
def test_insert_with_id_increments():
    obj1 = {'full_name': 'a test legislator',
            '_type': 'person',
            'state': 'ex'}
    obj2 = {'full_name': 'another legislator',
            '_type': 'person',
            'state': 'ex'}

    leg_id_re = re.compile(r'^EXL\d{6,6}$')

    id1 = utils.insert_with_id(obj1)
    assert leg_id_re.match(id1)
    found = db.legislators.find_one({'_id': id1})
    assert found['_all_ids'] == [id1]

    id2 = utils.insert_with_id(obj2)
    assert leg_id_re.match(id2)
    assert id2 != id1
    found = db.legislators.find_one({'_id': id2})
    assert found
    assert found['_all_ids'] == [id2]

    # also check the timestamp creation
    assert found['created_at'] == found['updated_at']
    assert isinstance(found['created_at'], datetime.datetime)


@with_setup(drop_everything)
def test_insert_with_id_types():
    person = {'_type': 'person', 'state': 'ex'}
    legislator = {'_type': 'person', 'state': 'ex'}
    committee = {'_type': 'committee', 'state': 'ex'}
    bill = {'_type': 'bill', 'state': 'ex'}
    other = {'_type': 'other', 'state': 'ex'}

    assert utils.insert_with_id(person).startswith('EXL')
    assert utils.insert_with_id(legislator).startswith('EXL')
    assert utils.insert_with_id(committee).startswith('EXC')
    assert utils.insert_with_id(bill).startswith('EXB')
    assert_raises(ValueError, utils.insert_with_id, other)


@with_setup(drop_everything)
def test_update():
    obj0 = {'_type': 'bill', 'state': 'ex', 'field1': 'stuff',
            'field2': 'original', '_locked_fields': ['field2']}

    id1 = utils.insert_with_id(obj0)
    obj1 = db.bills.find_one(id1)

    # Updating a bill with itself shouldn't cause 'updated_at' to be changed
    utils.update(obj1, obj1, db.bills)
    obj2 = db.bills.find_one({'_id': id1})
    assert obj2['created_at'] == obj2['updated_at'] == obj1['updated_at']

    initial_timestamp = obj2['created_at']   # we need this later

    # update with a few fields changed
    changes = {'field1': 'more stuff', 'field2': 'a change'}
    time.sleep(0.005)   # sleep long enough to avoid created_at == updated_at
    utils.update(obj1, changes, db.bills)
    obj2 = db.bills.find_one({'_id': id1})

    # check that timestamps have updated
    assert obj2['created_at'] < obj2['updated_at']
    assert initial_timestamp < obj2['updated_at']

    # make sure field1 gets overwritten and field 2 doesn't
    assert obj2['field1'] == 'more stuff'
    assert obj2['field2'] == 'original'


@with_setup(drop_everything)
def test_update_sneaky_filter():
    obj = {'_type': 'bill', 'state': 'ex', 'normal_field': 1,
           'set_field': [1, 2, 3]}

    def _set_changed(old, new):
        return set(old) != set(new)
    sneaky_filter = {'set_field': _set_changed}

    id = utils.insert_with_id(obj)
    obj = db.bills.find_one(id)

    # the set will be the same, shouldn't update
    utils.update(obj, {'set_field': [3, 2, 1]}, db.bills, sneaky_filter)
    assert obj['set_field'] == [1, 2, 3]
    assert obj['updated_at'] == obj['created_at']

    # the set now differs, should update
    utils.update(obj, {'set_field': [4, 3, 2, 1]}, db.bills, sneaky_filter)
    assert obj['set_field'] == [4, 3, 2, 1]
    assert obj['updated_at'] > obj['created_at']


def test_convert_timestamps():
    dt = datetime.datetime.now().replace(microsecond=0)
    ts = time.mktime(dt.utctimetuple())

    obj = {'date': ts,
           'actions': [{'when': ts}, {'date': ts}],
           'sources': [{'when': ts}, {'date': ts}],
           'votes': [{'when': ts}, {'date': ts}],
           }

    expect = {'date': dt,
              'actions': [{'when': dt}, {'date': dt}],
              'sources': [{'when': dt}, {'date': dt}],
              'votes': [{'when': dt}, {'date': dt}],
              }

    assert utils.convert_timestamps(obj) == expect

    # also modifies obj in place
    assert obj == expect


def test_split_name():
    obj = {'_type': 'person', 'full_name': 'Michael Stephens'}
    expect = {'_type': 'person', 'full_name': 'Michael Stephens',
              'first_name': 'Michael', 'last_name': 'Stephens',
              'suffixes': ''}
    assert utils.split_name(obj) == expect

    # Don't overwrite existing first/last name
    obj = {'_type': 'person', 'full_name': 'Michael Stephens',
           'first_name': 'Another', 'last_name': 'Name',
           'suffixes': ''}
    assert utils.split_name(obj) == obj

    # Don't try to split name for non-people
    obj = {'_type': 'not_a_person', 'full_name': 'A Name'}
    assert utils.split_name(obj) == obj


def test_make_plus_fields():
    bill = {'_type': 'bill', 'bill_id': 'AB 123',
            'title': 'An Awesome Bill',
            'extra_field': 'this is not normal',
            'actions': [{'actor': 'Tom Cruise',
                         'action': 'hero',
                         'date': 'now',
                         'superfluous': 42}]}

    expect = {'_type': 'bill', 'bill_id': 'AB 123', 'title': 'An Awesome Bill',
              '+extra_field': 'this is not normal',
              'actions': [{'actor': 'Tom Cruise', 'action': 'hero',
                           'date': 'now', '+superfluous': 42}]}

    plussed = utils.make_plus_fields(bill)

    assert plussed == expect


def test_next_big_id():
    db.test_ids.drop()
    db.vote_ids.drop()
    assert utils.next_big_id('xy', 'D', 'test_ids') == 'XYD00000001'
    assert utils.next_big_id('xy', 'D', 'test_ids') == 'XYD00000002'
    assert utils.next_big_id('xy', 'D', 'test_ids') == 'XYD00000003'
    assert utils.next_big_id('xy', 'V', 'vote_ids') == 'XYV00000001'
    db.test_ids.drop()
    assert utils.next_big_id('xy', 'D', 'test_ids') == 'XYD00000001'
    assert utils.next_big_id('xy', 'V', 'vote_ids') == 'XYV00000002'
