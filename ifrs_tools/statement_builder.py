"""
IFRS Statement Builder Module
Generates IFRS-compliant financial statements
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


def build_ifrs_profit_loss(
    trial_balance: List[Dict[str, Any]],
    ifrs_adjustments: List[Dict[str, Any]],
    period_start: str,
    period_end: str,
    comparative_period: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Build IFRS 18 compliant Statement of Profit or Loss
    
    Args:
        trial_balance: Trial balance data with IFRS mapping
        ifrs_adjustments: IFRS adjustments (leases, ECL, depreciation, etc.)
        period_start: Period start date
        period_end: Period end date
        comparative_period: Prior period data for comparison
        
    Returns:
        IFRS Profit or Loss statement
    """
    try:
        # Initialize statement structure
        statement = {
            "statement_type": "Statement of Profit or Loss",
            "period": f"{period_start} to {period_end}",
            "reporting_date": period_end,
            "currency": "USD",
            "amounts_in": "thousands",
            
            # Operating Performance
            "operating_performance": {
                "revenue": 0,
                "cost_of_sales": 0,
                "gross_profit": 0,
                "other_operating_income": 0,
                "distribution_costs": 0,
                "administrative_expenses": 0,
                "other_operating_expenses": 0,
                "operating_profit": 0
            },
            
            # Investing Activities
            "investing_activities": {
                "share_of_profit_associates": 0,
                "investment_income": 0,
                "gains_on_disposal": 0,
                "impairment_losses": 0
            },
            
            # Financing Activities
            "financing_activities": {
                "interest_income": 0,
                "interest_expense": 0,
                "other_finance_costs": 0,
                "net_finance_costs": 0
            },
            
            # Tax and Final Results
            "profit_before_tax": 0,
            "tax_expense": 0,
            "profit_for_period": 0,
            
            # Earnings per Share (if applicable)
            "earnings_per_share": {
                "basic": 0,
                "diluted": 0
            }
        }
        
        # Process trial balance
        for account in trial_balance:
            amount = account.get("balance", 0)
            ifrs_category = account.get("ifrs_category", "")
            ifrs_subcategory = account.get("ifrs_subcategory", "")
            
            # Map to statement line items
            if ifrs_category == "Operating":
                if ifrs_subcategory == "Revenue":
                    statement["operating_performance"]["revenue"] += amount
                elif ifrs_subcategory == "COGS":
                    statement["operating_performance"]["cost_of_sales"] += amount
                elif ifrs_subcategory == "Distribution":
                    statement["operating_performance"]["distribution_costs"] += amount
                elif ifrs_subcategory == "Administrative":
                    statement["operating_performance"]["administrative_expenses"] += amount
                elif ifrs_subcategory == "Other Operating Income":
                    statement["operating_performance"]["other_operating_income"] += amount
                elif ifrs_subcategory == "Other Operating Expenses":
                    statement["operating_performance"]["other_operating_expenses"] += amount
            
            elif ifrs_category == "Investing":
                if ifrs_subcategory == "Investment Income":
                    statement["investing_activities"]["investment_income"] += amount
                elif ifrs_subcategory == "Disposal Gains":
                    statement["investing_activities"]["gains_on_disposal"] += amount
                elif ifrs_subcategory == "Impairment":
                    statement["investing_activities"]["impairment_losses"] += amount
            
            elif ifrs_category == "Financing":
                if ifrs_subcategory == "Interest Income":
                    statement["financing_activities"]["interest_income"] += amount
                elif ifrs_subcategory == "Interest Expense":
                    statement["financing_activities"]["interest_expense"] += amount
                elif ifrs_subcategory == "Other Finance Costs":
                    statement["financing_activities"]["other_finance_costs"] += amount
        
        # Apply IFRS adjustments
        for adjustment in ifrs_adjustments:
            adjustment_type = adjustment.get("adjustment_type", "")
            debit_amount = adjustment.get("debit_amount", 0)
            credit_amount = adjustment.get("credit_amount", 0)
            net_amount = debit_amount - credit_amount
            
            if adjustment_type == "IFRS 16":
                # Lease adjustments
                if "interest" in adjustment.get("description", "").lower():
                    statement["financing_activities"]["interest_expense"] += net_amount
                elif "depreciation" in adjustment.get("description", "").lower():
                    statement["operating_performance"]["administrative_expenses"] += net_amount
            
            elif adjustment_type == "IFRS 9":
                # ECL adjustments
                statement["operating_performance"]["administrative_expenses"] += net_amount
            
            elif adjustment_type == "IAS 16":
                # Depreciation adjustments
                statement["operating_performance"]["administrative_expenses"] += net_amount
        
        # Calculate subtotals
        statement["operating_performance"]["gross_profit"] = (
            statement["operating_performance"]["revenue"] - 
            statement["operating_performance"]["cost_of_sales"]
        )
        
        statement["operating_performance"]["operating_profit"] = (
            statement["operating_performance"]["gross_profit"] +
            statement["operating_performance"]["other_operating_income"] -
            statement["operating_performance"]["distribution_costs"] -
            statement["operating_performance"]["administrative_expenses"] -
            statement["operating_performance"]["other_operating_expenses"]
        )
        
        statement["financing_activities"]["net_finance_costs"] = (
            statement["financing_activities"]["interest_expense"] +
            statement["financing_activities"]["other_finance_costs"] -
            statement["financing_activities"]["interest_income"]
        )
        
        statement["profit_before_tax"] = (
            statement["operating_performance"]["operating_profit"] +
            statement["investing_activities"]["share_of_profit_associates"] +
            statement["investing_activities"]["investment_income"] +
            statement["investing_activities"]["gains_on_disposal"] -
            statement["investing_activities"]["impairment_losses"] -
            statement["financing_activities"]["net_finance_costs"]
        )
        
        # Calculate tax (simplified - would normally be more complex)
        tax_rate = 0.24  # Assume 24% tax rate
        statement["tax_expense"] = statement["profit_before_tax"] * tax_rate
        statement["profit_for_period"] = statement["profit_before_tax"] - statement["tax_expense"]
        
        # Round all amounts
        round_statement_amounts(statement)
        
        # Add comparative period if provided
        if comparative_period:
            statement["comparative_period"] = comparative_period
        
        return {
            "statement": statement,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def build_ifrs_balance_sheet(
    trial_balance: List[Dict[str, Any]],
    ifrs_adjustments: List[Dict[str, Any]],
    reporting_date: str,
    comparative_date: str = None
) -> Dict[str, Any]:
    """
    Build IFRS compliant Statement of Financial Position (Balance Sheet)
    
    Args:
        trial_balance: Trial balance data with IFRS mapping
        ifrs_adjustments: IFRS adjustments
        reporting_date: Balance sheet date
        comparative_date: Prior year date for comparison
        
    Returns:
        IFRS Balance Sheet
    """
    try:
        statement = {
            "statement_type": "Statement of Financial Position",
            "reporting_date": reporting_date,
            "currency": "USD",
            "amounts_in": "thousands",
            
            # Assets
            "assets": {
                "current_assets": {
                    "cash_and_cash_equivalents": 0,
                    "trade_and_other_receivables": 0,
                    "contract_assets": 0,
                    "inventories": 0,
                    "prepaid_expenses": 0,
                    "other_current_assets": 0,
                    "total_current_assets": 0
                },
                "non_current_assets": {
                    "property_plant_equipment": 0,
                    "right_of_use_assets": 0,
                    "intangible_assets": 0,
                    "investment_property": 0,
                    "investments": 0,
                    "deferred_tax_assets": 0,
                    "other_non_current_assets": 0,
                    "total_non_current_assets": 0
                },
                "total_assets": 0
            },
            
            # Liabilities
            "liabilities": {
                "current_liabilities": {
                    "trade_and_other_payables": 0,
                    "contract_liabilities": 0,
                    "current_lease_liabilities": 0,
                    "current_borrowings": 0,
                    "current_tax_liabilities": 0,
                    "provisions": 0,
                    "other_current_liabilities": 0,
                    "total_current_liabilities": 0
                },
                "non_current_liabilities": {
                    "non_current_lease_liabilities": 0,
                    "non_current_borrowings": 0,
                    "deferred_tax_liabilities": 0,
                    "employee_benefit_obligations": 0,
                    "other_non_current_liabilities": 0,
                    "total_non_current_liabilities": 0
                },
                "total_liabilities": 0
            },
            
            # Equity
            "equity": {
                "share_capital": 0,
                "retained_earnings": 0,
                "other_reserves": 0,
                "total_equity": 0
            }
        }
        
        # Process trial balance
        for account in trial_balance:
            amount = account.get("balance", 0)
            statement_type = account.get("statement_type", "")
            ifrs_line_item = account.get("ifrs_line_item", "")
            
            if statement_type == "Balance Sheet":
                # Map to specific balance sheet line items
                if "cash" in ifrs_line_item.lower():
                    statement["assets"]["current_assets"]["cash_and_cash_equivalents"] += amount
                elif "receivables" in ifrs_line_item.lower():
                    statement["assets"]["current_assets"]["trade_and_other_receivables"] += amount
                elif "inventories" in ifrs_line_item.lower():
                    statement["assets"]["current_assets"]["inventories"] += amount
                elif "property, plant" in ifrs_line_item.lower():
                    statement["assets"]["non_current_assets"]["property_plant_equipment"] += amount
                elif "right-of-use" in ifrs_line_item.lower():
                    statement["assets"]["non_current_assets"]["right_of_use_assets"] += amount
                elif "payables" in ifrs_line_item.lower():
                    statement["liabilities"]["current_liabilities"]["trade_and_other_payables"] += amount
                elif "lease liabilities" in ifrs_line_item.lower():
                    # Split between current and non-current (simplified)
                    current_portion = amount * 0.3  # Assume 30% current
                    non_current_portion = amount * 0.7  # Assume 70% non-current
                    statement["liabilities"]["current_liabilities"]["current_lease_liabilities"] += current_portion
                    statement["liabilities"]["non_current_liabilities"]["non_current_lease_liabilities"] += non_current_portion
                elif "share capital" in ifrs_line_item.lower():
                    statement["equity"]["share_capital"] += amount
                elif "retained earnings" in ifrs_line_item.lower():
                    statement["equity"]["retained_earnings"] += amount
        
        # Apply IFRS adjustments
        for adjustment in ifrs_adjustments:
            adjustment_type = adjustment.get("adjustment_type", "")
            debit_amount = adjustment.get("debit_amount", 0)
            credit_amount = adjustment.get("credit_amount", 0)
            
            if adjustment_type == "IFRS 16":
                # Lease adjustments affect ROU assets and lease liabilities
                if "asset" in adjustment.get("description", "").lower():
                    statement["assets"]["non_current_assets"]["right_of_use_assets"] += debit_amount - credit_amount
                elif "liability" in adjustment.get("description", "").lower():
                    net_liability = credit_amount - debit_amount
                    current_portion = net_liability * 0.3
                    non_current_portion = net_liability * 0.7
                    statement["liabilities"]["current_liabilities"]["current_lease_liabilities"] += current_portion
                    statement["liabilities"]["non_current_liabilities"]["non_current_lease_liabilities"] += non_current_portion
            
            elif adjustment_type == "IFRS 9":
                # ECL adjustments affect receivables
                statement["assets"]["current_assets"]["trade_and_other_receivables"] -= (credit_amount - debit_amount)
        
        # Calculate totals
        statement["assets"]["current_assets"]["total_current_assets"] = sum(
            v for k, v in statement["assets"]["current_assets"].items() if k != "total_current_assets"
        )
        
        statement["assets"]["non_current_assets"]["total_non_current_assets"] = sum(
            v for k, v in statement["assets"]["non_current_assets"].items() if k != "total_non_current_assets"
        )
        
        statement["assets"]["total_assets"] = (
            statement["assets"]["current_assets"]["total_current_assets"] +
            statement["assets"]["non_current_assets"]["total_non_current_assets"]
        )
        
        statement["liabilities"]["current_liabilities"]["total_current_liabilities"] = sum(
            v for k, v in statement["liabilities"]["current_liabilities"].items() if k != "total_current_liabilities"
        )
        
        statement["liabilities"]["non_current_liabilities"]["total_non_current_liabilities"] = sum(
            v for k, v in statement["liabilities"]["non_current_liabilities"].items() if k != "total_non_current_liabilities"
        )
        
        statement["liabilities"]["total_liabilities"] = (
            statement["liabilities"]["current_liabilities"]["total_current_liabilities"] +
            statement["liabilities"]["non_current_liabilities"]["total_non_current_liabilities"]
        )
        
        statement["equity"]["total_equity"] = sum(
            v for k, v in statement["equity"].items() if k != "total_equity"
        )
        
        # Verify balance sheet balances
        total_liabilities_and_equity = statement["liabilities"]["total_liabilities"] + statement["equity"]["total_equity"]
        balance_check = abs(statement["assets"]["total_assets"] - total_liabilities_and_equity)
        
        # Round all amounts
        round_statement_amounts(statement)
        
        return {
            "statement": statement,
            "balance_check": round(balance_check, 2),
            "balanced": balance_check < 1.0,  # Allow for rounding differences
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def build_ifrs_cash_flow(
    profit_loss_data: Dict[str, Any],
    balance_sheet_current: Dict[str, Any],
    balance_sheet_prior: Dict[str, Any],
    period_start: str,
    period_end: str,
    method: str = "indirect"
) -> Dict[str, Any]:
    """
    Build IFRS compliant Statement of Cash Flows
    
    Args:
        profit_loss_data: Profit or loss statement data
        balance_sheet_current: Current period balance sheet
        balance_sheet_prior: Prior period balance sheet
        period_start: Period start date
        period_end: Period end date
        method: 'direct' or 'indirect' method
        
    Returns:
        IFRS Cash Flow statement
    """
    try:
        statement = {
            "statement_type": "Statement of Cash Flows",
            "period": f"{period_start} to {period_end}",
            "method": method,
            "currency": "USD",
            "amounts_in": "thousands",
            
            "operating_activities": {
                "profit_before_tax": 0,
                "adjustments": {
                    "depreciation_amortisation": 0,
                    "impairment_losses": 0,
                    "interest_expense": 0,
                    "interest_income": 0,
                    "other_non_cash_items": 0
                },
                "working_capital_changes": {
                    "trade_receivables": 0,
                    "inventories": 0,
                    "trade_payables": 0,
                    "other_working_capital": 0
                },
                "interest_paid": 0,
                "interest_received": 0,
                "tax_paid": 0,
                "net_cash_from_operating": 0
            },
            
            "investing_activities": {
                "purchase_ppe": 0,
                "disposal_ppe": 0,
                "purchase_investments": 0,
                "disposal_investments": 0,
                "other_investing": 0,
                "net_cash_from_investing": 0
            },
            
            "financing_activities": {
                "proceeds_borrowings": 0,
                "repayment_borrowings": 0,
                "lease_payments": 0,
                "dividends_paid": 0,
                "share_issues": 0,
                "other_financing": 0,
                "net_cash_from_financing": 0
            },
            
            "net_increase_cash": 0,
            "cash_beginning": 0,
            "cash_ending": 0
        }
        
        # Extract profit before tax
        if profit_loss_data and "statement" in profit_loss_data:
            statement["operating_activities"]["profit_before_tax"] = profit_loss_data["statement"].get("profit_before_tax", 0)
            
            # Extract adjustments from P&L
            operating_perf = profit_loss_data["statement"].get("operating_performance", {})
            financing_act = profit_loss_data["statement"].get("financing_activities", {})
            
            statement["operating_activities"]["adjustments"]["interest_expense"] = financing_act.get("interest_expense", 0)
            statement["operating_activities"]["adjustments"]["interest_income"] = -financing_act.get("interest_income", 0)
        
        # Calculate working capital changes from balance sheet movements
        if balance_sheet_current and balance_sheet_prior:
            current_assets = balance_sheet_current.get("assets", {}).get("current_assets", {})
            prior_assets = balance_sheet_prior.get("assets", {}).get("current_assets", {})
            current_liabilities = balance_sheet_current.get("liabilities", {}).get("current_liabilities", {})
            prior_liabilities = balance_sheet_prior.get("liabilities", {}).get("current_liabilities", {})
            
            # Changes in working capital (increase in assets = use of cash, increase in liabilities = source of cash)
            statement["operating_activities"]["working_capital_changes"]["trade_receivables"] = -(
                current_assets.get("trade_and_other_receivables", 0) - prior_assets.get("trade_and_other_receivables", 0)
            )
            
            statement["operating_activities"]["working_capital_changes"]["inventories"] = -(
                current_assets.get("inventories", 0) - prior_assets.get("inventories", 0)
            )
            
            statement["operating_activities"]["working_capital_changes"]["trade_payables"] = (
                current_liabilities.get("trade_and_other_payables", 0) - prior_liabilities.get("trade_and_other_payables", 0)
            )
            
            # Cash movement
            statement["cash_beginning"] = prior_assets.get("cash_and_cash_equivalents", 0)
            statement["cash_ending"] = current_assets.get("cash_and_cash_equivalents", 0)
        
        # Estimate some cash flow items (in practice, these would come from detailed records)
        statement["operating_activities"]["adjustments"]["depreciation_amortisation"] = 50000  # Estimate
        statement["operating_activities"]["interest_paid"] = -statement["operating_activities"]["adjustments"]["interest_expense"]
        statement["operating_activities"]["interest_received"] = -statement["operating_activities"]["adjustments"]["interest_income"]
        statement["operating_activities"]["tax_paid"] = -30000  # Estimate
        
        # Calculate net cash flows
        operating_cash = (
            statement["operating_activities"]["profit_before_tax"] +
            sum(statement["operating_activities"]["adjustments"].values()) +
            sum(statement["operating_activities"]["working_capital_changes"].values()) +
            statement["operating_activities"]["interest_paid"] +
            statement["operating_activities"]["interest_received"] +
            statement["operating_activities"]["tax_paid"]
        )
        statement["operating_activities"]["net_cash_from_operating"] = operating_cash
        
        investing_cash = sum(statement["investing_activities"][k] for k in statement["investing_activities"] if k != "net_cash_from_investing")
        statement["investing_activities"]["net_cash_from_investing"] = investing_cash
        
        financing_cash = sum(statement["financing_activities"][k] for k in statement["financing_activities"] if k != "net_cash_from_financing")
        statement["financing_activities"]["net_cash_from_financing"] = financing_cash
        
        statement["net_increase_cash"] = operating_cash + investing_cash + financing_cash
        
        # Verify cash reconciliation
        calculated_ending_cash = statement["cash_beginning"] + statement["net_increase_cash"]
        cash_difference = abs(calculated_ending_cash - statement["cash_ending"])
        
        # Round all amounts
        round_statement_amounts(statement)
        
        return {
            "statement": statement,
            "cash_reconciliation_difference": round(cash_difference, 2),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def round_statement_amounts(statement: Dict[str, Any], decimals: int = 2):
    """
    Recursively round all numeric amounts in a statement
    """
    for key, value in statement.items():
        if isinstance(value, dict):
            round_statement_amounts(value, decimals)
        elif isinstance(value, (int, float)) and key not in ["year", "period_id"]:
            statement[key] = round(value, decimals)


def generate_statement_notes(
    statements: Dict[str, Any],
    accounting_policies: List[str] = None,
    significant_estimates: List[str] = None
) -> Dict[str, Any]:
    """
    Generate notes to the financial statements
    
    Args:
        statements: Dictionary of financial statements
        accounting_policies: List of significant accounting policies
        significant_estimates: List of significant accounting estimates
        
    Returns:
        Structured notes to financial statements
    """
    try:
        notes = {
            "note_1_accounting_policies": {
                "basis_of_preparation": "These financial statements have been prepared in accordance with International Financial Reporting Standards (IFRS).",
                "functional_currency": "US Dollar (USD)",
                "significant_policies": accounting_policies or [
                    "Revenue recognition (IFRS 15)",
                    "Lease accounting (IFRS 16)",
                    "Financial instruments (IFRS 9)",
                    "Property, plant and equipment (IAS 16)"
                ]
            },
            
            "note_2_significant_estimates": {
                "description": "The preparation of financial statements requires management to make estimates and assumptions.",
                "key_estimates": significant_estimates or [
                    "Expected credit losses on receivables",
                    "Useful lives of property, plant and equipment",
                    "Lease terms and incremental borrowing rates",
                    "Fair value measurements"
                ]
            },
            
            "note_3_revenue": {
                "accounting_policy": "Revenue is recognized when control of goods or services is transferred to customers.",
                "disaggregation": "Revenue is primarily from sale of goods and provision of services.",
                "contract_balances": "Contract assets and liabilities are disclosed in the balance sheet."
            },
            
            "note_4_leases": {
                "accounting_policy": "Leases are recognized as right-of-use assets and lease liabilities at commencement date.",
                "lease_expenses": "Lease expenses comprise depreciation of ROU assets and interest on lease liabilities.",
                "maturity_analysis": "Lease liabilities mature over the next 1-5 years."
            },
            
            "note_5_financial_instruments": {
                "accounting_policy": "Financial assets are classified and measured based on business model and contractual cash flows.",
                "credit_risk": "Expected credit losses are recognized using a forward-looking approach.",
                "fair_value_hierarchy": "Fair values are categorized into Level 1, 2, or 3 based on inputs used."
            }
        }
        
        return {
            "notes": notes,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Example usage and testing
if __name__ == "__main__":
    # Test statement building with sample data
    sample_trial_balance = [
        {"account_code": "4000", "balance": 1000000, "ifrs_category": "Operating", "ifrs_subcategory": "Revenue"},
        {"account_code": "5000", "balance": 600000, "ifrs_category": "Operating", "ifrs_subcategory": "COGS"},
        {"account_code": "6100", "balance": 200000, "ifrs_category": "Operating", "ifrs_subcategory": "Administrative"},
        {"account_code": "7200", "balance": 25000, "ifrs_category": "Financing", "ifrs_subcategory": "Interest Expense"}
    ]
    
    sample_adjustments = [
        {"adjustment_type": "IFRS 16", "debit_amount": 0, "credit_amount": 15000, "description": "Lease interest expense"},
        {"adjustment_type": "IFRS 9", "debit_amount": 8000, "credit_amount": 0, "description": "ECL provision"}
    ]
    
    # Build P&L statement
    pl_statement = build_ifrs_profit_loss(
        trial_balance=sample_trial_balance,
        ifrs_adjustments=sample_adjustments,
        period_start="2026-01-01",
        period_end="2026-12-31"
    )
    
    if pl_statement["success"]:
        statement = pl_statement["statement"]
        print("IFRS Profit or Loss Statement:")
        print(f"Revenue: ${statement['operating_performance']['revenue']:,.2f}")
        print(f"Gross Profit: ${statement['operating_performance']['gross_profit']:,.2f}")
        print(f"Operating Profit: ${statement['operating_performance']['operating_profit']:,.2f}")
        print(f"Profit Before Tax: ${statement['profit_before_tax']:,.2f}")
        print(f"Profit for Period: ${statement['profit_for_period']:,.2f}")
    else:
        print(f"Error: {pl_statement['error']}")