from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

# get project root path
BASE_DIR = Path(__file__).resolve().parent.parent

# build path to json file
DATA_PATH = BASE_DIR / "data" / "onboarding.json"

with open(DATA_PATH, "r") as f:
    onboarding_data = json.load(f)


@router.get("/states")
def get_states():
    return onboarding_data["states"]


@router.get("/districts/{state}")
def get_districts(state: str):
    return onboarding_data["districts"].get(state, [])


@router.get("/crops")
def get_crops():
    return onboarding_data["crops"]