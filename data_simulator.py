import random
import time
from datetime import datetime
from threading import Thread, Lock
from queue import Queue
import concurrent.futures
from elasticsearch import Elasticsearch
from dataclasses import dataclass
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TelecomRecord:
    imei: str
    date_created: str
    imsi: str
    msisdn: str

class DataGenerator:
    @staticmethod
    def generate_random_number(length: int) -> str:
        return ''.join(random.choices('0123456789', k=length))
    
    @staticmethod
    def generate_msisdn() -> str:
        prefixes = ['2010', '2011', '2012']
        prefix = random.choice(prefixes)
        return prefix + DataGenerator.generate_random_number(8)
    
    @staticmethod
    def generate_record() -> TelecomRecord:
        return TelecomRecord(
            imei=DataGenerator.generate_random_number(15),
            date_created=datetime.now().isoformat(),
            imsi=DataGenerator.generate_random_number(15),
            msisdn=DataGenerator.generate_msisdn()
        )

class ElasticsearchClient:
    def __init__(self, host: str = 'localhost', port: int = 9200, index: str = 'telecom_data'):
        # Use a connection URL instead of the deprecated host/port dictionary
        self.es = Elasticsearch([f"http://{host}:{port}"])
        self.index = index
        self.setup_index()
    
    def setup_index(self):
        if not self.es.indices.exists(index=self.index):
            mappings = {
                "mappings": {
                    "properties": {
                        "imei": {"type": "keyword"},
                        "date_created": {"type": "date"},
                        "imsi": {"type": "keyword"},
                        "msisdn": {"type": "keyword"}
                    }
                }
            }
            self.es.indices.create(index=self.index, body=mappings)
            logger.info(f"Created index: {self.index}")

    def bulk_index(self, records: List[TelecomRecord]):
        bulk_data = []
        for record in records:
            bulk_data.append({"index": {"_index": self.index}})
            bulk_data.append(record.__dict__)
        
        if bulk_data:
            self.es.bulk(index=self.index, body=bulk_data, refresh=True)

class DataProcessor:
    def __init__(self, batch_size: int = 1000, max_queue_size: int = 10000):
        self.batch_size = batch_size
        self.queue = Queue(maxsize=max_queue_size)
        self.es_client = ElasticsearchClient()
        self.should_stop = False
        self.lock = Lock()
    
    def producer(self):
        """Continuously generate records and add them to the queue."""
        while not self.should_stop:
            try:
                record = DataGenerator.generate_record()
                self.queue.put(record)
                logger.debug(f"Produced record: {record}")
            except Exception as e:
                logger.error(f"Error in producer: {e}")
                break
    
    def consumer(self):
        """Consume records from the queue and index them in Elasticsearch."""
        batch = []
        while not self.should_stop or not self.queue.empty():
            try:
                record = self.queue.get(timeout=1)
                batch.append(record)
                
                if len(batch) >= self.batch_size:
                    self.es_client.bulk_index(batch)
                    logger.info(f"Indexed batch of {len(batch)} records")
                    batch = []
            except Exception as e:
                if not isinstance(e, TimeoutError):
                    logger.error(f"Error in consumer: {e}")
                
        # Index remaining records
        if batch:
            self.es_client.bulk_index(batch)
            logger.info(f"Indexed final batch of {len(batch)} records")

    def run(self, num_producers: int = 4, num_consumers: int = 2):
        """Run the streaming process with multiple producers and consumers."""
        try:
            # Start producer threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_producers + num_consumers) as executor:
                # Submit producer tasks
                producer_futures = [
                    executor.submit(self.producer)
                    for _ in range(num_producers)
                ]
                
                # Submit consumer tasks
                consumer_futures = [
                    executor.submit(self.consumer)
                    for _ in range(num_consumers)
                ]
                
                # Wait for producers to finish (they won't unless stopped)
                concurrent.futures.wait(producer_futures)
                
                # Signal consumers to stop and wait for them to finish
                self.should_stop = True
                concurrent.futures.wait(consumer_futures)
                
        except KeyboardInterrupt:
            logger.info("Stopping gracefully...")
            self.should_stop = True
        except Exception as e:
            logger.error(f"Error in main process: {e}")
        finally:
            self.should_stop = True

def main():
    # Configuration
    batch_size = 1000      # Number of records per batch
    max_queue_size = 10000 # Maximum number of records in queue
    num_producers = 4      # Number of producer threads
    num_consumers = 2      # Number of consumer threads
    
    processor = DataProcessor(batch_size=batch_size, max_queue_size=max_queue_size)
    processor.run(num_producers=num_producers, num_consumers=num_consumers)

if __name__ == "__main__":
    main()