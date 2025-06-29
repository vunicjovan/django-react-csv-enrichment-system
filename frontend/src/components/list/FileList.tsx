import { useState, useEffect } from 'react';
import { FiDownload, FiEye, FiTrash2, FiPlusCircle } from 'react-icons/fi';
import type { UploadedFile, FileStatus } from '../../types/file';
import { getFiles, getFileStatus, downloadFile, deleteFile, displayFile } from '../../services/api.service';
import Tooltip from '../utils/tooltip/Tooltip';
import ConfirmationModal from '../utils/modal/ConfirmationModal';
import FileDisplay from '../display/FileDisplay';
import FileEnrichment from '../enrich/FileEnrichment';
import './FileList.css';

/**
* Properties for the FileList component.
*
* @property {() => void} onRefresh - Callback to refresh the file list.
* @property {number} refreshTrigger - Trigger value to re-fetch files when changed.
*/
interface Props {
    onRefresh: () => void;
    refreshTrigger: number;
}

const FileList = ({ onRefresh, refreshTrigger }: Props) => {
    const [loading, setLoading] = useState<number | null>(null);
    const [files, setFiles] = useState<UploadedFile[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [displayFileId, setDisplayFileId] = useState<number | null>(null);
    const [enrichFileId, setEnrichFileId] = useState<number | null>(null);
    const [deleteFileId, setDeleteFileId] = useState<number | null>(null);
    const [fileStatuses, setFileStatuses] = useState<Record<number, FileStatus>>({});

    // This effect runs once on mount and whenever refreshTrigger changes
    // It fetches the list of files from the server and updates the state.
    // It also handles errors during the fetch operation.
    // Cleanup function ensures no state updates if the component is unmounted.
    useEffect(() => {
        let mounted = true;

        const fetchFiles = async () => {
            try {
                const fetchedFiles = await getFiles();
                if (mounted) {
                    setFiles(fetchedFiles);
                    setError(null);
                }
            } catch (err) {
                if (mounted) {
                    setError('Failed to fetch files');
                    console.error('Error fetching files:', err);
                }
            }
        };

        fetchFiles();

        return () => {
            mounted = false;
        };
    }, [refreshTrigger]);

    // This effect checks the status of files that are currently being processed.
    // It polls the server every 2 seconds to get the latest status.
    // If a file's status changes to 'Completed', it triggers a refresh.
    // Cleanup function clears the interval to prevent memory leaks.
    useEffect(() => {
        const processingFiles = files.filter(f => f.status === 'Processing');
        if (processingFiles.length === 0) return;

        const pollStatus = async () => {
            const newStatuses: Record<number, FileStatus> = {};
            for (const file of processingFiles) {
                try {
                    const status = await getFileStatus(file.id);
                    newStatuses[file.id] = status;

                    // If file is complete, trigger refresh
                    if (status.status === 'Completed') {
                        onRefresh();
                    }
                } catch (error) {
                    console.error(`Failed to fetch status for file ${file.id}:`, error);
                }
            }
            setFileStatuses(prev => ({ ...prev, ...newStatuses }));
        };

        const intervalId = setInterval(pollStatus, 2000);
        return () => clearInterval(intervalId);
    }, [files]);

    // This function renders the status of a file.
    // If the file is being processed, it shows a progress bar with the current percentage.
    // If the file is not being processed, it simply displays the status.
    const renderFileStatus = (file: UploadedFile) => {
        const status = fileStatuses[file.id];

        if (file.status === 'Processing' && status?.progress) {
            return (
                <div className="file-progress">
                    <div
                        className="progress-bar"
                        style={{ width: `${status.progress}%` }}
                    />
                    <span>{status.progress}%</span>
                </div>
            );
        }

        return <span className="file-upload-status">({file.status})</span>;
    };

    // Helper function to format file size in a human-readable format.
    // Example: 1024 bytes -> "1 KB", 1048576 bytes -> "1 MB".
    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    };

    // Helper function to format date strings into a more readable format.
    // Example: "2023-10-01T12:00:00Z" -> "Oct 1, 2023, 12:00 PM".
    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // This function handles the download of a file.
    // It sets the loading state to the file ID, fetches the file blob,
    // creates a download link, and triggers the download.
    const handleDownload = async (file: UploadedFile) => {
        try {
            setLoading(file.id);
            const blob = await downloadFile(file.id);

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.original_name;

            // Trigger download
            document.body.appendChild(a);
            a.click();

            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download failed:', error);
        } finally {
            setLoading(null);
        }
    };

    // This function handles the deletion of a file.
    // It sets the loading state to the file ID, calls the deleteFile service,
    // updates the file list by filtering out the deleted file, and triggers a refresh.
    const handleDelete = async (fileId: number) => {
        try {
            setLoading(fileId);
            await deleteFile(fileId);
            setFiles(files.filter(f => f.id !== fileId));
            onRefresh();
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to delete file');
            console.error('Delete failed:', error);
        } finally {
            setLoading(null);
            setDeleteFileId(null);
        }
    };

    if (error) {
        return <div className="file-list-error">{error}</div>;
    }

    if (!files || files.length === 0) {
        return <div className="file-list-empty">No files uploaded yet</div>;
    }

    return (
        <>
            <ul className="file-list fade-in">
                {files.map((file) => (
                    <li key={file.id} className="file-list-item">
                        <div className="file-info">
                            <span className="file-name">{file.original_name}</span>
                            <span className="file-size">{file.file_size_formatted}</span>
                            <span className="file-upload-date">
                                {new Date(file.uploaded_at).toLocaleString()}
                            </span>
                            <div className="file-status-group">
                                {file.is_enriched ? (
                                    <span className="file-enriched">Enriched</span>
                                ) : (
                                    <span className="file-original">Original</span>
                                )}
                                {renderFileStatus(file)}
                            </div>
                        </div>
                        <div className="file-actions">
                            <Tooltip content="Download File">
                                <button
                                    className="action-button"
                                    onClick={() => handleDownload(file)}
                                    disabled={loading === file.id}
                                >
                                    <FiDownload />
                                </button>
                            </Tooltip>
                            <Tooltip content="Display File">
                                <button
                                    className="action-button"
                                    onClick={() => setDisplayFileId(file.id)}
                                    disabled={loading === file.id}
                                >
                                    <FiEye />
                                </button>
                            </Tooltip>
                            <Tooltip content="Enrich File">
                                <button
                                    className="action-button"
                                    onClick={() => setEnrichFileId(file.id)}
                                    disabled={loading === file.id}
                                >
                                    <FiPlusCircle />
                                </button>
                            </Tooltip>
                            <Tooltip content="Delete File">
                                <button
                                    className="action-button delete"
                                    onClick={() => setDeleteFileId(file.id)}
                                    disabled={loading === file.id}
                                >
                                    <FiTrash2 />
                                </button>
                            </Tooltip>
                        </div>
                    </li>
                ))}
            </ul>
            <FileDisplay
                fileId={displayFileId!}
                fileName={files.find(f => f.id === displayFileId)?.original_name || ''}
                isOpen={displayFileId !== null}
                onClose={() => setDisplayFileId(null)}
            />
            {enrichFileId && (
                <FileEnrichment
                    fileId={enrichFileId}
                    fileName={files.find(f => f.id === enrichFileId)?.original_name || ''}
                    columns={files.find(f => f.id === enrichFileId)?.columns || []}
                    onEnrich={() => onRefresh()}
                    onClose={() => setEnrichFileId(null)}
                />
            )}
            <ConfirmationModal
                isOpen={deleteFileId !== null}
                title="Delete File"
                message="Are you sure you want to delete this file?"
                onConfirm={() => deleteFileId && handleDelete(deleteFileId)}
                onCancel={() => setDeleteFileId(null)}
            />
        </>
    );
};

export default FileList;
