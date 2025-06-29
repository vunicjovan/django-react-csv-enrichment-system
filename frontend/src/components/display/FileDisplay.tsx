/**
* A component to display file previews in a modal.
* It fetches data from the server and handles pagination.
*/

import { useState, useEffect } from 'react';
import { displayFile } from '../../services/api.service';
import type { PreviewData } from '../../types/file';
import './FileDisplay.css';

/**
* Props for the FileDisplay component.
* @property {number} fileId - The ID of the file to display.
* @property {string} fileName - The name of the file to display.
* @property {() => void} onClose - Callback function to call when the modal is closed.
* @property {boolean} isOpen - Flag indicating whether the modal is currently open.
*/
interface Props {
    fileId: number;
    fileName: string;
    onClose: () => void;
    isOpen: boolean;
}

/**
* FileDisplay component to show file previews in a modal.
* It fetches the file data from the server and displays it in a paginated table format.
* It also handles loading states and errors.
*/
const FileDisplay = ({ fileId, fileName, onClose, isOpen }: Props) => {
    const [data, setData] = useState<PreviewData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);

    // Reset state when modal opens or fileId changes
    useEffect(() => {
        if (isOpen && fileId) {
            fetchPreviewData(1); // Always start with page 1 when opening
            setCurrentPage(1);   // Reset page when opening new file
        }
        // Cleanup only when modal closes
        if (!isOpen) {
            setData(null);
            setLoading(true);
            setError(null);
            setCurrentPage(1);
        }
    }, [fileId, isOpen]);

    // Separate effect for page changes
    useEffect(() => {
        if (isOpen && fileId && data) { // Only fetch if modal is open and we have initial data
            fetchPreviewData(currentPage);
        }
    }, [currentPage]); // Only depends on page changes (pagination mechanism)

    const fetchPreviewData = async (page: number) => {
        try {
            setLoading(true);
            const jsonData = await displayFile(fileId, { page });
            setData(jsonData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load preview');
        } finally {
            setLoading(false);
        }
    };

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h2>File Preview: {fileName}</h2>
                    <button onClick={onClose} className="close-button">&times;</button>
                </div>
                <div className="modal-body">
                    {loading && <div>Loading...</div>}
                    {error && <div className="error">{error}</div>}
                    {data && (
                        <>
                            <div className="table-container">
                                <div className="table-wrapper">
                                    <table>
                                        <thead>
                                            <tr>
                                                {data.columns.map((column, index) => (
                                                    <th key={index}>{column}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.rows.map((row, rowIndex) => (
                                                <tr key={rowIndex}>
                                                    {data.columns.map((column, colIndex) => (
                                                        <td
                                                            key={colIndex}
                                                            data-content={row[column] || ''}
                                                            title={row[column] || ''}
                                                            className="table-cell"
                                                        >
                                                            {row[column] || '\u00A0'}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </>
                    )}
                </div>
                {data && (
                    <div className="modal-footer">
                        <div>
                            Showing {data.rows.length} of {data.row_count} rows
                        </div>
                        <div className="pagination">
                            <button
                                className="page-button"
                                onClick={() => handlePageChange(1)}
                                disabled={currentPage === 1}
                            >
                                &laquo;
                            </button>
                            <button
                                className="page-button"
                                onClick={() => handlePageChange(currentPage - 1)}
                                disabled={currentPage === 1}
                            >
                                &lsaquo;
                            </button>
                            {[...Array(data.total_pages)].map((_, index) => {
                                const pageNum = index + 1;
                                if (
                                    pageNum === 1 ||
                                    pageNum === data.total_pages ||
                                    Math.abs(currentPage - pageNum) <= 2
                                ) {
                                    return (
                                        <button
                                            key={pageNum}
                                            className={`page-button ${pageNum === currentPage ? 'active' : ''}`}
                                            onClick={() => handlePageChange(pageNum)}
                                        >
                                            {pageNum}
                                        </button>
                                    );
                                } else if (Math.abs(currentPage - pageNum) === 3) {
                                    return <span key={pageNum} className="page-ellipsis">...</span>;
                                }
                                return null;
                            })}
                            <button
                                className="page-button"
                                onClick={() => handlePageChange(currentPage + 1)}
                                disabled={currentPage === data.total_pages}
                            >
                                &rsaquo;
                            </button>
                            <button
                                className="page-button"
                                onClick={() => handlePageChange(data.total_pages)}
                                disabled={currentPage === data.total_pages}
                            >
                                &raquo;
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileDisplay;
