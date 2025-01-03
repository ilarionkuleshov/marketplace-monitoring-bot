from aiogram.exceptions import DetailedAiogramError

from bot.middlewares import ApiProvider
from database.schemas import MonitoringUpdate


async def update_monitoring(api: ApiProvider, monitoring_id: int, data: MonitoringUpdate) -> None:
    """Updates the monitoring via the API.

    Args:
        api (ApiProvider): Provider for the API.
        monitoring_id (int): Monitoring ID.
        data (MonitoringUpdate): Monitoring update data.

    """
    response_status = await api.request("PATCH", f"/monitorings/{monitoring_id}", json_data=data)
    if response_status != 200:
        raise DetailedAiogramError("Something went wrong. Please try again later.")
