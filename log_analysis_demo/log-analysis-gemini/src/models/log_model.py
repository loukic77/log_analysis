class LogModel:
    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message

    def __repr__(self):
        return f"LogModel(timestamp={self.timestamp}, level={self.level}, message={self.message})"

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message
        }