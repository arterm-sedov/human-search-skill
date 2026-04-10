#!/usr/bin/env python3
"""
Dependency verification script for human-search skill.
Tests all required packages and services.
"""
import sys
import subprocess
import json

def check_python_package(name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = name.replace('-', '_')
    try:
        __import__(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def check_command(cmd):
    """Check if a command is available."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, None
    except Exception as e:
        return False, str(e)

def check_url(url):
    """Check if a URL is accessible."""
    try:
        import requests
        resp = requests.get(url, timeout=5)
        return resp.status_code == 200, None
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Human Search - Dependency Verification")
    print("=" * 60)
    
    results = {'passed': [], 'failed': []}
    
    # Python packages
    print("\n[Python Packages]")
    packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml'),
        ('markdownify', 'markdownify'),
        ('tiktoken', 'tiktoken'),
    ]
    
    for name, import_name in packages:
        ok, error = check_python_package(name, import_name)
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
        if ok:
            results['passed'].append(f"Python: {name}")
        else:
            results['failed'].append(f"Python: {name} - {error}")
    
    # Node packages
    print("\n[Node Packages]")
    node_checks = [
        ('agent-browser', 'agent-browser --version'),
        ('playwright', 'npx playwright --version'),
    ]
    
    for name, cmd in node_checks:
        ok, error = check_command(cmd)
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
        if ok:
            results['passed'].append(f"Node: {name}")
        else:
            results['failed'].append(f"Node: {name}")
    
    # Docker services
    print("\n[Docker Services]")
    service_checks = [
        ('SearXNG Adapter', 'http://localhost:8000/health'),
        ('SearXNG UI', 'http://localhost:8999'),
    ]
    
    for name, url in service_checks:
        ok, error = check_url(url)
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
        if ok:
            results['passed'].append(f"Docker: {name}")
        else:
            results['failed'].append(f"Docker: {name} - {error}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Summary: {len(results['passed'])} passed, {len(results['failed'])} failed")
    print("=" * 60)
    
    if results['failed']:
        print("\nFailed checks:")
        for f in results['failed']:
            print(f"  - {f}")
        print("\nTo fix:")
        print("  Python: pip install requests beautifulsoup4 lxml markdownify tiktoken")
        print("  Node: npm install -g agent-browser")
        print("  Docker: cd D:/Repo/searxng-docker-tavily-adapter && docker compose up -d")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())