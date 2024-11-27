# Message Scheduling Service

## About
The Message Scheduling Service is a robust, distributed system designed to handle time-based message processing at scale. It allows users to schedule messages for future delivery and processes them efficiently using a combination of Redis-based queuing and multi-threaded execution.

### What it does
This service acts as a time-aware message processor that enables you to:
- Schedule messages for future processing with precise timing
- Handle large volumes of scheduled messages efficiently
- Process messages in a distributed, thread-safe manner
- Monitor and track message processing through comprehensive logging

### Key Benefits
- **Reliable Delivery**: Uses distributed locking and retry mechanisms to ensure messages are processed exactly once
- **Scalable Architecture**: Employs batch processing and thread pooling to handle high message volumes
- **Fault Tolerance**: Implements exponential backoff and automatic error recovery
- **Monitoring**: Provides detailed logging and health checks for operational visibility

### Use Cases
- Scheduled notifications and reminders
- Delayed job processing
- Time-based workflow automation
- Scheduled data processing tasks
- Message queuing and distribution

## Features
- Message scheduling with Redis queue
- Multi-threaded message processing
- RESTful API with Swagger documentation
- Dockerized deployment
- Automated testing

[Rest of the README remains the same...]

## Prerequisites
- Docker and Docker Compose
- Python 3.x
- Redis

## Quick Start
```bash
# Clone the repository
git clone [repository-url]

# Start the services
docker-compose up -d

# Access the API documentation
http://localhost:3000/docs
```

## Architecture
- **Flask API**: Handles HTTP requests and message scheduling
- **Redis**: Message queue and data storage
- **Scheduler**: Background worker processing scheduled messages
- **Logger**: Rotating log files with compression

## Configuration
Configuration is loaded from `appsettings.json`:
```json
{
  "Redis": {
    "ConnectionString": "localhost"
  }
}
```

## API Endpoints
- `/echoAtTime`: Schedule messages
- `/health`: Service health check
- `/docs`: Swagger UI documentation

## Development
```bash
# Run tests
docker-compose run test

# View logs
cd logs
```

## Message Processing
Messages are processed with:
- Configurable thread pool (default: 10 workers)
- Batch processing (default: 100 messages)
- Exponential backoff retry mechanism
- Distributed locking for message processing

## Docker Support
- Redis container with persistent storage
- Application container with live reload
- Separate test container
- Shared network for service communication

## Logging
Logs are stored in the `logs` directory with:
- Daily rotation
- ZIP compression
- ISO timestamp formatting
- Detailed error tracking

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
