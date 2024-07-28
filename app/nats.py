import nats

from app.settings import settings


async def get_nats():
    nc = await nats.connect(settings.NATS_URL)
    try:
        yield nc
    finally:
        await nc.close()
