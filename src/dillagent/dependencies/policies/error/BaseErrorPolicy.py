class BaseErrorPolicy():
    def __init__(self, policy):
        self.policy = policy
    
    def get_policy(self):
        return self.policy