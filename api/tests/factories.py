import random

import factory
from faker import Faker

from core import models

fake = Faker()


class AlertFactory(factory.Factory):
    class Meta:
        model = models.Alert

    name = factory.Faker('name')
    value = random.randint(0, 100)
    symbol = factory.LazyFunction(lambda: random.choice(['aapl', 'msft', 'nvda', 'sq']))
    frequency = factory.LazyFunction(lambda: random.choice(['1m', '5m', '15m', '4h']))