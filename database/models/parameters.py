class StatusParameters:
    def __init__(self, not_launched, launching, launched, to_review):
        self.not_launched = str(not_launched)
        self.launching = str(launching)
        self.launched = str(launched)
        self.to_review = str(to_review)

    def __repr__(self):
        return f"<StatusParameters NL={self.not_launched} LCH={self.launching} L={self.launched} TR={self.to_review}>"
