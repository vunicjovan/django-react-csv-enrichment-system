/**
* This file defines the interfaces for the health check data structure.
*/

/**
* Interface representing the health data structure returned by the health check API.
* It includes system information, database status, and Celery task information.
*
* @property {Object} system - Information about the system's OS, Python version, CPU count, memory, and disk usage.
*   @property {string} system.os - The operating system of the server.
*   @property {string} system.python_version - The version of Python running on the server.
*   @property {number} system.cpu_count - The number of CPU cores available on the server.
*   @property {Object} system.memory - Memory usage statistics.
*       @property {string} system.memory.total - Total memory available on the server.
*       @property {string} system.memory.available - Available memory on the server.
*       @property {string} system.memory.used_percent - Percentage of memory used on the server.
*   @property {Object} system.disk - Disk usage statistics.
*       @property {string} system.disk.total - Total disk space available on the server.
*       @property {string} system.disk.free - Free disk space available on the server.
*       @property {string} system.disk.used_percent - Percentage of disk space used on the server.
*
* @property {Object} database - Status of the database, including its status, tables, and engine type.
*   @property {Object} database.status - Status of the database connection.
*   @property {string[]} database.tables - List of tables in the database.
*   @property {string} database.engine - The database engine being used (e.g., PostgreSQL, SQLite).
*
* @property {Object} celery - Information about the Celery worker.
*   @property {string} celery.status - Status of the Celery worker (e.g., running, idle).
*   @property {string[]} celery.registered_tasks - List of tasks registered with the Celery worker.
*/
export interface HealthData {
  system: {
    os: string;
    python_version: string;
    cpu_count: number;
    memory: {
      total: string;
      available: string;
      used_percent: string;
    };
    disk: {
      total: string;
      free: string;
      used_percent: string;
    };
  };
  database: {
    status: string;
    tables: string[];
    engine: string;
  };
  celery: {
    status: string;
    registered_tasks: string[];
  };
}
