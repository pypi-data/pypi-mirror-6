from pytest import mark
import sqlalchemy as sa
from sqlalchemy_utils.types.file import File, FileFactory
from tests import TestCase


class TestComposites(TestCase):
    def create_models(self):
        class User(self.Base):
            __tablename__ = 'user'

            id = sa.Column(sa.Integer, primary_key=True)

            avatar = FileFactory()

        self.User = User

    def test_creates_file_columns(self):
        columns = self.User.__table__.c
        assert isinstance(columns.avatar_name.type, sa.UnicodeText)
        assert isinstance(columns.avatar_content_type.type, sa.Unicode)
        assert isinstance(columns.avatar_size.type, sa.Integer)

    @mark.parameterize(
        'column', ['avatar_name', 'avatar_content_type', 'avatar_size']
    )
    def test_assigns_attributes(self):
        assert self.User.avatar_name
        assert self.User.avatar_content_type
        assert self.User.avatar_size

    def test_something(self):
        u = self.User()
        self.session.add(u)
        self.session.commit()

        user = self.session.query(self.User).get(1)
