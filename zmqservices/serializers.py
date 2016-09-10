import base64
import json
import pickle

class DataSerializer(object):
    data_type = None

    @classmethod
    def serialize(cls, data):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError()


class Unicode(DataSerializer):
    data_type = 'unicode'

    @classmethod
    def serialize(cls, data):
        if isinstance(data, str):
            return data
        return data.encode('utf-8')

    @classmethod
    def deserialize(cls, data):
        return data.decode('utf-8')


class JSON(DataSerializer):
    data_type = 'json'

    @classmethod
    def serialize(cls, data):
        return json.dumps(data)

    @classmethod
    def deserialize(cls, data):
        return json.loads(data)


class Pickle(DataSerializer):
    data_type = 'pickle'

    @classmethod
    def serialize(cls, data):
        return pickle.dumps(data)

    @classmethod
    def deserialize(cls, data):
        return pickle.loads(data)


class FilePath(JSON):
    data_type = 'file_path'


class Base64(DataSerializer):
    data_type = 'base64'

    @classmethod
    def serialize(cls, data):
        return base64.b64encode(data)

    @classmethod
    def deserialize(cls, data):
        return base64.b64decode(data)
