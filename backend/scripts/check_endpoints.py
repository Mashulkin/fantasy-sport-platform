import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

print("=== Registered API Routes ===\n")

for route in app.routes:
    if hasattr(route, "path") and hasattr(route, "methods"):
        print(f"{route.methods} {route.path}")

print("\n=== Looking for task status endpoint ===")
task_endpoints = [r for r in app.routes if "task" in str(r.path) and "status" in str(r.path)]
if task_endpoints:
    print("Found task status endpoints:")
    for route in task_endpoints:
        print(f"  {route.methods} {route.path}")
else:
    print("No task status endpoints found!")

print("\n=== OpenAPI URL ===")
print(f"OpenAPI URL: {app.openapi_url}")