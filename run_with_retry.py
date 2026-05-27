#!/usr/bin/env python3
"""
Workflow-level retry wrapper for main.py
Handles complete workflow failures during peak API times by retrying after delays
"""
import subprocess
import sys
import time
from datetime import datetime

MAX_WORKFLOW_RETRIES = 3  # Retry entire workflow up to 3 times
RETRY_DELAY_MINUTES = 5   # Wait 5 minutes between workflow retries

def run_main():
    """Run main.py and return exit code"""
    print(f"\n{'='*60}")
    print(f"[retry-wrapper] Starting main.py at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    result = subprocess.run([sys.executable, "main.py"], capture_output=False)
    return result.returncode

def main():
    """Run main.py with workflow-level retry logic"""
    for attempt in range(1, MAX_WORKFLOW_RETRIES + 1):
        print(f"\n{'='*60}")
        print(f"[retry-wrapper] Workflow Attempt {attempt}/{MAX_WORKFLOW_RETRIES}")
        print(f"{'='*60}\n")
        
        exit_code = run_main()
        
        if exit_code == 0:
            print(f"\n{'='*60}")
            print(f"[retry-wrapper] ✅ SUCCESS on attempt {attempt}/{MAX_WORKFLOW_RETRIES}")
            print(f"{'='*60}\n")
            sys.exit(0)
        else:
            print(f"\n{'='*60}")
            print(f"[retry-wrapper] ❌ FAILED on attempt {attempt}/{MAX_WORKFLOW_RETRIES} (exit code: {exit_code})")
            print(f"{'='*60}\n")
            
            if attempt < MAX_WORKFLOW_RETRIES:
                wait_seconds = RETRY_DELAY_MINUTES * 60
                print(f"[retry-wrapper] Waiting {RETRY_DELAY_MINUTES} minutes before retry...")
                print(f"[retry-wrapper] This allows the Pollinations AI API to recover during peak times")
                print(f"[retry-wrapper] Retry will start at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Show countdown
                for remaining in range(wait_seconds, 0, -30):
                    mins = remaining // 60
                    secs = remaining % 60
                    print(f"[retry-wrapper] Time until retry: {mins}m {secs}s remaining...")
                    time.sleep(30)
                
                print(f"\n[retry-wrapper] Retry delay complete. Starting attempt {attempt + 1}...\n")
            else:
                print(f"\n{'='*60}")
                print(f"[retry-wrapper] ❌ ALL ATTEMPTS FAILED")
                print(f"[retry-wrapper] The Pollinations AI API may be experiencing extended downtime")
                print(f"[retry-wrapper] Please check API status or try again later")
                print(f"{'='*60}\n")
                sys.exit(exit_code)

if __name__ == "__main__":
    main()
