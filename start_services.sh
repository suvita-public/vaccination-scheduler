#!/bin/bash

# Start Flask in the background
echo "Starting Flask..."
waitress-serve --host=0.0.0.0 --port=5000 app:app

# Start Nginx in the foreground
#echo "Starting Nginx..."
#nginx -g "daemon off;"
