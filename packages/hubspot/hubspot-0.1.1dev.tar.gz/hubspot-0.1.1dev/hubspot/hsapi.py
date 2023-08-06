class HSApi:

    def __init__(self, parent):
        self.credentials = parent

    def add_authentication(self, params):
        params[self.credentials.authorization] = self.credentials.auth_value

        return params
