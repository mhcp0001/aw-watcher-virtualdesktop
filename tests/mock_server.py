#!/usr/bin/env python
"""
Standalone mock ActivityWatch server for testing
"""
import json
import time
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockActivityWatchHandler(BaseHTTPRequestHandler):
    """Mock ActivityWatch server handler"""
    
    # Store buckets and events in memory
    buckets = {}
    events = {}
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            if path == '/api/0/info':
                self._send_json_response({
                    'testing': True,
                    'version': '0.12.0',
                    'hostname': 'mock-server',
                    'device_id': 'mock-device'
                })
            elif path == '/api/0/buckets':
                self._send_json_response(self.buckets)
            elif path.startswith('/api/0/buckets/') and path.endswith('/events'):
                bucket_id = path.split('/')[-2]
                query = parse_qs(parsed.query)
                limit = int(query.get('limit', [100])[0])
                
                bucket_events = self.events.get(bucket_id, [])
                response_events = bucket_events[-limit:] if bucket_events else []
                self._send_json_response(response_events)
            else:
                self._send_error_response(404, 'Not Found')
                
        except Exception as e:
            logger.error(f"GET error: {e}")
            self._send_error_response(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if self.path.startswith('/api/0/buckets/') and '/heartbeat' in self.path:
                # Handle heartbeat
                bucket_id = self.path.split('/')[3]
                if post_data:
                    event_data = json.loads(post_data)
                    if bucket_id not in self.events:
                        self.events[bucket_id] = []
                    self.events[bucket_id].append(event_data)
                self._send_json_response({'success': True})
                
            elif self.path.startswith('/api/0/buckets/'):
                # Handle bucket creation
                bucket_id = self.path.split('/')[-1]
                if post_data:
                    bucket_data = json.loads(post_data)
                    self.buckets[bucket_id] = bucket_data
                else:
                    self.buckets[bucket_id] = {'id': bucket_id, 'created': time.time()}
                self._send_json_response({'success': True})
                
            else:
                self._send_error_response(404, 'Not Found')
                
        except Exception as e:
            logger.error(f"POST error: {e}")
            self._send_error_response(500, str(e))
    
    def _send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps(data).encode('utf-8')
        self.wfile.write(response)
    
    def _send_error_response(self, status, message):
        """Send error response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = json.dumps({'error': message}).encode('utf-8')
        self.wfile.write(error_response)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class MockActivityWatchServer:
    """Mock ActivityWatch server manager"""
    
    def __init__(self, host='localhost', port=5600):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """Start the mock server"""
        try:
            self.server = HTTPServer((self.host, self.port), MockActivityWatchHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.running = True
            logger.info(f"Mock ActivityWatch server started on {self.host}:{self.port}")
            
            # Wait a moment and verify server is responding
            time.sleep(1)
            return self._health_check()
            
        except Exception as e:
            logger.error(f"Failed to start mock server: {e}")
            return False
    
    def stop(self):
        """Stop the mock server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            logger.info("Mock server stopped")
    
    def _health_check(self):
        """Check if server is responding"""
        try:
            import urllib.request
            response = urllib.request.urlopen(f'http://{self.host}:{self.port}/api/0/info', timeout=5)
            return response.status == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def wait_for_ready(self, timeout=10):
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._health_check():
                logger.info("Mock server is ready")
                return True
            time.sleep(0.5)
        
        logger.error("Mock server failed to become ready")
        return False

if __name__ == "__main__":
    # Run as standalone server
    server = MockActivityWatchServer()
    try:
        if server.start():
            logger.info("Mock server running. Press Ctrl+C to stop.")
            while server.running:
                time.sleep(1)
        else:
            logger.error("Failed to start server")
    except KeyboardInterrupt:
        logger.info("Stopping server...")
    finally:
        server.stop()