import logging
import os

import pymysql
from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP("MySQL Server", dependencies=["pymysql"])

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mysql-mcp-server")


def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        # Add charset and collation to avoid utf8mb4_0900_ai_ci issues with older MySQL versions
        # These can be overridden via environment variables for specific MySQL versions
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        # Disable autocommit for better transaction control
        "autocommit": True,
        # Set SQL mode for better compatibility - can be overridden
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL"),
    }

    # Remove None values to let MySQL connector use defaults if not specified
    config = {k: v for k, v in config.items() if v is not None}

    if not all([config.get("user"), config.get("password"), config.get("database")]):
        logger.error(
            "Missing required database configuration. Please check environment variables:"
        )
        logger.error("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config


@mcp.resource("mysql://tables")
async def list_resources() -> list[str] | None:
    """List MySQL tables as resources."""
    config = get_db_config()
    try:
        logger.info(
            f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}"
        )
        with pymysql.connect(**config) as conn:
            logger.info(
                f"Successfully connected to MySQL server version: {conn.get_server_info()}"
            )
            with conn.cursor() as cursor:
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                return tables
    except Exception as e:
        logger.error(f"Failed to list resources: {e}")
        raise RuntimeError(f"Database error: {str(e)}")


@mcp.resource("mysql://{table}")
async def read_table_resource(table: str) -> str:
    """Read table contents."""
    config = get_db_config()
    logger.info(f"Reading resource for table: {table}")

    try:
        logger.info(
            f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}"
        )
        with pymysql.connect(**config) as conn:
            logger.info(
                f"Successfully connected to MySQL server version: {conn.get_server_info()}"
            )
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)

    except Exception as e:
        logger.error(f"Database error reading resource {table}: {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}")


@mcp.tool()
async def execute_sql(query: str) -> str:
    """Execute an SQL query on the MySQL server.

    Args:
        query: The SQL query to execute

    Returns:
        Query results as formatted text
    """
    config = get_db_config()
    logger.info(f"Executing SQL query: {query}")

    try:
        logger.info(
            f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}"
        )
        with pymysql.connect(**config) as conn:
            logger.info(
                f"Successfully connected to MySQL server version: {conn.get_server_info()}"
            )
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Return results for SELECT queries
                if query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    if not rows:
                        return "Query executed successfully. No rows returned."

                    # Format results as CSV
                    result_lines = [",".join(columns)]
                    for row in rows:
                        result_lines.append(
                            ",".join(
                                str(val) if val is not None else "NULL" for val in row
                            )
                        )

                    return "\n".join(result_lines)
                else:
                    # For INSERT, UPDATE, DELETE operations
                    affected_rows = cursor.rowcount
                    conn.commit()
                    return (
                        f"Query executed successfully. {affected_rows} rows affected."
                    )
    except Exception as e:
        logger.error(f"Database error executing query '{query}': {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}")


if __name__ == "__main__":
    # Initialize the MCP server with the database configuration
    mcp.run(transport="stdio")
