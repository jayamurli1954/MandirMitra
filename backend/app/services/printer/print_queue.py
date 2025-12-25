"""
Print Job Queue for MandirMitra
Handles asynchronous printing to avoid blocking API threads.
"""

import threading
import queue
import logging
import time
from datetime import datetime
from .printer_manager import get_printer_manager

logger = logging.getLogger(__name__)

class PrintJob:
    def __init__(self, printer_id: str, data: dict):
        self.id = f"JOB-{int(time.time()*1000)}"
        self.printer_id = printer_id
        self.data = data
        self.status = "queued"
        self.created_at = datetime.now()
        self.attempts = 0

class PrintQueueManager:
    def __init__(self):
        self.queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        self.jobs = {} # Keep track of job history (simple in-memory)

    def add_job(self, printer_id: str, data: dict) -> str:
        job = PrintJob(printer_id, data)
        self.jobs[job.id] = job
        self.queue.put(job)
        logger.info(f"Queued print job {job.id} for {printer_id}")
        return job.id

    def _process_queue(self):
        logger.info("Print Queue Worker Started")
        manager = get_printer_manager()
        
        while self.running:
            try:
                job = self.queue.get(timeout=1.0) # Check every second
            except queue.Empty:
                continue

            try:
                job.status = "printing"
                logger.info(f"Processing job {job.id}")
                
                # Execute Print
                success = manager.print_ticket(job.printer_id, job.data)
                
                if success:
                    job.status = "completed"
                    logger.info(f"Job {job.id} completed successfully")
                else:
                    job.attempts += 1
                    if job.attempts < 3:
                        job.status = "retrying"
                        logger.warning(f"Job {job.id} failed, retrying ({job.attempts}/3)")
                        self.queue.put(job) # Re-queue
                    else:
                        job.status = "failed"
                        logger.error(f"Job {job.id} failed permanently")

            except Exception as e:
                logger.error(f"Error processing print job {job.id}: {e}")
                job.status = "failed"
            
            finally:
                self.queue.task_done()

# Global Instance
_queue_manager = None

def get_print_queue():
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = PrintQueueManager()
    return _queue_manager
