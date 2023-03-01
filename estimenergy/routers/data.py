import datetime
from fastapi import APIRouter, HTTPException

from estimenergy.models import Collector


router = APIRouter()

@router.get("/collector/{collector_name}/data")
async def get_collector_data(collector_name):
    collector = await Collector.filter(name=collector_name).first()

    if collector is None:
        raise HTTPException(status_code=404, detail="Collector name not found.")
    
    date = datetime.datetime.now()
    
    current_day_kwh = await collector.get_day_kwh(date)
    current_day_cost = await collector.calculate_day_cost(date)
    current_day_cost_difference = await collector.calculate_day_cost_difference(date)
    predicted_month_kwh_raw = await collector.predict_month_kwh_raw(date)
    predicted_month_cost_raw = await collector.predict_month_cost_raw(date)
    predicted_month_cost_difference_raw = await collector.predict_month_cost_difference_raw(date)
    predicted_month_kwh = await collector.predict_month_kwh(date)
    predicted_month_cost = await collector.predict_month_cost(date)
    predicted_month_cost_difference = await collector.predict_month_cost_difference(date)
    predicted_year_kwh_raw = await collector.predict_year_kwh_raw(date)
    predicted_year_cost_raw = await collector.predict_year_cost_raw(date)
    predicted_year_cost_difference_raw = await collector.predict_year_cost_difference_raw(date)
    predicted_year_kwh = await collector.predict_year_kwh(date)
    predicted_year_cost = await collector.predict_year_cost(date)
    predicted_year_cost_difference = await collector.predict_year_cost_difference(date)

    return {
        "current_day_cost": current_day_cost,
        "current_day_cost_difference": current_day_cost_difference,
        "predicted_month_kwh_raw": predicted_month_kwh_raw,
        "predicted_month_cost_raw": predicted_month_cost_raw,
        "predicted_month_cost_difference_raw": predicted_month_cost_difference_raw,
        "predicted_month_kwh": predicted_month_kwh,
        "predicted_month_cost": predicted_month_cost,
        "predicted_month_cost_difference": predicted_month_cost_difference,
        "predicted_year_kwh_raw": predicted_year_kwh_raw,
        "predicted_year_cost_raw": predicted_year_cost_raw,
        "predicted_year_cost_difference_raw": predicted_year_cost_difference_raw,
        "predicted_year_kwh": predicted_year_kwh,
        "predicted_year_cost": predicted_year_cost,
        "predicted_year_cost_difference": predicted_year_cost_difference
    }
