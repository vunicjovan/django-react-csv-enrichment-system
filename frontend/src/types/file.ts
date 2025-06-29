/**
* This file defines TypeScript interfaces for file management in a web application.
* It includes interfaces for uploaded files, file status, preview data, and enrichment parameters.
*/

/**
* Interface representing an uploaded file with its metadata.
*
* @property {number} id - Unique identifier for the uploaded file.
* @property {string} original_name - The original name of the file as uploaded by the user.
* @property {string} file_size_formatted - The size of the file formatted as a string (e.g., "1.2 MB").
* @property {string} uploaded_at - Timestamp of when the file was uploaded.
* @property {boolean} is_enriched - Indicates whether the file has been enriched with additional data.
* @property {string} file - The path or URL to access the uploaded file.
* @property {string[]} columns - List of column names in the file.
*/
export interface UploadedFile {
    id: number;
    original_name: string;
    file_size_formatted: string;
    uploaded_at: string;
    is_enriched: boolean;
    file: string;
    columns: string[];
}

/**
* Interface representing the status of a file during processing.
*
* @property {string} status - Current status of the file (e.g., "processing", "completed", "failed").
* @property {number} progress - Progress percentage of the file processing (0-100).
* @property {number} updated_at - Timestamp of the last update to the file status.
*/
export interface FileStatus {
    status: string;
    progress: number;
    updated_at: number;
}

/**
* Interface representing the preview data of a file.
*
* @property {string[]} columns - List of column names in the file.
* @property {Record<string, any>[]} rows - Array of objects representing the rows in the file.
* @property {number} row_count - Total number of rows in the file.
* @property {number | null} current_page - Current page number for pagination, or null if not paginated.
* @property {number} total_pages - Total number of pages available for the file.
* @property {boolean} can_load_all - Indicates if all rows can be loaded at once.
*/
export interface PreviewData {
    columns: string[];
    rows: Record<string, any>[];
    row_count: number;
    current_page: number | null;
    total_pages: number;
    can_load_all: boolean;
}

/**
* Interface representing options for previewing of a file.
*
* @property {number} [page] - The page number to preview, if pagination is used.
* @property {number} [pageSize] - The number of rows per page for pagination.
*/
export interface PreviewOptions {
    page?: number;
    pageSize?: number;
}

/**
* Interface representing parameters for enriching a file with additional data.
* This is used when sending a request to an external API for enrichment.
*
* @property {string} api_endpoint - The endpoint URL of the external API to call for enrichment.
* @property {string} file_key - The key mapping for the file content.
* @property {string} api_key - The key mapping for the response of the external API.
* @property {string} enriched_file_name - The desired name for the enriched file, must end with ".csv".
*/
export interface EnrichmentParams {
    api_endpoint: string;
    file_key: string;
    api_key: string;
    enriched_file_name: string;
}
