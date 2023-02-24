from fastapi import APIRouter, HTTPException

from estimenergy.models import Collector


router = APIRouter()

@router.get("/collector/{collector_name}")
async def get_collector_data(collector_name):
    collector = await Collector.filter(name=collector_name).first()
    
    if collector is None:
        raise HTTPException(status_code=404, detail="Collector name not found.")
    
    current_day_cost = await collector.calculate_day_cost()
    current_day_cost_difference = await collector.calculate_day_cost_difference()
    predicted_month_kwh_raw = await collector.predict_month_kwh_raw()
    predicted_month_cost_raw = await collector.predict_month_cost_raw()
    predicted_month_cost_difference_raw = await collector.predict_month_cost_difference_raw()

    return {
        "current_day_cost": current_day_cost,
        "current_day_cost_difference": current_day_cost_difference,
        "predicted_month_kwh_raw": predicted_month_kwh_raw,
        "predicted_month_cost_raw": predicted_month_cost_raw,
        "predicted_month_cost_difference_raw": predicted_month_cost_difference_raw
    }
