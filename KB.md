# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TruScholar Compass Module - An AI-powered career discovery system using microservices architecture. Currently focused on the Compass module with architecture ready for future expansion.

## Current Focus: Compass Module Only

The active module provides:
- RIASEC personality profiling (Holland Codes)
- Career motivators analysis (12 dimensions)
- Personal interests mapping
- Dynamic GPT-4 powered assessments

## Tech Stack

- **Backend**: Python 3.11 with FastAPI
- **AI**: OpenAI GPT-4
- **Cache**: Redis
- **Architecture**: Microservices (API Gateway pattern)
- **Containerization**: Docker & Docker Compose
- **Frontend**: Next.js (separate repo)

## Quick Start Commands

```bash
# Docker mode (production-like)
./start.sh

# Local development mode
./start-dev.sh

# Stop development services
./stop-dev.sh

# View logs
docker-compose logs -f compass-service
# or
tail -f logs/compass-service.log
```

## Architecture

### Active Services
1. **API Gateway** (Port 8000) - All requests go through here
2. **Compass Service** (Port 8001) - Career discovery logic
3. **User Profile Service** (Port 8002) - Ready for future aggregation
4. **Redis** - Session management and caching

### Service Locations
```
services/
├── api-gateway/           # Entry point for all requests
├── compass-service/        # Main business logic
│   ├── compass_schemas.py # Data models
│   ├── compass_orchestrator.py # Main controller
│   ├── question_generator.py
│   ├── response_analyzer.py
│   ├── confidence_scorer.py
│   ├── decision_engine.py
│   └── profile_synthesizer.py
├── user-profile-service/   # Profile aggregation (minimal for now)
└── shared/                 # Common utilities and schemas
```

## Key Design Decisions

1. **Microservices from Day 1**: Even with one module, architecture is ready for expansion
2. **Service Independence**: Compass can run standalone
3. **Event-Driven Ready**: Redis Pub/Sub for future module communication
4. **API Gateway Pattern**: Single entry point for all clients
5. **Shared Libraries**: Common schemas prevent duplication

## API Flow

```
Client → API Gateway (8000) → Compass Service (8001)
                            ↓
                        Redis Cache
                            ↓
                    Profile Service (8002)
```

## Important Implementation Details

### Compass Journey Flow
1. **Questions 1-15**: Standard assessment
2. **Questions 16-18**: Optional clarifications
3. **85% confidence**: Can complete early (after 12+ questions)
4. **75% confidence**: Normal completion threshold
5. **Skip penalty**: -10% confidence per skip

### GPT-4 Integration
- Dynamic question generation
- Multi-dimensional response analysis
- Profile synthesis with insights
- All prompts in respective service files

### State Management
- Journey state stored in Redis
- 1-hour TTL for cache entries
- Event publishing for future modules

## Testing Endpoints

```bash
# Start journey
curl -X POST http://localhost:8000/api/v1/compass/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test123","demographics":{"age":25}}'

# Check health
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/admin/services/health
```

## Future Module Integration

When adding new modules:
1. Create new service directory
2. Use shared schemas
3. Register with service registry
4. Publish profile components as events
5. User Profile Service will auto-aggregate

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `REDIS_URL` - Default: redis://localhost:6379
- `CORS_ORIGINS` - Default: http://localhost:3000

## Common Tasks

### Add a new endpoint
1. Add route to API Gateway (`services/api-gateway/main.py`)
2. Implement in Compass Service
3. Test via http://localhost:8000/docs

### Modify question generation
Edit `services/compass-service/question_generator.py`

### Adjust confidence thresholds
Edit `services/compass-service/decision_engine.py`

### Change response analysis
Edit `services/compass-service/response_analyzer.py`

## Debugging

- API Docs: http://localhost:8000/docs
- Service logs: `docker-compose logs -f [service-name]`
- Redis monitoring: `redis-cli monitor`
- Health checks: Each service has `/health` endpoint