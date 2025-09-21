# 🎛️ TURTLE TRADER - DASHBOARD CONTROLS GUIDE

## ✨ **Everything You Can Control from Dashboard**

### 🏦 **1. CAPITAL MANAGEMENT**
**Location**: Main Dashboard → Capital Settings

#### **Real-Time Controls:**
- ✅ **Total Capital Amount** - Change your trading capital
- ✅ **Deployment Percentage** - Adjust how much to use (default: 70%)
- ✅ **Reserve Percentage** - Keep safe money (default: 30%)
- ✅ **Per Trade Amount** - Set money per trade (default: 5% of deployable)

#### **Example Settings You Can Change:**
```
💰 Total Capital: ₹10,00,000 → Change to any amount
🎯 Deployable: 70% → Adjust to 60%, 80%, etc.
🛡️ Reserve: 30% → Adjust to 20%, 40%, etc.
💵 Per Trade: 5% → Change to 3%, 7%, 10%, etc.
```

### 📊 **2. TRADING STRATEGY PARAMETERS**
**Location**: Sidebar → Strategy Settings

#### **ETF Strategy Controls:**
- ✅ **Buy Dip %** - When to buy (default: 1% drop)
- ✅ **Sell Target %** - When to sell (default: 3% profit) 
- ✅ **Loss Alert %** - When to alert (default: 5% loss)
- ✅ **Max Positions** - How many ETFs at once (default: 8)
- ✅ **Position Size** - Money per position (default: 3%)

#### **Example Changes:**
```
📉 Buy at 2% dip instead of 1%
📈 Sell at 5% profit instead of 3%
⚠️ Alert at 3% loss instead of 5%
🎯 Hold 5 positions instead of 8
💰 Use 5% per position instead of 3%
```

### 🎮 **3. TRADING MODE CONTROLS**
**Location**: Sidebar → Trading Mode

#### **Demo vs Live Trading:**
- 🧪 **DEMO Mode** - Paper trading (no real money)
- 🔴 **LIVE Mode** - Real trading (real money)
- ✅ **One-Click Switch** - Change modes instantly
- 🔐 **Safety Confirmations** - Multiple checks before live

#### **Mode Features:**
```
DEMO Mode:
- Test strategies safely
- Practice interface
- No real money risk
- Full feature access

LIVE Mode:
- Real API orders
- Actual money trades
- Real P&L tracking
- Live notifications
```

### 💹 **4. REAL-TIME MONITORING**
**Location**: Main Dashboard → Multiple Tabs

#### **Live Data Controls:**
- ✅ **Auto-Refresh Toggle** - Turn on/off auto-updates
- ✅ **Refresh Interval** - Set update frequency (30s, 1m, 5m)
- ✅ **Portfolio View** - See all positions live
- ✅ **P&L Tracking** - Real-time profit/loss
- ✅ **Account Balance** - Live balance from Breeze API

### 🎯 **5. MANUAL TRADING CONTROLS**
**Location**: Dashboard → Trading Tab

#### **Manual Order Controls:**
- ✅ **Buy/Sell Buttons** - Manual order placement
- ✅ **Quantity Input** - Custom position sizes
- ✅ **Price Controls** - Market/Limit orders
- ✅ **Order Type** - MTF/CNC selection
- ✅ **Confirmation Steps** - Safety checks

#### **Example Manual Trades:**
```
🛒 Buy NIFTYBEES - 100 shares - Market price
🏷️ Sell BANKBEES - 50 shares - Limit ₹450
📊 MTF Order (4x leverage) or CNC (delivery)
```

### ⚙️ **6. SESSION TOKEN MANAGEMENT**
**Location**: Sidebar → API Settings

#### **Daily Token Update:**
- ✅ **Token Input Field** - Paste new token
- ✅ **Auto-Validation** - Instant connection test  
- ✅ **Connection Status** - Live API status
- ✅ **Token Expiry Alert** - Daily reminders

### 📊 **7. DASHBOARD CUSTOMIZATION**
**Location**: Various Tabs

#### **Visual Controls:**
- ✅ **Chart Time Frames** - 1D, 1W, 1M, 3M, 1Y
- ✅ **Display Options** - Show/hide sections
- ✅ **Color Themes** - Light/dark mode
- ✅ **Mobile Layout** - Auto-responsive design

### 🔔 **8. NOTIFICATION SETTINGS**
**Location**: Settings → Notifications

#### **Alert Controls:**
- ✅ **Telegram Alerts** - Trade confirmations
- ✅ **Email Notifications** - Daily summaries  
- ✅ **Browser Notifications** - Instant alerts
- ✅ **Sound Alerts** - Audio notifications

---

## 🚀 **DAILY STARTUP METHODS**

### **Method 1: Desktop Icon (Easiest)**
1. Run: `./create_desktop_shortcut.sh`
2. Double-click desktop icon daily
3. Dashboard opens automatically

### **Method 2: Terminal Command**
```bash
./start_daily.sh
```

### **Method 3: Direct Launch**
```bash
cd "/Users/rubeenakhan/Downloads/Turtel trader"
source turtle_env/bin/activate
streamlit run app.py
```

### **Method 4: Bookmark**
- Launch once, bookmark: `http://localhost:8501`
- Next time: Just open bookmark (if server running)

---

## 📋 **DAILY ROUTINE CHECKLIST**

### **Morning Setup (5 minutes):**
1. ✅ Launch dashboard (`./start_daily.sh`)
2. ✅ Update session token (in sidebar)
3. ✅ Check account balance (auto-displays)
4. ✅ Review strategy settings
5. ✅ Switch to LIVE mode when ready

### **During Market Hours:**
- 📊 Monitor positions (auto-updates)
- 🎯 Manual trades as needed
- 📈 Watch P&L in real-time
- 🔔 Receive trade alerts

### **End of Day:**
- 📊 Review performance
- 💾 Data automatically saved
- 🔄 Close browser/terminal

---

## 💡 **PRO TIPS**

1. **Start in DEMO Mode** - Always test changes first
2. **Bookmark Dashboard** - Quick daily access
3. **Mobile Friendly** - Use on phone/tablet
4. **Real-time Updates** - Enable auto-refresh
5. **Safety First** - Multiple confirmations for live trades

**🎯 EVERYTHING IS CONTROLLABLE FROM THE DASHBOARD!**
No need to edit config files - change everything live!