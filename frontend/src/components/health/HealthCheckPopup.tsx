import { useState, useEffect } from 'react';
import { FiActivity, FiCpu, FiHardDrive, FiDatabase, FiCoffee, FiRefreshCw } from 'react-icons/fi';
import { getHealthStatus } from '../../services/api.service';
import type { HealthData } from '../../types/health';
import './HealthCheckPopup.css';

/**
* HealthCheckPopup component displays the system health status including system info,
* resource usage, database status, and Celery task status.
* It fetches health data from the backend and updates every 30 seconds.
*/
const HealthCheckPopup = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getHealthStatus();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="health-panel">
      <div className="health-panel-header">
        <h3>System Health</h3>
        <button
          className="refresh-button"
          onClick={fetchHealthData}
          disabled={loading}
          title="Refresh health status"
        >
          <FiRefreshCw className={loading ? 'spinning' : ''} />
        </button>
      </div>
      {error && <div className="health-error">{error}</div>}
      {health && (
        <div className="health-section">
          <div className="health-item">
            <FiCpu className="health-icon" />
            <div className="health-info">
              <strong>System</strong>
              <span>OS: {health.system.os}</span>
              <span>Python: {health.system.python_version}</span>
              <span>CPU Cores: {health.system.cpu_count}</span>
            </div>
          </div>
          <div className="health-item">
            <FiHardDrive className="health-icon" />
            <div className="health-info">
              <strong>Resources</strong>
              <span>Available Memory: {health.system.memory.available} / {health.system.memory.total}</span>
              <span>Used Memory: {health.system.memory.used_percent}</span>
              <span>Available Space: {health.system.disk.free} / {health.system.disk.total}</span>
              <span>Used Space: {health.system.disk.used_percent}</span>
            </div>
          </div>
          <div className="health-item">
            <FiDatabase className="health-icon" />
            <div className="health-info">
              <strong>Database</strong>
              <span>Status: {health.database.status}</span>
              <span>Engine: {health.database.engine}</span>
              <span>Tables: {health.database.tables.length}</span>
            </div>
          </div>
          <div className="health-item">
            <FiCoffee className="health-icon" />
            <div className="health-info">
              <strong>Celery</strong>
              <span>Status: {health.celery.status}</span>
              <span>Tasks: {health.celery.registered_tasks.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthCheckPopup;
