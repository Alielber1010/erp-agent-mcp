"""
IFRS 15 Revenue from Contracts with Customers Module
Handles revenue recognition, performance obligations, and contract modifications
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import math


def identify_performance_obligations(contract_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify distinct performance obligations in a contract
    
    Args:
        contract_details: Contract information including goods/services
        
    Returns:
        List of identified performance obligations
    """
    try:
        obligations = []
        items = contract_details.get("contract_items", [])
        
        for i, item in enumerate(items):
            # Determine if item is distinct
            is_distinct = determine_if_distinct(item, items)
            
            obligation = {
                "obligation_id": f"PO-{i+1}",
                "description": item.get("description", ""),
                "goods_or_services": item.get("type", "goods"),  # 'goods', 'services', 'license'
                "is_distinct": is_distinct,
                "bundled_with": [] if is_distinct else ["other_items"],
                "satisfaction_method": determine_satisfaction_method(item),
                "estimated_standalone_price": item.get("standalone_price", 0)
            }
            
            obligations.append(obligation)
        
        return obligations
        
    except Exception as e:
        return [{"error": str(e)}]


def determine_if_distinct(item: Dict[str, Any], all_items: List[Dict[str, Any]]) -> bool:
    """
    Determine if an item represents a distinct performance obligation
    
    Args:
        item: Individual contract item
        all_items: All items in the contract
        
    Returns:
        True if distinct, False if should be bundled
    """
    # Simplified logic - in practice this would be more complex
    item_type = item.get("type", "goods")
    
    # Services are typically distinct unless highly integrated
    if item_type == "services":
        return not item.get("integrated_with_goods", False)
    
    # Goods are distinct unless they're components of a combined item
    if item_type == "goods":
        return not item.get("component_of_system", False)
    
    # Licenses are typically distinct
    if item_type == "license":
        return True
    
    return True


def determine_satisfaction_method(item: Dict[str, Any]) -> str:
    """
    Determine if performance obligation is satisfied over time or at a point in time
    
    Args:
        item: Contract item details
        
    Returns:
        'over_time' or 'point_in_time'
    """
    item_type = item.get("type", "goods")
    
    # Services are typically over time
    if item_type == "services":
        return "over_time"
    
    # Construction/manufacturing with no alternative use
    if item.get("no_alternative_use", False) and item.get("enforceable_payment_right", False):
        return "over_time"
    
    # Customer controls asset as it's created
    if item.get("customer_controls_during_creation", False):
        return "over_time"
    
    # Default to point in time for goods
    return "point_in_time"


def allocate_transaction_price(
    total_consideration: float,
    performance_obligations: List[Dict[str, Any]],
    variable_consideration: float = 0
) -> Dict[str, Any]:
    """
    Allocate transaction price to performance obligations based on standalone selling prices
    
    Args:
        total_consideration: Total contract consideration
        performance_obligations: List of performance obligations
        variable_consideration: Variable consideration amount
        
    Returns:
        Allocation results
    """
    try:
        # Calculate total standalone prices
        total_standalone_price = sum(po.get("estimated_standalone_price", 0) for po in performance_obligations)
        
        if total_standalone_price == 0:
            return {
                "error": "Cannot allocate price - no standalone prices provided",
                "success": False
            }
        
        # Allocate based on relative standalone selling prices
        allocated_obligations = []
        total_allocated = 0
        
        for i, po in enumerate(performance_obligations):
            standalone_price = po.get("estimated_standalone_price", 0)
            allocation_percentage = standalone_price / total_standalone_price
            allocated_amount = total_consideration * allocation_percentage
            
            allocated_po = {
                **po,
                "standalone_price": round(standalone_price, 2),
                "allocation_percentage": round(allocation_percentage * 100, 2),
                "allocated_amount": round(allocated_amount, 2)
            }
            
            allocated_obligations.append(allocated_po)
            total_allocated += allocated_amount
        
        return {
            "total_consideration": round(total_consideration, 2),
            "total_standalone_price": round(total_standalone_price, 2),
            "discount_premium": round(total_consideration - total_standalone_price, 2),
            "allocated_obligations": allocated_obligations,
            "total_allocated": round(total_allocated, 2),
            "variable_consideration": round(variable_consideration, 2),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def calculate_ifrs15_revenue(
    contract_id: str,
    contract_start_date: str,
    contract_end_date: str = None,
    performance_obligations: List[Dict[str, Any]] = None,
    progress_to_date: Dict[str, float] = None,
    reporting_date: str = None
) -> Dict[str, Any]:
    """
    Calculate revenue recognition under IFRS 15
    
    Args:
        contract_id: Contract identifier
        contract_start_date: Contract start date
        contract_end_date: Contract end date (for over-time obligations)
        performance_obligations: List of performance obligations with allocations
        progress_to_date: Progress percentage for each obligation
        reporting_date: Current reporting date
        
    Returns:
        Revenue recognition calculation
    """
    try:
        if not performance_obligations:
            return {
                "contract_id": contract_id,
                "error": "Performance obligations required",
                "success": False
            }
        
        reporting_date = reporting_date or datetime.now().strftime("%Y-%m-%d")
        start_date = datetime.strptime(contract_start_date, "%Y-%m-%d")
        report_date = datetime.strptime(reporting_date, "%Y-%m-%d")
        
        revenue_calculations = []
        total_revenue_to_date = 0
        total_contract_assets = 0
        total_contract_liabilities = 0
        
        for po in performance_obligations:
            po_id = po.get("obligation_id", "")
            allocated_amount = po.get("allocated_amount", 0)
            satisfaction_method = po.get("satisfaction_method", "point_in_time")
            
            if satisfaction_method == "over_time":
                # Calculate revenue based on progress
                progress = progress_to_date.get(po_id, 0) if progress_to_date else 0
                revenue_recognized = allocated_amount * (progress / 100)
                
                # Calculate contract asset/liability
                cash_received = po.get("cash_received", 0)
                if revenue_recognized > cash_received:
                    contract_asset = revenue_recognized - cash_received
                    contract_liability = 0
                else:
                    contract_asset = 0
                    contract_liability = cash_received - revenue_recognized
                
            else:  # point_in_time
                # Revenue recognized when control transfers
                control_transferred = po.get("control_transferred", False)
                revenue_recognized = allocated_amount if control_transferred else 0
                
                cash_received = po.get("cash_received", 0)
                if control_transferred:
                    contract_asset = max(0, revenue_recognized - cash_received)
                    contract_liability = 0
                else:
                    contract_asset = 0
                    contract_liability = cash_received
            
            po_calculation = {
                "obligation_id": po_id,
                "description": po.get("description", ""),
                "allocated_amount": round(allocated_amount, 2),
                "satisfaction_method": satisfaction_method,
                "progress_percentage": progress_to_date.get(po_id, 0) if progress_to_date else 0,
                "revenue_recognized": round(revenue_recognized, 2),
                "remaining_revenue": round(allocated_amount - revenue_recognized, 2),
                "contract_asset": round(contract_asset, 2),
                "contract_liability": round(contract_liability, 2)
            }
            
            revenue_calculations.append(po_calculation)
            total_revenue_to_date += revenue_recognized
            total_contract_assets += contract_asset
            total_contract_liabilities += contract_liability
        
        return {
            "contract_id": contract_id,
            "reporting_date": reporting_date,
            "contract_start_date": contract_start_date,
            "total_contract_value": sum(po.get("allocated_amount", 0) for po in performance_obligations),
            "total_revenue_recognized": round(total_revenue_to_date, 2),
            "total_remaining_revenue": round(sum(po.get("allocated_amount", 0) for po in performance_obligations) - total_revenue_to_date, 2),
            "total_contract_assets": round(total_contract_assets, 2),
            "total_contract_liabilities": round(total_contract_liabilities, 2),
            "performance_obligation_details": revenue_calculations,
            "accounting_entries": generate_revenue_entries(contract_id, total_revenue_to_date, total_contract_assets, total_contract_liabilities),
            "success": True
        }
        
    except Exception as e:
        return {
            "contract_id": contract_id,
            "error": str(e),
            "success": False
        }


def generate_revenue_entries(
    contract_id: str,
    revenue_amount: float,
    contract_assets: float,
    contract_liabilities: float
) -> List[Dict[str, Any]]:
    """
    Generate accounting entries for revenue recognition
    
    Args:
        contract_id: Contract identifier
        revenue_amount: Revenue to recognize
        contract_assets: Contract assets amount
        contract_liabilities: Contract liabilities amount
        
    Returns:
        List of accounting entries
    """
    entries = []
    
    if revenue_amount > 0:
        entry = {
            "entry_type": "Revenue Recognition",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": f"IFRS15-{contract_id}",
            "entries": []
        }
        
        # Revenue recognition
        if contract_assets > 0:
            entry["entries"].append({
                "account": "1250 - Contract Assets",
                "debit": round(contract_assets, 2),
                "credit": 0,
                "description": f"Contract asset for {contract_id}"
            })
        
        if contract_liabilities > 0:
            entry["entries"].append({
                "account": "2150 - Contract Liabilities",
                "debit": 0,
                "credit": round(contract_liabilities, 2),
                "description": f"Contract liability for {contract_id}"
            })
        
        entry["entries"].append({
            "account": "4000 - Revenue",
            "debit": 0,
            "credit": round(revenue_amount, 2),
            "description": f"Revenue recognition for {contract_id}"
        })
        
        # If no contract asset/liability, assume receivable
        if contract_assets == 0 and contract_liabilities == 0:
            entry["entries"].append({
                "account": "1200 - Accounts Receivable",
                "debit": round(revenue_amount, 2),
                "credit": 0,
                "description": f"Receivable for {contract_id}"
            })
        
        entries.append(entry)
    
    return entries


def calculate_contract_modification(
    original_contract: Dict[str, Any],
    modification_details: Dict[str, Any],
    modification_date: str
) -> Dict[str, Any]:
    """
    Calculate impact of contract modification under IFRS 15
    
    Args:
        original_contract: Original contract details
        modification_details: Details of the modification
        modification_date: Date of modification
        
    Returns:
        Contract modification analysis
    """
    try:
        modification_type = determine_modification_type(modification_details)
        
        if modification_type == "separate_contract":
            # Treat as separate contract
            result = {
                "modification_type": "separate_contract",
                "accounting_treatment": "Create new contract",
                "original_contract_unchanged": True,
                "new_contract_required": True
            }
        elif modification_type == "termination_and_new":
            # Terminate existing and create new
            result = {
                "modification_type": "termination_and_new",
                "accounting_treatment": "Terminate existing, create new contract",
                "termination_adjustment": calculate_termination_adjustment(original_contract, modification_date),
                "new_contract_required": True
            }
        else:  # prospective_adjustment
            # Adjust remaining performance obligations
            result = {
                "modification_type": "prospective_adjustment",
                "accounting_treatment": "Adjust remaining performance obligations",
                "price_adjustment": modification_details.get("price_change", 0),
                "scope_adjustment": modification_details.get("scope_change", ""),
                "revised_allocation_required": True
            }
        
        return {
            "contract_id": original_contract.get("contract_id"),
            "modification_date": modification_date,
            "modification_analysis": result,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def determine_modification_type(modification_details: Dict[str, Any]) -> str:
    """
    Determine the type of contract modification for accounting purposes
    """
    # Simplified logic - in practice this would be more complex
    if modification_details.get("distinct_goods_services", False) and modification_details.get("standalone_price", False):
        return "separate_contract"
    
    if modification_details.get("remaining_goods_not_distinct", False):
        return "termination_and_new"
    
    return "prospective_adjustment"


def calculate_termination_adjustment(contract: Dict[str, Any], termination_date: str) -> Dict[str, Any]:
    """
    Calculate adjustment for contract termination
    """
    # This would calculate the impact of terminating the existing contract
    return {
        "revenue_adjustment": 0,
        "contract_asset_adjustment": 0,
        "contract_liability_adjustment": 0
    }


def calculate_variable_consideration(
    contract_id: str,
    variable_elements: List[Dict[str, Any]],
    constraint_assessment: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Calculate variable consideration and apply constraint
    
    Args:
        contract_id: Contract identifier
        variable_elements: List of variable consideration elements
        constraint_assessment: Assessment of constraint factors
        
    Returns:
        Variable consideration calculation
    """
    try:
        total_expected_value = 0
        total_most_likely = 0
        constraint_adjustment = 0
        
        for element in variable_elements:
            element_type = element.get("type", "bonus")  # bonus, penalty, discount, etc.
            
            if element.get("method") == "expected_value":
                # Expected value method
                expected_value = sum(
                    scenario.get("amount", 0) * scenario.get("probability", 0)
                    for scenario in element.get("scenarios", [])
                )
                total_expected_value += expected_value
            else:
                # Most likely amount method
                most_likely = element.get("most_likely_amount", 0)
                total_most_likely += most_likely
        
        # Apply constraint (only include amounts that are highly probable not to reverse)
        if constraint_assessment:
            constraint_factor = constraint_assessment.get("constraint_factor", 1.0)
            constraint_adjustment = (total_expected_value + total_most_likely) * (1 - constraint_factor)
        
        constrained_amount = (total_expected_value + total_most_likely) - constraint_adjustment
        
        return {
            "contract_id": contract_id,
            "expected_value_method": round(total_expected_value, 2),
            "most_likely_method": round(total_most_likely, 2),
            "constraint_adjustment": round(constraint_adjustment, 2),
            "constrained_variable_consideration": round(max(0, constrained_amount), 2),
            "success": True
        }
        
    except Exception as e:
        return {
            "contract_id": contract_id,
            "error": str(e),
            "success": False
        }


# Example usage and testing
if __name__ == "__main__":
    # Test revenue recognition
    sample_contract = {
        "contract_items": [
            {
                "description": "Software License",
                "type": "license",
                "standalone_price": 50000
            },
            {
                "description": "Implementation Services",
                "type": "services",
                "standalone_price": 30000
            },
            {
                "description": "Annual Support",
                "type": "services",
                "standalone_price": 20000
            }
        ]
    }
    
    # Identify performance obligations
    obligations = identify_performance_obligations(sample_contract)
    print("Performance Obligations:")
    for po in obligations:
        print(f"  {po['obligation_id']}: {po['description']} ({po['satisfaction_method']})")
    
    # Allocate transaction price
    allocation = allocate_transaction_price(90000, obligations)
    print(f"\nPrice Allocation (Total: ${allocation['total_consideration']:,.2f}):")
    for po in allocation['allocated_obligations']:
        print(f"  {po['obligation_id']}: ${po['allocated_amount']:,.2f} ({po['allocation_percentage']:.1f}%)")
    
    # Calculate revenue recognition
    progress = {"PO-1": 100, "PO-2": 60, "PO-3": 25}  # Progress percentages
    revenue_calc = calculate_ifrs15_revenue(
        contract_id="C-001",
        contract_start_date="2026-01-01",
        performance_obligations=allocation['allocated_obligations'],
        progress_to_date=progress
    )
    
    print(f"\nRevenue Recognition:")
    print(f"Total Revenue Recognized: ${revenue_calc['total_revenue_recognized']:,.2f}")
    print(f"Contract Assets: ${revenue_calc['total_contract_assets']:,.2f}")
    print(f"Contract Liabilities: ${revenue_calc['total_contract_liabilities']:,.2f}")