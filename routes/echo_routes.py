import uuid
import base64

from datetime import datetime, timedelta
from flask import request, jsonify, Response
from flask_restx import fields, Namespace, Resource
import redis
import os
from loguru import logger
if not os.path.exists('logs'):
    os.makedirs('logs')

# Initialize Flask-RESTx Namespace
echo_ns = Namespace('echoAtTime', description='Echo message scheduling operations')

# Define the model for the request body (time and message)
echo_model = echo_ns.model('EchoModel', {
    'time': fields.String(required=True, description='The scheduled time in ISO format (YYYY-MM-DDTHH:MM:SS)'),
    'message': fields.String(required=True, description='The message to be scheduled')
})

# Redis client setup (assuming it's properly configured)
ma_redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

log_filename = f"logs/register_message_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logger.add("logs/app.log", rotation="1 week", retention="10 days", compression="zip")  # Log rotation & retention

# Define routes within the echoAtTime namespace
@echo_ns.route('')
class EchoAtTime(Resource):
    @echo_ns.expect(echo_model)  # This links the model to the POST method
    def post(self):
        try:
            # Parse request data
            data = request.get_json()
            logger.info(f"Received data: {data}")

            # Validate required fields
            if not all(key in data for key in ['time', 'message']):
                logger.error("Missing required fields: time and message")
                return {'error': 'Missing required fields: time and message'}, 400
            if data['time'] is None or data['message'] is None:
                logger.error("Time and message cannot be None")
                return {'error': 'Time and message cannot be None'}, 400

            # Validate time field format
            try:

                future_time = data["time"]
                schedule_time = datetime.fromisoformat(future_time)

                if schedule_time < datetime.now():
                    logger.error(f"Scheduled time {schedule_time} is in the past")
                    return {'error': 'Scheduled time must be in the future'}, 400

            except ValueError:
                logger.error("Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
                return {'error': 'Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, 400

            # Validate message field
            if not data["message"]:
                logger.error("Message cannot be empty")
                return {'error': 'Message cannot be empty'}, 400
            
            logger.info(f"Message scheduled for: {schedule_time}")

            # Generate unique message ID
            message_id = str(uuid.uuid4())
            logger.info(f"Generated message ID: {message_id}")

            # Create message object
            message_data = {
                'id': message_id,
                'message': data['message'],
                'scheduled_time': data['time'],
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }

            # Store in Redis (use a sorted set for time-based querying)
            ma_redis_client.zadd('scheduled_messages', {message_id: schedule_time.timestamp()})
            logger.info(f"Stored message in Redis with ID {message_id}")

            # Store message details in a hash
            ma_redis_client.hset(f'message:{message_id}', mapping=message_data)
            logger.info(f"Stored message details in Redis with ID {message_id}")

            return {
                'status': 'Message scheduled successfully',
                'message_id': message_id,
                'scheduled_time': data['time']
            }, 200

        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            return {'error': str(e)}, 500