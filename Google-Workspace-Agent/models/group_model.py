from datetime import datetime
from bson import ObjectId

class GroupModel:
    def __init__(self, db):
        self.collection = db.groups

    def create_group(self, name, members, user_id):
        group = {
            "name": name,
            "members": members,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(group)
        return str(result.inserted_id)

    def get_groups(self, user_id):
        groups = list(self.collection.find({"user_id": user_id}))
        for g in groups:
            g["_id"] = str(g["_id"])
        return groups

    def delete_group(self, group_id, user_id):
        return self.collection.delete_one({
            "_id": ObjectId(group_id),
            "user_id": user_id
        })