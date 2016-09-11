from zmqservices import messages


class TestMessage(object):
    message = messages.Message(data='asdf')

    def test_validate(self):
        self.message.validate()

    def test_validate_serialized_data(self):
        self.message.validate_serialized_data(self.message.data)

    def test_serialize(self):
        self.message.serialize()

    def test_deserialize(self):
        self.message.deserialize(self.message.serialize())


class TestBase64(object):
    base64 = messages.Base64(topic='test', data='asdf')

    def test_get_topic_storage_dir(self):
        self.base64.get_topic_storage_dir(self.base64.topic)

    def test_get_file_name(self):
        self.base64.get_file_name()

    def test_set_file_path(self):
        self.base64.set_file_path()

    def test_save(self):
        self.base64.save()


class TestFilePath(object):
    file_path = messages.FilePath(topic='test', data='asdf')

    def test_set_file_path(self):
        self.file_path.set_file_path()


def test_parse():
    msgs = (
        messages.Message(data='test'),
        messages.Base64(data='test'),
        messages.JSON(data='test'),
        messages.FilePath(data='test'),
        messages.Pickle(data='test'),
    )

    for message in msgs:
        assert isinstance(
            messages.parse(message.serialize()), message.__class__
        )
