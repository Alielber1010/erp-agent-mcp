"""
IFRS 9 Expected Credit Loss Module
Calculates Expected Credit Loss provisions using the 3-stage model
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


def determine_ecl_stage(
    days_overdue: int,
    credit_rating: str = None,
    payment_history_score: float = None,
    significant_increase_threshold: int = 30
) -> int:
    """
    Determine ECL stage based on credit risk assessment
    
    Args:
        days_overdue: Number of days past due
        credit_rating: Internal credit rating
        payment_history_score: Historical payment performance (0-100)
        significant_increase_threshold: Days threshold for Stage 2
        
    Returns:
        ECL stage (1, 2, or 3)
    """
    # Stage 3: Credit-impaired (>90 days overdue or other indicators)
    if days_overdue > 90:
        return 3
    
    # Stage 2: Significant increase in credit risk
    if days_overdue > significant_increase_threshold:
        return 2
    
    # Additional Stage 2 criteria based on credit rating
    if credit_rating and credit_rating in ['D', 'E', 'F']:  # Poor ratings
        return 2
    
    # Additional Stage 2 criteria based on payment history
    if payment_history_score and payment_history_score < 60:  # Poor payment history
        return 2
    
    # Stage 1: 12-month ECL (performing assets)
    return 1


def get_ecl_rates() -> Dict[str, Dict[int, float]]:
    """
    Get ECL rates by aging bucket and stage
    
    Returns:
        Dictionary of ECL rates by aging bucket and stage
    """
    return {
        "current": {1: 0.005, 2: 0.02, 3: 0.50},      # 0.5%, 2%, 50%
        "1-30": {1: 0.01, 2: 0.05, 3: 0.60},          # 1%, 5%, 60%
        "31-60": {1: 0.02, 2: 0.10, 3: 0.70},         # 2%, 10%, 70%
        "61-90": {1: 0.05, 2: 0.20, 3: 0.80},         # 5%, 20%, 80%
        "91-120": {1: 0.10, 2: 0.35, 3: 0.85},        # 10%, 35%, 85%
        "121-180": {1: 0.20, 2: 0.50, 3: 0.90},       # 20%, 50%, 90%
        "180+": {1: 0.40, 2: 0.75, 3: 0.95}           # 40%, 75%, 95%
    }


def get_aging_bucket(days_overdue: int) -> str:
    """
    Determine aging bucket based on days overdue
    
    Args:
        days_overdue: Number of days past due
        
    Returns:
        Aging bucket string
    """
    if days_overdue <= 0:
        return "current"
    elif days_overdue <= 30:
        return "1-30"
    elif days_overdue <= 60:
        return "31-60"
    elif days_overdue <= 90:
        return "61-90"
    elif days_overdue <= 120:
        return "91-120"
    elif days_overdue <= 180:
        return "121-180"
    else:
        return "180+"


def stage_receivables(receivables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Stage receivables according to IFRS 9 3-stage model
    
    Args:
        receivables: List of receivable records
        
    Returns:
        Staging analysis and recommendations
    """
    try:
        staged_receivables = []
        stage_summary = {1: {"count": 0, "amount": 0}, 2: {"count": 0, "amount": 0}, 3: {"count": 0, "amount": 0}}
        
        for receivable in receivables:
            amount = receivable.get("amount", 0)
            days_overdue = receivable.get("days_overdue", 0)
            credit_rating = receivable.get("credit_rating")
            payment_history_score = receivable.get("payment_history_score")
            
            # Determine stage
            stage = determine_ecl_stage(days_overdue, credit_rating, payment_history_score)
            aging_bucket = get_aging_bucket(days_overdue)
            
            staged_receivable = {
                **receivable,
                "ecl_stage": stage,
                "aging_bucket": aging_bucket,
                "stage_reason": get_stage_reason(stage, days_overdue, credit_rating, payment_history_score)
            }
            
            staged_receivables.append(staged_receivable)
            stage_summary[stage]["count"] += 1
            stage_summary[stage]["amount"] += amount
        
        return {
            "staged_receivables": staged_receivables,
            "stage_summary": stage_summary,
            "total_receivables": len(receivables),
            "total_amount": sum(r.get("amount", 0) for r in receivables),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def get_stage_reason(stage: int, days_overdue: int, credit_rating: str, payment_history_score: float) -> str:
    """Get reason for ECL stage assignment"""
    if stage == 3:
        return f"Credit-impaired: {days_overdue} days overdue"
    elif stage == 2:
        reasons = []
        if days_overdue > 30:
            reasons.append(f"{days_overdue} days overdue")
        if credit_rating in ['D', 'E', 'F']:
            reasons.append(f"Poor credit rating: {credit_rating}")
        if payment_history_score and payment_history_score < 60:
            reasons.append(f"Poor payment history: {payment_history_score}%")
        return "Significant increase in credit risk: " + ", ".join(reasons)
    else:
        return "Performing asset"


def calculate_ifrs9_ecl(
    receivables: List[Dict[str, Any]],
    custom_rates: Dict[str, Dict[int, float]] = None,
    forward_looking_adjustment: float = 0,
    collective_assessment: bool = True
) -> Dict[str, Any]:
    """
    Calculate Expected Credit Loss under IFRS 9
    
    Args:
        receivables: List of receivables with aging data
        custom_rates: Custom ECL rates (optional)
        forward_looking_adjustment: Forward-looking adjustment factor
        collective_assessment: Whether to use collective assessment
        
    Returns:
        ECL calculation results
    """
    try:
        # Use custom rates or default rates
        ecl_rates = custom_rates or get_ecl_rates()
        
        # Stage receivables first
        staging_result = stage_receivables(receivables)
        if not staging_result["success"]:
            return staging_result
        
        staged_receivables = staging_result["staged_receivables"]
        
        # Calculate ECL for each receivable
        total_receivables = 0
        total_ecl = 0
        ecl_by_stage = {1: {"amount": 0, "ecl": 0}, 2: {"amount": 0, "ecl": 0}, 3: {"amount": 0, "ecl": 0}}
        ecl_by_aging = {}
        detailed_calculations = []
        
        for receivable in staged_receivables:
            amount = receivable.get("amount", 0)
            stage = receivable["ecl_stage"]
            aging_bucket = receivable["aging_bucket"]
            
            # Get ECL rate for this combination
            ecl_rate = ecl_rates.get(aging_bucket, {}).get(stage, 0.05)  # Default 5%
            
            # Apply forward-looking adjustment
            adjusted_rate = ecl_rate * (1 + forward_looking_adjustment)
            
            # Calculate ECL
            ecl_amount = amount * adjusted_rate
            
            # Update totals
            total_receivables += amount
            total_ecl += ecl_amount
            ecl_by_stage[stage]["amount"] += amount
            ecl_by_stage[stage]["ecl"] += ecl_amount
            
            # Update aging analysis
            if aging_bucket not in ecl_by_aging:
                ecl_by_aging[aging_bucket] = {"amount": 0, "ecl": 0, "rate": 0}
            ecl_by_aging[aging_bucket]["amount"] += amount
            ecl_by_aging[aging_bucket]["ecl"] += ecl_amount
            
            detailed_calculations.append({
                "invoice_id": receivable.get("invoice_id"),
                "customer_id": receivable.get("customer_id"),
                "amount": round(amount, 2),
                "days_overdue": receivable.get("days_overdue", 0),
                "aging_bucket": aging_bucket,
                "ecl_stage": stage,
                "ecl_rate": round(adjusted_rate * 100, 2),  # As percentage
                "ecl_provision": round(ecl_amount, 2),
                "stage_reason": receivable["stage_reason"]
            })
        
        # Calculate rates for aging buckets
        for bucket in ecl_by_aging:
            if ecl_by_aging[bucket]["amount"] > 0:
                ecl_by_aging[bucket]["rate"] = round(
                    ecl_by_aging[bucket]["ecl"] / ecl_by_aging[bucket]["amount"] * 100, 2
                )
        
        # Round all amounts
        for stage in ecl_by_stage:
            ecl_by_stage[stage]["amount"] = round(ecl_by_stage[stage]["amount"], 2)
            ecl_by_stage[stage]["ecl"] = round(ecl_by_stage[stage]["ecl"], 2)
            if ecl_by_stage[stage]["amount"] > 0:
                ecl_by_stage[stage]["rate"] = round(
                    ecl_by_stage[stage]["ecl"] / ecl_by_stage[stage]["amount"] * 100, 2
                )
            else:
                ecl_by_stage[stage]["rate"] = 0
        
        for bucket in ecl_by_aging:
            ecl_by_aging[bucket]["amount"] = round(ecl_by_aging[bucket]["amount"], 2)
            ecl_by_aging[bucket]["ecl"] = round(ecl_by_aging[bucket]["ecl"], 2)
        
        return {
            "calculation_date": datetime.now().strftime("%Y-%m-%d"),
            "total_receivables": round(total_receivables, 2),
            "total_ecl_provision": round(total_ecl, 2),
            "net_receivables": round(total_receivables - total_ecl, 2),
            "overall_ecl_rate": round(total_ecl / total_receivables * 100, 2) if total_receivables > 0 else 0,
            "ecl_by_stage": ecl_by_stage,
            "ecl_by_aging": ecl_by_aging,
            "forward_looking_adjustment": forward_looking_adjustment,
            "detailed_calculations": detailed_calculations[:20],  # Limit for display
            "accounting_entries": generate_ecl_accounting_entries(total_ecl),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def generate_ecl_accounting_entries(ecl_provision: float) -> List[Dict[str, Any]]:
    """
    Generate accounting entries for ECL provision
    
    Args:
        ecl_provision: Total ECL provision amount
        
    Returns:
        List of accounting entries
    """
    return [
        {
            "entry_type": "ECL Provision",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": f"IFRS9-ECL-{datetime.now().strftime('%Y%m%d')}",
            "entries": [
                {
                    "account": "6400 - Bad Debt Expense",
                    "debit": round(ecl_provision, 2),
                    "credit": 0,
                    "description": "IFRS 9 Expected Credit Loss provision"
                },
                {
                    "account": "1200 - Allowance for Credit Losses",
                    "debit": 0,
                    "credit": round(ecl_provision, 2),
                    "description": "Contra-asset for expected credit losses"
                }
            ]
        }
    ]


def calculate_ecl_movement(
    previous_ecl: float,
    current_ecl: float,
    write_offs: float = 0,
    recoveries: float = 0
) -> Dict[str, Any]:
    """
    Calculate ECL provision movement analysis
    
    Args:
        previous_ecl: Previous period ECL provision
        current_ecl: Current period ECL provision
        write_offs: Actual write-offs during period
        recoveries: Recoveries of previously written-off amounts
        
    Returns:
        ECL movement analysis
    """
    try:
        net_movement = current_ecl - previous_ecl
        charge_to_income = net_movement + write_offs - recoveries
        
        return {
            "opening_provision": round(previous_ecl, 2),
            "charge_to_income": round(charge_to_income, 2),
            "write_offs": round(write_offs, 2),
            "recoveries": round(recoveries, 2),
            "closing_provision": round(current_ecl, 2),
            "net_movement": round(net_movement, 2),
            "movement_percentage": round(net_movement / previous_ecl * 100, 2) if previous_ecl > 0 else 0,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Example usage and testing
if __name__ == "__main__":
    # Test ECL calculation
    sample_receivables = [
        {"invoice_id": 1, "customer_id": 101, "amount": 10000, "days_overdue": 0, "credit_rating": "A"},
        {"invoice_id": 2, "customer_id": 102, "amount": 5000, "days_overdue": 45, "credit_rating": "B"},
        {"invoice_id": 3, "customer_id": 103, "amount": 8000, "days_overdue": 120, "credit_rating": "D"},
        {"invoice_id": 4, "customer_id": 104, "amount": 3000, "days_overdue": 15, "payment_history_score": 85}
    ]
    
    ecl_result = calculate_ifrs9_ecl(sample_receivables)
    
    print("IFRS 9 ECL Calculation Test:")
    print(f"Total Receivables: ${ecl_result['total_receivables']:,.2f}")
    print(f"Total ECL Provision: ${ecl_result['total_ecl_provision']:,.2f}")
    print(f"Overall ECL Rate: {ecl_result['overall_ecl_rate']:.2f}%")
    print(f"Net Receivables: ${ecl_result['net_receivables']:,.2f}")
    
    print("\nECL by Stage:")
    for stage, data in ecl_result['ecl_by_stage'].items():
        print(f"  Stage {stage}: ${data['amount']:,.2f} @ {data['rate']:.2f}% = ${data['ecl']:,.2f}")