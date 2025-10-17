#!/usr/bin/env python3
"""
Test script for the LLM Code Deployment API
"""

import requests
import json
import sys
import time

def test_health(base_url):
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_api_endpoint(base_url, secret):
    """Test the main API endpoint"""
    print("\n🧪 Testing API endpoint...")

    payload = {
        "email": "test@example.com",
        "task": f"test-app-{int(time.time())}",
        "round": 1,
        "nonce": f"test-{int(time.time())}",
        "secret": secret,
        "brief": "Create a simple calculator web app with buttons for numbers 0-9 and operations +, -, *, /. Display the result in a large text field.",
        "evaluation": {
            "url": "https://httpbin.org/post"  # Test URL that echoes back
        }
    }

    try:
        print(f"   Sending request to {base_url}/api-endpoint...")
        response = requests.post(
            f"{base_url}/api-endpoint",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ Request accepted!")
            print("   Processing started in background...")
            print("   Check logs/api.log for progress")
            return True
        else:
            print(f"\n❌ Request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("LLM Code Deployment API - Test Suite")
    print("=" * 60)

    # Configuration
    base_url = input("\nEnter API base URL (default: http://localhost:5000): ").strip()
    if not base_url:
        base_url = "http://localhost:5000"

    secret = input("Enter your SHARED_SECRET: ").strip()
    if not secret:
        print("❌ Secret is required!")
        sys.exit(1)

    # Run tests
    health_ok = test_health(base_url)

    if health_ok:
        api_ok = test_api_endpoint(base_url, secret)

        if api_ok:
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Check logs/api.log for processing details")
            print("2. Wait 2-3 minutes for GitHub Pages to be ready")
            print("3. Visit the generated GitHub Pages URL")
        else:
            print("\n❌ API endpoint test failed")
    else:
        print("\n❌ Health check failed - is the server running?")

if __name__ == "__main__":
    main()
