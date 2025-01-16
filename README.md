<div align="center">
  <h1>Second Brain Semantic AI Engine: Powered by LLMs & RAG </h1>
  <p class="tagline">Open-source bootcamp by <a href="https://decodingml.substack.com">Decoding ML</a> in collaboration with <a href="...">...</a>.</p>
</div>

---

# ZenML RAG Pipeline: Foundational Stack

This repository offers a **foundational stack** for building and integrating into ZenML Retrieval-Augmented Generation (RAG) pipelines. By leveraging **ZenML** for pipeline orchestration and **Local MongoDB Atlas** for document storage, this stack is designed to run seamlessly in both local and Dockerized environments. 

While advanced ZenML configurations (e.g., custom stacks or orchestrators) are purposefully omitted for now, the stack provides a robust and flexible base for future enterprise-level enhancements.

---

## Features and Capabilities

### Core Features
1. **Pipeline Orchestration with ZenML**:
   - Modular pipeline design for document ingestion and retrieval.
   - Easily extendable for advanced RAG workflows.

2. **Local MongoDB Atlas Integration**:
   - **Document Ingestion**: Insert sample movie metadata from JSON files into MongoDB.
   - **Genre-Based Retrieval**: Query MongoDB for documents by genre with case-insensitive filtering.

3. **Sample Dataset**:
   - Uses data from **`sample_mflix`**, containing:
     - Movie metadata.
     - User-generated comments.
     - Movie theaters and related metadata.

4. **Flexible Runtime Environments**:
   - Supports **local execution** with Python virtual environments (`.venv`).
   - Fully **Dockerized deployment** for consistent, reproducible builds.

5. **Enterprise-Grade Logging**:
   - Structured logging with verbosity toggles (via `ENABLE_STRUCTURED_LOGGING` in `.env`).
   - Detailed runtime logs for pipeline steps and MongoDB operations.

---

## Prerequisites

Before running the stack, ensure the following are installed:

- **`Docker`**
- **`Docker Compose`**
- **`Python` 3.12+**
- **`uv`**
- **`mongosh`**

---

## Installation and Setup

### Local Execution (Windows, MacOS, Linux)

1. **Install Dependencies**:
   Use `uv` to set up the environment and sync dependencies:
   ```bash
   uv clean
   uv sync
   ```

2. **Run the Stack**:
   Execute the pipeline locally:
   ```bash
   python main.py
   ```

---

### **Dockerized Execution (Windows, MacOS, Linux)**

For Docker-based execution, this stack uses **Docker Compose** for container orchestration. The entry point of the Dockerfile is set to:
```dockerfile
# Default command to allow debugging
CMD ["tail", "-f", "/dev/null"]
```
This allows you to debug and modify the containers as necessary during development.

#### Basic Commands
1. **Build Docker Containers**:
   Builds the Docker images for the stack:
   ```bash
   docker-compose build
   ```

2. **Start the Containers**:
   Starts the stack, including the MongoDB and ZenML-related services:
   ```bash
   docker-compose up
   ```

3. **Stop the Stack**:
   Stops and removes the running containers:
   ```bash
   docker-compose down
   ```

---

#### **Optional Commands**

These commands are helpful for specific scenarios:

1. **Remove Volumes**:
   Use this command if you need to clear persistent data stored in Docker volumes, such as the MongoDB database:
   ```bash
   docker-compose down --volumes
   ```

2. **Rebuild Without Cache**:
   Use this command if you want to rebuild the images from scratch without using the Docker cache, which is useful when there are changes to the `Dockerfile` or dependencies:
   ```bash
   docker-compose build --no-cache
   ```

---

### Example Workflow

For most scenarios, the basic commands will suffice. However, if you encounter issues or need a clean slate (e.g., resetting the database or dependencies), the optional commands can be added to your workflow. For example:
```bash
docker-compose down --volumes  # Clear persistent data
docker-compose build --no-cache  # Rebuild images without cache
docker-compose up  # Start the stack
```

---

## Troubleshooting

### Using `.venv` with Docker

If you prefer using the local `.venv` while the stack runs in Docker, update your local hosts file to resolve `127.0.0.1` to the MongoDB container:

1. Open your hosts file:
   - **Linux/MacOS**: `/etc/hosts`
   - **Windows**: `C:\Windows\System32\drivers\etc\hosts`

2. Add the following entry:
   ```plaintext
   127.0.0.1 mongodb-atlas-local
   ```

---

## Directory Structure

```plaintext
zenml-rag-pipeline/
├── .venv/                          # Local Python environment (local runs only).
│
├── configs/
│   ├── config.py                   # Centralized settings management.
│   └── __init__.py
│
├── data/
│   └── sample_data_set.json        # JSON dataset for ingestion.
│
├── logs/
│   └── mongodb_atlas_pipeline.log  # Pipeline logs (local only).
│
├── pipelines/
│   ├── mongodb_atlas_pipeline.py   # ZenML pipeline definitions.
│   └── __init__.py
│
├── steps/
│   ├── infrastructure/
│   │   ├── mongodb_data_processing.py  # MongoDB ingestion and query steps.
│   │   └── __init__.py
│   └── __init__.py
│
├── .dockerignore                   # Files to exclude during Docker builds.
├── .env                            # Local environment variables.
├── .env.example                    # Template for .env.
├── .gitignore                      # Git ignored files.
├── .python-version                 # Python version for consistency.
├── docker-compose.yml              # Multi-container setup.
├── Dockerfile                      # Docker image definition.
├── LICENSE                         # Project license.
├── main.py                         # Entry point for the stack.
├── pyproject.toml                  # Python project dependencies.
├── README.md                       # This documentation.
└── uv.lock                         # Lock file for dependencies (local only).
```

---

## Stack Features: MongoDB Class Capabilities

The `MongoDBService` class powers MongoDB integration with the following functionalities:

1. **Ingestion**:
   - Clears existing data and inserts new documents from JSON files.
   - Avoids duplicates through proper collection handling.

2. **Querying**:
   - Retrieves documents by genre using case-insensitive regex queries.
   - Configurable fetch limits to manage query sizes effectively.

3. **Validation**:
   - Counts total documents in the collection.
   - Verifies genre-specific document counts for accurate operations.

---

## Pipeline Features: Modular Design

### Document Storage
- **Local MongoDB Atlas** stores sample movie data from the **`sample_mflix` database**, including movies, users, comments, and genres.

### Pipeline Orchestration
- Leverages **ZenML** for defining and executing modular pipelines:
  - **Ingestion**: Reads data from `sample_data_set.json` and ingests it into MongoDB.
  - **Querying**: Retrieves documents by specific genres with robust logging.

### Dual Runtime Environments
- Local development with `.venv`.
- Docker-based runtime with `docker-compose`.

---

## Example `.env` File

```ini
# MongoDB Offline Configuration
MONGODB_OFFLINE_URI=mongodb://mongodb-atlas-local:27017
MONGODB_OFFLINE_DATABASE=rag_pipeline
MONGODB_OFFLINE_COLLECTION=offline_documents

# Local Data Files
LOCAL_JSON_FILE_PATH="data/sample_data_set.json"

# Data Fetching Limits
MAX_FETCH_LIMIT=50
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For issues or inquiries, contact [jlmoses@outlook.com](mailto:jlmoses@outlook.com).

---