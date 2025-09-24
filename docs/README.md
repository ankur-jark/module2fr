# TruScholar - Compass Module

AI-powered career discovery system built with microservices architecture. Currently featuring the **Compass Module** for personality assessment, career motivators, and interest mapping.

## 🎯 Current Focus: Compass Module

The Compass Module provides:
- **RIASEC Profile**: Six personality dimensions (Realistic, Investigative, Artistic, Social, Enterprising, Conventional)
- **Career Motivators**: 12 key drivers (Money, Growth, Purpose, Autonomy, etc.)
- **Personal Interests**: Specific activities and domains

### Revolutionary Approach
- Dynamic question generation using GPT-4
- Extracts all dimensions from single responses
- Confidence-based completion (15-18 questions max)
- Natural conversational flow

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/truscholar.git
cd truscholar

# 2. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start all services
./start.sh

# Access at http://localhost:8000
```

### Option 2: Local Development
```bash
# 1. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Start services locally
./start-dev.sh

# Stop services
./stop-dev.sh
```

## 📡 API Endpoints

Base URL: `http://localhost:8000`

### Start Journey
```bash
POST /api/v1/compass/start
{
  "user_id": "user123",
  "demographics": {
    "age": 25,
    "education_level": "bachelor",
    "current_status": "working"
  },
  "preferences": {
    "language": "en",
    "question_style": "casual"
  }
}
```

### Get Journey Status
```bash
GET /api/v1/compass/journey/{journey_id}
```

### Submit Response
```bash
POST /api/v1/compass/journey/{journey_id}/respond
{
  "question_id": "q123",
  "response_text": "I enjoy solving complex problems...",
  "response_time_seconds": 45
}
```

### Get Profile
```bash
GET /api/v1/profile/{user_id}/complete
```

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Frontend  │────▶│ API Gateway │────▶│   Compass    │
│  (Next.js)  │     │  Port 8000  │     │   Service    │
└─────────────┘     └─────────────┘     │  Port 8001   │
                           │             └──────────────┘
                           │                     │
                           ▼                     ▼
                    ┌─────────────┐      ┌─────────────┐
                    │   Profile   │      │    Redis    │
                    │   Service   │◀─────│    Cache    │
                    │  Port 8002  │      └─────────────┘
                    └─────────────┘
```

### Current Services
1. **API Gateway** - Central entry point, routing, rate limiting
2. **Compass Service** - Career discovery logic
3. **User Profile Service** - Profile aggregation (ready for future modules)
4. **Redis** - Caching and session management

## 📁 Project Structure

```
Truscholar/
├── services/
│   ├── api-gateway/           # Main entry point
│   ├── compass-service/        # Compass module
│   ├── user-profile-service/   # Profile aggregation
│   └── shared/                 # Shared utilities
├── docker-compose.yml
├── start.sh                    # Production start script
├── start-dev.sh               # Development start script
└── .env.example               # Environment template
```

## 🔧 Development

### Running Tests
```bash
cd services/compass-service
python -m pytest
```

### Viewing Logs
```bash
# Docker mode
docker-compose logs -f compass-service

# Development mode
tail -f logs/compass-service.log
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔑 Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults provided)
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
```

## 🚦 Service Health

Check service health:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/admin/services/health
```

## 🎯 Journey Flow

1. **Start Journey** → Initialize with user demographics
2. **Generate Question** → AI creates contextual scenario
3. **User Responds** → Natural language response
4. **Analyze Response** → Extract signals for all dimensions
5. **Calculate Confidence** → Determine if more data needed
6. **Decision Point** → Continue, clarify, or complete
7. **Synthesize Profile** → Generate comprehensive insights

## 📈 Future Modules (Architecture Ready)

The microservices architecture is ready for:
- **Skill Analyzer Service** - Technical skills assessment
- **Expertise Analyzer Service** - Domain expertise evaluation
- **Resume Parser Service** - CV analysis
- **Job Matcher Service** - Career opportunities matching

Each new module will:
- Run as independent service
- Integrate automatically via events
- Contribute to aggregated profile
- Scale independently

## 🤝 Contributing

1. Focus on Compass module improvements
2. Maintain microservices patterns
3. Use shared schemas and utilities
4. Write tests for new features

## 📄 License

Proprietary and confidential.

## 🆘 Support

For issues and questions, please contact the development team.