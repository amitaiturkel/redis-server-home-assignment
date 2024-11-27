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
# Redis client setup (assuming it's properly configured)
ma_redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

log_filename = f"logs/register_message_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logger.add("logs/app.log", rotation="1 week", retention="10 days", compression="zip")  # Log rotation & retention
health_ns = Namespace('health', description='Health check operations')

# Health check endpoint
@health_ns.route('')
class HealthCheck(Resource):
    def get(self):
        logger.info("Health check requested")
        base64_image = 'IC4uLiAgICAuLi4gICAuLi4uLi4gIC4uLi4uLiAgLi4uICAuLi4gICAjIyMjICAjIyMjIyggIyMjIyMjIyAlIyMgIyMsICAlIyMgIyMvLy4KIC4uLi4gICAuLi4gIC4uLiAgLi4gLi4uICAuLiAgLi4uICAuLi4gICAjIyMjICAoIyMgICAgICAjIyMgICAqJSUgJSMjICAjIyAgIyMgICAKIC4uLi4uIC4uLi4uIC4uLiAgLi4uLi4uICAuLi4gLi4uLiAuLi4gICUjJSMjKCAvIyMgICAgICAjIyMgICAsIyMgLiMjIC4jIyAgIyMgICAKIC4uLi4uIC4uLi4uIC4uLiAgLi4uLi4uICAuLi4gLi4uLi4uLi4gICMjIC4jIyAqIyMgICAgICAjIyMgICAqIyMgICMjICUjIyAgIyMgICAKIC4uLi4uLi4uLi4uIC4uLiAgLi4uLi4uICAuLi4gLi4uLi4uLi4gICMjIyMjIyAuIyMgICAgICAjIyMgICAoIyMgICMjLyMjLiAgIyMjIyAKIC4uIC4uLi4uIC4uIC4uLiAgLi4uLi4uICAuLi4gLi4gLi4uLi4gKiMjICAjIyAgIyMsICAgICAjIyMgICAlIyMgICgjIyMjICAgIyMgICAKIC4uIC4uLi4gIC4uLiAuLiAgLi4gIC4uICAuLiAuLi4gIC4uLi4gJSMjICAjIy8gIyMjICAgICAjIyMgICAlIyMgICAjIyMjICAgIyMgICAKLi4uICAuLi4gIC4uLiAuLi4uLi4gIC4uLi4uLiAuLi4gIC4uLi4gIyMsICAjIyMgIyMjIyMgICAjIyMgICAoIyMgICAjIyMvICAgIyMjIyM='
        image = base64.b64decode(base64_image).decode('utf-8')
        print(ma_redis_client.set('key', 'value'))
        print(ma_redis_client.get('key'))
        return Response(image, mimetype='text/plain')
