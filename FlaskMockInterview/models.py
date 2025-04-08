

class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password  # Would be hashed in production
        self.resume = ""
        self.preferences = {}
        self.skills = []

class Interview:
    def __init__(self, user_email, job_role, interview_type, difficulty, duration):
        self.user_email = user_email
        self.job_role = job_role
        self.interview_type = interview_type
        self.difficulty = difficulty
        self.duration = duration
        self.timestamp = 0
        self.questions = []
        self.answers = {}
        self.feedback = {}
        self.score = 0
