#!/bin/bash

# Start the backend server
cd backend
npm install
npm start &

# Start the frontend server
cd ../frontend
npm install
npm start

# Wait for both servers to exit
wait
