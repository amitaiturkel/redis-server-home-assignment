import time
from datetime import datetime
from threading import Thread
import os
from redis_client import ma_redis_client
from concurrent.futures import ThreadPoolExecutor
from loguru import logger  # Import Loguru for logging
# Ensure the 'logs' folder exists
if not os.path.exists('logs'):
    os.makedirs('logs')

class MessageProcessor:
    def __init__(self, max_workers=10, batch_size=100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Loguru configuration - can be customized to log to a file, etc.
        log_filename = f"logs/message_processor_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

        logger.add(log_filename, rotation="1 day", compression="zip")  # Log to file with rotation

    def process_message(self, message_id):
        """Process a single message with retries"""
        lock_key = f'lock:{message_id}'
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # Try to acquire lock with 10-second expiry
                if ma_redis_client.set(lock_key, 'locked', ex=10, nx=True):
                    try:
                        message_data = ma_redis_client.hgetall(f'message:{message_id}')
                        if message_data:
                            # Convert bytes to string
                            message_data = {k.decode('utf-8'): v.decode('utf-8') 
                                         for k, v in message_data.items()}
                            
                            # Process message
                            logger.info(f"\nScheduled message at {datetime.now().isoformat()}:")
                            logger.info(f"Message ID: {message_id}")
                            logger.info(f"Content: {message_data['message']}")
                            
                            # Clean up
                            ma_redis_client.delete(f'message:{message_id}')
                            ma_redis_client.zrem('scheduled_messages', message_id)
                            return True
                    finally:
                        ma_redis_client.delete(lock_key)
                return False
            except Exception as e:
                logger.error(f"Error processing message {message_id}: {str(e)}")
                retry_count += 1
                # Exponential backoff for reducing the load on Redis and giving the system a better chance to succeed without 
                # overloading the Redis server or the processing thread pool.
                time.sleep(2 ** retry_count)  

        return False

    def process_batch(self, current_time):
        """Process a batch of messages"""
        # Get batch of due messages
        due_messages = ma_redis_client.zrangebyscore(
            'scheduled_messages',
            '-inf',
            current_time,
            start=0,
            num=self.batch_size
        )
        
        if due_messages:
            # Submit each message to thread pool
            futures = [
                self.executor.submit(self.process_message, msg_id.decode('utf-8'))
                for msg_id in due_messages
            ]
            
            # Wait for all messages in batch to complete
            for future in futures:
                try:
                    future.result(timeout=30)  # 30-second timeout
                except Exception as e:
                    logger.error(f"Message processing failed: {str(e)}")

def start_scheduler():
    processor = MessageProcessor(max_workers=10, batch_size=100)
    
    def scheduler():
        logger.info("Enhanced scheduler started...")
        while True:
            try:
                current_time = datetime.now().timestamp()
                processor.process_batch(current_time)
                time.sleep(0.1)  # Check more frequently
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(1)  # Wait on error
    
    thread = Thread(target=scheduler, daemon=True)
    thread.start()
    return thread
