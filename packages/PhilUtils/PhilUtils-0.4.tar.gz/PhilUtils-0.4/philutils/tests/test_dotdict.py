#!/usr/bin/env python

#Name: test_dotdict.py
#Author: Philip Zerull
#Date Created: Thursday April 11, 2013


import os
import sys
import unittest
import copy
import threading
from time import sleep
from Queue import Queue
from philutils.containers import DotDict, dictapply, ThreadSafeDotDict
from philutils.tests.test_reverse_semaphore import queue2list


class ThreadTester(object):
    def __init__(self, dotdict, result_queue):
        self.dotdict = dotdict
        self.result_queue = result_queue
        self.finished = threading.Event()

    def start(self, target, *args, **kwargs):
        args2send = [target, self.dotdict]
        args2send.extend(args)
        self.thread = threading.Thread(
            target=self.main,
            args=args2send,
            kwargs=kwargs
        )
        self.thread.daemon = True
        self.daemon = True
        self.thread.start()

    def main(self, target,  *args, **kwargs):
        self.result_queue.put(target(*args, **kwargs))
        self.finished.set()


class TestProtectedDotDict(unittest.TestCase):
    def setUp(self):
        self.valuequeue = Queue()
        self.dotdict = ThreadSafeDotDict()
        self.dotdict.animal = 'monkey'
        self.dotdict.number = 444
        self.dotdict.child = DotDict()
        self.dotdict.child.animal = 'cow'
        self.dotdict.child.number = 2
        self.tester = ThreadTester(self.dotdict, self.valuequeue)

    def test_lock_utilized_when_getting_attr(self):
        args = ('animal', )
        themethod = ThreadSafeDotDict.__getattr__
        with self.dotdict.lock:
            self.tester.start(themethod, *args)
            sleep(.5)
            self.valuequeue.put('starting')
        self.tester.finished.wait(5)
        results = queue2list(self.valuequeue)
        expected = ['starting', 'monkey']
        self.assertEqual(results, expected)

    def test_lock_utilized_when_setting_attr(self):
        args = ('bug', 'ant')
        themethod = ThreadSafeDotDict.__setattr__
        with self.dotdict.lock:
            self.tester.start(themethod, *args)
            sleep(.5)
            self.assertEqual(len(self.dotdict.keys()), 3)
        self.tester.finished.wait(5)
        self.assertEqual(len(self.dotdict.keys()), 4)

    def test_lock_utilized_when_deling_attr(self):
        args = ('animal',)
        themethod = ThreadSafeDotDict.__delattr__
        with self.dotdict.lock:
            self.tester.start(themethod, *args)
            sleep(.5)
            self.assertEqual(len(self.dotdict.keys()), 3)
        self.tester.finished.wait(5)
        self.assertEqual(len(self.dotdict.keys()), 2)

    def test_lock_utilized_when_getting_dict_keys(self):
        del self.dotdict.child

        def method(somedict):
            values = set()
            for key in somedict.keys():
                values.add(somedict.pop(key))
            return values

        args = []
        with self.dotdict.lock:
            self.tester.start(method, *args)
            sleep(.5)
            tempresults = queue2list(self.valuequeue)
            self.assertEqual(tempresults, [])
            self.dotdict.bug = 'ant'
        self.tester.finished.wait(5)
        results = queue2list(self.valuequeue)
        expected = [set(['ant', 'monkey', 444])]
        self.assertEqual(results, expected)


class TestDotDict(unittest.TestCase):
    def test_getting_using_dot_notation(self):
        newdict = DotDict(fruit='banana')
        self.assertEqual(newdict.fruit, 'banana')

    def test_getting_using_bracket_notation(self):
        newdict = DotDict(animal='dog')
        self.assertEqual(newdict['animal'], 'dog')

    def test_assignment_using_dot_notation(self):
        newdict = DotDict()
        newdict.utensil = 'fork'
        self.assertEqual(newdict['utensil'], 'fork')

    def test_assignment_using_bracket_notation(self):
        newdict = DotDict()
        newdict['utensil'] = 'knife'
        self.assertEqual(newdict.utensil, 'knife')

    def test_getattr_for_defined_item(self):
        newdict = DotDict(a='b')
        self.assertEqual(getattr(newdict, 'a'), 'b')

    def test_getattr_for_classitem(self):
        newdict = DotDict()
        self.assertEqual(getattr(newdict, 'items'), newdict.items)

    def test_copy(self):
        newdict = DotDict(a='a', b=[1, 2, 3])
        thecopy = copy.copy(newdict)
        self.assertEqual(thecopy, newdict)
        self.assertNotEqual(id(thecopy), id(newdict))

    def test_deepcopy(self):
        newdict = DotDict(a='a', b=[1, 2, 3])
        thecopy = copy.deepcopy(newdict)
        self.assertEqual(thecopy, newdict)
        self.assertNotEqual(id(thecopy), id(newdict))

    def test_deepcopy_using_a_sub_dotdict(self):
        newdict = DotDict(
            a='a',
            b=DotDict(
                fruit='banana',
                animal='bear'
            )
        )
        thecopy = copy.deepcopy(newdict)
        self.assertEqual(thecopy, newdict)
        self.assertNotEqual(id(thecopy), id(newdict))

    def test_that_deepcopy_is_idempotent(self):
        firstdict = DotDict(a=1, b=2)
        deep = copy.deepcopy
        self.assertEqual(deep(firstdict), deep(deep(firstdict)))

    def test_catching_infinite_deepcopying(self):
        firstdict = DotDict(a='a', b='b')
        seconddict = DotDict(a=firstdict, b='boy')
        firstdict.c = seconddict
        self.assertRaises(ValueError, copy.deepcopy, firstdict)

    def test_usage_of_key_unusable_by_dot_notation(self):
        newdict = DotDict()
        newdict["can't be|used*"] = 5
        self.assertEqual(newdict["can't be|used*"], 5)

    def test_looping_over_keys_defined_using_dot_notation(self):
        newdict = DotDict(a=1, b=2, c=3)
        for key in newdict:
            self.assertIn(key, ['a', 'b', 'c'])
        for item in ['a', 'b', 'c']:
            self.assertIn(item, newdict)

    def test_assignment_of_reserved_word_doesnt_override_dict_behavior(self):
        newdict = DotDict(items=456)
        result = list(newdict.items())
        self.assertEqual(result, [('items', 456)])

    def test_getting_preset_reserved_word_returns_class_method(self):
        newdict = DotDict(values='morals')
        funk = newdict.values
        self.assertEqual(set(funk()), set(['morals']))

    def test_reserved_word_assignment_accessable_using_bracket_notation(self):
        newdict = DotDict(pop='coke')
        self.assertEqual(newdict['pop'], 'coke')


class Test_dictapply(unittest.TestCase):
    def test_application_to_empty_dictionary_copies(self):
        base = dict()
        overrider = dict(a='a', b='b', c=[1, 2, 3])
        result = dictapply(base, overrider)
        self.assertEqual(result, overrider)
        self.assertNotEqual(id(result), id(overrider))

    def test_application_with_overrided_singletons(self):
        base = dict(a='a', b='b')
        overrider = dict(b='banana', c=[2, 1, 0])
        expected_result = dict(a='a', b='banana', c=[2, 1, 0])
        result = dictapply(base, overrider)
        self.assertEqual(result, expected_result)
        self.assertEqual(id(result['b']), id(overrider['b']))
        #the ids are going to be the same because they are the same string
        overrider['b'] = 'orange'
        self.assertNotEqual(result['b'], overrider['b'])

    def test_application_overidding_dingletons_with_dicts(self):
        base = dict(a='a', b='b')
        overrider = dict(b=dict(fruit='banana', animal='bear'), c='test')
        expected = dict(a='a', b=dict(fruit='banana', animal='bear'), c='test')
        result = dictapply(base, overrider)
        self.assertEqual(result, expected)

    def test_overriding_dict_with_dict(self):
        base = dict(a='a', b=dict(fruit='orange', grain='wheat'))
        overrider = dict(b=dict(fruit='banana', animal='bear'), c='test')
        expected = dict(
            a='a',
            b=dict(
                fruit='banana',
                animal='bear',
                grain='wheat'
            ),
            c='test'
        )
        result = dictapply(base, overrider)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
