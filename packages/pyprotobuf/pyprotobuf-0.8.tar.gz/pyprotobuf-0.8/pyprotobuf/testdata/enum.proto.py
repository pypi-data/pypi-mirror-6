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

    query = messages.StringField(1, required=True)
    page_number = messages.IntegerField(2)
    result_per_page = messages.IntegerField(3, default=10)
    corpus = messages.EnumField(Corpus, 4, default=Corpus.UNIVERSAL)


