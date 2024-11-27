# Message Echo Service

## Problem Statement
A server application that schedules messages for future delivery with a single API endpoint. Messages are stored in Redis and printed to the console at specified times.

### Key Requirements
- Single API endpoint `/echoAtTime` accepting time and message parameters
- Messages persist through server restarts using Redis
- Support multiple servers behind a load balancer
- Process delayed messages after server recovery
- Handle high message volumes efficiently
- Ensure exactly-once message delivery
- Scalable architecture

## Technical Architecture

### Components
- **Flask API**: REST endpoint for scheduling messages
- **Redis**: Message persistence and distributed queue
- **Scheduler**: Multi-threaded message processor
- **Docker**: Containerized deployment

### Key Features
- Distributed locking for exactly-once processing
- Batch message processing
- Automatic retry mechanism
- Health monitoring
- Comprehensive logging

## Prerequisites
- Docker and Docker Compose
- Python 3.x
- Redis

## Quick Start
```bash
# Clone the repository
git clone [repository-url]

# Start services
docker-compose up -d

# Access API documentation
http://localhost:3000/docs
```

## API Documentation

### POST /echoAtTime
Schedule a message for future delivery.

**Parameters:**
- `time`: Future timestamp when message should be printed
- `message`: Text to be printed at specified time

## Message Processing
- Thread pool (10 workers default)
- Batch processing (100 messages/batch)
- Exponential backoff retry
- Distributed locking for exactly-once delivery

## Docker Setup
- Redis container with persistent storage
- Application container with live reload
- Test container
- Shared network between services

## Configuration
`appsettings.json`:
```json
{
  "Redis": {
    "ConnectionString": "localhost"
  }
}
```

## Logging
- Location: `logs` directory
- Daily rotation
- ZIP compression
- ISO timestamp format
- Error tracking

## Development
```bash
# Run tests
docker-compose run test

# View logs
cd logs
```

## Technical Considerations
1. Redis used for:
   - Message queue
   - Distributed locking
   - Message persistence

2. Scalability features:
   - Multi-threading
   - Batch processing
   - Load balancer support
   - Distributed architecture

3. Reliability:
   - Message persistence
   - Retry mechanism
   - Server restart recovery
   - Exactly-once delivery

## Contributing
1. Fork repository
2. Create feature branch
3. Submit pull request

