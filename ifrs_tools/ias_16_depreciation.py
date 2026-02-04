"""
IAS 16 Property, Plant and Equipment Module
Calculates depreciation and impairment for fixed assets
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import math


def calculate_ias16_depreciation(
    asset_id: str,
    asset_name: str,
    cost: float,
    useful_life_years: int,
    residual_value: float,
    method: str = "straight-line",
    acquisition_date: str = None,
    reporting_date: str = None,
    accumulated_depreciation: float = 0
) -> Dict[str, Any]:
    """
    Calculate depreciation under IAS 16
    
    Args:
        asset_id: Unique asset identifier
        asset_name: Asset description
        cost: Original cost of asset
        useful_life_years: Estimated useful life
        residual_value: Estimated residual value
        method: Depreciation method ('straight-line', 'declining-balance', 'units-of-production')
        acquisition_date: Asset acquisition date (YYYY-MM-DD)
        reporting_date: Current reporting date (YYYY-MM-DD)
        accumulated_depreciation: Existing accumulated depreciation
        
    Returns:
        Dictionary with depreciation calculations and schedules
    """
    try:
        depreciable_amount = cost - residual_value
        
        if depreciable_amount <= 0:
            return {
                "asset_id": asset_id,
                "error": "Depreciable amount must be positive (cost > residual value)",
                "success": False
            }
        
        # Calculate time-based depreciation if dates provided
        years_elapsed = 0
        if acquisition_date and reporting_date:
            acq_date = datetime.strptime(acquisition_date, "%Y-%m-%d")
            rep_date = datetime.strptime(reporting_date, "%Y-%m-%d")
            years_elapsed = (rep_date - acq_date).days / 365.25
        
        # Calculate depreciation based on method
        if method == "straight-line":
            result = calculate_straight_line_depreciation(
                asset_id, asset_name, cost, useful_life_years, residual_value,
                years_elapsed, accumulated_depreciation
            )
        elif method == "declining-balance":
            result = calculate_declining_balance_depreciation(
                asset_id, asset_name, cost, useful_life_years, residual_value,
                years_elapsed, accumulated_depreciation
            )
        elif method == "units-of-production":
            # For units of production, would need additional parameters
            result = {
                "asset_id": asset_id,
                "error": "Units of production method requires additional parameters",
                "success": False
            }
        else:
            result = {
                "asset_id": asset_id,
                "error": f"Unsupported depreciation method: {method}",
                "success": False
            }
        
        return result
        
    except Exception as e:
        return {
            "asset_id": asset_id,
            "error": str(e),
            "success": False
        }


def calculate_straight_line_depreciation(
    asset_id: str,
    asset_name: str,
    cost: float,
    useful_life_years: int,
    residual_value: float,
    years_elapsed: float = 0,
    accumulated_depreciation: float = 0
) -> Dict[str, Any]:
    """
    Calculate straight-line depreciation
    """
    depreciable_amount = cost - residual_value
    annual_depreciation = depreciable_amount / useful_life_years
    
    # Calculate current accumulated depreciation
    if years_elapsed > 0:
        calculated_accumulated = min(annual_depreciation * years_elapsed, depreciable_amount)
    else:
        calculated_accumulated = accumulated_depreciation
    
    carrying_amount = cost - calculated_accumulated
    remaining_life = max(0, useful_life_years - years_elapsed)
    
    # Generate depreciation schedule
    schedule = generate_depreciation_schedule(
        cost, annual_depreciation, useful_life_years, residual_value, "straight-line"
    )
    
    return {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "cost": round(cost, 2),
        "residual_value": round(residual_value, 2),
        "depreciable_amount": round(depreciable_amount, 2),
        "useful_life_years": useful_life_years,
        "method": "straight-line",
        "annual_depreciation": round(annual_depreciation, 2),
        "years_elapsed": round(years_elapsed, 2),
        "accumulated_depreciation": round(calculated_accumulated, 2),
        "carrying_amount": round(carrying_amount, 2),
        "remaining_life": round(remaining_life, 2),
        "depreciation_rate": round(100 / useful_life_years, 2),
        "depreciation_schedule": schedule,
        "accounting_entries": generate_depreciation_entries(asset_id, annual_depreciation),
        "success": True
    }


def calculate_declining_balance_depreciation(
    asset_id: str,
    asset_name: str,
    cost: float,
    useful_life_years: int,
    residual_value: float,
    years_elapsed: float = 0,
    accumulated_depreciation: float = 0,
    rate_multiplier: float = 2.0
) -> Dict[str, Any]:
    """
    Calculate declining balance depreciation (typically double declining balance)
    """
    straight_line_rate = 1 / useful_life_years
    declining_rate = straight_line_rate * rate_multiplier
    
    # Generate schedule to calculate current position
    schedule = []
    book_value = cost
    total_accumulated = 0
    
    for year in range(1, useful_life_years + 1):
        # Calculate depreciation for this year
        depreciation_expense = book_value * declining_rate
        
        # Don't depreciate below residual value
        max_depreciation = book_value - residual_value
        depreciation_expense = min(depreciation_expense, max_depreciation)
        
        book_value -= depreciation_expense
        total_accumulated += depreciation_expense
        
        schedule.append({
            "year": year,
            "opening_book_value": round(book_value + depreciation_expense, 2),
            "depreciation_rate": round(declining_rate * 100, 2),
            "depreciation_expense": round(depreciation_expense, 2),
            "accumulated_depreciation": round(total_accumulated, 2),
            "closing_book_value": round(book_value, 2)
        })
        
        # Stop if we've reached residual value
        if book_value <= residual_value:
            break
    
    # Calculate current position based on years elapsed
    if years_elapsed > 0:
        year_index = min(int(years_elapsed), len(schedule) - 1)
        if year_index < len(schedule):
            current_accumulated = schedule[year_index]["accumulated_depreciation"]
            current_book_value = schedule[year_index]["closing_book_value"]
        else:
            current_accumulated = total_accumulated
            current_book_value = residual_value
    else:
        current_accumulated = accumulated_depreciation
        current_book_value = cost - current_accumulated
    
    return {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "cost": round(cost, 2),
        "residual_value": round(residual_value, 2),
        "useful_life_years": useful_life_years,
        "method": "declining-balance",
        "declining_rate": round(declining_rate * 100, 2),
        "years_elapsed": round(years_elapsed, 2),
        "accumulated_depreciation": round(current_accumulated, 2),
        "carrying_amount": round(current_book_value, 2),
        "depreciation_schedule": schedule,
        "accounting_entries": generate_depreciation_entries(asset_id, schedule[0]["depreciation_expense"] if schedule else 0),
        "success": True
    }


def generate_depreciation_schedule(
    cost: float,
    annual_depreciation: float,
    useful_life_years: int,
    residual_value: float,
    method: str
) -> List[Dict[str, Any]]:
    """
    Generate complete depreciation schedule
    """
    schedule = []
    accumulated = 0
    
    for year in range(1, useful_life_years + 1):
        if method == "straight-line":
            depreciation = annual_depreciation
        else:
            # For other methods, would calculate differently
            depreciation = annual_depreciation
        
        # Don't depreciate below residual value
        remaining_depreciable = cost - residual_value - accumulated
        depreciation = min(depreciation, remaining_depreciable)
        
        accumulated += depreciation
        carrying_amount = cost - accumulated
        
        schedule.append({
            "year": year,
            "depreciation_expense": round(depreciation, 2),
            "accumulated_depreciation": round(accumulated, 2),
            "carrying_amount": round(carrying_amount, 2)
        })
        
        # Stop if fully depreciated
        if carrying_amount <= residual_value:
            break
    
    return schedule


def generate_depreciation_entries(asset_id: str, annual_depreciation: float) -> List[Dict[str, Any]]:
    """
    Generate accounting entries for depreciation
    """
    return [
        {
            "entry_type": "Annual Depreciation",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": f"DEP-{asset_id}-{datetime.now().year}",
            "entries": [
                {
                    "account": "6300 - Depreciation Expense",
                    "debit": round(annual_depreciation, 2),
                    "credit": 0,
                    "description": f"Annual depreciation for asset {asset_id}"
                },
                {
                    "account": "1500 - Accumulated Depreciation",
                    "debit": 0,
                    "credit": round(annual_depreciation, 2),
                    "description": f"Accumulated depreciation for asset {asset_id}"
                }
            ]
        }
    ]


def calculate_impairment_test(
    asset_id: str,
    carrying_amount: float,
    fair_value: float = None,
    value_in_use: float = None,
    disposal_costs: float = 0
) -> Dict[str, Any]:
    """
    Perform IAS 36 impairment test
    
    Args:
        asset_id: Asset identifier
        carrying_amount: Current carrying amount
        fair_value: Fair value less costs to sell
        value_in_use: Value in use calculation
        disposal_costs: Costs to sell the asset
        
    Returns:
        Impairment test results
    """
    try:
        # Calculate recoverable amount (higher of fair value less costs to sell and value in use)
        recoverable_amounts = []
        
        if fair_value is not None:
            fair_value_less_costs = fair_value - disposal_costs
            recoverable_amounts.append(fair_value_less_costs)
        
        if value_in_use is not None:
            recoverable_amounts.append(value_in_use)
        
        if not recoverable_amounts:
            return {
                "asset_id": asset_id,
                "error": "Either fair value or value in use must be provided",
                "success": False
            }
        
        recoverable_amount = max(recoverable_amounts)
        impairment_loss = max(0, carrying_amount - recoverable_amount)
        
        return {
            "asset_id": asset_id,
            "carrying_amount": round(carrying_amount, 2),
            "fair_value": round(fair_value, 2) if fair_value else None,
            "fair_value_less_costs": round(fair_value - disposal_costs, 2) if fair_value else None,
            "value_in_use": round(value_in_use, 2) if value_in_use else None,
            "recoverable_amount": round(recoverable_amount, 2),
            "impairment_loss": round(impairment_loss, 2),
            "impairment_required": impairment_loss > 0,
            "revised_carrying_amount": round(carrying_amount - impairment_loss, 2),
            "accounting_entries": generate_impairment_entries(asset_id, impairment_loss) if impairment_loss > 0 else [],
            "success": True
        }
        
    except Exception as e:
        return {
            "asset_id": asset_id,
            "error": str(e),
            "success": False
        }


def generate_impairment_entries(asset_id: str, impairment_loss: float) -> List[Dict[str, Any]]:
    """
    Generate accounting entries for impairment loss
    """
    return [
        {
            "entry_type": "Impairment Loss",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": f"IMP-{asset_id}-{datetime.now().strftime('%Y%m%d')}",
            "entries": [
                {
                    "account": "6500 - Impairment Loss",
                    "debit": round(impairment_loss, 2),
                    "credit": 0,
                    "description": f"Impairment loss on asset {asset_id}"
                },
                {
                    "account": "1500 - Accumulated Impairment",
                    "debit": 0,
                    "credit": round(impairment_loss, 2),
                    "description": f"Accumulated impairment for asset {asset_id}"
                }
            ]
        }
    ]


def calculate_revaluation(
    asset_id: str,
    carrying_amount: float,
    fair_value: float,
    previous_revaluation_surplus: float = 0
) -> Dict[str, Any]:
    """
    Calculate revaluation under IAS 16 revaluation model
    
    Args:
        asset_id: Asset identifier
        carrying_amount: Current carrying amount
        fair_value: Current fair value
        previous_revaluation_surplus: Previous revaluation surplus for this asset
        
    Returns:
        Revaluation calculation results
    """
    try:
        revaluation_difference = fair_value - carrying_amount
        
        if revaluation_difference > 0:
            # Revaluation gain
            # First reverse any previous revaluation decrease
            gain_to_income = min(revaluation_difference, abs(previous_revaluation_surplus) if previous_revaluation_surplus < 0 else 0)
            gain_to_equity = revaluation_difference - gain_to_income
        else:
            # Revaluation loss
            # First reduce revaluation surplus
            loss_to_equity = min(abs(revaluation_difference), max(0, previous_revaluation_surplus))
            loss_to_income = abs(revaluation_difference) - loss_to_equity
            gain_to_income = -loss_to_income
            gain_to_equity = -loss_to_equity
        
        return {
            "asset_id": asset_id,
            "carrying_amount": round(carrying_amount, 2),
            "fair_value": round(fair_value, 2),
            "revaluation_difference": round(revaluation_difference, 2),
            "gain_loss_to_income": round(gain_to_income, 2),
            "gain_loss_to_equity": round(gain_to_equity, 2),
            "revised_carrying_amount": round(fair_value, 2),
            "accounting_entries": generate_revaluation_entries(asset_id, fair_value - carrying_amount, gain_to_income, gain_to_equity),
            "success": True
        }
        
    except Exception as e:
        return {
            "asset_id": asset_id,
            "error": str(e),
            "success": False
        }


def generate_revaluation_entries(asset_id: str, total_adjustment: float, gain_to_income: float, gain_to_equity: float) -> List[Dict[str, Any]]:
    """
    Generate accounting entries for revaluation
    """
    entries = []
    
    if total_adjustment != 0:
        entry = {
            "entry_type": "Asset Revaluation",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": f"REV-{asset_id}-{datetime.now().strftime('%Y%m%d')}",
            "entries": []
        }
        
        # Asset adjustment
        if total_adjustment > 0:
            entry["entries"].append({
                "account": "1500 - Property, Plant & Equipment",
                "debit": round(total_adjustment, 2),
                "credit": 0,
                "description": f"Revaluation increase for asset {asset_id}"
            })
        else:
            entry["entries"].append({
                "account": "1500 - Property, Plant & Equipment",
                "debit": 0,
                "credit": round(abs(total_adjustment), 2),
                "description": f"Revaluation decrease for asset {asset_id}"
            })
        
        # Income statement impact
        if gain_to_income > 0:
            entry["entries"].append({
                "account": "7400 - Revaluation Gain",
                "debit": 0,
                "credit": round(gain_to_income, 2),
                "description": f"Revaluation gain on asset {asset_id}"
            })
        elif gain_to_income < 0:
            entry["entries"].append({
                "account": "6600 - Revaluation Loss",
                "debit": round(abs(gain_to_income), 2),
                "credit": 0,
                "description": f"Revaluation loss on asset {asset_id}"
            })
        
        # Equity impact
        if gain_to_equity > 0:
            entry["entries"].append({
                "account": "3200 - Revaluation Surplus",
                "debit": 0,
                "credit": round(gain_to_equity, 2),
                "description": f"Revaluation surplus for asset {asset_id}"
            })
        elif gain_to_equity < 0:
            entry["entries"].append({
                "account": "3200 - Revaluation Surplus",
                "debit": round(abs(gain_to_equity), 2),
                "credit": 0,
                "description": f"Revaluation surplus reduction for asset {asset_id}"
            })
        
        entries.append(entry)
    
    return entries


# Example usage and testing
if __name__ == "__main__":
    # Test depreciation calculation
    test_asset = calculate_ias16_depreciation(
        asset_id="FA-001",
        asset_name="Manufacturing Equipment",
        cost=100000,
        useful_life_years=10,
        residual_value=10000,
        method="straight-line",
        acquisition_date="2020-01-01",
        reporting_date="2026-02-04"
    )
    
    print("IAS 16 Depreciation Test:")
    print(f"Annual Depreciation: ${test_asset['annual_depreciation']:,.2f}")
    print(f"Accumulated Depreciation: ${test_asset['accumulated_depreciation']:,.2f}")
    print(f"Carrying Amount: ${test_asset['carrying_amount']:,.2f}")
    
    # Test impairment
    impairment_test = calculate_impairment_test(
        asset_id="FA-001",
        carrying_amount=test_asset['carrying_amount'],
        fair_value=45000,
        disposal_costs=2000
    )
    
    print(f"\nImpairment Test:")
    print(f"Recoverable Amount: ${impairment_test['recoverable_amount']:,.2f}")
    print(f"Impairment Loss: ${impairment_test['impairment_loss']:,.2f}")
    print(f"Impairment Required: {impairment_test['impairment_required']}")