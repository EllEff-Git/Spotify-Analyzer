def progressReporter(func: function, message: str, progress: int):
    """
    Args:
        func: function called to report progress
        message: string containing progress message
        progress: progress in integer percentage points 
    
    Returns:
        None
    """
    func(message, progress)
    print(func)