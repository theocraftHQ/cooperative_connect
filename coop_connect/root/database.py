from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from theocraft_coop.root.settings import Settings

settings = Settings()
engine = create_async_engine(url=str(settings.postgres_url))


async_session = async_sessionmaker(engine, expire_on_commit=False)
