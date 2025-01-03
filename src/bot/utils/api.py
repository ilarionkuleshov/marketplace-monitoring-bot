from bot.middlewares import ApiProvider
from database.schemas import MonitoringUpdate


async def update_monitoring(api: ApiProvider, monitoring_id: int, json_data: MonitoringUpdate) -> bool:
    """Updates the monitoring via the API.

    Args:
        api (ApiProvider): Provider for the API.
        monitoring_id (int): Monitoring ID.
        json_data (MonitoringUpdate): Monitoring update data.

    Returns:
        bool: True if the monitoring was updated successfully, False otherwise.

    """
    response_status = await api.request("PATCH", f"/monitorings/{monitoring_id}", json_data=json_data)
    return response_status == 200
