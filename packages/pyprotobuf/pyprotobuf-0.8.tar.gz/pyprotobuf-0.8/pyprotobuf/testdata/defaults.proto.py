from protorpc import messages


class SearchRequest(messages.Message):
    class Corpus(messages.Enum):
        UNIVERSAL = 0
        WEB = 1
        IMAGES = 2
        LOCAL = 3
        NEWS = 4
        PRODUCTS = 5
        VIDEO = 6

    string = messages.StringField(1, required=True, default="test")
    bool = messages.BooleanField(2, default=False)
    int = messages.IntegerField(3, default=10)
    corpus = messages.EnumField(Corpus, 4, default=Corpus.UNIVERSAL)


