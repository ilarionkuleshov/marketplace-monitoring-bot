from sqlalchemy.orm import DeclarativeMeta, declarative_base

DatabaseModel = declarative_base(metaclass=DeclarativeMeta)
DatabaseModelType = type[DeclarativeMeta]
