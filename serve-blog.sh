#!/bin/bash
# Serve blog on port 8001 while game runs on 8000
echo "🎯 Starting Skeeball Blog Server on http://localhost:8001/skeeball_game_blog.html"
python3 -m http.server 8001 --bind 127.0.0.1