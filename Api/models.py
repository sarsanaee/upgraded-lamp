from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.orm import relationship

from Api.database import Base


class AdminUsers(Base):
    __tablename__ = 'AdminUsers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    first_name = sqlalchemy.Column(sqlalchemy.String(100))
    last_name = sqlalchemy.Column(sqlalchemy.String(100))
    login = sqlalchemy.Column(sqlalchemy.String(80), unique=True)
    email = sqlalchemy.Column(sqlalchemy.String(120))
    password = sqlalchemy.Column(sqlalchemy.String(400))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return u'self.first_name'


class User(Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    # username = Column(Unicode(80), unique=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.Unicode(80), index=True)
    password = sqlalchemy.Column(sqlalchemy.String(40))
    email = sqlalchemy.Column(sqlalchemy.String(120))
    register_date = sqlalchemy.Column(sqlalchemy.DateTime)
    last_check = sqlalchemy.Column(sqlalchemy.DateTime)
    total_level = sqlalchemy.Column(sqlalchemy.Integer)
    shop = sqlalchemy.Column(sqlalchemy.Integer)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    gold = sqlalchemy.Column(sqlalchemy.Integer)
    diamond = sqlalchemy.Column(sqlalchemy.Integer)
    chars_bought = sqlalchemy.Column(sqlalchemy.Integer)
    is_banned = sqlalchemy.Column(sqlalchemy.Boolean)
    wins = sqlalchemy.Column(sqlalchemy.Integer)
    last_daily_reward_date = sqlalchemy.Column(sqlalchemy.DateTime)
    daily_reward_with_price_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    daily_reward_with_price_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())

    status = relationship('Level', backref='users',
                          lazy='dynamic')
    trans = relationship('Transaction', backref='users',
                         lazy='dynamic')
    gamedb = relationship('GameDb', backref='users',
                          lazy='dynamic')

    def __init__(self, username=None, password=None, email=None):
        self.username = username
        self.email = email
        self.password = password
        self.register_date = datetime.now()
        self.last_check = datetime.now()
        self.total_level = 1
        self.gold = 0
        self.diamond = 0
        self.shop = 0
        self.score = (59 * 60 + 59) * 120
        self.chars_bought = 0
        self.wins = 0
        self.is_banned = False
        self.last_daily_reward_date = datetime.now() - timedelta(hours=4)

    def recent_access_time(self):
        self.last_check = datetime.now()

    def shopping(self, amount):
        self.shop = self.shop + amount

    def set_gold(self, gold):
        self.gold = gold

    def set_diamond(self, diamond):
        self.diamond = diamond

    def set_gold_diamond(self, gold, diamond):
        self.diamond = diamond
        self.gold = gold

    def buy_gold_diamond(self, diamond):
        self.diamond = self.diamond + diamond

    def set_score(self, level_time):
        self.score = self.score - level_time

    def update_score(self, previous_time, time):
        self.score = self.score - previous_time + time

    def win(self):
        if self.wins is not None:
            self.wins += 1
        else:
            self.wins = 1

    def update_profile(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
         return self.username if all(ord(c) < 128 for c in self.username) else self.username[::-1]

    def __unicode__(self):
        return self.username


class Level(Base):
    __tablename__ = 'level'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    time = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    level = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

    __mapper_args__ = \
        {
            "order_by": time
        }

    def __init__(self, id, time=None, level=None):
        self.time = time
        self.level = level
        self.user_id = id

    def set_time(self, time):
        self.time = time

    def __repr__(self):
        return '%r' % self.id

class OnlineServer(Base):
    __tablename__ = 'online_server'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    status = sqlalchemy.Column(sqlalchemy.Boolean)

    def __init__(self, status=None):
        self.status = status

    def __repr__(self):
        return '%r' % self.id


class Transaction(Base):
    __tablename__ = 'transaction'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    discount = sqlalchemy.Column(sqlalchemy.Integer)
    diamond = sqlalchemy.Column(sqlalchemy.Integer)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    token = sqlalchemy.Column(sqlalchemy.String)
    product_id = sqlalchemy.Column(sqlalchemy.String)
    complete = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))


    # def __init__(self, id, discount, diamond, price):
    def __init__(self, id=None, discount=None, diamond=None, price=None, token=None, product_id=None):
        self.date = datetime.now()
        self.price = price
        self.discount = discount
        self.user_id = id
        self.diamond = diamond
        self.token = token
        self.product_id = product_id

    def __repr__(self):
        return '<Transaction id %r >' % self.id


class Giftcards(Base):
    __tablename__ = 'giftcard'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.Integer)
    count = sqlalchemy.Column(sqlalchemy.Integer)
    validity = sqlalchemy.Column(sqlalchemy.Integer)
    diamond_count = sqlalchemy.Column(sqlalchemy.Integer)
    username = sqlalchemy.Column(sqlalchemy.Unicode)

    def __init__(self, code=None, count=None, diamond_count=None):
        self.code = code
        self.validity = 1
        self.count = count
        self.diamond_count = diamond_count

    def __repr__(self):
        return '<Gift_card id %r >' % self.id


class GameDb(Base):
    __tablename__ = 'gamedb'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    IsInitilized = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    ActiveCarLevel_Capacity = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveCarLevelSpeed = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveHeliLevelCapacity = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveHeliLevelSpeed = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveBuilderLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveCar = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveCharecter = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    ActiveHeli = sqlalchemy.Column(sqlalchemy.String, default=u'1', nullable=True)
    ActivePlantsLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveProductionLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    ActiveRepositoryLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    Charecters = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1,0,0,0,0,0,0,0,0,0,0,0,0,0,0', nullable=True)
    Coins = sqlalchemy.Column(sqlalchemy.Unicode, default=u'200', nullable=True)
    CurrentLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    Diamonds = sqlalchemy.Column(sqlalchemy.Unicode, default=u'5', nullable=True)
    FactoryLevel = sqlalchemy.Column(sqlalchemy.Unicode,
                                     default=u'T,F,F,T,T,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,',
                                     nullable=True)
    FarmCost = sqlalchemy.Column(sqlalchemy.Unicode, default=u'20', nullable=True)
    GiveRate = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    LastDayCounter = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    LastDayPlayed = sqlalchemy.Column(sqlalchemy.Unicode, default=u'-1', nullable=True)
    LastTempLevel = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    LevelsStatus = sqlalchemy.Column(sqlalchemy.Unicode,
                                     default=u'0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,',
                                     nullable=True)
    LevelTimeStatus = sqlalchemy.Column(sqlalchemy.Unicode,
                                        default=u'3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,',
                                        nullable=True)
    LevelTutorial1 = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    LevelTutorial2 = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    LevelTutorial3 = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    MainMenuTutorial = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    MapTutorial_1 = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    MapTutorial_2 = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    MusicState = sqlalchemy.Column(sqlalchemy.Integer, default=1, nullable=True)
    pickedUpItemDeletionTime = sqlalchemy.Column(sqlalchemy.Unicode, default=u'10', nullable=True)
    Prize = sqlalchemy.Column(sqlalchemy.Unicode, default=u'1', nullable=True)
    Share = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    WorkingTime = sqlalchemy.Column(sqlalchemy.Integer, default=u'0', nullable=True)
    EffectState = sqlalchemy.Column(sqlalchemy.Integer, default=u'1', nullable=True)
    username = sqlalchemy.Column(sqlalchemy.Unicode(80), nullable=True)
    Email = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
    BuySpecialOffer = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    XP = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    XpLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'0', nullable=True)
    XpNextLevel = sqlalchemy.Column(sqlalchemy.Unicode, default=u'300', nullable=True)
    Gandoms = sqlalchemy.Column(sqlalchemy.Unicode, default=u'200', nullable=True)
    DatabaseRestored = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    LevelTutorial_Online = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    MapTutorial_Online = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    MainMenuTutorial_Online = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    FactoryBuy = sqlalchemy.Column(sqlalchemy.Unicode,
                                   default='FTFFFFFFFFFFFFFFFFFFFFF',
                                   nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))


    __mapper_args__ = \
        {
            "order_by": id
        }

    def __init__(self, json=None, user_id=None):
        if json:
            self.IsInitilized = json["IsInitilized"]
            self.ActiveCarLevel_Capacity = json['Active_Car_Level_Capacity']
            self.ActiveCarLevelSpeed = json['Active_CaR_Level_Speed']
            self.ActiveHeliLevelCapacity = json['Active_Heli_Level_Capacity']
            self.ActiveHeliLevelSpeed = json['Active_Heli_Level_Speed']
            self.ActiveBuilderLevel = json['ActiveBuilderLevel']
            self.ActiveCar = json['ActiveCar']
            self.ActiveCharecter = json['ActiveCharecter']
            self.ActiveHeli = json['ActiveHeli']
            self.ActivePlantsLevel = json['ActivePlantsLevel']
            self.ActiveProductionLevel = json['ActiveProductionLevel']
            self.ActiveRepositoryLevel = json['ActiveRepositoryLevel']
            self.Coins = json['Coins']
            self.CurrentLevel = json['CurrentLevel']
            self.Diamonds = json['Diamonds']
            self.FactoryLevel = json['FactoryLevel']
            self.FarmCost = json['FarmCost']
            self.GiveRate = json['GiveRate']
            self.LastDayPlayed = json['LastDayPlayed']
            self.LastDayCounter = json['LastDayCounter']
            self.LastTempLevel = json['LastTempLevel']
            self.LevelsStatus = json['LevelsStatus']
            self.LevelTimeStatus = json['LevelTimeStatue']
            self.LevelTutorial1 = json['LevelTutorial1']
            self.LevelTutorial2 = json['LevelTutorial2']
            self.LevelTutorial3 = json['LevelTutorial3']
            self.MainMenuTutorial = json['MainMenuTutorial']
            self.MapTutorial_1 = json['MapTutorial_1']
            self.MapTutorial_2 = json['MapTutorial_2']
            self.MusicState = json['MusicState']
            self.pickedUpItemDeletionTime = json['pickedUpItemDeletionTime']
            self.Prize = json['Prize']
            self.Share = json['Share']
            self.BuySpecialOffer = json["BuySpecialOffer"]
            self.WorkingTime = json['WorkingTime']
            self.EffectState = json["EffectState"]
            self.Email = json["Email"]
            self.username = json["Username"]
            self.user_id = json["id"]
            self.Gandoms = json["Gandoms"]
            self.XP = json["XP"]
            self.XpLevel = json["XpLevel"]
            self.XpNextLevel = json["XpNextLevel"]
            self.Charecters = json["Charecters"]
            self.DatabaseRestored = json["DatabaseRestored"]
            self.LevelTutorial_Online = json["LevelTutorial_Online"]
            self.MapTutorial_Online = json["MapTutorial_Online"]
            self.MainMenuTutorial_Online = json["MainMenuTutorial_Online"]
            self.FactoryBuy = json["FactoryBuy"]
        else:
            self.user_id = user_id

    def update_data(self, json):
        self.__init__(json)

    def to_dict(self):
        return {
            "IsInitilized": self.IsInitilized,
            "Active_Car_Level_Capacity": self.ActiveCarLevel_Capacity,
            "Active_CaR_Level_Speed": self.ActiveCarLevelSpeed,
            "Active_Heli_Level_Capacity": self.ActiveHeliLevelCapacity,
            "Active_Heli_Level_Speed": self.ActiveHeliLevelSpeed,
            "ActiveBuilderLevel": self.ActiveBuilderLevel,
            "ActiveCar": self.ActiveCar,
            "ActiveCharecter": self.ActiveCharecter,
            "ActiveHeli": self.ActiveHeli,
            "ActivePlantsLevel": self.ActivePlantsLevel,
            "ActiveProductionLevel": self.ActiveProductionLevel,
            "ActiveRepositoryLevel": self.ActiveRepositoryLevel,
            "Charecters": self.Charecters,
            "Coins": self.Coins,
            "CurrentLevel": self.CurrentLevel,
            "Diamonds": self.Diamonds,
            "FactoryLevel": self.FactoryLevel,
            "FarmCost": self.FarmCost,
            "GiveRate": self.GiveRate,
            "LastDayPlayed": self.LastDayPlayed,
            "LastDayCounter": self.LastDayCounter,
            "LastTempLevel": self.LastTempLevel,
            "LevelsStatus": self.LevelsStatus,
            "LevelTimeStatue": self.LevelTimeStatus,
            "LevelTutorial1": self.LevelTutorial1,
            "LevelTutorial2": self.LevelTutorial2,
            "LevelTutorial3": self.LevelTutorial3,
            "MainMenuTutorial": self.MainMenuTutorial,
            "MapTutorial_1": self.MapTutorial_1,
            "MapTutorial_2": self.MapTutorial_2,
            "pickedUpItemDeletionTime": self.pickedUpItemDeletionTime,
            "Prize": self.Prize,
            "Share": self.Share,
            "WorkingTime": self.WorkingTime,  #
            "EffectState": self.EffectState,
            "Email": self.Email,
            "BuySpecialOffer": self.BuySpecialOffer,
            "Username": self.username,
            "id": self.user_id,
            "Gandoms": self.Gandoms,
            "XP": self.XP,
            "XpLevel": self.XpLevel,
            "XpNextLevel": self.XpNextLevel,
            "MusicState": self.MusicState,
            "DatabaseRestored": self.DatabaseRestored,
            "LevelTutorial_Online": self.LevelTutorial_Online,
            "MapTutorial_Online": self.MapTutorial_Online,
            "MainMenuTutorial_Online": self.MainMenuTutorial_Online,
            "FactoryBuy": self.FactoryBuy
        }

    def __unicode__(self):
        return self.username



class Special_Packages(Base):
    __tablename__ = 'specialpack'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    product_id = sqlalchemy.Column(sqlalchemy.Unicode)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    coin = sqlalchemy.Column(sqlalchemy.Integer)
    diamond = sqlalchemy.Column(sqlalchemy.Integer)
    discount_price = sqlalchemy.Column(sqlalchemy.Integer)
    character = sqlalchemy.Column(sqlalchemy.Boolean)
    discount = sqlalchemy.Column(sqlalchemy.Integer)
    gandom = sqlalchemy.Column(sqlalchemy.Integer)

    __mapper_args__ = \
        {
            "order_by": id
        }

    def __init__(self,
                 number=None,
                 price=None,
                 diamond=None,
                 discount=None,
                 product_id=None,
                 character=None,
                 gandom=None,
                 discount_price=None,
                 coin=None):
        self.number = number
        self.product_id = product_id
        self.price = price
        self.diamond = diamond
        self.discount = discount
        self.character = character
        self.coin = coin
        self.discount_price = discount_price
        self.gandom = gandom

    def to_dict(self):
        return {
            "number": self.number,
            "product_id": self.product_id,
            "price": self.price,
            "diamond": self.diamond,
            "discount": self.discount,
            "character": self.character,
            "coin": self.coin,
            "discount_price": self.discount_price,
            "gandom": self.gandom

        }

    def __unicode__(self):
        return self.product_id


class Store(Base):
    __tablename__ = 'store'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    product_id = sqlalchemy.Column(sqlalchemy.Unicode)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    diamond = sqlalchemy.Column(sqlalchemy.Integer)
    discount = sqlalchemy.Column(sqlalchemy.Integer)

    __mapper_args__ = \
        {
            "order_by": id
        }

    def __init__(self, number=None, price=None, diamond=None, discount=None, product_id=None):
        self.number = number
        self.price = price
        self.diamond = diamond
        self.discount = discount
        self.product_id = product_id

    def __unicode__(self):
        return self.number


class Api(Base):
    __tablename__ = 'api'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    version = sqlalchemy.Column(sqlalchemy.Unicode)

    def __init__(self, version=None):
        self.version = version

    def __unicode__(self):
        return self.version
