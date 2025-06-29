import { useState } from 'react';
import { enrichFile } from '../../services/api.service';
import type { EnrichmentParams } from '../../types/file';
import './FileEnrichment.css';

/**
* Properties for the FileEnrichment component.
*
* @property {number} fileId - The ID of the file to be enriched.
* @property {string} fileName - The name of the file to be enriched.
* @property {string[]} columns - The columns available in the file for enrichment.
* @property {(enrichedFile: any) => void} onEnrich - Callback function to handle the enriched file.
* @property {() => void} onClose - Callback function to close the enrichment modal.
*/
interface Props {
    fileId: number;
    fileName: string;
    columns: string[];
    onEnrich: (enrichedFile: any) => void;
    onClose: () => void;
}

/**
* Component for enriching file data using an external API.
*
* This component allows users to specify an API endpoint, select a file key column,
* provide an API response key, and specify a name for the enriched file. It handles
* the submission of these parameters to enrich the file data and provides feedback
* on the enrichment process.
*/
const FileEnrichment = ({ fileId, fileName, columns, onEnrich, onClose }: Props) => {
    const [apiEndpoint, setApiEndpoint] = useState('');
    const [fileKey, setFileKey] = useState(columns[0]);
    const [apiKey, setApiKey] = useState('');
    const [enrichedFileName, setEnrichedFileName] = useState(() => {return fileName;});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Handles the form submission for enriching the file data.
    // Validates the input fields, constructs the enrichment parameters,
    // and calls the enrichFile service function. Displays any errors that occur.
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        if (!apiEndpoint || !fileKey || !apiKey || !enrichedFileName) {
            setError('All fields are required');
            setLoading(false);
            return;
        }

        if (!/^https?:\/\/.+/.test(apiEndpoint)) {
            setError('Invalid API endpoint URL');
            setLoading(false);
            return;
        }

        if (!enrichedFileName.endsWith('.csv')) {
            setError('Enriched file name must end with .csv');
            setLoading(false);
            return;
        }

        try {
            const params: EnrichmentParams = {
                api_endpoint: apiEndpoint,
                file_key: fileKey,
                api_key: apiKey,
                enriched_file_name: enrichedFileName,
            };

            const enrichedFile = await enrichFile(fileId, params);
            onEnrich(enrichedFile);
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to enrich file');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="enrich-modal">
                <div className="modal-header">
                    <h2>Enrich File Data</h2>
                    <button onClick={onClose} className="close-button">&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>API Endpoint:</label>
                        <input
                            type="url"
                            value={apiEndpoint}
                            onChange={(e) => setApiEndpoint(e.target.value)}
                            placeholder="https://api.example.com/data"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>File Key Column:</label>
                        <select
                            value={fileKey}
                            onChange={(e) => setFileKey(e.target.value)}
                            required
                        >
                            {columns.map(column => (
                                <option key={column} value={column}>
                                    {column}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>API Response Key:</label>
                        <input
                            type="text"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder="id"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Enriched File Name:</label>
                        <input
                            type="text"
                            value={enrichedFileName}
                            onChange={(e) => setEnrichedFileName(e.target.value)}
                            pattern="^[\w\-. ]+\.csv$"
                            title="File name must end with .csv"
                            required
                        />
                    </div>
                    {error && <div className="error">{error}</div>}
                    <div className="modal-footer">
                        <button type="button" onClick={onClose}>Cancel</button>
                        <button type="submit" disabled={loading}>
                            {loading ? 'Enriching...' : 'Enrich Data'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default FileEnrichment;
