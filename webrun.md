backend
cd "/Users/pratikkumar/Desktop/Human Digit Twin" && uvicorn pdt.api.main:app --reload --port 8000

frontend
cd "/Users/pratikkumar/Desktop/Human Digit Twin/frontend" && npm run dev

check servers
sleep 3 && lsof -ti:8000 && echo "✓ Backend API is running on port 8000" || echo "⚠ Backend API may still be starting..."
