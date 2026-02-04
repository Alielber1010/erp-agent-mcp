import os
import re
import sqlite3
import sys
from typing import List, Dict, Any
from fastmcp import FastMCP

# Add IFRS tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ifrs_tools'))

# Import IFRS calculation modules
try:
    from ifrs_tools.ifrs_16_leases import calculate_ifrs16_lease, generate_lease_schedule
    from ifrs_tools.ifrs_9_ecl import calculate_ifrs9_ecl, stage_receivables
    from ifrs_tools.ias_16_depreciation import calculate_ias16_depreciation, calculate_impairment_test
    from ifrs_tools.ifrs_15_revenue import calculate_ifrs15_revenue, allocate_transaction_price
    from ifrs_tools.statement_builder import build_ifrs_profit_loss, build_ifrs_balance_sheet, build_ifrs_cash_flow
    from ifrs_tools.disclosure_generator import generate_ifrs_disclosures, format_disclosure_notes
    IFRS_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: IFRS tools not available: {e}")
    IFRS_TOOLS_AVAILABLE = False

# Database path
DATABASE_PATH = "C:/Users/DELL/Downloads/erp-mcp-dify/erp_database.db"

# Create MCP server
mcp = FastMCP("SQLite ERP MCP")

# ---------- Safety Guard ----------
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create)\b", re.I)

def is_safe_sql(sql: str) -> bool:
    """Only allow SELECT statements"""
    return sql.strip().lower().startswith("select") and not FORBIDDEN.search(sql)

# ---------- Helper Function ----------
def execute_query(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SQL query and return results as list of dictionaries"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This allows column access by name
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to list of dictionaries
        return [dict(row) for row in rows]
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")

# ---------- SQL Query Tool ----------
@mcp.tool()
async def run_sql_query(sql: str) -> dict:
    """
    Execute a safe SELECT query on the ERP database.
    
    Args:
        sql: A SELECT SQL query to execute
        
    Returns:
        Dictionary with rows and row_count, or error message
        
    Example:
        sql = "SELECT * FROM customers LIMIT 10"
    """
    if not is_safe_sql(sql):
        return {"error": "Only safe SELECT queries are allowed. No INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements."}
    
    try:
        rows = execute_query(sql)
        return {
            "rows": rows,
            "row_count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Database Schema ----------
@mcp.tool()
async def get_database_schema() -> dict:
    """
    Get the complete database schema including all tables and their columns.
    
    Returns:
        Dictionary with table names and their column information
    """
    try:
        # Get all tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        tables = execute_query(tables_query)
        
        schema = {}
        for table in tables:
            table_name = table['name']
            # Get column info for each table
            columns_query = f"PRAGMA table_info({table_name})"
            columns = execute_query(columns_query)
            schema[table_name] = columns
        
        return {
            "schema": schema,
            "table_count": len(tables),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Table Data ----------
@mcp.tool()
async def get_table_data(table_name: str, limit: int = 100) -> dict:
    """
    Get all data from a specific table with optional limit.
    
    Args:
        table_name: Name of the table to query
        limit: Maximum number of rows to return (default: 100)
        
    Returns:
        Dictionary with table data
        
    Example:
        table_name = "customers"
        limit = 50
    """
    # Validate table name (prevent SQL injection)
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        return {"error": "Invalid table name"}
    
    try:
        # Check if table exists
        check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        table_exists = execute_query(check_query, (table_name,))
        
        if not table_exists:
            return {"error": f"Table '{table_name}' does not exist"}
        
        # Get data
        sql = f"SELECT * FROM {table_name} LIMIT {limit}"
        rows = execute_query(sql)
        
        return {
            "table_name": table_name,
            "rows": rows,
            "row_count": len(rows),
            "limited": limit,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Top Customers ----------
@mcp.tool()
async def get_top_customers(limit: int = 10) -> dict:
    """
    Get top customers by total spending.
    
    Args:
        limit: Number of top customers to return (default: 10)
        
    Returns:
        List of top customers with their total spending
    """
    try:
        sql = """
            SELECT 
                c.customer_id,
                c.customer_name,
                c.email,
                c.city,
                c.country,
                COUNT(o.order_id) as total_orders,
                ROUND(SUM(o.total_amount), 2) as total_spent,
                ROUND(AVG(o.total_amount), 2) as avg_order_value
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id
            HAVING total_orders > 0
            ORDER BY total_spent DESC
            LIMIT ?
        """
        rows = execute_query(sql, (limit,))
        
        return {
            "top_customers": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Low Stock Products ----------
@mcp.tool()
async def get_low_stock_products() -> dict:
    """
    Get products that are below their reorder level.
    
    Returns:
        List of products that need to be reordered
    """
    try:
        sql = """
            SELECT 
                product_id,
                product_name,
                category,
                sku,
                stock_quantity,
                reorder_level,
                (reorder_level - stock_quantity) as units_needed,
                unit_price,
                supplier_id
            FROM products
            WHERE stock_quantity < reorder_level
            ORDER BY units_needed DESC
        """
        rows = execute_query(sql)
        
        return {
            "low_stock_products": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Sales Summary ----------
@mcp.tool()
async def get_sales_summary(start_date: str = None, end_date: str = None) -> dict:
    """
    Get sales summary with optional date filtering.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        
    Returns:
        Sales summary including total orders, revenue, and average order value
    """
    try:
        if start_date and end_date:
            sql = """
                SELECT 
                    COUNT(*) as total_orders,
                    ROUND(SUM(total_amount), 2) as total_revenue,
                    ROUND(AVG(total_amount), 2) as avg_order_value,
                    MIN(order_date) as first_order,
                    MAX(order_date) as last_order,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM orders
                WHERE order_date BETWEEN ? AND ?
            """
            rows = execute_query(sql, (start_date, end_date))
        else:
            sql = """
                SELECT 
                    COUNT(*) as total_orders,
                    ROUND(SUM(total_amount), 2) as total_revenue,
                    ROUND(AVG(total_amount), 2) as avg_order_value,
                    MIN(order_date) as first_order,
                    MAX(order_date) as last_order,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM orders
            """
            rows = execute_query(sql)
        
        return {
            "summary": rows[0] if rows else {},
            "date_range": {
                "start": start_date,
                "end": end_date
            } if start_date and end_date else None,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Monthly Sales ----------
@mcp.tool()
async def get_monthly_sales(months: int = 12) -> dict:
    """
    Get monthly sales breakdown.
    
    Args:
        months: Number of recent months to retrieve (default: 12)
        
    Returns:
        Monthly sales data
    """
    try:
        sql = """
            SELECT 
                strftime('%Y-%m', order_date) as month,
                COUNT(*) as num_orders,
                ROUND(SUM(total_amount), 2) as revenue,
                ROUND(AVG(total_amount), 2) as avg_order_value
            FROM orders
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
        """
        rows = execute_query(sql, (months,))
        
        return {
            "monthly_sales": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Product Performance ----------
@mcp.tool()
async def get_product_performance(limit: int = 20) -> dict:
    """
    Get best-selling products.
    
    Args:
        limit: Number of top products to return (default: 20)
        
    Returns:
        List of best-selling products with sales metrics
    """
    try:
        sql = """
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                p.sku,
                SUM(oi.quantity) as units_sold,
                ROUND(SUM(oi.subtotal), 2) as total_revenue,
                COUNT(DISTINCT oi.order_id) as num_orders,
                ROUND(AVG(oi.unit_price), 2) as avg_price
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id
            ORDER BY units_sold DESC
            LIMIT ?
        """
        rows = execute_query(sql, (limit,))
        
        return {
            "top_products": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Invoice Status ----------
@mcp.tool()
async def get_invoice_status() -> dict:
    """
    Get invoice payment status summary.
    
    Returns:
        Invoice status breakdown with payment information
    """
    try:
        sql = """
            SELECT 
                status,
                COUNT(*) as num_invoices,
                ROUND(SUM(total_amount), 2) as total_invoiced,
                ROUND(SUM(paid_amount), 2) as total_paid,
                ROUND(SUM(total_amount - paid_amount), 2) as outstanding
            FROM invoices
            GROUP BY status
            ORDER BY outstanding DESC
        """
        rows = execute_query(sql)
        
        return {
            "invoice_status": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Employee Performance ----------
@mcp.tool()
async def get_employee_performance(limit: int = 20) -> dict:
    """
    Get employee performance based on orders handled.
    
    Args:
        limit: Number of top employees to return (default: 20)
        
    Returns:
        Employee performance metrics
    """
    try:
        sql = """
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name as employee_name,
                e.department,
                e.position,
                COUNT(o.order_id) as orders_handled,
                ROUND(SUM(o.total_amount), 2) as total_sales,
                ROUND(AVG(o.total_amount), 2) as avg_order_value
            FROM employees e
            LEFT JOIN orders o ON e.employee_id = o.employee_id
            GROUP BY e.employee_id
            HAVING orders_handled > 0
            ORDER BY orders_handled DESC
            LIMIT ?
        """
        rows = execute_query(sql, (limit,))
        
        return {
            "employee_performance": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Get Inventory Value ----------
@mcp.tool()
async def get_inventory_value() -> dict:
    """
    Get inventory value by category.
    
    Returns:
        Inventory value breakdown by product category
    """
    try:
        sql = """
            SELECT 
                category,
                COUNT(*) as num_products,
                SUM(stock_quantity) as total_units,
                ROUND(SUM(stock_quantity * cost_price), 2) as inventory_cost,
                ROUND(SUM(stock_quantity * unit_price), 2) as potential_revenue,
                ROUND(SUM(stock_quantity * (unit_price - cost_price)), 2) as potential_profit
            FROM products
            GROUP BY category
            ORDER BY inventory_cost DESC
        """
        rows = execute_query(sql)
        
        return {
            "inventory_by_category": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- IFRS Database Query Functions ----------

@mcp.tool()
async def get_ifrs_mapped_accounts() -> dict:
    """
    Get chart of accounts with IFRS mapping.
    
    Returns:
        Dictionary with IFRS mapped accounts
    """
    try:
        sql = """
            SELECT account_code, account_name, ifrs_category, 
                   ifrs_subcategory, statement_type, ifrs_line_item, notes_required
            FROM ifrs_account_mapping
            ORDER BY ifrs_category, ifrs_subcategory
        """
        rows = execute_query(sql)
        return {
            "mapped_accounts": rows,
            "count": len(rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def get_trial_balance(start_date: str, end_date: str) -> dict:
    """
    Get trial balance for period (foundation for IFRS statements).
    
    Args:
        start_date: Period start date (YYYY-MM-DD)
        end_date: Period end date (YYYY-MM-DD)
        
    Returns:
        Trial balance with IFRS mapping
    """
    try:
        # Get revenue from orders (simplified trial balance)
        sql = """
            SELECT 
                '4000' as account_code,
                'Revenue' as account_name,
                SUM(total_amount) as balance,
                'Operating' as ifrs_category,
                'Revenue' as ifrs_subcategory,
                'P&L' as statement_type
            FROM orders
            WHERE order_date BETWEEN ? AND ?
            AND status IN ('Delivered', 'Shipped')
            
            UNION ALL
            
            SELECT 
                '5000' as account_code,
                'Cost of Sales' as account_name,
                SUM(subtotal * 0.6) as balance,
                'Operating' as ifrs_category,
                'COGS' as ifrs_subcategory,
                'P&L' as statement_type
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_date BETWEEN ? AND ?
            AND o.status IN ('Delivered', 'Shipped')
        """
        rows = execute_query(sql, (start_date, end_date, start_date, end_date))
        
        return {
            "trial_balance": rows,
            "period": {"start": start_date, "end": end_date},
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def get_fixed_assets_register() -> dict:
    """
    Get fixed assets register for depreciation calculations.
    
    Returns:
        List of fixed assets with details
    """
    try:
        sql = """
            SELECT asset_id, asset_name, asset_category, acquisition_date,
                   cost, useful_life_years, residual_value, depreciation_method,
                   accumulated_depreciation, carrying_amount, location
            FROM fixed_assets
            ORDER BY asset_category, asset_name
        """
        rows = execute_query(sql)
        return {
            "fixed_assets": rows,
            "count": len(rows),
            "total_cost": sum(row.get('cost', 0) for row in rows),
            "total_carrying_amount": sum(row.get('carrying_amount', 0) for row in rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def get_lease_portfolio() -> dict:
    """
    Get active leases for IFRS 16 calculations.
    
    Returns:
        List of active leases
    """
    try:
        sql = """
            SELECT lease_id, lease_type, lessor_name, start_date, end_date,
                   annual_payment, payment_frequency, incremental_borrowing_rate,
                   rou_asset_initial, lease_liability_initial, status
            FROM leases
            WHERE status = 'active'
            ORDER BY lease_type, start_date
        """
        rows = execute_query(sql)
        return {
            "active_leases": rows,
            "count": len(rows),
            "total_annual_payments": sum(row.get('annual_payment', 0) for row in rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def get_revenue_contracts() -> dict:
    """
    Get revenue contracts for IFRS 15 analysis.
    
    Returns:
        List of revenue contracts
    """
    try:
        sql = """
            SELECT contract_id, customer_id, contract_date, total_consideration,
                   performance_obligations, revenue_recognition_pattern,
                   revenue_recognized_to_date, contract_status
            FROM revenue_contracts
            WHERE contract_status = 'active'
            ORDER BY contract_date DESC
        """
        rows = execute_query(sql)
        return {
            "revenue_contracts": rows,
            "count": len(rows),
            "total_consideration": sum(row.get('total_consideration', 0) for row in rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def get_receivables_aging() -> dict:
    """
    Get receivables aging for IFRS 9 ECL calculation.
    
    Returns:
        Receivables aging analysis
    """
    try:
        # Create receivables aging from invoices (simplified)
        sql = """
            SELECT 
                invoice_id,
                customer_id,
                invoice_date,
                due_date,
                total_amount as amount,
                CASE 
                    WHEN due_date >= date('now') THEN 0
                    ELSE julianday('now') - julianday(due_date)
                END as days_overdue
            FROM invoices
            WHERE status IN ('Sent', 'Overdue')
            ORDER BY days_overdue DESC
        """
        rows = execute_query(sql)
        
        # Add ECL staging
        for row in rows:
            days_overdue = row.get('days_overdue', 0)
            if days_overdue > 90:
                row['ecl_stage'] = 3
            elif days_overdue > 30:
                row['ecl_stage'] = 2
            else:
                row['ecl_stage'] = 1
        
        return {
            "receivables": rows,
            "count": len(rows),
            "total_amount": sum(row.get('amount', 0) for row in rows),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- IFRS Calculation Functions ----------

@mcp.tool()
async def calculate_ifrs16_lease_liability(
    lease_id: str,
    start_date: str,
    end_date: str,
    annual_payment: float,
    ibr_rate: float,
    frequency: str = "monthly"
) -> dict:
    """
    Calculate IFRS 16 lease liability and ROU asset.
    
    Args:
        lease_id: Lease identifier
        start_date: Lease start date (YYYY-MM-DD)
        end_date: Lease end date (YYYY-MM-DD)
        annual_payment: Annual lease payment
        ibr_rate: Incremental borrowing rate (as decimal, e.g., 0.06)
        frequency: Payment frequency (monthly, quarterly, annually)
        
    Returns:
        IFRS 16 lease calculation results
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        result = calculate_ifrs16_lease(
            lease_id=lease_id,
            start_date=start_date,
            end_date=end_date,
            annual_payment=annual_payment,
            ibr_rate=ibr_rate,
            frequency=frequency
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def calculate_ifrs9_expected_credit_loss(receivables_data: list) -> dict:
    """
    Calculate Expected Credit Loss under IFRS 9.
    
    Args:
        receivables_data: List of receivables with aging information
        
    Returns:
        ECL calculation results
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        result = calculate_ifrs9_ecl(receivables_data)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def calculate_ias16_asset_depreciation(
    asset_id: str,
    asset_name: str,
    cost: float,
    useful_life_years: int,
    residual_value: float,
    method: str = "straight-line",
    acquisition_date: str = None,
    reporting_date: str = None
) -> dict:
    """
    Calculate depreciation under IAS 16.
    
    Args:
        asset_id: Asset identifier
        asset_name: Asset description
        cost: Original cost
        useful_life_years: Useful life in years
        residual_value: Estimated residual value
        method: Depreciation method
        acquisition_date: Acquisition date (YYYY-MM-DD)
        reporting_date: Reporting date (YYYY-MM-DD)
        
    Returns:
        Depreciation calculation results
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        result = calculate_ias16_depreciation(
            asset_id=asset_id,
            asset_name=asset_name,
            cost=cost,
            useful_life_years=useful_life_years,
            residual_value=residual_value,
            method=method,
            acquisition_date=acquisition_date,
            reporting_date=reporting_date
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def calculate_ifrs15_revenue_recognition(
    contract_id: str,
    contract_start_date: str,
    performance_obligations: list,
    progress_to_date: dict = None,
    reporting_date: str = None
) -> dict:
    """
    Calculate revenue recognition under IFRS 15.
    
    Args:
        contract_id: Contract identifier
        contract_start_date: Contract start date
        performance_obligations: List of performance obligations
        progress_to_date: Progress percentage for each obligation
        reporting_date: Current reporting date
        
    Returns:
        Revenue recognition calculation
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        result = calculate_ifrs15_revenue(
            contract_id=contract_id,
            contract_start_date=contract_start_date,
            performance_obligations=performance_obligations,
            progress_to_date=progress_to_date,
            reporting_date=reporting_date
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def perform_ias36_impairment_test(
    asset_id: str,
    carrying_amount: float,
    fair_value: float = None,
    value_in_use: float = None,
    disposal_costs: float = 0
) -> dict:
    """
    Perform IAS 36 impairment test.
    
    Args:
        asset_id: Asset identifier
        carrying_amount: Current carrying amount
        fair_value: Fair value of asset
        value_in_use: Value in use calculation
        disposal_costs: Costs to dispose of asset
        
    Returns:
        Impairment test results
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        result = calculate_impairment_test(
            asset_id=asset_id,
            carrying_amount=carrying_amount,
            fair_value=fair_value,
            value_in_use=value_in_use,
            disposal_costs=disposal_costs
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- IFRS Statement Generation Functions ----------

@mcp.tool()
async def generate_ifrs_profit_loss_statement(
    period_start: str,
    period_end: str,
    include_adjustments: bool = True
) -> dict:
    """
    Generate IFRS 18 compliant Profit or Loss statement.
    
    Args:
        period_start: Period start date (YYYY-MM-DD)
        period_end: Period end date (YYYY-MM-DD)
        include_adjustments: Whether to include IFRS adjustments
        
    Returns:
        IFRS Profit or Loss statement
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        # Get trial balance
        trial_balance_result = await get_trial_balance(period_start, period_end)
        if not trial_balance_result["success"]:
            return trial_balance_result
        
        # Get IFRS adjustments if requested
        adjustments = []
        if include_adjustments:
            adj_sql = """
                SELECT adjustment_type, debit_amount, credit_amount, description
                FROM ifrs_adjustments
                WHERE period_start <= ? AND period_end >= ?
            """
            adjustments = execute_query(adj_sql, (period_start, period_end))
        
        # Build statement
        result = build_ifrs_profit_loss(
            trial_balance=trial_balance_result["trial_balance"],
            ifrs_adjustments=adjustments,
            period_start=period_start,
            period_end=period_end
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def generate_ifrs_balance_sheet(
    reporting_date: str,
    include_adjustments: bool = True
) -> dict:
    """
    Generate IFRS compliant Statement of Financial Position.
    
    Args:
        reporting_date: Balance sheet date (YYYY-MM-DD)
        include_adjustments: Whether to include IFRS adjustments
        
    Returns:
        IFRS Balance Sheet
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        # Get account balances (simplified - would normally come from GL)
        balance_sql = """
            SELECT account_code, account_name, 
                   CASE 
                       WHEN account_code LIKE '1%' THEN 100000  -- Assets
                       WHEN account_code LIKE '2%' THEN 50000   -- Liabilities  
                       WHEN account_code LIKE '3%' THEN 150000  -- Equity
                       ELSE 0
                   END as balance,
                   ifrs_category, ifrs_subcategory, statement_type, ifrs_line_item
            FROM ifrs_account_mapping
            WHERE statement_type = 'Balance Sheet'
        """
        trial_balance = execute_query(balance_sql)
        
        # Get IFRS adjustments if requested
        adjustments = []
        if include_adjustments:
            adj_sql = """
                SELECT adjustment_type, debit_amount, credit_amount, description
                FROM ifrs_adjustments
                WHERE period_end <= ?
            """
            adjustments = execute_query(adj_sql, (reporting_date,))
        
        # Build balance sheet
        result = build_ifrs_balance_sheet(
            trial_balance=trial_balance,
            ifrs_adjustments=adjustments,
            reporting_date=reporting_date
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def generate_ifrs_cash_flow_statement(
    period_start: str,
    period_end: str,
    method: str = "indirect"
) -> dict:
    """
    Generate IFRS compliant Statement of Cash Flows.
    
    Args:
        period_start: Period start date (YYYY-MM-DD)
        period_end: Period end date (YYYY-MM-DD)
        method: Cash flow method ('direct' or 'indirect')
        
    Returns:
        IFRS Cash Flow statement
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        # Get P&L data
        pl_result = await generate_ifrs_profit_loss_statement(period_start, period_end)
        if not pl_result["success"]:
            return pl_result
        
        # Get balance sheet data (current and prior)
        bs_current = await generate_ifrs_balance_sheet(period_end)
        bs_prior = await generate_ifrs_balance_sheet(period_start)
        
        if not (bs_current["success"] and bs_prior["success"]):
            return {"error": "Could not generate balance sheet data", "success": False}
        
        # Build cash flow statement
        result = build_ifrs_cash_flow(
            profit_loss_data=pl_result,
            balance_sheet_current=bs_current["statement"],
            balance_sheet_prior=bs_prior["statement"],
            period_start=period_start,
            period_end=period_end,
            method=method
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.tool()
async def generate_ifrs_disclosure_notes(
    reporting_period: str,
    entity_name: str = "Sample Entity",
    output_format: str = "text"
) -> dict:
    """
    Generate IFRS disclosure notes.
    
    Args:
        reporting_period: Reporting period (e.g., "2026")
        entity_name: Entity name
        output_format: Output format ('text', 'html', 'pdf')
        
    Returns:
        IFRS disclosure notes
    """
    if not IFRS_TOOLS_AVAILABLE:
        return {"error": "IFRS tools not available", "success": False}
    
    try:
        # Get financial statements
        period_start = f"{reporting_period}-01-01"
        period_end = f"{reporting_period}-12-31"
        
        pl_statement = await generate_ifrs_profit_loss_statement(period_start, period_end)
        bs_statement = await generate_ifrs_balance_sheet(period_end)
        
        financial_statements = {
            "profit_loss": pl_statement.get("statement", {}),
            "balance_sheet": bs_statement.get("statement", {})
        }
        
        entity_info = {
            "name": entity_name,
            "incorporation": "Country of incorporation",
            "business": "Business description",
            "currency": "USD"
        }
        
        # Generate disclosures
        disclosures = generate_ifrs_disclosures(
            financial_statements=financial_statements,
            entity_info=entity_info,
            reporting_period=reporting_period
        )
        
        if disclosures["success"]:
            # Format disclosures
            formatted = format_disclosure_notes(disclosures, output_format)
            return formatted
        else:
            return disclosures
            
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

# ---------- Run MCP ----------
if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"ERROR: Database not found at {DATABASE_PATH}")
        print("Please ensure the database file exists at the specified path.")
    else:
        print(f"Starting SQLite ERP MCP Server...")
        print(f"Database: {DATABASE_PATH}")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8027)