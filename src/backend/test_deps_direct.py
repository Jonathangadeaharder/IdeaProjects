# Test importing dependencies directly without going through core.__init__
try:
    from core.dependencies.dependencies import get_processing_session_repository
    print(f"Direct import successful! Function: {get_processing_session_repository}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
