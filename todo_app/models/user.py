class User:
    def __init__(self, id,  username="", email="", password="", created_at=""):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        created_at = created_at


    @classmethod
    #create user object from directory data
    def from_dict(cls, data_tuple):
        return cls(
            id=data_tuple[0],
            username=data_tuple[1],
            password=data_tuple[2],
            created_at=data_tuple[3],
        )

        
    #convert user to dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            # "password": self.password
            }

            