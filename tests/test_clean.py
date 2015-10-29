# -*- coding: utf-8; -*-
#
# (c) 2015 Alberto Planas <aplanas@gmail.com>
#
# This file is part of KManga.
#
# KManga is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KManga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KManga.  If not, see <http://www.gnu.org/licenses/>.

from datetime import date
from datetime import datetime
import unittest

import mock

from scraper.pipelines import CleanBasePipeline
from scraper.pipelines import convert_to_date
from scraper.pipelines import convert_to_number


# Use a class instead of a mock because __class__.__name__ is used
class MyItem(object):
    pass


class TestCleanBasePipeline(unittest.TestCase):

    def setUp(self):
        self.clean = CleanBasePipeline()

    def tearDown(self):
        self.clean = None

    @mock.patch('scraper.pipelines.clean.datetime')
    @mock.patch('scraper.pipelines.clean.date')
    def test_convert_to_date_relative(self, date_mock, datetime_mock):
        today = date(year=2015, month=1, day=1)
        date_mock.today.return_value = today
        self.assertEqual(convert_to_date('Today'), today)

        yesterday = date(year=2014, month=12, day=31)
        self.assertEqual(convert_to_date('Yesterday'), yesterday)
        self.assertEqual(convert_to_date('now'), today)

        now = datetime(year=2015, month=1, day=1, hour=1)
        datetime_mock.now.return_value = now
        self.assertEqual(convert_to_date('one minute ago'), today)
        self.assertEqual(convert_to_date('1 minute ago'), today)
        self.assertEqual(convert_to_date('10 minutes ago'), today)
        self.assertEqual(convert_to_date('one hour ago'), today)
        self.assertEqual(convert_to_date('1 hour ago'), today)
        self.assertEqual(convert_to_date('2 hours ago'), yesterday)

        two_days_ago = date(year=2014, month=12, day=30)
        self.assertEqual(convert_to_date('one day ago'), yesterday)
        self.assertEqual(convert_to_date('1 day ago'), yesterday)
        self.assertEqual(convert_to_date('2 days ago'), two_days_ago)

        one_week_ago = date(year=2014, month=12, day=25)
        two_weeks_ago = date(year=2014, month=12, day=18)
        self.assertEqual(convert_to_date('one week ago'), one_week_ago)
        self.assertEqual(convert_to_date('1 week ago'), one_week_ago)
        self.assertEqual(convert_to_date('2 weeks ago'), two_weeks_ago)

    def test_convert_to_date_absolute(self):
        today = date(year=2015, month=1, day=1)
        yesterday = date(year=2014, month=12, day=31)
        self.assertEqual(convert_to_date('01 January 2015 - 10:00 AM'), today)
        self.assertEqual(convert_to_date('31 December 2014 - 10:00 AM'),
                         yesterday)
        self.assertEqual(convert_to_date('01 Jan 2015'), today)
        self.assertEqual(convert_to_date('31 Dec 2014'), yesterday)
        self.assertEqual(convert_to_date('Jan 1, 2015'), today)
        self.assertEqual(convert_to_date('Dec 31, 2014'), yesterday)
        self.assertEqual(convert_to_date('01/01/2015'), today)
        self.assertEqual(convert_to_date('31/12/2014', dmy=True), yesterday)
        self.assertEqual(convert_to_date('12/31/2014', dmy=False), yesterday)
        with self.assertRaises(ValueError):
            convert_to_date('Not valid date')

    def test_convert_to_number(self):
        value_flt = convert_to_number('10k')
        value_int = convert_to_number('10k', as_int=True)
        self.assertEqual(value_flt, 10000.0)
        self.assertEqual(type(value_flt), type(10000.0))
        self.assertEqual(value_int, 10000)
        self.assertEqual(type(value_int), type(10000))
        self.assertEqual(convert_to_number('10m'), 10000000.0)
        self.assertEqual(convert_to_number('10'), 10.0)
        self.assertEqual(convert_to_number('Not valid number'), 0.0)
        self.assertEqual(convert_to_number('Not valid number', default=1), 1)

    def test_process_item_skip(self):
        spider = mock.Mock(dry_run=True)
        self.assertEqual(self.clean.process_item(None, spider), None)

    def test_process_item_no_method(self):
        spider = mock.Mock(name='spider')
        del spider.dry_run
        item = MyItem()
        self.assertEqual(self.clean.process_item(item, spider), item)

    def test_process_item_item_method(self):
        spider = mock.Mock(name='spider')
        del spider.dry_run
        item = MyItem()
        self.clean.clean_myitem = mock.Mock(return_value=item)
        self.assertEqual(self.clean.process_item(item, spider), item)
        self.clean.clean_myitem.assert_called_with(item, spider)

    def test_process_item_spider_method(self):
        spider = mock.Mock(name='spider')
        del spider.dry_run
        item = MyItem()
        self.clean.clean_spider_myitem = mock.Mock(return_value=item)
        self.assertEqual(self.clean.process_item(item, spider), item)
        self.clean.clean_spider_myitem.assert_called_with(item, spider)

    def test_as_str(self):
        self.assertEqual(self.clean._as_str([u' ', u' ']), u'')
        self.assertEqual(self.clean._as_str([u' ', u'a']), u'a')
        self.assertEqual(self.clean._as_str([u' 5', u' 0'], separator=''),
                         u'50')
