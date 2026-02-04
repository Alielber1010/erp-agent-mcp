# Contributing to IFRS-Compliant ERP MCP Server

Thank you for your interest in contributing to this project! This guide will help you get started.

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.11+
- Git
- Basic understanding of IFRS accounting standards

### Setup Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Alielber1010/erp-agent-mcp.git
   cd erp-agent-mcp
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests:**
   ```bash
   python test_ifrs_simple.py
   ```

5. **Start the server:**
   ```bash
   python server.py
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Maintain IFRS compliance in all calculations

### Adding New IFRS Standards
1. Create new module in `ifrs_tools/`
2. Implement calculation functions
3. Add corresponding MCP tools in `server.py`
4. Include comprehensive tests
5. Update documentation

### Testing
- All new features must include tests
- Ensure IFRS calculations are mathematically correct
- Test with realistic financial data

## 📋 Areas for Contribution

### High Priority
- Multi-currency support (IAS 21)
- Consolidation accounting (IFRS 10)
- Business combinations (IFRS 3)
- Share-based payments (IFRS 2)

### Medium Priority
- Enhanced disclosure templates
- Additional export formats
- Performance optimizations
- Advanced analytics

### Documentation
- API documentation improvements
- More use case examples
- Video tutorials
- Translation to other languages

## 🔍 Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📞 Getting Help

- Open an issue for bugs or feature requests
- Join discussions in the repository
- Review existing issues and PRs

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.