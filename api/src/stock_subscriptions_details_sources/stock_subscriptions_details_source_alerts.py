from core.models import Alert

class Alerts:

    def list_subscriptions(self):
        return list((a.symbol, a.frequency) for a in Alert.objects.all())