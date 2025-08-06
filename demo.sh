# demo.sh
#!/bin/bash

# A script to demonstrate the /hackrx/run endpoint.
# Make sure the uvicorn server is running before executing this.

curl -X 'POST' \
  'http://127.0.0.1:8000/hackrx/run' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "documents": [
      "https://limewire.com/d/LEfyX#ZjeIl7Q7Y3"
  ],
  "questions": [
      "Who is the project manager for Project Starlight?",
      "What is the primary goal of Project Starlight?",
      "What is the grace period for premium payment?"
  ]
}'
