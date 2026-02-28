#!/usr/bin/env python3
"""
Setup Mobile Deployment for AI Wellness Vision
Configures the app to work on mobile devices
"""

import socket
import subprocess
import sys
from pathlib import Path

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.100"  # Fallback IP

def update_flutter_config(ip_address):
    """Update Flutter configuration files with the correct IP"""
    
    # Update API config
    api_config_path = Path("flutter_app/lib/core/config/api_config.dart")
    if api_config_path.exists():
        content = api_config_path.read_text()
        updated_content = content.replace(
            "static const String baseUrl = 'http://localhost:8000';",
            f"static const String baseUrl = 'http://{ip_address}:8000';"
        )
        api_config_path.write_text(updated_content)
        print(f"✅ Updated API config with IP: {ip_address}")
    
    # Update main.dart VQA URL
    main_dart_path = Path("flutter_app/lib/main.dart")
    if main_dart_path.exists():
        try:
            content = main_dart_path.read_text(encoding='utf-8')
            updated_content = content.replace(
                "http://192.168.1.100:8000/api/v1/analysis/visual-qa",
                f"http://{ip_address}:8000/api/v1/analysis/visual-qa"
            )
            main_dart_path.write_text(updated_content, encoding='utf-8')
            print(f"✅ Updated main.dart with IP: {ip_address}")
        except UnicodeDecodeError:
            print(f"⚠️ Could not update main.dart automatically (encoding issue)")
            print(f"   Please manually update the VQA URL to: http://{ip_address}:8000/api/v1/analysis/visual-qa")

def setup_backend_for_mobile(ip_address):
    """Configure backend to accept connections from mobile devices"""
    
    print(f"\n🔧 Backend Configuration for Mobile:")
    print(f"   Your computer IP: {ip_address}")
    print(f"   Backend will run on: http://{ip_address}:8000")
    print(f"   Mobile app will connect to: http://{ip_address}:8000")
    
    # Check if Windows Firewall might block connections
    print(f"\n🔥 Firewall Configuration:")
    print(f"   Make sure Windows Firewall allows Python on port 8000")
    print(f"   Or temporarily disable firewall for testing")

def build_mobile_app():
    """Build the Flutter app for mobile"""
    
    print(f"\n📱 Building Mobile App...")
    
    try:
        # Change to flutter directory
        flutter_dir = Path("flutter_app")
        
        # Build APK for Android
        print("🔨 Building Android APK...")
        result = subprocess.run([
            "flutter", "build", "apk", "--release"
        ], cwd=flutter_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            apk_path = flutter_dir / "build/app/outputs/flutter-apk/app-release.apk"
            print(f"✅ APK built successfully!")
            print(f"   Location: {apk_path}")
            print(f"   Transfer this APK to your Android phone and install it")
        else:
            print(f"❌ APK build failed:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ Flutter not found. Make sure Flutter is installed and in PATH")
    except Exception as e:
        print(f"❌ Build error: {e}")

def create_mobile_instructions(ip_address):
    """Create instructions for mobile deployment"""
    
    instructions = f"""
# 📱 Mobile Deployment Instructions

## 🚀 Quick Setup

### 1. Backend Setup
```bash
# Start your backend server
python main_api_server_cnn.py
```
Your backend will be accessible at: http://{ip_address}:8000

### 2. Network Requirements
- ✅ Phone and computer on same WiFi network
- ✅ Computer IP: {ip_address}
- ✅ Backend port: 8000
- ✅ Firewall configured to allow connections

### 3. Mobile App Options

#### Option A: Install APK (Android)
1. Transfer `flutter_app/build/app/outputs/flutter-apk/app-release.apk` to your phone
2. Enable "Install from unknown sources" in Android settings
3. Install the APK
4. Open the app and test!

#### Option B: USB Debugging (Android)
1. Enable Developer Options and USB Debugging on your phone
2. Connect phone via USB
3. Run: `flutter run` in the flutter_app directory

#### Option C: Wireless Debugging (Android 11+)
1. Enable Wireless Debugging in Developer Options
2. Connect to same WiFi network
3. Pair device and run: `flutter run`

### 4. Testing Checklist
- [ ] Backend running on http://{ip_address}:8000
- [ ] Phone connected to same WiFi
- [ ] App installed and opened
- [ ] Image upload works
- [ ] Visual Q&A responds
- [ ] CNN analysis works

### 5. Troubleshooting
- **Connection refused**: Check firewall settings
- **Timeout errors**: Verify IP address and network
- **App crashes**: Check backend logs for errors

## 🔧 Advanced Configuration

### Custom IP Configuration
If your IP changes, update these files:
- `flutter_app/lib/core/config/api_config.dart`
- `flutter_app/lib/main.dart` (VQA URL)

### Network Security
- Consider using HTTPS for production
- Set up proper authentication
- Configure CORS policies

## 📞 Support
If you encounter issues:
1. Check backend logs
2. Verify network connectivity
3. Test API endpoints manually
4. Check mobile app logs
"""
    
    instructions_path = Path("MOBILE_DEPLOYMENT_GUIDE.md")
    instructions_path.write_text(instructions)
    print(f"✅ Created deployment guide: {instructions_path}")

def main():
    """Main setup function"""
    
    print("🚀 AI Wellness Vision - Mobile Deployment Setup")
    print("=" * 50)
    
    # Get local IP address
    ip_address = get_local_ip()
    print(f"🌐 Detected IP Address: {ip_address}")
    
    # Ask user to confirm IP
    user_ip = input(f"\nIs this IP correct? Press Enter to use {ip_address}, or type a different IP: ").strip()
    if user_ip:
        ip_address = user_ip
    
    print(f"\n📝 Using IP Address: {ip_address}")
    
    # Update Flutter configuration
    update_flutter_config(ip_address)
    
    # Setup backend configuration
    setup_backend_for_mobile(ip_address)
    
    # Ask if user wants to build APK
    build_apk = input(f"\n📱 Build Android APK now? (y/n): ").strip().lower()
    if build_apk == 'y':
        build_mobile_app()
    
    # Create instructions
    create_mobile_instructions(ip_address)
    
    print(f"\n" + "=" * 50)
    print(f"🎉 Mobile deployment setup complete!")
    print(f"📖 Check MOBILE_DEPLOYMENT_GUIDE.md for detailed instructions")
    print(f"🚀 Start your backend: python main_api_server_cnn.py")
    print(f"📱 Your app will connect to: http://{ip_address}:8000")

if __name__ == "__main__":
    main()