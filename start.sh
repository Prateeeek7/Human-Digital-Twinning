#!/bin/bash

# ==============================================================================
# HF-Digital Twin Platform - Startup Script
# ==============================================================================
# This script starts the entire platform, including:
# - Backend API (FastAPI) via Docker Compose
# - Database (SQLite internally handled, optional Redis via Docker)
# - Frontend Application (React/Vite)
# ==============================================================================

# Custom colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}                 HF-DIGITAL TWIN PLATFORM INITIALIZATION                      ${NC}"
echo -e "${BLUE}==============================================================================${NC}"

# Function to clean up background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down HF-Digital Twin Platform services...${NC}"
    
    # 1. Stop Frontend Background Process
    if [ -n "$FRONTEND_PID" ]; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi

    # 2. Stop Docker Compose (Backend/Database)
    echo -e "Stopping Docker containers..."
    docker-compose down
    
    echo -e "${GREEN}✅ All services stopped successfully.${NC}"
    exit 0
}

# Catch termination signals (Ctrl+C)
trap cleanup SIGINT SIGTERM EXIT

# ------------------------------------------------------------------------------
# STEP 1: Start Backend & DB (via Docker Compose)
# ------------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/2] Preparing Backend Environment (Docker)...${NC}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker is not running. Please start Docker Desktop and try again.${NC}"
    exit 1
fi

echo -e "Building and starting containers in detached mode..."
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to start backend via docker-compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend API (FastAPI) and Databases started on localhost:8000${NC}"


# ------------------------------------------------------------------------------
# STEP 2: Start Frontend (React/Vite)
# ------------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/2] Preparing Frontend Environment (Node.js)...${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: 'npm' could not be found. Please install Node.js.${NC}"
    exit 1
fi

cd frontend || { echo -e "${RED}ERROR: frontend directory not found!${NC}"; exit 1; }

echo -e "Checking frontend dependencies..."
if [ ! -d "node_modules" ]; then
    echo -e "Installing frontend dependencies..."
    npm install
fi

echo -e "Starting React Development Server..."
npm run dev -- --host &
FRONTEND_PID=$!

cd ..

echo -e "\n${GREEN}==============================================================================${NC}"
echo -e "${GREEN}🚀 HF-DIGITAL TWIN PLATFORM IS LIVE!                                          ${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo -e "   Frontend URL:  ${BLUE}http://localhost:5173${NC} (or check output above for exact URL)"
echo -e "   Backend API:   ${BLUE}http://localhost:8000/docs${NC} (Swagger UI)"
echo -e "   Database:      SQLite data is persisted inside ./data via Docker volumes"
echo -e "${GREEN}==============================================================================${NC}"
echo -e "${YELLOW}Press [CTRL+C] to gracefully shut down all services.${NC}\n"

# Wait for the frontend background process so the script doesn't exit immediately
wait $FRONTEND_PID
