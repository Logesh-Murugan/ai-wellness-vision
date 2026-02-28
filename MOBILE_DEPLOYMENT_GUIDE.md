# 📱 Mobile Deployment Guide - AI Wellness Vision

## 🎯 **Your Configuration**
- **Computer IP**: 10.98.177.214
- **Backend URL**: http://10.98.177.214:8000
- **Status**: ✅ Configuration Updated

## 🚀 **Quick Mobile Setup**

### **Step 1: Start Backend Server**
```bash
# In your main project directory
python main_api_server_cnn.py
```
Your backend will be accessible at: **http://10.98.177.214:8000**

### **Step 2: Configure Windows Firewall**
```bash
# Option A: Allow Python through firewall
# Go to Windows Defender Firewall → Allow an app → Add Python

# Option B: Temporarily disable firewall (for testing only)
# Windows Settings → Network & Internet → Windows Firewall → Turn off
```

### **Step 3: Test Backend from Phone**
1. Connect your phone to the **same WiFi network**
2. Open browser on phone
3. Visit: **http://10.98.177.214:8000/health**
4. Should show: `{"status": "healthy"}`

### **Step 4: Build Mobile App**

#### **For Android (APK):**
```bash
cd flutter_app

# Build release APK
flutter build apk --release

# APK location:
# build/app/outputs/flutter-apk/app-release.apk
```

#### **For Direct Installation (USB):**
```bash
cd flutter_app

# Connect phone via USB with Developer Mode enabled
flutter run --release
```

## 📱 **Installation Methods**

### **Method 1: APK Installation (Recommended)**
1. **Build APK**: `flutter build apk --release`
2. **Transfer APK** to your phone (via USB, email, or cloud)
3. **Enable Unknown Sources** in Android Settings
4. **Install APK** on your phone
5. **Open app** and test!

### **Method 2: USB Debugging**
1. **Enable Developer Options** on your phone
2. **Enable USB Debugging**
3. **Connect phone via USB**
4. **Run**: `flutter run --release`

### **Method 3: Wireless Debugging (Android 11+)**
1. **Enable Wireless Debugging** in Developer Options
2. **Connect to same WiFi**
3. **Pair device** and run: `flutter run --release`

## 🧪 **Testing Checklist**

### **Backend Testing**
- [ ] Backend running: `python main_api_server_cnn.py`
- [ ] Health check works: http://10.98.177.214:8000/health
- [ ] Phone and computer on same WiFi
- [ ] Firewall allows connections

### **Mobile App Testing**
- [ ] App installs successfully
- [ ] Home page loads with 4 quick actions
- [ ] Image upload works (camera/gallery)
- [ ] CNN analysis responds
- [ ] Visual Q&A works
- [ ] Chat functionality works

## 🔧 **Troubleshooting**

### **Connection Issues**
```bash
# Problem: "Connection refused"
# Solution: Check firewall settings

# Problem: "Timeout"
# Solution: Verify IP address and WiFi connection

# Problem: "Network error"
# Solution: Restart backend server
```

### **App Issues**
```bash
# Problem: App crashes on startup
# Solution: Check backend logs for errors

# Problem: Images won't upload
# Solution: Check camera/storage permissions

# Problem: No response from AI
# Solution: Verify backend is running and accessible
```

## 📊 **Network Configuration**

### **Your Network Setup**
```
Phone (WiFi) ←→ Router ←→ Computer (10.98.177.214:8000)
     ↓                           ↓
  Flutter App              Backend Server
```

### **Required Ports**
- **8000**: Backend API server
- **3000**: Flutter web server (if using web version)

## 🎉 **Success Indicators**

When everything works correctly, you should see:

### **Backend Terminal**
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: 10.98.177.214:xxxxx - "POST /api/v1/analysis/visual-qa HTTP/1.1" 200 OK
```

### **Mobile App**
- ✅ Splash screen loads
- ✅ Home page shows 4 quick actions
- ✅ Visual Q&A page opens
- ✅ Image upload works
- ✅ AI responses appear
- ✅ 85% confidence ratings

## 🚀 **Next Steps**

1. **Build APK**: `flutter build apk --release`
2. **Install on phone**: Transfer and install APK
3. **Test features**: Try all functionality
4. **Share with others**: Send APK to friends/family

## 📞 **Support**

If you encounter issues:
1. Check this guide's troubleshooting section
2. Verify network connectivity
3. Check backend server logs
4. Test API endpoints manually

**Your AI Wellness Vision app is ready for mobile! 🌟**