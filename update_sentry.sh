#!/bin/bash

# Sentry DSN
SENTRY_DSN="https://430e59de3774687749e13e2b1adab024@o4509251436150789.ingest.us.sentry.io/4509251457187840"

# Set backend Sentry DSN
echo "Setting backend Sentry DSN..."
export SENTRY_DSN="$SENTRY_DSN"

# Create .env in project root if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file in project root..."
  echo "SENTRY_DSN=$SENTRY_DSN" > .env
else
  # Update existing .env
  if grep -q "SENTRY_DSN" .env; then
    echo "Updating existing SENTRY_DSN in .env..."
    sed -i "s|SENTRY_DSN=.*|SENTRY_DSN=$SENTRY_DSN|g" .env
  else
    echo "Adding SENTRY_DSN to .env..."
    echo "SENTRY_DSN=$SENTRY_DSN" >> .env
  fi
fi

# Update frontend .env
echo "Setting frontend Sentry DSN..."
cd frontend

# Create .env in frontend if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating new .env file for frontend..."
  echo "REACT_APP_API_URL=http://172.16.16.6:5004" > .env
  echo "REACT_APP_SENTRY_DSN=$SENTRY_DSN" >> .env
else
  # Update or add SENTRY_DSN in frontend .env
  if grep -q "REACT_APP_SENTRY_DSN" .env; then
    echo "Updating existing REACT_APP_SENTRY_DSN in frontend .env..."
    sed -i "s|REACT_APP_SENTRY_DSN=.*|REACT_APP_SENTRY_DSN=$SENTRY_DSN|g" .env
  else
    echo "Adding REACT_APP_SENTRY_DSN to frontend .env..."
    echo "REACT_APP_SENTRY_DSN=$SENTRY_DSN" >> .env
  fi
fi

echo "Sentry DSN has been set. You'll need to restart the servers for the changes to take effect."
echo ""
echo "Next steps:"
echo "1. Start the development server with: './reset_servers.sh'"
echo "2. Test the Sentry integration at: http://localhost:3001/debug/sentry-test" 