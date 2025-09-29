#!/bin/bash

# Flask Trading Dashboard - Deployment Helper Script

echo "🚀 ETF Trading Dashboard - Vercel Deployment Helper"
echo "=================================================="

# Check if Flask app is working locally
echo "📋 Step 1: Testing Flask app locally..."
if python flask_app.py &
then
    FLASK_PID=$!
    sleep 3
    
    # Test if the app is responding
    if curl -s http://localhost:5001 > /dev/null; then
        echo "✅ Flask app is working locally!"
        kill $FLASK_PID
    else
        echo "❌ Flask app is not responding"
        kill $FLASK_PID
        exit 1
    fi
else
    echo "❌ Failed to start Flask app"
    exit 1
fi

# Check if git is initialized
echo "📋 Step 2: Checking Git repository..."
if [ -d .git ]; then
    echo "✅ Git repository exists"
else
    echo "🔧 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Add all files to git
echo "📋 Step 3: Adding files to git..."
git add .
git commit -m "Add Flask-based trading dashboard for Vercel deployment"
echo "✅ Files committed to git"

# Check if remote origin exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Git remote origin exists"
    
    # Push to GitHub
    echo "📋 Step 4: Pushing to GitHub..."
    git push origin main
    echo "✅ Code pushed to GitHub"
else
    echo "⚠️  Git remote origin not found"
    echo "📋 Please add your GitHub repository as origin:"
    echo "   git remote add origin https://github.com/DMHCAIT/turteltrader.git"
    echo "   git push -u origin main"
fi

echo ""
echo "🎉 Deployment Preparation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Click 'New Project'"
echo "3. Import your GitHub repository: DMHCAIT/turteltrader"
echo "4. Vercel will auto-detect the Python project"
echo "5. Click 'Deploy'"
echo ""
echo "📋 After deployment:"
echo "1. Visit your Vercel app URL"
echo "2. Go to /config page"
echo "3. Generate and configure your access token"
echo "4. Start trading!"
echo ""
echo "🔗 Local app is running at: http://localhost:5001"
echo "🔗 Configuration page: http://localhost:5001/config"