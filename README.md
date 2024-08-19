# FastAPI Application

This is a FastAPI application that provides endpoints for processing website content and running a custom engine. It integrates with `Engine` components to process URLs and handle results.

## Features

- **Run Engine**: Executes a custom engine and returns processed content.

## Prerequisites

- Python 3.7 or higher
- FastAPI
- Uvicorn
- Pydantic

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Piyush-Use-Personal/media-source-integration.git
    cd media-source-integration
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, use Uvicorn:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```