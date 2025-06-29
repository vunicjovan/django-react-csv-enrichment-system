# Django/React CSV Enrichment System

This project is a Django- and React-based web application designed to enrich CSV files with data from external APIs. 

It allows users to upload CSV files, fetch additional data from specified APIs, and download the enriched CSV files.


## Features

- Upload CSV files
  - Supports files with `.csv` extension
  - Validates file size (must be greater than 0 bytes, maximum 100 MB)
  - Validates file name (a file with the same name cannot be uploaded again)
- Display CSV file contents in a table (pagination supported)
- Download any of the uploaded CSV files
- Fetch data from external APIs to enrich the contents of the CSV files
  - Supports file names with `.csv` extension
  - Validates file name (a file with the same name cannot be uploaded again)
  - Validates API response structure (a non-empty list of dictionaries)
  - Validates existence of file keys and API keys in the CSV file and API response
- Delete uploaded CSV files
- Show system information

---

## Technology Stack

- **Back-End**:
  - Python 3.11
  - [Django](https://www.djangoproject.com/) / [Django REST Framework](https://www.django-rest-framework.org/) (for API development)
  - [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) (for background tasks)
  - [Redis](https://redis.io/) (as a message broker for Celery)
  - [Requests](https://requests.readthedocs.io/en/latest/) (for making HTTP requests to external APIs)
  - [Psutil](https://psutil.readthedocs.io/en/latest/) (for system information)

- **Front-End**: [React](https://react.dev/) (with TypeScript)

- **Database**: [PostgreSQL](https://www.postgresql.org/) (for storing metadata about uploaded files and enriched data)

- **File Storage**: Local file system (can be configured to use cloud storage, e.g. [AWS S3](https://aws.amazon.com/s3/))

- **External APIs**: [JSONPlaceholder](https://jsonplaceholder.typicode.com/) APIs for demonstration purposes

- **Testing**: [unittest](https://docs.python.org/3/library/unittest.html) (for back-end unit tests)

- **Deployment / Environment Management**: [Docker](https://www.docker.com/) for containerization, [Docker Compose](https://docs.docker.com/compose/) for multi-container applications

---

## Setup & Run Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vunicjovan/django-react-csv-enrichment-system.git
    ```
2. **Navigate to the project directory**:
   ```bash
   cd django-react-csv-enrichment-system
   ```
3. **Run Docker Compose**:
   ```bash
   docker-compose up --build
   ```

---

## Usage Instructions

1. **Access the Application**:
   - Open your web browser and go to `http://localhost:5173` to access the React front-end.
   - The Django back-end API will be available at `http://localhost:8000/api/`.

   ![Home_Page_Screen](/screens/home-page.png)

2. **Upload a CSV File**:
   - Use the upload feature in the React application to select and upload a CSV file.

   ![Uploaded_Files_Screen](/screens/uploaded-files.png)

3. **View CSV Contents**:
   - After uploading, the contents of the CSV file will be displayed in a table format.

   ![File_Preview_Screen](/screens/file-preview.png)

4. **Enrich CSV Data**:
   - Use the provided API endpoints to fetch additional data from external APIs and enrich the CSV file contents.

   ![File_Enrichment_Screen](/screens/file-enrichment.png)

5. **Download Enriched CSV**:
   - After enrichment, you can download the enriched CSV file directly from the application.

6. **Delete CSV Files**:
   - You can delete any uploaded CSV files through the application interface.

---

## Running Unit Tests for Back-End

To run the unit tests for the back-end, follow these steps:
1. **Navigate to the back-end directory**:
   ```bash
   cd backend
   ```
2. **Run the tests**:
   ```bash
    python manage.py test -v 2
    ```

---

## Test Data

The project includes sample CSV files located at `csv-test-data`.

This directory contains two CSV files:
- `people-10000.csv`: Contains sample data of 10,000 people.
- `users_posts_audience.csv`: Contains users' posts views data.

These files can be used for testing of the upload and enrichment functionalities.


## Demonstration Purpose APIs / Use Cases

| CSV File                   | External API                                             | File Key          | API Key  |
|----------------------------|----------------------------------------------------------|-------------------|----------|
| `people-10000.csv`         | [Posts API](https://jsonplaceholder.typicode.com/posts/) | `id`              | `userId` |
| `users_posts_audience.csv` | [Users API](https://jsonplaceholder.typicode.com/users/) | `posting_user_id` | `id`     |
| `people-10000.csv`         | [Users API](https://jsonplaceholder.typicode.com/users/) | `id`              | `id`     |
| `users_posts_audience.csv` | [Posts API](https://jsonplaceholder.typicode.com/posts/) | `post_id`         | `id`     |

---

## Potential Improvements

- [ ] Use [Pandas](https://pandas.pydata.org/) or [Polars](https://pola.rs/) for CSV-based operations (upload, enrichment)
- [ ] Consider [asyncio](https://docs.python.org/3/library/asyncio.html)/[aiohttp](https://docs.aiohttp.org/en/stable/) for asynchronous API calls
- [ ] Implement user authentication and authorization
- [ ] Use state management pattern in front-end (e.g. [Redux](https://redux.js.org/))
- [ ] Improve enrichment logic in a way that it accepts mappings for common columns under different names to avoid duplicated columns
- [ ] Consider storing file contents only per explicit demand
- [ ] Design rules to handle cases where user provides mismatching key mappings (e.g. `file_key=post_id`, `api_key=title`)
- [ ] Use [Redis Commander](https://github.com/joeferner/redis-commander) to monitor cached data and Redis performance in general
- [ ] Use a service like [Vault](https://developer.hashicorp.com/vault) or at least environment (`.env`) files for sensitive information (DB info, Redis info, Celery info, Django secrets, etc.)
- [ ] Write front-end tests with tools like [Jest](https://jestjs.io/) or [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [ ] Write API tests for the back-end with tools like [PyTest](https://docs.pytest.org/en/stable/) or DRF's [APITestCase](https://www.django-rest-framework.org/api-guide/testing/)
- [ ] [MinIO](https://min.io/) could be considered as file storage solution for development purposes
- [ ] Spread the back-end logic across multiple Django apps for better organization
- [ ] Consider API versioning for better maintainability (e.g. v1, v2, v3, and so on)
- [ ] Use custom exception instead of plain assertions in the back-end
- [ ] Use [UV](https://astral.sh/blog/uv) for dependency management in the back-end
- [ ] Provide API documentation with tools like [Swagger](https://swagger.io/) or [Redoc](https://redocly.com/)
