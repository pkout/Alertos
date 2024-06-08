#pylint: disable=missing-class-docstring

"""
MongoEngine model classes.
"""

from mongoengine import Document, StringField, IntField

class Alert(Document):
    meta = {'collection': 'alerts'}

    name = StringField(required=True)
    value = IntField(required=True, min_value=0, max_value=100)
    symbol = StringField(max_length=4, required=True)
    frequency = StringField(max_length=10, required=True)
    period = StringField(max_length=10, required=True)

    def __str__(self):
        return (
            f'<Alert name={self.name} '
            f'value={self.value} '
            f'symbol={self.symbol} '
            f'frequency={self.frequency} '
            f'period={self.period}'
            ' />'
        )