import { useState, useRef } from 'react';
import { uploadFile } from '../../services/api.service';
import { MIN_FILE_SIZE, MAX_FILE_SIZE } from '../../constants/api.constants';
import './FileUpload.css';

/**
* Properties for the FileUpload component.
* @property {Function} onUploadSuccess - Callback function to be called when a file is successfully uploaded.
*/
interface Props {
    onUploadSuccess: () => void;
}

/**
* FileUpload component allows users to upload CSV files via drag-and-drop or file selection.
* It validates the file type and size, and provides feedback during the upload process.
*/
const FileUpload = ({ onUploadSuccess }: Props) => {
  const [dragActive, setDragActive] = useState(false);  // State to track if a file is being dragged over the upload area
  const [error, setError] = useState<string | null>(null); // State to hold any error messages
  const [uploading, setUploading] = useState(false); // State to track if a file is currently being uploaded
  const inputRef = useRef<HTMLInputElement>(null); // Reference to the file input element

  const validateFile = (file: File): boolean => {
        setError(null);

        if (!file.name.endsWith('.csv')) {
            setError('Only CSV files are allowed');
            return false;
        }

        if (file.size <= MIN_FILE_SIZE) {
            setError('File size is below the minimum limit of 0 bytes.');
            return false;
        }

        if (file.size > MAX_FILE_SIZE) {
            setError('File size must be less than 100MB');
            return false;
        }

        return true;
    };

    const handleFile = async (file: File) => {
        if (validateFile(file)) {
            setUploading(true);
            try {
                const uploadedFile = await uploadFile(file);
                onUploadSuccess(uploadedFile);
                if (inputRef.current) {
                    inputRef.current.value = '';
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to upload file');
            } finally {
                setUploading(false);
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
    };

    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        if (!uploading && inputRef.current) {
            inputRef.current.click();
        }
    };

    return (
        <div className="upload-container">
            <div
                className={`upload-area ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={handleClick}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleChange}
                    onClick={(e) => e.stopPropagation()}
                    style={{ display: 'none' }}
                    disabled={uploading}
                />
                <div className="upload-content">
                    <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M7 10v-3a5 5 0 0 1 10 0v3" />
                        <path d="M12 14v7" />
                        <path d="M9 17l3-3 3 3" />
                    </svg>
                    <p>{uploading ? 'Uploading...' : 'Drag and drop a CSV file here, or click to select'}</p>
                    <p className="upload-hint">Maximum file size: 100MB</p>
                </div>
            </div>
            {error && <div className="upload-error">{error}</div>}
        </div>
    );
};

export default FileUpload;
