from django.test import TestCase

from core.templatetags.admin_extras import admin_analytics_data


class AdminAnalyticsDataTests(TestCase):
    def test_chart_data_is_a_mapping_for_json_script(self):
        data = admin_analytics_data()

        self.assertIsInstance(data['charts_json'], dict)
        self.assertEqual(len(data['charts_json']['labels']), 30)
        self.assertEqual(len(data['charts_json']['visits']), 30)
