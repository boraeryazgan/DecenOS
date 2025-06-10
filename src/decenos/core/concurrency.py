import threading
import time
import random

buffer = []
BUFFER_SIZE = 5
logs = []

lock = threading.Lock()
not_empty = threading.Condition(lock)
not_full = threading.Condition(lock)

class Producer(threading.Thread):
    def run(self):
        for _ in range(10):
            item = random.randint(1, 100)
            with not_full:
                while len(buffer) >= BUFFER_SIZE:
                    not_full.wait()
                buffer.append(item)
                msg = f"Produced: {item}"
                logs.append(msg)
                print(msg)
                not_empty.notify()
            time.sleep(random.uniform(0.1, 0.5))

class Consumer(threading.Thread):
    def run(self):
        for _ in range(10):
            with not_empty:
                while not buffer:
                    not_empty.wait()
                item = buffer.pop(0)
                msg = f"Consumed: {item}"
                logs.append(msg)
                print(msg)
                not_full.notify()
            time.sleep(random.uniform(0.1, 0.5))

def run_producer_consumer():
    producer = Producer()
    consumer = Consumer()
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()

def get_logs():
    return logs