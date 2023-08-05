from protorpc import messages
import protorpc.message_types


class Test(messages.Message):
    datetime = protorpc.message_types.DateTimeField(1)


