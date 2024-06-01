import unittest
from unittest.mock import Mock, patch

from stock_subscriptions_details_sources.stock_subscriptions_details_source_alerts import Alerts
from tests.factories import AlertFactory

class TestStockSubscriptionsDetailsSourceAlerts(unittest.TestCase):

    @patch('stock_subscriptions_details_sources.stock_subscriptions_details_source_alerts.Alert')
    def test_list_subscriptions_returns_list_of_subscriptions(self, mock_alert):
        stub_alert_models = AlertFactory.create_batch(5)
        mock_alert.objects = Mock(**{'all.return_value': stub_alert_models})
        alerts = Alerts()
        actual_subscriptions = alerts.list_subscriptions()
        # Subscriptions are pairs of (symbol, frequency) tuples
        expected_subscriptions = list((a.symbol, a.frequency) for a in stub_alert_models)
        self.assertEqual(actual_subscriptions, expected_subscriptions)
