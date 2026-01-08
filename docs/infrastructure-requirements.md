# Infrastructure Requirements for Luminote

This document details all infrastructure and setup work required before feature
implementation can begin, following Step 1.2 of the
[github-issue-creation-methodology.md](github-issue-creation-methodology.md).

## Table of Contents

- [Overview](#overview)
- [Backend Infrastructure](#backend-infrastructure)
- [Frontend Infrastructure](#frontend-infrastructure)
- [DevOps Infrastructure](#devops-infrastructure)
- [Development Tools](#development-tools)
- [Testing Infrastructure](#testing-infrastructure)
- [Documentation Infrastructure](#documentation-infrastructure)
- [Prioritized Implementation Order](#prioritized-implementation-order)

______________________________________________________________________

## Overview

### Purpose

This document ensures that all foundational infrastructure is in place before
feature development begins. Each infrastructure component is designed to support
the development workflow and enable GitHub Copilot to work effectively.

### Success Criteria

- [ ] All infrastructure issues can be completed independently
- [ ] Each infrastructure component has clear acceptance criteria
- [ ] Setup can be completed by a new developer in \< 2 hours
- [ ] All tooling is documented with examples
- [ ] CI/CD pipeline validates all components

______________________________________________________________________

## Backend Infrastructure

### 1. Python/FastAPI Project Structure

**Priority:** P0 (Must have first)

**Purpose:** Establish the foundational backend architecture that all API
endpoints and services will build upon.

**Components:**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # API version 1 router
│   │   │   └── endpoints/      # API endpoints
│   │   │       └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── errors.py           # Custom exceptions
│   │   ├── logging.py          # Logging configuration
│   │   └── security.py         # Security utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   └── __init__.py         # Business logic services
│   └── utils/
│       └── __init__.py         # Utility functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── api/
│   ├── services/
│   └── utils/
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Project metadata and tool config
├── .env.example               # Environment variables template
└── README.md                  # Backend setup instructions
```

**Required Files to Create:**

1. `backend/app/main.py` - FastAPI app with basic configuration
1. `backend/app/config.py` - Settings management using Pydantic
1. `backend/app/core/errors.py` - Custom exception classes
1. `backend/app/core/logging.py` - Structured logging setup
1. `backend/app/api/v1/router.py` - API router with versioning
1. `backend/requirements.txt` - Core dependencies
1. `backend/requirements-dev.txt` - Development dependencies
1. `backend/pyproject.toml` - Black, Ruff, MyPy configuration
1. `backend/.env.example` - Environment variables template
1. `backend/README.md` - Setup and development instructions

**Key Dependencies (requirements.txt):**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
python-multipart==0.0.6
readabilipy==0.2.0
```

**Development Dependencies (requirements-dev.txt):**

```txt
pytest==7.4.3
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==23.12.1
ruff==0.1.11
mypy==1.8.0
pre-commit==3.6.0
```

**Acceptance Criteria:**

- [ ] Backend directory structure created
- [ ] FastAPI app starts with `uvicorn app.main:app --reload`
- [ ] Health check endpoint at `GET /health` returns 200
- [ ] API versioning at `/api/v1/` works
- [ ] Logging outputs structured JSON
- [ ] All linters pass (black, ruff, mypy)
- [ ] Tests can be run with `pytest`

### 2. API Response Models & Error Handling

**Priority:** P0 (Must have first)

**Purpose:** Define consistent API response formats and error handling patterns.

**Components:**

```python
# app/models/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime
    version: str

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str
    message: str
    field: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    details: List[ErrorDetail]
    request_id: Optional[str] = None

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
```

**Custom Exceptions (app/core/errors.py):**

```python
class LuminoteException(Exception):
    """Base exception for all Luminote errors"""
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class InvalidURLError(LuminoteException):
    """Raised when URL format is invalid"""
    def __init__(self, url: str):
        super().__init__(
            message=f"Invalid URL format: {url}",
            code="INVALID_URL",
            status_code=400
        )

class ExtractionError(LuminoteException):
    """Raised when content extraction fails"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="EXTRACTION_FAILED",
            status_code=422
        )

class APIKeyError(LuminoteException):
    """Raised when API key is invalid or unauthorized"""
    def __init__(self, provider: str):
        super().__init__(
            message=f"Invalid or unauthorized API key for {provider}",
            code="INVALID_API_KEY",
            status_code=401
        )

class RateLimitError(LuminoteException):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: int):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )
```

**Acceptance Criteria:**

- [ ] All response models defined in `schemas.py`
- [ ] Custom exceptions defined in `errors.py`
- [ ] Exception handler middleware added to FastAPI app
- [ ] All errors return consistent JSON format
- [ ] HTTP status codes match error types
- [ ] Request ID tracking implemented

### 3. CORS & Middleware Configuration

**Priority:** P1 (Required before frontend integration)

**Purpose:** Enable frontend-backend communication and request/response
processing.

**Configuration (app/main.py):**

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import uuid

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Timing middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Acceptance Criteria:**

- [ ] CORS configured for localhost:5173
- [ ] Gzip compression enabled
- [ ] Request ID added to all responses
- [ ] Process time logged for all requests
- [ ] Frontend can make successful API calls

### 4. Configuration Management

**Priority:** P0 (Must have first)

**Purpose:** Centralized configuration with environment variable support.

**Implementation (app/config.py):**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "Luminote API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # Content Extraction
    extraction_timeout: int = 30  # seconds
    extraction_max_size: int = 10_000_000  # 10MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
```

**Environment Variables (.env.example):**

```bash
# Application
APP_NAME=Luminote API
APP_VERSION=0.1.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Content Extraction
EXTRACTION_TIMEOUT=30
EXTRACTION_MAX_SIZE=10000000
```

**Acceptance Criteria:**

- [ ] Settings class defined with Pydantic
- [ ] Environment variables loaded from .env
- [ ] Settings accessible via dependency injection
- [ ] `.env.example` provided for developers
- [ ] All configuration documented

______________________________________________________________________

## Frontend Infrastructure

### 1. SvelteKit Project Structure

**Priority:** P0 (Must have first)

**Purpose:** Establish the foundational frontend architecture.

**Components:**

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/        # Reusable UI components
│   │   │   └── README.md
│   │   ├── stores/           # Svelte stores for state
│   │   │   └── README.md
│   │   ├── utils/            # Utility functions
│   │   │   ├── api.ts        # API client
│   │   │   └── validation.ts
│   │   └── types/            # TypeScript types
│   │       └── index.ts
│   ├── routes/
│   │   ├── +page.svelte      # Home page
│   │   └── +layout.svelte    # Root layout
│   └── app.html              # HTML template
├── static/                   # Static assets
├── tests/
│   ├── unit/
│   └── integration/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── .env.example
└── README.md
```

**Required Files to Create:**

1. `src/lib/utils/api.ts` - API client with error handling
1. `src/lib/types/index.ts` - TypeScript interfaces
1. `src/lib/stores/config.ts` - Configuration store
1. `src/routes/+page.svelte` - Main application page
1. `src/routes/+layout.svelte` - Root layout
1. `package.json` - Dependencies and scripts
1. `tsconfig.json` - TypeScript configuration
1. `vite.config.ts` - Vite configuration
1. `tailwind.config.js` - Tailwind CSS configuration
1. `.env.example` - Environment variables

**Key Dependencies (package.json):**

```json
{
  "dependencies": {
    "@sveltejs/kit": "^2.5.0",
    "svelte": "^4.2.8",
    "typescript": "^5.3.3"
  },
  "devDependencies": {
    "@sveltejs/adapter-auto": "^3.1.1",
    "@sveltejs/vite-plugin-svelte": "^3.0.1",
    "@typescript-eslint/eslint-plugin": "^6.18.1",
    "@typescript-eslint/parser": "^6.18.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.56.0",
    "eslint-plugin-svelte": "^2.35.1",
    "postcss": "^8.4.33",
    "prettier": "^3.1.1",
    "prettier-plugin-svelte": "^3.1.2",
    "tailwindcss": "^3.4.1",
    "vite": "^5.0.11",
    "vitest": "^1.1.3"
  }
}
```

**Acceptance Criteria:**

- [ ] Frontend directory structure created
- [ ] SvelteKit app starts with `npm run dev`
- [ ] TypeScript compilation works
- [ ] Tailwind CSS configured and working
- [ ] API client utility created
- [ ] Type definitions established
- [ ] Linting passes (ESLint)
- [ ] Tests can be run with `npm test`

### 2. API Client & Error Handling

**Priority:** P0 (Must have first)

**Purpose:** Consistent API communication with error handling.

**Implementation (src/lib/utils/api.ts):**

```typescript
export interface APIError {
  error: string;
  details: Array<{
    code: string;
    message: string;
    field?: string;
  }>;
  request_id?: string;
}

export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: APIError = await response.json();
      throw new Error(error.details[0]?.message || error.error);
    }
    return response.json();
  }

  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${path}`);
    return this.handleResponse<T>(response);
  }

  async post<T>(path: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return this.handleResponse<T>(response);
  }

  async put<T>(path: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return this.handleResponse<T>(response);
  }

  async delete<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'DELETE',
    });
    return this.handleResponse<T>(response);
  }
}

export const api = new APIClient();
```

**Type Definitions (src/lib/types/index.ts):**

```typescript
export interface ContentBlock {
  type: 'paragraph' | 'heading' | 'list' | 'quote' | 'code' | 'image';
  text: string;
  level?: number;  // For headings
  metadata?: Record<string, any>;
}

export interface ExtractedContent {
  title: string;
  author?: string;
  published_date?: string;
  url: string;
  content_blocks: ContentBlock[];
}

export interface TranslationRequest {
  content: ExtractedContent;
  target_language: string;
  provider: string;
  model: string;
  api_key: string;
}

export interface TranslationResponse {
  translated_blocks: ContentBlock[];
  block_mapping: Record<string, string>;
  metadata: {
    provider: string;
    model: string;
    total_tokens?: number;
    processing_time: number;
  };
}

export interface ConfigState {
  provider: string;
  model: string;
  api_key: string;
  target_language: string;
}
```

**Acceptance Criteria:**

- [ ] API client created with all HTTP methods
- [ ] Error handling implemented
- [ ] TypeScript interfaces defined
- [ ] API client can be imported and used
- [ ] Request/response types match backend

### 3. Tailwind CSS & UI Foundations

**Priority:** P1 (Required before UI components)

**Purpose:** Establish design system and styling approach.

**Configuration (tailwind.config.js):**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
```

**Global Styles (src/app.css):**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --color-text-primary: #1f2937;
    --color-text-secondary: #6b7280;
    --color-bg-primary: #ffffff;
    --color-bg-secondary: #f9fafb;
  }

  body {
    @apply font-sans text-gray-900 bg-white;
  }

  h1 {
    @apply text-3xl font-bold;
  }

  h2 {
    @apply text-2xl font-semibold;
  }

  h3 {
    @apply text-xl font-semibold;
  }
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors;
  }

  .btn-secondary {
    @apply px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition-colors;
  }

  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500;
  }
}
```

**Acceptance Criteria:**

- [ ] Tailwind CSS configured
- [ ] Custom color palette defined
- [ ] Typography system established
- [ ] Component utilities created
- [ ] Global styles applied
- [ ] Design tokens documented

### 4. State Management Setup

**Priority:** P1 (Required before complex features)

**Purpose:** Centralized state management for application data.

**Implementation (src/lib/stores/config.ts):**

```typescript
import { writable } from 'svelte/store';
import type { ConfigState } from '$lib/types';

const DEFAULT_CONFIG: ConfigState = {
  provider: 'openai',
  model: 'gpt-4',
  api_key: '',
  target_language: 'en',
};

function createConfigStore() {
  const { subscribe, set, update } = writable<ConfigState>(DEFAULT_CONFIG);

  // Load from localStorage on init
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('luminote_config');
    if (stored) {
      try {
        const config = JSON.parse(stored);
        set({ ...DEFAULT_CONFIG, ...config, api_key: '' }); // Never persist API key
      } catch (e) {
        console.error('Failed to parse stored config:', e);
      }
    }
  }

  return {
    subscribe,
    setProvider: (provider: string) =>
      update((state) => {
        const newState = { ...state, provider };
        persistConfig(newState);
        return newState;
      }),
    setModel: (model: string) =>
      update((state) => {
        const newState = { ...state, model };
        persistConfig(newState);
        return newState;
      }),
    setAPIKey: (api_key: string) =>
      update((state) => ({ ...state, api_key })),
    setTargetLanguage: (target_language: string) =>
      update((state) => {
        const newState = { ...state, target_language };
        persistConfig(newState);
        return newState;
      }),
    reset: () => {
      set(DEFAULT_CONFIG);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('luminote_config');
      }
    },
  };
}

function persistConfig(config: ConfigState) {
  if (typeof window !== 'undefined') {
    const { api_key, ...persistable } = config;
    localStorage.setItem('luminote_config', JSON.stringify(persistable));
  }
}

export const configStore = createConfigStore();
```

**Acceptance Criteria:**

- [ ] Configuration store created
- [ ] Persistent storage (localStorage)
- [ ] API key not persisted
- [ ] Store methods work correctly
- [ ] Store can be used in components

______________________________________________________________________

## DevOps Infrastructure

### 1. Docker Development Environment

**Priority:** P1 (Nice to have, not blocking)

**Purpose:** Consistent development environment across machines.

**Files to Create:**

1. `docker-compose.yml` - Development services
1. `backend/Dockerfile` - Backend container
1. `frontend/Dockerfile` - Frontend container
1. `.dockerignore` - Exclude unnecessary files

**Docker Compose (docker-compose.yml):**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev -- --host 0.0.0.0
```

**Backend Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Frontend Dockerfile:**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Acceptance Criteria:**

- [ ] Docker Compose file created
- [ ] Backend Dockerfile working
- [ ] Frontend Dockerfile working
- [ ] Services start with `docker-compose up`
- [ ] Hot reload works for both services
- [ ] Documented in README

### 2. CI/CD Pipeline (GitHub Actions)

**Priority:** P1 (Required before merging code)

**Purpose:** Automated testing, linting, and validation.

**Files to Create:**

1. `.github/workflows/backend-ci.yml` - Backend CI
1. `.github/workflows/frontend-ci.yml` - Frontend CI
1. `.github/workflows/integration-ci.yml` - Integration tests

**Backend CI (.github/workflows/backend-ci.yml):**

```yaml
name: Backend CI

on:
  push:
    branches: [ master, develop ]
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'
  pull_request:
    branches: [ master, develop ]
    paths:
      - 'backend/**'

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements*.txt') }}

    - name: Install dependencies
      working-directory: backend
      run: |
        pip install -r requirements.txt -r requirements-dev.txt

    - name: Lint with Ruff
      working-directory: backend
      run: ruff check .

    - name: Format check with Black
      working-directory: backend
      run: black --check .

    - name: Type check with MyPy
      working-directory: backend
      run: mypy app/

    - name: Run tests
      working-directory: backend
      run: pytest --cov=app --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
```

**Frontend CI (.github/workflows/frontend-ci.yml):**

```yaml
name: Frontend CI

on:
  push:
    branches: [ master, develop ]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [ master, develop ]
    paths:
      - 'frontend/**'

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['20']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      working-directory: frontend
      run: npm ci

    - name: Lint with ESLint
      working-directory: frontend
      run: npm run lint

    - name: Format check with Prettier
      working-directory: frontend
      run: npm run format:check

    - name: Type check
      working-directory: frontend
      run: npm run check

    - name: Run tests
      working-directory: frontend
      run: npm test

    - name: Build
      working-directory: frontend
      run: npm run build
```

**Acceptance Criteria:**

- [ ] GitHub Actions workflows created
- [ ] CI runs on push and PR
- [ ] All linters configured
- [ ] Tests run automatically
- [ ] Coverage reporting enabled
- [ ] Build verification works

### 3. Pre-commit Hooks

**Priority:** P1 (Required before team development)

**Purpose:** Catch issues before commit.

**Configuration (.pre-commit-config.yaml):**

```yaml
repos:
  # Backend hooks
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        files: ^backend/
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.11
    hooks:
      - id: ruff
        files: ^backend/
        args: [--fix]

  # Frontend hooks
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        files: ^frontend/
        types_or: [javascript, typescript, svelte, json, css]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: ^frontend/
        types_or: [javascript, typescript, svelte]
        additional_dependencies:
          - eslint@8.56.0
          - eslint-plugin-svelte@2.35.1

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
```

**Setup Script (scripts/setup-dev-env.sh):**

```bash
#!/bin/bash
set -e

echo "Setting up Luminote development environment..."

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm ci
cp .env.example .env
cd ..

# Pre-commit hooks
echo "Installing pre-commit hooks..."
pip install pre-commit
pre-commit install

echo "Development environment setup complete!"
echo "To start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "To start frontend: cd frontend && npm run dev"
```

**Acceptance Criteria:**

- [ ] Pre-commit config created
- [ ] Hooks install successfully
- [ ] Hooks run on commit
- [ ] Setup script works
- [ ] Documentation provided

______________________________________________________________________

## Development Tools

### 1. Linting & Formatting Configuration

**Priority:** P0 (Must have first)

**Backend Configuration (backend/pyproject.toml):**

```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | venv
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # function calls in argument defaults
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

**Frontend Configuration (frontend/.eslintrc.cjs):**

```javascript
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:svelte/recommended',
    'prettier',
  ],
  plugins: ['@typescript-eslint'],
  ignorePatterns: ['*.cjs', '.svelte-kit', 'build'],
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 2020,
    extraFileExtensions: ['.svelte'],
  },
  env: {
    browser: true,
    es2017: true,
    node: true,
  },
  overrides: [
    {
      files: ['*.svelte'],
      parser: 'svelte-eslint-parser',
      parserOptions: {
        parser: '@typescript-eslint/parser',
      },
    },
  ],
};
```

**Prettier Configuration (frontend/.prettierrc):**

```json
{
  "useTabs": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-svelte"],
  "overrides": [
    {
      "files": "*.svelte",
      "options": {
        "parser": "svelte"
      }
    }
  ]
}
```

**Acceptance Criteria:**

- [ ] Black configuration works
- [ ] Ruff configuration works
- [ ] MyPy configuration works
- [ ] ESLint configuration works
- [ ] Prettier configuration works
- [ ] All configs documented

______________________________________________________________________

## Testing Infrastructure

### 1. Backend Testing Setup

**Priority:** P0 (Must have first)

**Test Configuration (backend/tests/conftest.py):**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "sk-test-1234567890"

@pytest.fixture
def sample_extracted_content():
    """Sample extracted content for testing"""
    return {
        "title": "Test Article",
        "author": "Test Author",
        "published_date": "2026-01-07",
        "url": "https://example.com/article",
        "content_blocks": [
            {"type": "heading", "text": "Introduction", "level": 1},
            {"type": "paragraph", "text": "This is a test paragraph."},
        ]
    }
```

**Acceptance Criteria:**

- [ ] Pytest fixtures created
- [ ] Test client available
- [ ] Sample data fixtures created
- [ ] Tests run with `pytest`
- [ ] Coverage reporting works

### 2. Frontend Testing Setup

**Priority:** P0 (Must have first)

**Test Configuration (frontend/vitest.config.ts):**

```typescript
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}'],
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
```

**Test Setup (frontend/tests/setup.ts):**

```typescript
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/svelte';
import matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

**Acceptance Criteria:**

- [ ] Vitest configured
- [ ] Testing Library set up
- [ ] Test utilities available
- [ ] Tests run with `npm test`
- [ ] Component testing works

______________________________________________________________________

## Documentation Infrastructure

### 1. README Files

**Priority:** P0 (Must have first)

**Files to Create:**

1. Root `README.md` - Project overview
1. `backend/README.md` - Backend setup
1. `frontend/README.md` - Frontend setup
1. `docs/DEVELOPMENT.md` - Development guide
1. `docs/CONTRIBUTING.md` - Contribution guidelines

**Root README Template:**

````markdown
# Luminote

Dual-pane translation workbench for dense web content.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Docker & Docker Compose

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
````

**Frontend:**

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

**With Docker:**

```bash
docker-compose up
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [API Documentation](docs/API.md)
- [Contributing](docs/CONTRIBUTING.md)

## License

MIT

```

**Acceptance Criteria:**

- [ ] All README files created
- [ ] Setup instructions clear
- [ ] Links between docs work
- [ ] Code examples tested
- [ ] Up-to-date with structure

---

## Prioritized Implementation Order

### Phase 0: Infrastructure Setup (Week 1)

**Priority Order:**

1. **Day 1-2: Repository & Project Structure**
   - [ ] Create backend directory structure
   - [ ] Create frontend directory structure
   - [ ] Initialize git repository
   - [ ] Create root README.md

2. **Day 2-3: Backend Foundation**
   - [ ] Set up FastAPI project
   - [ ] Create configuration management
   - [ ] Define error handling framework
   - [ ] Create API response models
   - [ ] Add health check endpoint

3. **Day 3-4: Frontend Foundation**
   - [ ] Initialize SvelteKit project
   - [ ] Configure TypeScript
   - [ ] Set up Tailwind CSS
   - [ ] Create API client utility
   - [ ] Define TypeScript types

4. **Day 4-5: Development Tools**
   - [ ] Configure linters (Black, Ruff, MyPy)
   - [ ] Configure linters (ESLint, Prettier)
   - [ ] Set up pre-commit hooks
   - [ ] Create development setup script

5. **Day 5-6: Testing Infrastructure**
   - [ ] Set up Pytest with fixtures
   - [ ] Set up Vitest with Testing Library
   - [ ] Create sample test files
   - [ ] Verify test execution

6. **Day 6-7: CI/CD & Documentation**
   - [ ] Create GitHub Actions workflows
   - [ ] Set up Docker Compose (optional)
   - [ ] Write backend README
   - [ ] Write frontend README
   - [ ] Write development guide

### Success Criteria for Phase 0 Completion

- [ ] Both backend and frontend start successfully
- [ ] Health check endpoint returns 200
- [ ] Frontend can call backend API
- [ ] All linters pass
- [ ] All tests pass
- [ ] CI/CD pipeline runs successfully
- [ ] New developer can set up environment in < 2 hours

---

## Infrastructure Issues Checklist

Use this checklist to track infrastructure implementation:

### Backend Infrastructure
- [ ] Issue: Create backend project structure
- [ ] Issue: Set up FastAPI application
- [ ] Issue: Create error handling framework
- [ ] Issue: Define API response models
- [ ] Issue: Configure CORS and middleware
- [ ] Issue: Set up configuration management
- [ ] Issue: Create health check endpoint

### Frontend Infrastructure
- [ ] Issue: Create frontend project structure
- [ ] Issue: Initialize SvelteKit application
- [ ] Issue: Configure TypeScript
- [ ] Issue: Set up Tailwind CSS
- [ ] Issue: Create API client utility
- [ ] Issue: Define TypeScript types
- [ ] Issue: Set up state management

### DevOps Infrastructure
- [ ] Issue: Create Docker Compose setup
- [ ] Issue: Create GitHub Actions workflows
- [ ] Issue: Set up pre-commit hooks
- [ ] Issue: Create development setup script

### Testing Infrastructure
- [ ] Issue: Set up Pytest with fixtures
- [ ] Issue: Set up Vitest with Testing Library
- [ ] Issue: Create test utilities
- [ ] Issue: Configure coverage reporting

### Documentation Infrastructure
- [ ] Issue: Write root README
- [ ] Issue: Write backend README
- [ ] Issue: Write frontend README
- [ ] Issue: Write development guide
- [ ] Issue: Write contributing guide

---

## Next Steps

After completing infrastructure setup:

1. Create Architecture Decision Records (ADRs) - see [github-issue-creation-methodology.md](github-issue-creation-methodology.md) Step 1.3
2. Begin feature decomposition - see methodology Step 2.1
3. Create GitHub issues for Phase 1 features
4. Assign first batch of issues to GitHub Copilot

**References:**
- [Feature Specifications](feature-specifications.md)
- [Feature Dependency Analysis](feature-dependency-analysis.md)
- [GitHub Issue Creation Methodology](github-issue-creation-methodology.md)
```
