/**
* API Service for handling file operations and health checks.
* This service provides methods to upload, download, preview, enrich, and delete files,
* as well as to check the health status of the backend service.
*/

import type { HealthData } from '../types/health';
import type { UploadedFile, FileStatus, PreviewData, PreviewOptions, EnrichmentParams } from '../types/file';
import { API_URL, DEFAULT_PAGE, DEFAULT_PAGE_SIZE } from '../constants/api.constants';

/**
* Retrieves the health status of the back-end service.
*
* @returns {Promise<HealthData>} A promise that resolves to the health data.
* @throws {Error} If the health check fails or API is unreachable.
*/
export const getHealthStatus = async (): Promise<HealthData> => {
  const response = await fetch(`${API_URL.replace('/api', '')}/health`);
  if (!response.ok) {
    throw new Error('Failed to fetch health status');
  }
  return response.json();
};

/**
* Uploads a file to the server.
*
* @param {File} file - The file to upload.
* @returns {Promise<UploadedFile>} A promise that resolves to the uploaded file data.
* @throws {Error} If the upload fails or API is unreachable.
*/
export const uploadFile = async (file: File): Promise<UploadedFile> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/files/`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
    }

    return response.json();
};

/**
* Retrieves the status of a specific file.
*
* @param {number} fileId - The ID of the file to check.
* @returns {Promise<FileStatus>} A promise that resolves to the file status.
* @throws {Error} If the file status check fails or API is unreachable.
*/
export const getFileStatus = async (fileId: number): Promise<FileStatus> => {
    const response = await fetch(`${API_URL}/files/${fileId}/status/`);
    if (!response.ok) {
        throw new Error('Failed to fetch file status');
    }
    return response.json();
};

/**
* Retrieves a list of uploaded files.
*
* @returns {Promise<UploadedFile[]>} A promise that resolves to an array of uploaded files.
* @throws {Error} If the file list retrieval fails or API is unreachable.
*/
export const getFiles = async (): Promise<UploadedFile[]> => {
    const response = await fetch(`${API_URL}/files/`);
    if (!response.ok) {
        throw new Error('Failed to fetch files');
    }
    return response.json();
};

/**
* Downloads a file by its ID.
*
* @param {number} fileId - The ID of the file to download.
* @returns {Promise<Blob>} A promise that resolves to the file blob.
* @throws {Error} If the download fails or API is unreachable.
*/
export const downloadFile = async (fileId: number): Promise<Blob> => {
    const response = await fetch(`${API_URL}/files/${fileId}/download/`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Download failed');
    }
    return response.blob();
};

/**
* Displays a preview of a file.
*
* @param {number} fileId - The ID of the file to preview.
* @param {PreviewOptions} options - Optional parameters for pagination.
* @returns {Promise<PreviewData>} A promise that resolves to the preview data.
* @throws {Error} If the preview fails or API is unreachable.
*/
export const displayFile = async (fileId: number, options: PreviewOptions = {}): Promise<PreviewData> => {
    const { page = 1, pageSize = 100 } = options;
    const queryParams = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
    });

    const response = await fetch(`${API_URL}/files/${fileId}/preview/?${queryParams}`);
    if (!response.ok) {
        throw new Error('Failed to load file preview');
    }
    return response.json();
};

/**
* Enriches a file with additional data.
*
* @param {number} fileId - The ID of the file to enrich.
* @param {EnrichmentParams} params - Parameters for the enrichment process.
* @returns {Promise<UploadedFile>} A promise that resolves to the enriched file data.
* @throws {Error} If the enrichment fails or API is unreachable.
*/
export const enrichFile = async (fileId: number, params: EnrichmentParams): Promise<UploadedFile> => {
    const response = await fetch(
        `${API_URL}/files/${fileId}/enrich/`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params),
        }
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to enrich file');
    }

    return response.json();
};

/**
* Deletes a file by its ID.
*
* @param {number} fileId - The ID of the file to delete.
* @returns {Promise<void>} A promise that resolves when the file is deleted.
* @throws {Error} If the delete operation fails or API is unreachable.
*/
export const deleteFile = async (fileId: number): Promise<void> => {
    const response = await fetch(`${API_URL}/files/${fileId}/`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Delete failed' }));
        throw new Error(error.error || 'Failed to delete file');
    }
};
