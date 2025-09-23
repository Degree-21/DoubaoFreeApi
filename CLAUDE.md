# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is DoubaoFreeApi - a lightweight proxy service for the Doubao (豆包) AI platform that provides an API gateway to access Doubao's chat capabilities. It's built with FastAPI and implements session pooling for both logged-in and guest users.

## Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
uv init
uv venv venv
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Start the development server
uv run app.py
# Or directly with Python
python app.py
```

The service runs on `http://localhost:8001` by default (note: port 8001, not 8000 as mentioned in README).

### API Documentation
- Swagger UI: `http://localhost:8001/docs`
- Frontend Demo: `http://localhost:8001/` 

## Architecture

### Core Components

1. **Session Management (`src/pool/`)**
   - `session_pool.py`: Manages both guest and logged-in user sessions
   - `fetcher.py`: Handles session credential extraction from Doubao platform
   - Implements session rotation for load balancing

2. **API Layer (`src/api/`)**
   - `endpoints/chat.py`: Chat completion endpoints (`/api/chat/completions`, `/api/chat/delete`)
   - `endpoints/file.py`: File upload endpoint (`/api/file/upload`)
   - `router.py`: Main API router configuration

3. **Service Layer (`src/service/`)**
   - `doubao_service.py`: Core business logic for interfacing with Doubao's API
   - Handles authentication, request formatting, and response processing

4. **Data Models (`src/model/`)**
   - `request.py`: API request schemas
   - `response.py`: API response schemas

### Configuration Requirements

The application requires a `session.json` file containing Doubao platform credentials:
- `tea_uuid`, `device_id`, `web_id`: From request parameters
- `cookie`, `x_flow_trace`: From request headers  
- `room_id`: From browser URL or referer header

Guest sessions are automatically generated on startup (configurable count in `app.py:37`).

## Key Features

- **Dual Session Support**: Both authenticated users and guests
- **Context Management**: Conversation continuity via `conversation_id` and `section_id`
- **File Uploads**: Image and document support through Doubao's upload API
- **Advanced Features**: Auto Chain-of-Thought (`use_auto_cot`) and Deep Think mode (`use_deep_think`)

## Important Notes

- Guest sessions don't support conversation context persistence
- Session credentials have expiration and may need periodic renewal
- The service proxies requests to `https://www.doubao.com/samantha/chat/completion`
- Frontend demo is minimal and doesn't support all features (image uploads, references)

## Dependencies

Built on FastAPI with key dependencies:
- `aiohttp`/`httpx` for async HTTP requests
- `uvicorn` for ASGI server
- `loguru` for logging
- `playwright` for potential browser automation (session fetching)