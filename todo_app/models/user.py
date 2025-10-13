class User:
    def __init__(self, id, username="", email="", password="", created_at=""):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at


    @classmethod
    #create user object from directory data
    def from_dict(cls, data_dict):
        return cls(
            id=data_dict.get('id'),
            username=data_dict.get('username'),
            email=data_dict.get('email'),
            created_at=data_dict.get('created_at')
        )

        
    #convert user to dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            # "password": self.password
            }

            