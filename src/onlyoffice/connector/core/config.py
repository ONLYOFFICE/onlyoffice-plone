class Config():
    docUrl = None

    def __init__(self, registry):
        self.docUrl = registry.get('onlyoffice.connector.docUrl')