# MySQL MCP Server

A Model Context Protocol (MCP) server that provides MySQL database integration for AI assistants and other MCP clients.

## Features

- **Database Resource Management**: List and read MySQL tables as MCP resources
- **SQL Query Execution**: Execute arbitrary SQL queries through MCP tools
- **Environment-based Configuration**: Flexible database connection setup
- **UTF-8 Support**: Full Unicode support with proper charset handling
- **Error Handling**: Comprehensive error logging and exception management

## Installation

### Prerequisites

- Python 3.12 or higher
- MySQL server (5.7+ or 8.0+)
- Access to a MySQL database

### Setup

1. Clone the repository:
```bash
git clone https://github.com/slg1119/mysql-mcp.git
cd mysql-mcp
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

Or with pip:
```bash
pip install -e .
```

## Configuration

Configure your MySQL connection using environment variables:

```bash
export MYSQL_HOST=localhost          # Default: localhost
export MYSQL_PORT=3306              # Default: 3306
export MYSQL_USER=your_username      # Required
export MYSQL_PASSWORD=your_password  # Required
export MYSQL_DATABASE=your_database  # Required
export MYSQL_CHARSET=utf8mb4        # Default: utf8mb4
export MYSQL_COLLATION=utf8mb4_unicode_ci  # Default: utf8mb4_unicode_ci
export MYSQL_SQL_MODE=TRADITIONAL    # Default: TRADITIONAL
```

### Required Environment Variables

- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password  
- `MYSQL_DATABASE`: Target database name

### Optional Environment Variables

- `MYSQL_HOST`: MySQL server host (default: localhost)
- `MYSQL_PORT`: MySQL server port (default: 3306)
- `MYSQL_CHARSET`: Character set (default: utf8mb4)
- `MYSQL_COLLATION`: Collation (default: utf8mb4_unicode_ci)
- `MYSQL_SQL_MODE`: SQL mode (default: TRADITIONAL)

## Usage

### Running the Server

Start the MCP server:

```bash
python server.py
```

The server will run using stdio transport and wait for MCP client connections.

### Available Resources

- `mysql://tables` - Lists all available tables in the database
- `mysql://{table_name}` - Returns the first 100 rows of the specified table

### Available Tools

- `execute_sql(query: str)` - Executes SQL queries and returns formatted results

## MCP Client Integration

To use this server with an MCP client, configure it in your client's settings:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "python",
      "args": ["/path/to/mysql-mcp/server.py"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "your_username",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_database"
      }
    }
  }
}
```

## Examples

### Reading Table Data

```python
# List all tables
tables = await client.list_resources("mysql://tables")

# Read specific table
table_data = await client.read_resource("mysql://users")
```

### Executing SQL Queries

```python
# Select query
result = await client.call_tool("execute_sql", {
    "query": "SELECT * FROM users WHERE active = 1 LIMIT 10"
})

# Insert query
result = await client.call_tool("execute_sql", {
    "query": "INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')"
})
```

## Security Considerations

- Store database credentials securely using environment variables
- Use database users with minimal required privileges
- Validate and sanitize SQL inputs in production environments
- Consider using connection pooling for high-traffic scenarios

## Dependencies

- **mcp[cli]**: Model Context Protocol implementation
- **pymysql**: Pure Python MySQL client library

## Development

### Project Structure

```
mysql-mcp/
├── server.py          # Main MCP server implementation
├── pyproject.toml     # Project configuration and dependencies
├── README.md          # This file
├── .python-version    # Python version specification
├── .gitignore         # Git ignore rules
└── uv.lock           # Dependency lock file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

**Connection Failed**: Verify your MySQL server is running and credentials are correct.

**Charset Issues**: Ensure your MySQL server supports utf8mb4 charset. For older MySQL versions, you may need to adjust `MYSQL_CHARSET` and `MYSQL_COLLATION`.

**Permission Denied**: Check that your MySQL user has the necessary privileges for the target database.

### Logging

The server provides detailed logging. Check the console output for connection status and error messages.

## License

This project is available under the MIT License. See the LICENSE file for more details.

## Support

For issues and questions, please open an issue on the GitHub repository.