class AlertsStub:

    def __init__(self, subscriptions_count=2):
        self._subscriptions_count = subscriptions_count

    def list_subscriptions(self):
        possible_subs = [
            ('aapl', '1minute', '1day'),
            ('msft', '5minute', '10day')
        ]

        return_subs = [possible_subs[i]
                       for i in range(self._subscriptions_count)]

        return return_subs

class OneMinuteSubscriptionAlertsStub:

    def list_subscriptions(self):
        return [('aapl', '1minute', '1day')]