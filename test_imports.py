#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        print("Testing basic imports...")
        
        # Test configuration system
        from config_manager import config
        print("✓ config_manager")
        
        # Test error handling
        from error_handler import logger
        print("✓ error_handler")
        
        # Test analysis modules
        from pitch_analysis import get_pitch_score
        print("✓ pitch_analysis")
        
        from resonance_analysis import get_resonance_score
        print("✓ resonance_analysis")
        
        from intonation_analysis import get_intonation_score
        print("✓ intonation_analysis")
        
        # Test library modules
        from library import phones, preprocessing, resonance, settings
        print("✓ library modules")
        
        # Test GUI modules (may fail without display)
        try:
            from overlay_gui import VoicePracticeOverlay
            print("✓ overlay_gui")
        except ImportError as e:
            print(f"⚠ overlay_gui (expected if no display): {e}")
        
        # Test audio modules (may fail without audio system)
        try:
            from audio_stream import start_stream
            print("✓ audio_stream")
        except ImportError as e:
            print(f"⚠ audio_stream (expected if no audio): {e}")
        
        # Test live analysis
        from live_analysis_system import AnalysisWorker
        print("✓ live_analysis_system")
        
        print("\n✓ All critical imports successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    exit(0 if success else 1)