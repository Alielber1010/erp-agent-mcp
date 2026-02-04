"""
IFRS Tools Package
Comprehensive IFRS calculation modules for financial reporting compliance
"""

__version__ = "1.0.0"
__author__ = "IFRS Integration System"

# Import all IFRS modules for easy access
try:
    from .ifrs_16_leases import calculate_ifrs16_lease, generate_lease_schedule
    from .ifrs_9_ecl import calculate_ifrs9_ecl, stage_receivables
    from .ias_16_depreciation import calculate_ias16_depreciation, generate_depreciation_schedule
    from .ifrs_15_revenue import calculate_ifrs15_revenue, allocate_transaction_price
    from .statement_builder import build_ifrs_profit_loss, build_ifrs_balance_sheet, build_ifrs_cash_flow
    from .disclosure_generator import generate_ifrs_disclosures, format_disclosure_notes
except ImportError:
    # Handle case where modules are not yet available
    pass

__all__ = [
    'calculate_ifrs16_lease',
    'generate_lease_schedule',
    'calculate_ifrs9_ecl',
    'stage_receivables',
    'calculate_ias16_depreciation',
    'generate_depreciation_schedule',
    'calculate_ifrs15_revenue',
    'allocate_transaction_price',
    'build_ifrs_profit_loss',
    'build_ifrs_balance_sheet',
    'build_ifrs_cash_flow',
    'generate_ifrs_disclosures',
    'format_disclosure_notes'
]