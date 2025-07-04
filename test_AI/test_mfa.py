#!/usr/bin/env python3
"""
Test MFA Installation and Integration
"""

import asyncio
import sys
import os

# Add the FastTTS directory to Python path
sys.path.insert(0, '/mnt/d/FastTTS')

from alignment.mfa_aligner import MFAAligner

async def test_mfa_installation():
    """Test MFA installation and model availability"""
    print("🧪 Testing MFA Installation...")
    
    aligner = MFAAligner()
    
    print(f"✅ MFA Available: {aligner.is_available}")
    
    if aligner.is_available:
        # Check model status
        status = aligner.get_installation_status()
        print(f"📊 Installation Status: {status}")
        
        # Test model availability
        models_status = aligner._check_models_available()
        print(f"🎯 Models Status: {models_status}")
        
        if status["ready"]:
            print("✅ MFA is fully configured and ready for use!")
            return True
        else:
            print("⚠️ MFA installed but models missing")
            
            # Try to download models
            print("📥 Attempting to download missing models...")
            download_result = await aligner.download_models()
            print(f"📊 Download Result: {download_result}")
            
            if download_result["success"]:
                print("✅ Models downloaded successfully!")
                return True
            else:
                print(f"❌ Model download failed: {download_result['error']}")
                return False
    else:
        print("❌ MFA not available - please check installation")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mfa_installation())
    if success:
        print("\n🎉 MFA Integration Test: PASSED")
        print("   MFA is ready for integration with FastTTS!")
    else:
        print("\n❌ MFA Integration Test: FAILED") 
        print("   Please check installation and try again.")
    
    sys.exit(0 if success else 1)