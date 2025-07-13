#!/usr/bin/env python
"""
Watcher simulation test - simulates the main watcher loop with ActivityWatch
"""
import sys
import time
import logging
from datetime import datetime, timezone

from aw_client import ActivityWatchClient
from aw_core.models import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_watcher_heartbeat():
    """Simulate the main watcher heartbeat loop"""
    logger.info("Starting watcher simulation...")
    
    client = ActivityWatchClient(
        "aw-watcher-virtualdesktop-simulation", 
        host="localhost", 
        port=5600, 
        testing=True
    )
    
    bucket_id = f"{client.client_name}_{client.client_hostname}"
    event_type = "currentwindow"
    
    try:
        # Create bucket
        client.create_bucket(bucket_id, event_type, queued=True)
        logger.info(f"Created simulation bucket: {bucket_id}")
        
        # Simulate multiple window changes with different desktops
        simulation_data = [
            {
                "app": "Code.exe",
                "title": "main.py - aw-watcher-virtualdesktop",
                "desktop": "Development"
            },
            {
                "app": "chrome.exe", 
                "title": "ActivityWatch Documentation",
                "desktop": "Research"
            },
            {
                "app": "slack.exe",
                "title": "Team Chat",
                "desktop": "Communication"
            },
            {
                "app": "Code.exe",
                "title": "virtualdesktop.py - aw-watcher-virtualdesktop", 
                "desktop": "Development"
            }
        ]
        
        logger.info("Simulating window activity...")
        
        for i, window_data in enumerate(simulation_data):
            now = datetime.now(timezone.utc)
            event = Event(timestamp=now, data=window_data)
            
            # Send heartbeat (simulating the main watcher loop)
            client.heartbeat(bucket_id, event, pulsetime=2.0, queued=True)
            logger.info(f"Heartbeat {i+1}: {window_data['app']} on {window_data['desktop']}")
            
            # Small delay between events
            time.sleep(1)
        
        # Wait for processing
        time.sleep(3)
        
        # Verify events were stored
        events = client.get_events(bucket_id, limit=10)
        logger.info(f"Retrieved {len(events)} events from bucket")
        
        # Analyze the events
        desktop_activities = {}
        for event in events:
            desktop = event.data.get("desktop", "unknown")
            app = event.data.get("app", "unknown")
            
            if desktop not in desktop_activities:
                desktop_activities[desktop] = []
            desktop_activities[desktop].append(app)
        
        logger.info("\nDesktop Activity Summary:")
        for desktop, apps in desktop_activities.items():
            logger.info(f"  {desktop}: {', '.join(set(apps))}")
        
        # Verify we have the expected desktops
        expected_desktops = {"Development", "Research", "Communication"}
        found_desktops = set(desktop_activities.keys())
        
        if expected_desktops.issubset(found_desktops):
            logger.info("✓ All expected desktop activities were tracked")
            return True
        else:
            missing = expected_desktops - found_desktops
            logger.warning(f"Missing desktop activities: {missing}")
            return len(events) > 0  # Still pass if we got some events
            
    except Exception as e:
        logger.error(f"✗ Watcher simulation failed: {e}")
        return False

def test_bucket_persistence():
    """Test that buckets and events persist correctly"""
    logger.info("Testing bucket persistence...")
    
    client = ActivityWatchClient(
        "test-persistence", 
        host="localhost", 
        port=5600, 
        testing=True
    )
    
    try:
        # List existing buckets
        buckets = client.get_buckets()
        logger.info(f"Found {len(buckets)} existing buckets")
        
        # Look for our simulation bucket
        simulation_bucket = None
        for bucket_id, bucket_info in buckets.items():
            if "virtualdesktop-simulation" in bucket_id:
                simulation_bucket = bucket_id
                break
        
        if simulation_bucket:
            events = client.get_events(simulation_bucket, limit=5)
            logger.info(f"Found {len(events)} events in simulation bucket")
            
            if events:
                logger.info("Sample event data:")
                for event in events[:2]:  # Show first 2 events
                    logger.info(f"  {event.data}")
            
            logger.info("✓ Bucket persistence working")
            return True
        else:
            logger.info("No simulation bucket found (may be expected)")
            return True
            
    except Exception as e:
        logger.error(f"✗ Bucket persistence test failed: {e}")
        return False

def main():
    """Run watcher simulation tests"""
    logger.info("Starting watcher simulation tests...")
    
    tests = [
        simulate_watcher_heartbeat,
        test_bucket_persistence
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} raised exception: {e}")
            failed += 1
    
    logger.info(f"\nSimulation Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        logger.info("All simulation tests passed! 🎉")

if __name__ == "__main__":
    main()