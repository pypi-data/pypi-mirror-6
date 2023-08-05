from protorpc import messages


class Item(messages.Message):
    aString = messages.StringField(1)
    aNumber = messages.IntegerField(2)
    aRequiredString = messages.StringField(3, required=True)
    aRepeatedString = messages.StringField(4, repeated=True)


