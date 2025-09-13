from sqlalchemy import delete

from coop_connect.database.orms.cooperative_orm import Cooperative, Member
from coop_connect.database.orms.misc_orm import File
from coop_connect.database.orms.user_orm import MfaToken, User, UserBio
from coop_connect.root.coop_enums import UserType
from coop_connect.root.database import async_session


async def delete_cooperative():

    async with async_session() as session:
        await session.execute(delete(Member))
        await session.execute(delete(Cooperative))

        await session.commit()


async def delete_non_admin_users():
    async with async_session() as session:
        await session.execute(delete(MfaToken))
        await session.execute(delete(UserBio))
        await session.execute(
            delete(User).filter(User.user_type != UserType.ADMIN.value)
        )

        await session.commit()
