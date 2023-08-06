from pacific.db import repository_config


@repository_config(name='users', namespace='pacific')
class UsersRepository(object):
    def __init__(self, session):
        """

        :param session: SQLAlchemy's Session instance.
        :type session: :class:`sqlalchemy.orm.session.Session`
        """
        self.session = session

    def get_by_id(self, user_id):
        """

        :param user_id:
        :type user_id: int
        """
        return self.session.execute("SELECT 1").fetchone()
