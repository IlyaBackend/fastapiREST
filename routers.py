from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models import Essence
from schemas import EssenceCreate, EssenceOut, EssenceReplace, EssenceUpdate


URL_PREFIX = '/api/essences'
SUMMARY_GET_ESSENCE_LIST = 'Получить список сущностей'
SUMMARY_CREATE_ESSENCE = 'Создать сущность'
SUMMARY_PUT_ESSENCE = 'Обновить сущность полностью'
SUMMARY_PATCH_ESSENCE = 'Частично обновить сущность'
SUMMARY_ONE_ESSENCE = 'Получить одну сущность'
SUMMARY_DELETE_ESSENCE = 'Удалить сущность'
SUMMARY_BULK_ESSENCE = 'Массовое создание сущностей'
DESC_ESSENCE_LIST_FILTERS_PAGINATIONS = (
    'Список сущностей с фильтрацией и пагинацией')
DESC_FILTERS_NAME = 'Фильтр по названию'
DESC_MIN_QUANTITY = 'Минимальное количество'
DESC_MAX_QUANTITY = 'Максимальное количество'
DESC_LIMIT_LIST = 'Количество записей на страницу'
DESC_PAGINATION_LIST = 'Смещение для пагинации'
DESC_BULK_ESSENCE = 'Создаёт несколько сущностей за один запрос'
DESC_PATCH_ESSENCE = 'Позволяет обновлять только указанные поля сущности'
ERROR_ESSENCE_NOT_FOUND = 'Сущность не найдена'
RESPONSE_DELETE_ESSENCE = 'ESSENCE DELETED'


async def get_db() -> AsyncSession:
    """Асинхронный генератор сессий базы данных."""
    async with AsyncSessionLocal() as session:
        yield session


router = APIRouter(
    prefix=URL_PREFIX,
    tags=['Essences'],
)


@router.get(
    '',
    response_model=List[EssenceOut],
    summary=SUMMARY_GET_ESSENCE_LIST,
    description=DESC_ESSENCE_LIST_FILTERS_PAGINATIONS,
)
async def list_essences(
    db: AsyncSession = Depends(get_db),
    name: Optional[str] = Query(
        default=None,
        description=DESC_FILTERS_NAME,
        example='Task',
    ),
    is_done: Optional[bool] = Query(
        default=None,
        example=True,
    ),
    min_quantity: Optional[int] = Query(
        default=None,
        ge=0,
        description=DESC_MIN_QUANTITY,
        example=1,
    ),
    max_quantity: Optional[int] = Query(
        default=None,
        ge=0,
        description=DESC_MAX_QUANTITY,
        example=10,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description=DESC_LIMIT_LIST,
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description=DESC_PAGINATION_LIST,
    ),
):
    query = select(Essence)
    if name:
        query = query.where(Essence.name.ilike(f'%{name}%'))
    if is_done is not None:
        query = query.where(Essence.is_done == is_done)
    if min_quantity is not None:
        query = query.where(Essence.quantity >= min_quantity)
    if max_quantity is not None:
        query = query.where(Essence.quantity <= max_quantity)
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


@router.get(
    '/{essence_id}',
    response_model=EssenceOut,
    summary=SUMMARY_ONE_ESSENCE,
)
async def get_essence(essence_id: int, db: AsyncSession = Depends(get_db)):
    essence = await db.get(Essence, essence_id)
    if not essence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ESSENCE_NOT_FOUND
        )
    return essence


@router.post(
    '/bulk',
    response_model=List[EssenceOut],
    status_code=status.HTTP_201_CREATED,
    summary=SUMMARY_BULK_ESSENCE,
    description=DESC_BULK_ESSENCE,
)
async def create_essences_bulk(
    essences_in: List[EssenceCreate],
    db: AsyncSession = Depends(get_db),
):
    essences = [Essence(**item.model_dump()) for item in essences_in]
    db.add_all(essences)
    await db.commit()
    for essence in essences:
        await db.refresh(essence)
    return essences


@router.post(
    '',
    response_model=EssenceOut,
    status_code=status.HTTP_201_CREATED,
    summary=SUMMARY_CREATE_ESSENCE,
)
async def create_essence(
    essence_in: Annotated[EssenceCreate, Depends()],
    db: AsyncSession = Depends(get_db),
):
    essence = Essence(**essence_in.model_dump())
    db.add(essence)
    await db.commit()
    await db.refresh(essence)
    return essence


@router.put(
    '/{essence_id}',
    response_model=EssenceOut,
    summary=SUMMARY_PUT_ESSENCE,
)
async def put_essence(
    essence_id: int,
    essence_in: EssenceReplace,
    db: AsyncSession = Depends(get_db),
):
    essence = await db.get(Essence, essence_id)
    if not essence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ESSENCE_NOT_FOUND
        )
    for key, value in essence_in.model_dump().items():
        setattr(essence, key, value)
    await db.commit()
    await db.refresh(essence)
    return essence


@router.patch(
    '/{essence_id}',
    response_model=EssenceOut,
    summary=SUMMARY_PATCH_ESSENCE,
    description=DESC_PATCH_ESSENCE,
)
async def patch_essence(
    essence_id: int,
    essence_in: EssenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    essence = await db.get(Essence, essence_id)
    if not essence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ESSENCE_NOT_FOUND
        )
    for key, value in essence_in.model_dump(exclude_unset=True).items():
        setattr(essence, key, value)
    await db.commit()
    await db.refresh(essence)
    return essence


@router.delete(
    '/{essence_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary=SUMMARY_DELETE_ESSENCE,
)
async def delete_essence(
    essence_id: int,
    db: AsyncSession = Depends(get_db),
):
    essence = await db.get(Essence, essence_id)
    if not essence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ESSENCE_NOT_FOUND
        )
    await db.delete(essence)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
