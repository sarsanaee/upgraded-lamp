__author__ = 'alireza'


class gameDbJsonScheme():
    storage = {
        "IsInitilized": "IsInitilized",
        "Active_Car_Level_Capacity": "ActiveCarLevel_Capacity",
        "Active_CaR_Level_Speed": "ActiveCarLevelSpeed",
        "Active_Heli_Level_Capacity": "ActiveHeliLevelCapacity",
        "Active_Heli_Level_Speed": "ActiveHeliLevelSpeed",
        "ActiveBuilderLevel": "ActiveBuilderLevel",
        "ActiveCar": "ActiveCar",
        "ActiveCharecter": "ActiveCharecter",
        "ActiveHeli": "ActiveHeli",
        "LevelTimeStatue": "LevelTimeStatus",
        "Username": "username",
        "id": "user_id",
    }

    keys_to_add = {"ActiveSex": 0,
                   "WomanCharecters": ""}

    def get_correspond(self, key):
        if key in self.storage:
            return self.storage[key]
        return key

    def add_diff_keys(self,json):
        for i in self.keys_to_add.keys():
            if i not in json:
                json[i] = self.keys_to_add[i]
        return json

