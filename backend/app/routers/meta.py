from fastapi import APIRouter, Depends

from app.dependencies import get_graphdb
from app.graphdb import GraphDBClient
from app.services import meta_service

router = APIRouter()


@router.get("/phases")
def phases(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_phases(db)


@router.get("/clusters")
def clusters(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_clusters(db)


@router.get("/paradigms")
def paradigms(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_paradigms(db)


@router.get("/tasks")
def tasks(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_tasks(db)


@router.get("/enums/dataset-types")
def dataset_types(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_dataset_types(db)


@router.get("/enums/conditions")
def conditions(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_conditions(db)


@router.get("/enums/performance")
def performance(db: GraphDBClient = Depends(get_graphdb)):
    return meta_service.get_performance(db)
