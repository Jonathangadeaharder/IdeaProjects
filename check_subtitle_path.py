#!/usr/bin/env python3
import requests
import time

# Login
token_response = requests.post('http://localhost:8000/api/auth/login',
    data={'username': 'test@example.com', 'password': 'TestPassword123!'})
token = token_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get the task ID from your logs
task_id = 'chunk_af5d10e8-fe04-40c8-be3a-d7993f195ce0_0_600_1758969962.836445'

# Get task progress
progress_response = requests.get(f'http://localhost:8000/api/processing/progress/{task_id}', headers=headers)
if progress_response.status_code == 200:
    progress = progress_response.json()
    print('[INFO] Task progress data:')
    for key, value in progress.items():
        if key != 'vocabulary':  # Skip vocabulary array for readability
            print(f'  {key}: {value}')
    if 'subtitle_path' in progress:
        print(f'[PASS] subtitle_path is set: {progress["subtitle_path"]}')
    else:
        print('[WARN] subtitle_path not found in progress data')
        print('[INFO] Available keys:', list(progress.keys()))
else:
    print(f'[ERROR] Could not get progress: {progress_response.status_code}')