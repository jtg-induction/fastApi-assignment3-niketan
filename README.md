# Assignment 2: Food Delivery Platform API (FastAPI Engine)

## Overview

Your goal now is to build an asynchronous, high-performance RESTful API using FastAPI (Python) to drive the frontend, manage state, enforce strict schema validation, handle database operations, and enforce role-based authorization.

## Tech Stack

- **Language & Framework:** Python 3.12+, FastAPI.
- **Environment & Dependency Manager:** `uv`
- **Data Validation:** Pydantic v2 (Strict typing, custom field validators).
- **Database & ORM:** PostgreSQL using SQLAlchemy v2 (Async) or SQLModel. Database migrations handled via Alembic.
- **Authentication:** OAuth2 with Password Flow & JWT (`python-jose`, `passlib`).
- **Architecture:** Clean modular architecture (`routers/`, `schemas/`, `models/`, `services/`, `core/config.py`).
- **Linting & Formatting:** Ruff.

## Getting Started

### Installing

To set up the project on your local environment, follow these steps:

1. **Clone the Repository**

   First, clone the repository to your local machine and navigate into the project directory.

2. **Set Up Environment and Install Dependencies (`uv`)**

   `uv` will automatically read your project configuration, spin up a local virtual environment (`.venv`), and compile your project packages using your system's default Python installation:
   ```bash
   uv sync
   ```

3. **Configure Environment Variables**

   Create a `.env` file at the root level of the project to manage your application runtime variables (check `.env.template` for reference).
   ```env
   PORT=8000
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   JWT_SECRET_KEY=your_super_secret_key
   ```

4. **Run Database Migrations**

   Apply your structural database changes securely using your isolated project stack context:
   ```bash
   uv run alembic upgrade head
   ```

5. **Run the Development Server**

   Start the FastAPI application locally inside your isolated workspace context:
   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```
   The interactive API documentation will be available at http://localhost:8000/docs.

6. **Format the Code**

   Automatically format layout rules and clean up spacing across all files using Ruff:
   ```bash
   uv run ruff format .
   ```

7. **Lint the Code**

   Check for code bugs, unused imports, standard design flaws, or security vulnerabilities:
   ```bash
   uv run ruff check .
   ```

8. **To Fix Lint Errors**

   Automatically resolve all safe and fixable linting issues found throughout your package:
   ```bash
   uv run ruff check --fix .
   ```

9. **Set Up Pre-Commit Hooks**

   Ensure your code standard rules are verified immediately prior to saving code checkpoints inside your Git stream:
   ```bash
   uv run pre-commit install
   ```
