# pylint:disable=missing-module-docstring, invalid-name, line-too-long
# pylint:disable=missing-function-docstring

import unittest

from unittest.mock import Mock, patch

from factories import AlertFactory
from stock_subscriptions_sources.alerts import Alerts

class Test_Alerts_Alerts(unittest.TestCase):

    @patch('stock_subscriptions_sources.alerts.Alert')
    def test_list_subscriptions_returns_list_of_subscriptions(self, mock_alert):
        stub_alert_models = AlertFactory.create_batch(5)
        mock_alert.objects = Mock(**{'all.return_value': stub_alert_models})
        alerts = Alerts()
        actual_subscriptions = alerts.list_subscriptions()
        # Subscriptions are pairs of (symbol, frequency) tuples
        expected_subscriptions = list((a.symbol, a.frequency, a.period) for a in stub_alert_models)
        self.assertEqual(actual_subscriptions, expected_subscriptions)
