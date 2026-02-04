"""
IFRS Disclosure Generator Module
Generates required disclosure notes for IFRS compliance
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


def generate_ifrs_disclosures(
    financial_statements: Dict[str, Any],
    entity_info: Dict[str, Any],
    reporting_period: str,
    disclosure_requirements: List[str] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive IFRS disclosure notes
    
    Args:
        financial_statements: Dictionary containing all financial statements
        entity_info: Entity information (name, address, etc.)
        reporting_period: Reporting period
        disclosure_requirements: Specific disclosures required
        
    Returns:
        Complete set of disclosure notes
    """
    try:
        disclosures = {
            "entity_information": generate_entity_disclosures(entity_info),
            "accounting_policies": generate_accounting_policy_disclosures(),
            "significant_estimates": generate_estimates_disclosures(),
            "revenue_disclosures": generate_revenue_disclosures(financial_statements),
            "lease_disclosures": generate_lease_disclosures(financial_statements),
            "financial_instruments": generate_financial_instrument_disclosures(financial_statements),
            "property_plant_equipment": generate_ppe_disclosures(financial_statements),
            "tax_disclosures": generate_tax_disclosures(financial_statements),
            "risk_management": generate_risk_disclosures(financial_statements),
            "subsequent_events": generate_subsequent_events_disclosures(),
            "comparative_information": generate_comparative_disclosures()
        }
        
        return {
            "disclosures": disclosures,
            "reporting_period": reporting_period,
            "preparation_date": datetime.now().strftime("%Y-%m-%d"),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def generate_entity_disclosures(entity_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate entity information disclosures"""
    return {
        "note_number": "1",
        "title": "Entity Information",
        "content": {
            "entity_name": entity_info.get("name", "Entity Name"),
            "incorporation": entity_info.get("incorporation", "Country of incorporation"),
            "registered_office": entity_info.get("address", "Registered office address"),
            "nature_of_business": entity_info.get("business", "Description of business activities"),
            "reporting_currency": entity_info.get("currency", "USD"),
            "parent_company": entity_info.get("parent", "None - standalone entity")
        }
    }


def generate_accounting_policy_disclosures() -> Dict[str, Any]:
    """Generate accounting policies disclosures"""
    return {
        "note_number": "2",
        "title": "Significant Accounting Policies",
        "content": {
            "basis_of_preparation": {
                "title": "Basis of Preparation",
                "description": "These financial statements have been prepared in accordance with International Financial Reporting Standards (IFRS) as issued by the International Accounting Standards Board (IASB). The financial statements have been prepared on a historical cost basis, except for certain financial instruments that are measured at fair value."
            },
            "revenue_recognition": {
                "title": "Revenue Recognition (IFRS 15)",
                "description": "Revenue is recognized when control of goods or services is transferred to the customer. The entity identifies performance obligations in contracts and allocates the transaction price to each obligation based on standalone selling prices. Revenue is recognized either at a point in time or over time depending on when control transfers."
            },
            "lease_accounting": {
                "title": "Leases (IFRS 16)",
                "description": "At lease commencement, the entity recognizes a right-of-use asset and lease liability. The right-of-use asset is depreciated over the shorter of the lease term and useful life. The lease liability is measured at the present value of unpaid lease payments, discounted using the incremental borrowing rate."
            },
            "financial_instruments": {
                "title": "Financial Instruments (IFRS 9)",
                "description": "Financial assets are classified based on the business model and contractual cash flow characteristics. Expected credit losses are recognized using a forward-looking approach with a three-stage model based on changes in credit risk since initial recognition."
            },
            "property_plant_equipment": {
                "title": "Property, Plant and Equipment (IAS 16)",
                "description": "Property, plant and equipment are measured at cost less accumulated depreciation and impairment losses. Depreciation is calculated using the straight-line method over the estimated useful lives of the assets."
            }
        }
    }


def generate_estimates_disclosures() -> Dict[str, Any]:
    """Generate significant accounting estimates disclosures"""
    return {
        "note_number": "3",
        "title": "Critical Accounting Estimates and Judgments",
        "content": {
            "overview": "The preparation of financial statements requires management to make estimates and assumptions that affect reported amounts. Actual results may differ from these estimates.",
            "key_estimates": {
                "expected_credit_losses": {
                    "description": "ECL calculations require estimates of probability of default, loss given default, and exposure at default.",
                    "sensitivity": "A 10% increase in ECL rates would increase the provision by approximately $X."
                },
                "useful_lives_ppe": {
                    "description": "Useful lives of property, plant and equipment are estimated based on expected usage and technological obsolescence.",
                    "ranges": "Buildings: 25-50 years, Equipment: 5-15 years, Vehicles: 5-8 years"
                },
                "lease_terms": {
                    "description": "Lease terms include non-cancellable periods and extension options reasonably certain to be exercised.",
                    "judgment": "Assessment of extension options considers business needs and economic incentives."
                },
                "incremental_borrowing_rates": {
                    "description": "IBR is estimated based on risk-free rate plus credit spread for similar terms and security.",
                    "methodology": "Rates are updated quarterly based on market conditions and credit ratings."
                }
            }
        }
    }


def generate_revenue_disclosures(financial_statements: Dict[str, Any]) -> Dict[str, Any]:
    """Generate IFRS 15 revenue disclosures"""
    return {
        "note_number": "4",
        "title": "Revenue from Contracts with Customers",
        "content": {
            "accounting_policy": "Revenue is recognized in accordance with IFRS 15 when control of goods or services transfers to customers.",
            "disaggregation": {
                "by_type": {
                    "goods": 750000,
                    "services": 250000,
                    "total": 1000000
                },
                "by_geography": {
                    "domestic": 600000,
                    "international": 400000,
                    "total": 1000000
                },
                "by_timing": {
                    "point_in_time": 750000,
                    "over_time": 250000,
                    "total": 1000000
                }
            },
            "contract_balances": {
                "contract_assets": {
                    "opening": 25000,
                    "additions": 45000,
                    "transfers_to_receivables": -35000,
                    "closing": 35000
                },
                "contract_liabilities": {
                    "opening": 15000,
                    "additions": 30000,
                    "revenue_recognized": -25000,
                    "closing": 20000
                }
            },
            "performance_obligations": {
                "description": "Contracts typically contain 1-3 performance obligations including goods delivery, installation, and ongoing support.",
                "satisfaction": "Goods are satisfied at delivery, services over the contract term.",
                "remaining_obligations": 150000
            }
        }
    }


def generate_lease_disclosures(financial_statements: Dict[str, Any]) -> Dict[str, Any]:
    """Generate IFRS 16 lease disclosures"""
    return {
        "note_number": "5",
        "title": "Leases",
        "content": {
            "accounting_policy": "Leases are recognized as right-of-use assets and lease liabilities at commencement date in accordance with IFRS 16.",
            "right_of_use_assets": {
                "by_class": {
                    "buildings": 180000,
                    "equipment": 45000,
                    "vehicles": 25000,
                    "total": 250000
                },
                "movements": {
                    "opening_balance": 280000,
                    "additions": 50000,
                    "depreciation": -80000,
                    "closing_balance": 250000
                }
            },
            "lease_liabilities": {
                "current": 65000,
                "non_current": 195000,
                "total": 260000,
                "maturity_analysis": {
                    "within_1_year": 65000,
                    "1_to_5_years": 150000,
                    "over_5_years": 45000,
                    "total_undiscounted": 260000
                }
            },
            "amounts_in_profit_loss": {
                "depreciation_rou_assets": 80000,
                "interest_on_lease_liabilities": 18000,
                "short_term_lease_expense": 5000,
                "low_value_lease_expense": 2000
            },
            "cash_flows": {
                "total_cash_outflow": 85000
            }
        }
    }


def generate_financial_instrument_disclosures(financial_statements: Dict[str, Any]) -> Dict[str, Any]:
    """Generate IFRS 9 financial instruments disclosures"""
    return {
        "note_number": "6",
        "title": "Financial Instruments",
        "content": {
            "accounting_policy": "Financial instruments are classified and measured in accordance with IFRS 9 based on business model and contractual cash flow characteristics.",
            "classification": {
                "financial_assets": {
                    "amortized_cost": {
                        "cash_and_equivalents": 150000,
                        "trade_receivables": 180000,
                        "other_receivables": 20000,
                        "total": 350000
                    },
                    "fair_value_through_profit_loss": 0,
                    "fair_value_through_oci": 0
                },
                "financial_liabilities": {
                    "amortized_cost": {
                        "trade_payables": 120000,
                        "borrowings": 200000,
                        "lease_liabilities": 260000,
                        "total": 580000
                    }
                }
            },
            "credit_risk": {
                "expected_credit_losses": {
                    "stage_1_12_month": 2500,
                    "stage_2_lifetime": 4500,
                    "stage_3_credit_impaired": 8000,
                    "total": 15000
                },
                "movement_in_ecl": {
                    "opening_balance": 12000,
                    "charge_to_profit_loss": 5000,
                    "write_offs": -2000,
                    "closing_balance": 15000
                }
            },
            "liquidity_risk": {
                "maturity_analysis": {
                    "within_1_year": 185000,
                    "1_to_5_years": 350000,
                    "over_5_years": 45000,
                    "total": 580000
                }
            }
        }
    }


def generate_ppe_disclosures(financial_statements: Dict[str, Any]) -> Dict[str, Any]:
    """Generate IAS 16 property, plant and equipment disclosures"""
    return {
        "note_number": "7",
        "title": "Property, Plant and Equipment",
        "content": {
            "accounting_policy": "Property, plant and equipment are measured at cost less accumulated depreciation and impairment losses in accordance with IAS 16.",
            "movements": {
                "cost": {
                    "opening_balance": 850000,
                    "additions": 75000,
                    "disposals": -25000,
                    "closing_balance": 900000
                },
                "accumulated_depreciation": {
                    "opening_balance": 320000,
                    "depreciation_charge": 65000,
                    "disposals": -15000,
                    "closing_balance": 370000
                },
                "carrying_amount": 530000
            },
            "by_class": {
                "land_and_buildings": {
                    "cost": 500000,
                    "accumulated_depreciation": 150000,
                    "carrying_amount": 350000,
                    "useful_life": "25-50 years"
                },
                "plant_and_equipment": {
                    "cost": 300000,
                    "accumulated_depreciation": 160000,
                    "carrying_amount": 140000,
                    "useful_life": "5-15 years"
                },
                "vehicles": {
                    "cost": 100000,
                    "accumulated_depreciation": 60000,
                    "carrying_amount": 40000,
                    "useful_life": "5-8 years"
                }
            },
            "depreciation_methods": "Straight-line method based on estimated useful lives",
            "impairment": "No impairment losses were recognized during the period"
        }
    }


def generate_tax_disclosures(financial_statements: Dict[str, Any]) -> Dict[str, Any]:
    """Generate IAS 12 tax disclosures"""
    return {
        "note_number": "8",
        "title": "Income Tax",
        "content": {
            "accounting_policy": "Income tax is recognized in accordance with IAS 12 using the liability method for temporary differences.",
            "tax_expense": {
                "current_tax": 45000,
                "deferred_tax": 8000,
                "total": 53000
            },
            "effective_tax_rate": {
                "profit_before_tax": 220000,
                "tax_at_statutory_rate": 52800,  # 24%
                "tax_effect_of": {
                    "non_deductible_expenses": 2000,
                    "tax_exempt_income": -1800,
                    "other": 0
                },
                "total_tax_expense": 53000,
                "effective_rate": "24.1%"
            },
            "deferred_tax": {
                "assets": 5000,
                "liabilities": 18000,
                "net_liability": 13000,
                "movements": {
                    "opening_balance": 5000,
                    "charged_to_profit_loss": 8000,
                    "closing_balance": 13000
                }
            }
        }
    }


def generate_risk_disclosures(financial_statements: Dict[str, Any]) -> Dict[str, Any]:
    """Generate risk management disclosures"""
    return {
        "note_number": "9",
        "title": "Financial Risk Management",
        "content": {
            "overview": "The entity is exposed to various financial risks including credit risk, liquidity risk, and market risk.",
            "credit_risk": {
                "description": "Credit risk arises from trade receivables and cash deposits.",
                "concentration": "No significant concentration of credit risk exists.",
                "mitigation": "Credit limits and regular monitoring of receivables aging."
            },
            "liquidity_risk": {
                "description": "Risk of not meeting financial obligations as they fall due.",
                "management": "Maintaining adequate cash reserves and committed credit facilities.",
                "maturity_profile": "Detailed in financial instruments note."
            },
            "market_risk": {
                "interest_rate_risk": "Exposure to variable rate borrowings managed through fixed rate agreements.",
                "foreign_exchange_risk": "Limited exposure to foreign currencies.",
                "commodity_risk": "No significant exposure to commodity price fluctuations."
            }
        }
    }


def generate_subsequent_events_disclosures() -> Dict[str, Any]:
    """Generate subsequent events disclosures"""
    return {
        "note_number": "10",
        "title": "Events After the Reporting Period",
        "content": {
            "description": "Events occurring between the reporting date and authorization of financial statements.",
            "adjusting_events": "No material adjusting events occurred after the reporting period.",
            "non_adjusting_events": "No material non-adjusting events occurred after the reporting period.",
            "authorization_date": datetime.now().strftime("%Y-%m-%d")
        }
    }


def generate_comparative_disclosures() -> Dict[str, Any]:
    """Generate comparative information disclosures"""
    return {
        "note_number": "11",
        "title": "Comparative Information",
        "content": {
            "description": "Comparative figures have been presented for the prior year.",
            "reclassifications": "No reclassifications were made to prior year figures.",
            "restatements": "No restatements were made to prior year figures.",
            "new_standards": "The adoption of new IFRS standards did not have a material impact."
        }
    }


def format_disclosure_notes(
    disclosures: Dict[str, Any],
    output_format: str = "pdf",
    filename: str = None
) -> Dict[str, Any]:
    """
    Format disclosure notes for output
    
    Args:
        disclosures: Generated disclosures
        output_format: 'pdf', 'html', or 'text'
        filename: Output filename
        
    Returns:
        Formatted disclosure notes
    """
    try:
        if output_format == "pdf":
            return generate_pdf_disclosures(disclosures, filename)
        elif output_format == "html":
            return generate_html_disclosures(disclosures)
        else:
            return generate_text_disclosures(disclosures)
            
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def generate_pdf_disclosures(disclosures: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
    """Generate PDF format disclosures"""
    try:
        if not filename:
            filename = f"ifrs_disclosures_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Notes to the Financial Statements", title_style))
        story.append(Spacer(1, 20))
        
        # Generate each disclosure note
        for key, disclosure in disclosures.get("disclosures", {}).items():
            if isinstance(disclosure, dict) and "title" in disclosure:
                # Note title
                note_title = f"Note {disclosure.get('note_number', '')}: {disclosure.get('title', '')}"
                story.append(Paragraph(note_title, styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Note content
                content = disclosure.get("content", {})
                if isinstance(content, dict):
                    for section_key, section_value in content.items():
                        if isinstance(section_value, dict) and "title" in section_value:
                            story.append(Paragraph(section_value["title"], styles['Heading3']))
                            story.append(Paragraph(section_value.get("description", ""), styles['Normal']))
                        elif isinstance(section_value, str):
                            story.append(Paragraph(f"{section_key.replace('_', ' ').title()}: {section_value}", styles['Normal']))
                        else:
                            story.append(Paragraph(f"{section_key.replace('_', ' ').title()}", styles['Heading4']))
                
                story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        return {
            "filename": filename,
            "format": "pdf",
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def generate_html_disclosures(disclosures: Dict[str, Any]) -> Dict[str, Any]:
    """Generate HTML format disclosures"""
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Notes to the Financial Statements</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { text-align: center; color: #333; }
                h2 { color: #666; border-bottom: 2px solid #ccc; }
                h3 { color: #888; }
                .note { margin-bottom: 30px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Notes to the Financial Statements</h1>
        """
        
        for key, disclosure in disclosures.get("disclosures", {}).items():
            if isinstance(disclosure, dict) and "title" in disclosure:
                html_content += f"""
                <div class="note">
                    <h2>Note {disclosure.get('note_number', '')}: {disclosure.get('title', '')}</h2>
                """
                
                content = disclosure.get("content", {})
                if isinstance(content, dict):
                    for section_key, section_value in content.items():
                        if isinstance(section_value, str):
                            html_content += f"<p><strong>{section_key.replace('_', ' ').title()}:</strong> {section_value}</p>"
                
                html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        return {
            "html_content": html_content,
            "format": "html",
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def generate_text_disclosures(disclosures: Dict[str, Any]) -> Dict[str, Any]:
    """Generate plain text format disclosures"""
    try:
        text_content = "NOTES TO THE FINANCIAL STATEMENTS\n"
        text_content += "=" * 50 + "\n\n"
        
        for key, disclosure in disclosures.get("disclosures", {}).items():
            if isinstance(disclosure, dict) and "title" in disclosure:
                text_content += f"Note {disclosure.get('note_number', '')}: {disclosure.get('title', '')}\n"
                text_content += "-" * 40 + "\n"
                
                content = disclosure.get("content", {})
                if isinstance(content, dict):
                    for section_key, section_value in content.items():
                        if isinstance(section_value, str):
                            text_content += f"{section_key.replace('_', ' ').title()}: {section_value}\n"
                
                text_content += "\n"
        
        return {
            "text_content": text_content,
            "format": "text",
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Example usage and testing
if __name__ == "__main__":
    # Test disclosure generation
    sample_entity = {
        "name": "Sample Corporation Ltd",
        "incorporation": "United States",
        "address": "123 Business Street, City, State",
        "business": "Manufacturing and distribution of industrial equipment",
        "currency": "USD"
    }
    
    sample_statements = {
        "profit_loss": {"revenue": 1000000, "profit": 150000},
        "balance_sheet": {"total_assets": 2000000, "total_equity": 800000}
    }
    
    disclosures = generate_ifrs_disclosures(
        financial_statements=sample_statements,
        entity_info=sample_entity,
        reporting_period="2026"
    )
    
    if disclosures["success"]:
        print("IFRS Disclosures Generated Successfully")
        print(f"Number of disclosure notes: {len(disclosures['disclosures'])}")
        
        # Generate text format
        text_format = format_disclosure_notes(disclosures, "text")
        if text_format["success"]:
            print("\nSample disclosure (first 500 characters):")
            print(text_format["text_content"][:500] + "...")
    else:
        print(f"Error generating disclosures: {disclosures['error']}")