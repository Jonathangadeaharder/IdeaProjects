try:
    from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor
    print("SUCCESS: Import worked!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
