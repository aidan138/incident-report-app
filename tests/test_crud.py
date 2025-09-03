import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud import crud  
from app.models import portal, incidents
from app.schemas import schemas


# @pytest.mark.asyncio
# async def test_get_lifeguard_by_phone():
#     # Mock session and query
#     mock_session = AsyncMock(spec=AsyncSession)
#     mock_result = AsyncMock()
#     mock_result.scalars().first.return_value = portal.Lifeguard(phone="123456789")
#     mock_session.execute.return_value = mock_result

#     lifeguard = await crud.get_lifeguard_by_phone(mock_session, "123456789")
#     assert lifeguard.phone == "123456789"
#     mock_session.execute.assert_called_once()

# @pytest.mark.asyncio
# async def test_create_lifeguard():
#     mock_session = AsyncMock(spec=AsyncSession)
#     lifeguard_data = schemas.Lifeguard(phone="987654321")
    
#     new_lg = await crud.create_lifeguard(mock_session, lifeguard_data)
#     assert new_lg.phone == "987654321"
#     mock_session.add.assert_called_once()
#     mock_session.commit.assert_called_once()
#     mock_session.refresh.assert_called_once_with(new_lg)

@pytest.mark.asyncio
async def test_get_incident_by_phone():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_session.execute.return_value = mock_result

    mock_scalars = AsyncMock()
    mock_result.scalars.return_value = mock_scalars
    
    mock_scalars.first.return_value = incidents.Incident(creator_phone="5551234")

    incident = await crud.get_incident_by_phone(mock_session, "5551234")
    assert incident.creator_phone == "5551234"
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_incident():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_incident = MagicMock()
    mock_incident.employee_phone = "5551234"
    crud.incidents.Incident = MagicMock(return_value=mock_incident)
    # Suppose create_incident is implemented like create_lifeguard
    incident = await crud.create_incident(mock_session, "5551234")
    assert incident.employee_phone == "5551234"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(incident)
