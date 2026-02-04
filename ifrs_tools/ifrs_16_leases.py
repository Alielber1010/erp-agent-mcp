"""
IFRS 16 Lease Accounting Module
Calculates Right-of-Use Assets and Lease Liabilities according to IFRS 16
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


def calculate_present_value(payments: List[float], discount_rate: float) -> float:
    """
    Calculate present value of lease payments
    
    Args:
        payments: List of future lease payments
        discount_rate: Incremental borrowing rate
        
    Returns:
        Present value of payments
    """
    pv = 0
    for i, payment in enumerate(payments):
        pv += payment / ((1 + discount_rate) ** (i + 1))
    return pv


def generate_payment_schedule(
    start_date: str,
    end_date: str,
    annual_payment: float,
    frequency: str = "monthly"
) -> List[Dict[str, Any]]:
    """
    Generate payment schedule for lease term
    
    Args:
        start_date: Lease start date (YYYY-MM-DD)
        end_date: Lease end date (YYYY-MM-DD)
        annual_payment: Annual lease payment
        frequency: Payment frequency (monthly, quarterly, annually)
        
    Returns:
        List of payment dates and amounts
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Calculate payment amount based on frequency
    if frequency == "monthly":
        payment_amount = annual_payment / 12
        delta = timedelta(days=30)  # Approximate monthly
    elif frequency == "quarterly":
        payment_amount = annual_payment / 4
        delta = timedelta(days=90)  # Approximate quarterly
    elif frequency == "annually":
        payment_amount = annual_payment
        delta = timedelta(days=365)  # Annual
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")
    
    schedule = []
    current_date = start
    payment_number = 1
    
    while current_date <= end:
        schedule.append({
            "payment_number": payment_number,
            "payment_date": current_date.strftime("%Y-%m-%d"),
            "payment_amount": round(payment_amount, 2)
        })
        current_date += delta
        payment_number += 1
    
    return schedule


def calculate_ifrs16_lease(
    lease_id: str,
    start_date: str,
    end_date: str,
    annual_payment: float,
    ibr_rate: float,
    frequency: str = "monthly",
    initial_direct_costs: float = 0,
    prepaid_payments: float = 0,
    lease_incentives: float = 0
) -> Dict[str, Any]:
    """
    Calculate IFRS 16 Right-of-Use Asset and Lease Liability
    
    Args:
        lease_id: Unique lease identifier
        start_date: Lease commencement date (YYYY-MM-DD)
        end_date: Lease end date (YYYY-MM-DD)
        annual_payment: Annual lease payment
        ibr_rate: Incremental borrowing rate (as decimal, e.g., 0.06 for 6%)
        frequency: Payment frequency
        initial_direct_costs: Initial direct costs incurred
        prepaid_payments: Prepaid lease payments
        lease_incentives: Lease incentives received
        
    Returns:
        Dictionary with lease calculations and schedules
    """
    try:
        # Calculate lease term
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        lease_term_days = (end - start).days
        lease_term_years = lease_term_days / 365.25
        
        # Generate payment schedule
        payment_schedule = generate_payment_schedule(start_date, end_date, annual_payment, frequency)
        
        # Extract payment amounts for PV calculation
        payments = [p["payment_amount"] for p in payment_schedule]
        
        # Calculate present value of lease payments (lease liability)
        if frequency == "monthly":
            monthly_rate = ibr_rate / 12
            lease_liability = calculate_present_value(payments, monthly_rate)
        elif frequency == "quarterly":
            quarterly_rate = ibr_rate / 4
            lease_liability = calculate_present_value(payments, quarterly_rate)
        else:  # annually
            lease_liability = calculate_present_value(payments, ibr_rate)
        
        # Calculate Right-of-Use Asset
        # ROU Asset = Lease Liability + Initial Direct Costs + Prepaid Payments - Lease Incentives
        rou_asset_initial = lease_liability + initial_direct_costs + prepaid_payments - lease_incentives
        
        # Generate amortization schedule
        amortization_schedule = generate_lease_schedule(
            lease_liability, payments, ibr_rate, frequency, start_date
        )
        
        # Calculate annual depreciation for ROU asset (straight-line)
        annual_rou_depreciation = rou_asset_initial / lease_term_years
        
        return {
            "lease_id": lease_id,
            "lease_term_years": round(lease_term_years, 2),
            "total_payments": len(payments),
            "lease_liability_initial": round(lease_liability, 2),
            "rou_asset_initial": round(rou_asset_initial, 2),
            "annual_rou_depreciation": round(annual_rou_depreciation, 2),
            "ibr_rate": ibr_rate,
            "payment_frequency": frequency,
            "payment_schedule": payment_schedule[:12],  # First 12 payments for display
            "amortization_schedule": amortization_schedule[:5],  # First 5 years for display
            "total_interest_expense": round(sum(p["interest_expense"] for p in amortization_schedule), 2),
            "accounting_entries": generate_accounting_entries(lease_id, rou_asset_initial, lease_liability),
            "success": True
        }
        
    except Exception as e:
        return {
            "lease_id": lease_id,
            "error": str(e),
            "success": False
        }


def generate_lease_schedule(
    initial_liability: float,
    payments: List[float],
    annual_rate: float,
    frequency: str,
    start_date: str
) -> List[Dict[str, Any]]:
    """
    Generate lease liability amortization schedule
    
    Args:
        initial_liability: Initial lease liability
        payments: List of payment amounts
        annual_rate: Annual interest rate
        frequency: Payment frequency
        start_date: Lease start date
        
    Returns:
        Amortization schedule by year
    """
    # Determine periodic rate
    if frequency == "monthly":
        periods_per_year = 12
        periodic_rate = annual_rate / 12
    elif frequency == "quarterly":
        periods_per_year = 4
        periodic_rate = annual_rate / 4
    else:  # annually
        periods_per_year = 1
        periodic_rate = annual_rate
    
    schedule = []
    remaining_liability = initial_liability
    start = datetime.strptime(start_date, "%Y-%m-%d")
    
    # Group payments by year
    current_year = start.year
    year_payments = 0
    year_interest = 0
    year_principal = 0
    
    for i, payment in enumerate(payments):
        # Calculate interest for this period
        interest_expense = remaining_liability * periodic_rate
        principal_payment = payment - interest_expense
        remaining_liability -= principal_payment
        
        # Determine which year this payment belongs to
        payment_date = start + timedelta(days=(i * (365 / periods_per_year)))
        payment_year = payment_date.year
        
        if payment_year == current_year:
            year_payments += payment
            year_interest += interest_expense
            year_principal += principal_payment
        else:
            # Save current year data
            if year_payments > 0:
                schedule.append({
                    "year": current_year,
                    "opening_liability": round(remaining_liability + year_principal, 2),
                    "payments": round(year_payments, 2),
                    "interest_expense": round(year_interest, 2),
                    "principal_reduction": round(year_principal, 2),
                    "closing_liability": round(remaining_liability, 2)
                })
            
            # Start new year
            current_year = payment_year
            year_payments = payment
            year_interest = interest_expense
            year_principal = principal_payment
    
    # Add final year
    if year_payments > 0:
        schedule.append({
            "year": current_year,
            "opening_liability": round(remaining_liability + year_principal, 2),
            "payments": round(year_payments, 2),
            "interest_expense": round(year_interest, 2),
            "principal_reduction": round(year_principal, 2),
            "closing_liability": round(max(0, remaining_liability), 2)
        })
    
    return schedule


def generate_accounting_entries(
    lease_id: str,
    rou_asset: float,
    lease_liability: float
) -> List[Dict[str, Any]]:
    """
    Generate initial accounting entries for lease recognition
    
    Args:
        lease_id: Lease identifier
        rou_asset: Right-of-use asset amount
        lease_liability: Lease liability amount
        
    Returns:
        List of accounting entries
    """
    return [
        {
            "entry_type": "Initial Recognition",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": f"IFRS16-{lease_id}",
            "entries": [
                {
                    "account": "1600 - Right-of-Use Assets",
                    "debit": round(rou_asset, 2),
                    "credit": 0,
                    "description": f"Recognition of ROU asset for lease {lease_id}"
                },
                {
                    "account": "2200 - Lease Liabilities",
                    "debit": 0,
                    "credit": round(lease_liability, 2),
                    "description": f"Recognition of lease liability for lease {lease_id}"
                }
            ]
        }
    ]


def calculate_lease_modification(
    original_lease: Dict[str, Any],
    modification_date: str,
    new_end_date: str = None,
    new_annual_payment: float = None,
    new_ibr_rate: float = None
) -> Dict[str, Any]:
    """
    Calculate lease modification impact under IFRS 16
    
    Args:
        original_lease: Original lease calculation results
        modification_date: Date of modification
        new_end_date: New lease end date (if extended)
        new_annual_payment: New annual payment (if changed)
        new_ibr_rate: New incremental borrowing rate
        
    Returns:
        Modification impact analysis
    """
    try:
        # This would implement lease modification logic
        # For now, return basic structure
        return {
            "modification_type": "Extension" if new_end_date else "Payment Change",
            "modification_date": modification_date,
            "original_liability": original_lease.get("lease_liability_initial", 0),
            "revised_liability": 0,  # Would calculate based on modification
            "rou_asset_adjustment": 0,  # Would calculate adjustment
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Example usage and testing
if __name__ == "__main__":
    # Test IFRS 16 calculation
    test_lease = calculate_ifrs16_lease(
        lease_id="L-001",
        start_date="2026-01-01",
        end_date="2030-12-31",
        annual_payment=48000,
        ibr_rate=0.06,
        frequency="monthly"
    )
    
    print("IFRS 16 Lease Calculation Test:")
    print(f"Lease Liability: ${test_lease['lease_liability_initial']:,.2f}")
    print(f"ROU Asset: ${test_lease['rou_asset_initial']:,.2f}")
    print(f"Annual Depreciation: ${test_lease['annual_rou_depreciation']:,.2f}")
    print(f"Total Interest: ${test_lease['total_interest_expense']:,.2f}")