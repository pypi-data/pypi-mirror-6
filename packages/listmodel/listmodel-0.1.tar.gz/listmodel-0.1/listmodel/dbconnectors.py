class MongoConnected(object):
    @classmethod
    def connect(cls, client, db, collection):
        cls.__db_client__ = client
        cls.__db_name__ = db
        cls.__collection_name__ = collection

    def save(self):
        client = self.__db_client__
        collection = client[self.__db_name__][self.__collection_name__]
        return collection.save(self.dict())
