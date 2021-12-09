from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self, host, port, user, password, db):
        SQLALCHEMY_DATABASE_URL = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}' \
                                  f'/{db}?charset=utf8&auth_plugin=mysql_native_password'
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
        )

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_session(self):
        return next(self.get_db())

    def execute_sql(self, statement):
        with self.engine.connect() as conn:
            conn.execute(statement)  # 返回值为ResultProxy类型
            conn.close()


Base = declarative_base()
