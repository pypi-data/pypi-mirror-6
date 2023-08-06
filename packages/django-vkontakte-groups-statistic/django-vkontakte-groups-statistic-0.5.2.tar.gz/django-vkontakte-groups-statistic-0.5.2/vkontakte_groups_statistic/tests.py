# -*- coding: utf-8 -*-
from django.test import TestCase
from models import GroupStat, GroupStatistic
from vkontakte_groups.factories import GroupFactory
from datetime import datetime, timedelta

GROUP_ID = 1

class VkontakteGroupsStatisticTest(TestCase):

    def test_fetch_statistic(self):

        group = GroupFactory(remote_id=GROUP_ID)
        self.assertEqual(GroupStat.objects.count(), 0)

        group.fetch_statistic()
        self.assertTrue(GroupStat.objects.count() > 350)

        stat = GroupStat.objects.filter(period=30)[0]
        self.assertTrue(stat.views > 0)
        self.assertTrue(stat.visitors > 0)
        self.assertNotEqual(stat.date, None)

        stat = GroupStat.objects.filter(period=1)[0]
        self.assertTrue(stat.members > 0)
        self.assertTrue(stat.views > 0)
        self.assertTrue(stat.visitors > 0)
        self.assertTrue(stat.males > 0)
        self.assertTrue(stat.females > 0)
        self.assertNotEqual(stat.date, None)

        # test date_from argument
        date_from = datetime.now() - timedelta(5)
        stat_month_count = GroupStat.objects.filter(period=30).count()
        GroupStat.objects.all().delete()

        group.fetch_statistic(date_from=date_from)
        self.assertEqual(GroupStat.objects.filter(period=1).count(), 6)
        self.assertEqual(GroupStat.objects.filter(period=30).count(), stat_month_count)

    def test_fetch_statistic_via_api(self):

        group = GroupFactory(remote_id=GROUP_ID)
        self.assertEqual(GroupStatistic.objects.count(), 0)

        group.fetch_statistic(source='api')
        self.assertNotEqual(GroupStatistic.objects.count(), 0)

        stat = GroupStatistic.objects.all()[0]
        self.assertTrue(stat.views > 0)
        self.assertTrue(stat.visitors > 0)
        self.assertTrue(stat.males > 0)
        self.assertTrue(stat.females > 0)
        self.assertNotEqual(stat.date, None)