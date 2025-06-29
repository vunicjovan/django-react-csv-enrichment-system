/**
* Contains the main application component that integrates file upload/enrichment and listing functionalities.
*/

import { useState } from 'react';
import './App.css';
import FileList from './components/list/FileList';
import FileUpload from './components/upload/FileUpload';
import HealthCheckPopup from './components/health/HealthCheckPopup';

/**
* Main application component that renders the file upload and file list components,
* along with a health check popup.
*/
function App() {
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);

    const handleUploadSuccess = (file: UploadedFile) => {
        setUploadedFile(file);
        setRefreshTrigger(prev => prev + 1);
    };

    return (
        <div className="container">
            <div className="content">
                <div className="main-content">
                    <div className="card">
                        <FileUpload onUploadSuccess={handleUploadSuccess} />
                        <FileList
                            onRefresh={() => setRefreshTrigger(prev => prev + 1)}
                            refreshTrigger={refreshTrigger}
                        />
                    </div>
                </div>
                <div className="health-check-container">
                    <HealthCheckPopup />
                </div>
            </div>
        </div>
    );
}

export default App;
