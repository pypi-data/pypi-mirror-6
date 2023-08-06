import sqlalchemy as sa


class FileMixin(object):
    __abstract__ = True

    name = sa.Column(sa.UnicodeText)

    mime_type = sa.Column(sa.Unicode(255))

    def __repr__(self):
        return '%r(name=%r)' % self.name


class ImageMixin(FileMixin):
    width = sa.Column(sa.Integer)

    height = sa.Column(sa.Integer)

    def __html__(self):
        pass
