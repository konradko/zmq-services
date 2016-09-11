import datetime
from uuid import uuid4
import os
import time

from zmqservices import serializers, logger, FILE_MESSAGE_STORAGE_PATH


class InvalidMessageError(Exception):
    pass


class Message(object):
    serializer = serializers.Unicode
    delimiter = "|"

    def __init__(self, *args, **kwargs):
        """
        Args:
            topic (str): topic of the message
            data (str): message data
        """
        self.serializer = kwargs.get('serializer', self.serializer)
        self.uuid = kwargs.get('uuid', str(uuid4()))
        self.timestamp = kwargs.get('timestamp', time.time())
        self.topic = kwargs.get('topic')
        self.data = kwargs.get('data')

    def validate(self):
        logger.debug("Validating message '{}'".format(self.uuid))
        try:
            self.serialize()
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))

    @classmethod
    def validate_serialized_data(cls, data):
        if cls.delimiter in data:
            raise InvalidMessageError(
                "Data contains delimiter: '{}'".format(cls.delimiter)
            )

    def serialize(self):
        """Returns serialized message

        Returns:
            str: serialized message
        """
        logger.debug("Serializing message '{}'".format(self.uuid))

        serialized_data = self.serializer.serialize(self.data)
        self.validate_serialized_data(serialized_data)

        return "{topic}{d}{uuid}{d}{timestamp}{d}{data_type}{d}{data}".format(
            d=self.delimiter,
            topic=self.topic,
            uuid=self.uuid,
            timestamp=self.timestamp,
            data_type=self.serializer.data_type,
            data=serialized_data
        )

    def deserialize(self, raw_message):
        """Deserializes a message

        Args:
            raw_message (str): serialized message

        Returns:
            Message: new instance of the message
        """
        logger.debug("Deserializing message...")
        try:
            topic, uuid, timestamp, data_type, data = raw_message.split(
                self.delimiter
            )

            if data_type != self.serializer.data_type:
                raise InvalidMessageError(
                    u"Invalid data_type '{}', "
                    "expected: '{}'".format(
                        data_type, self.data_type
                    )
                )

            data = self.serializer.deserialize(data)
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))
        else:
            logger.debug("Message '{}' deserialized".format(uuid))
            return self.__class__(
                topic=topic,
                uuid=uuid,
                timestamp=timestamp,
                data_type=data_type,
                data=data,
            )

    def __unicode__(self):
        return self.serialize()


class FileMixin(object):
    file_path = None

    @staticmethod
    def get_topic_storage_dir(topic):
        topic_storage_dir = os.path.join(
            FILE_MESSAGE_STORAGE_PATH, topic
        )

        if not os.path.exists(topic_storage_dir):
            os.makedirs(topic_storage_dir)

        return topic_storage_dir

    def get_file_name(self):
        return "{}-{}".format(
            datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            self.uuid,
        )

    def set_file_path(self, file_name=None):
        self.file_path = os.path.join(
            self.get_topic_storage_dir(self.topic),
            file_name or self.get_file_name()
        )


class Base64(FileMixin, Message):
    serializer = serializers.Base64

    def save(self, file_name=None):
        self.set_file_path(file_name)

        logger.debug("Saving message '{}' data to '{}'".format(
            self.uuid, self.file_path
        ))

        with open(self.file_path, 'w') as destination:
            destination.write(bytearray(self.data))

        logger.debug("Message '{}' data saved".format(self.uuid))


class JSON(Message):
    serializer = serializers.JSON


class Pickle(Message):
    serializer = serializers.Pickle


class FilePath(FileMixin, JSON):
    serializer = serializers.FilePath

    def set_file_path(self, *args, **kwargs):
        super(FilePath, self).set_file_path(*args, **kwargs)
        self.data = self.file_path


MESSAGE_FOR_DATA_TYPE = {
    Message.serializer.data_type: Message,
    Base64.serializer.data_type: Base64,
    JSON.serializer.data_type: JSON,
    FilePath.serializer.data_type: FilePath,
    Pickle.serializer.data_type: Pickle,
}


def parse(raw_message):
    """Parses a raw message and returns a Message instance of correct type

    Args:
        raw_message (str): serialized message

    Returns:
        Message: deserialized message
    """
    logger.debug("Deserializing message...")
    try:
        topic, uuid, timestamp, data_type, data = raw_message.split(
            Message.delimiter
        )
    except Exception as e:
        raise InvalidMessageError(u"Invalid message: {}".format(e))
    else:
        if data_type not in MESSAGE_FOR_DATA_TYPE:
            raise InvalidMessageError(
                u"Invalid message data_type '{}', "
                "allowed data types: '{}'".format(
                    data_type, ", ".join(MESSAGE_FOR_DATA_TYPE.keys())
                )
            )

        message = MESSAGE_FOR_DATA_TYPE[data_type]
        data = message.serializer.deserialize(data)

        logger.debug("Message '{}' deserialized".format(uuid))

        return message(
            topic=topic,
            uuid=uuid,
            timestamp=timestamp,
            data_type=data_type,
            data=data,
        )
