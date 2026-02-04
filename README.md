# IFRS-Compliant ERP MCP Server

[![GitHub Stars](https://img.shields.io/github/stars/Alielber1010/erp-agent-mcp?style=flat-square)](https://github.com/Alielber1010/erp-agent-mcp/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Alielber1010/erp-agent-mcp?style=flat-square)](https://github.com/Alielber1010/erp-agent-mcp/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

A comprehensive Model Context Protocol (MCP) server that transforms your ERP data into IFRS-compliant financial statements with automated calculations and professional disclosures.

## 📺 Demo & Documentation

- **Live Demo:** [Coming Soon]
- **Documentation:** [GitHub Wiki](https://github.com/Alielber1010/erp-agent-mcp/wiki)
- **API Reference:** [GitHub Pages](https://alielber1010.github.io/erp-agent-mcp/)

## 🎯 What This Does

This MCP server connects to your existing ERP database and provides 18+ specialized tools for:
- **IFRS 16** lease accounting (ROU assets, lease liabilities)
- **IFRS 9** expected credit loss calculations
- **IFRS 15** revenue recognition from contracts
- **IAS 16** property, plant & equipment depreciation
- **Complete financial statement generation** (P&L, Balance Sheet, Cash Flow)
- **Professional disclosure notes** with automated formatting

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   python server.py
   ```
   Server runs on `http://localhost:8027`

2. **Connect from your AI assistant** (Claude, ChatGPT, etc.) using MCP protocol

3. **Start asking IFRS questions!**

## 💡 Use Cases & Example Prompts

### 1. Lease Accounting (IFRS 16)
**Use Case:** Calculate lease liabilities and right-of-use assets for office, equipment, or vehicle leases.

**Example Prompt:**
```
"Calculate the IFRS 16 lease accounting for our new office lease:
- Lease starts January 1, 2026
- Lease ends December 31, 2030  
- Annual payment: $48,000
- Monthly payments
- Our borrowing rate is 6%

Show me the lease liability, ROU asset, and annual depreciation."
```

### 2. Expected Credit Loss (IFRS 9)
**Use Case:** Calculate provisions for bad debts using the 3-stage ECL model.

**Example Prompt:**
```
"Analyze our receivables for expected credit losses. Get the current receivables aging and calculate the IFRS 9 ECL provision. Show me the breakdown by stage and the total provision needed."
```

### 3. Revenue Recognition (IFRS 15)
**Use Case:** Properly recognize revenue from multi-element contracts.

**Example Prompt:**
```
"We have a software contract with:
- Software license: $60,000 (delivered immediately)
- Implementation services: $30,000 (6 months)
- Annual support: $20,000 (ongoing)

How should we recognize revenue under IFRS 15? Show the allocation and recognition pattern."
```

### 4. Asset Depreciation (IAS 16)
**Use Case:** Calculate depreciation schedules and check for impairment.

**Example Prompt:**
```
"Calculate depreciation for our manufacturing equipment:
- Cost: $150,000
- Useful life: 10 years
- Residual value: $15,000
- Acquired: January 2022

Show current carrying amount and annual depreciation expense."
```

### 5. Complete Financial Statements
**Use Case:** Generate full IFRS-compliant financial statements.

**Example Prompt:**
```
"Generate complete IFRS financial statements for 2026 including:
- Statement of Profit or Loss
- Statement of Financial Position  
- Statement of Cash Flows
- All required disclosure notes

Include all IFRS adjustments for leases, ECL, and depreciation."
```

### 6. Specific IFRS Analysis
**Use Case:** Get detailed analysis of specific IFRS requirements.

**Example Prompts:**
```
"Show me all our active leases and their IFRS 16 impact on the balance sheet."

"What's our total expected credit loss provision and how does it break down by customer aging?"

"Generate the property, plant & equipment note with depreciation methods and useful lives."

"Create a lease maturity analysis showing payments due in the next 5 years."
```

### 7. Compliance Reporting
**Use Case:** Prepare audit-ready IFRS documentation.

**Example Prompt:**
```
"Prepare a complete IFRS compliance package including:
- All financial statements with comparative figures
- Detailed accounting policy notes
- Risk management disclosures
- Significant estimates and judgments
- Export everything to PDF format"
```

## 🔧 Available MCP Tools

### Database Query Tools (6)
- `get_ifrs_mapped_accounts` - Chart of accounts with IFRS mapping
- `get_trial_balance` - Foundation data for statements
- `get_fixed_assets_register` - Asset details for depreciation
- `get_lease_portfolio` - Active leases for IFRS 16
- `get_revenue_contracts` - Contract details for IFRS 15
- `get_receivables_aging` - AR aging for ECL calculation

### IFRS Calculation Tools (6)
- `calculate_ifrs16_lease_liability` - Lease accounting calculations
- `calculate_ifrs9_expected_credit_loss` - ECL provisions
- `calculate_ias16_asset_depreciation` - Depreciation schedules
- `calculate_ifrs15_revenue_recognition` - Revenue recognition
- `perform_ias36_impairment_test` - Asset impairment testing
- Plus additional specialized calculations

### Statement Generation Tools (4)
- `generate_ifrs_profit_loss_statement` - P&L with IFRS adjustments
- `generate_ifrs_balance_sheet` - Statement of Financial Position
- `generate_ifrs_cash_flow_statement` - Cash flow statement
- `generate_ifrs_disclosure_notes` - Professional disclosure notes

## 📊 Sample Data Included

The system comes with realistic sample data:
- 4 fixed assets with depreciation schedules
- 3 active leases for IFRS 16 testing
- 20 receivables with aging for ECL calculation
- 5 revenue contracts for IFRS 15 analysis
- Complete chart of accounts with IFRS mapping

## 🎨 Output Formats

- **Structured JSON** for programmatic use
- **Formatted tables** for easy reading
- **Professional PDF reports** for audit documentation
- **Excel exports** for further analysis

## 💼 Perfect For

- **CFOs & Finance Teams** preparing IFRS statements
- **External Auditors** reviewing IFRS compliance
- **Financial Consultants** implementing IFRS
- **AI Assistants** providing financial analysis
- **ERP Systems** needing IFRS reporting

## 🔒 Data Security

- Read-only access to your ERP database
- No data modification capabilities
- Local processing - your data stays on your servers
- Audit trail of all calculations

## 📈 Business Impact

- **Reduce** manual IFRS calculations from days to minutes
- **Ensure** compliance with latest IFRS standards
- **Generate** audit-ready documentation automatically
- **Eliminate** calculation errors and inconsistencies
- **Accelerate** month-end and year-end reporting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Areas
- 🌍 Multi-currency support (IAS 21)
- 🏢 Consolidation accounting (IFRS 10) 
- 📊 Enhanced analytics and dashboards
- 📚 Documentation improvements
- 🧪 Additional test scenarios

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Support

If this project helps you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs via [Issues](https://github.com/Alielber1010/erp-agent-mcp/issues)
- 💡 Suggesting features via [Discussions](https://github.com/Alielber1010/erp-agent-mcp/discussions)
- 🤝 Contributing code via [Pull Requests](https://github.com/Alielber1010/erp-agent-mcp/pulls)

## 🔗 Related Projects

- [FastMCP](https://github.com/jlowin/fastmcp) - The MCP framework powering this server
- [Model Context Protocol](https://github.com/modelcontextprotocol) - Official MCP specification

---

**Ready to transform your financial reporting?** 
[⚡ Get Started](https://github.com/Alielber1010/erp-agent-mcp#-quick-start) | [📖 Documentation](https://github.com/Alielber1010/erp-agent-mcp/wiki) | [💬 Discussions](https://github.com/Alielber1010/erp-agent-mcp/discussions)