__author__ = 'alireza'

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode, Boolean, Text, NVARCHAR
from database import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship


class AdminUsers(Base):
    __tablename__ = 'AdminUsers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    login = Column(String(80), unique=True)
    email = Column(String(120))
    password = Column(String(400))

    # Flask-Login integration
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

    id = Column(Integer, primary_key=True, index=True)
    # username = Column(Unicode(80), unique=True, index=True)
    username = Column(Unicode(80), index=True)
    password = Column(String(40))
    email = Column(String(120))
    register_date = Column(DateTime)
    last_check = Column(DateTime)
    total_level = Column(Integer)
    shop = Column(Integer)
    score = Column(Integer)
    gold = Column(Integer)
    diamond = Column(Integer)
    chars_bought = Column(Integer)
    is_banned = Column(Boolean)
    wins = Column(Integer)
    last_daily_reward_date = Column(DateTime)
    daily_reward_with_price_count = Column(Integer, default=0)
    daily_reward_with_price_date = Column(DateTime, default=datetime.now())

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


class Level(Base):
    __tablename__ = 'level'

    id = Column(Integer, primary_key=True, index=True)
    time = Column(Integer, index=True)
    level = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

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


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    discount = Column(Integer)
    diamond = Column(Integer)
    price = Column(Integer)
    token = Column(String)
    product_id = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

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

    id = Column(Integer, primary_key=True)
    code = Column(Integer)
    count = Column(Integer)
    validity = Column(Integer)
    diamond_count = Column(Integer)
    username = Column(Unicode)

    # def __init__(self, code, count):
    def __init__(self, code=None, count=None, diamond_count=None):
        self.code = code
        self.validity = 1
        self.count = count
        self.diamond_count = diamond_count

    def __repr__(self):
        return '<Gift_card id %r >' % self.id


class Xmlbase(Base):
    __tablename__ = 'xmlbase'

    id = Column(Integer, primary_key=True)
    xml_code = Column(String(64))
    api_version = Column(String(10))

    # def __init__(self, code, api_version):
    def __init__(self, code=None, api_version=None):
        self.xml_code = code
        self.api_version = api_version

    def __repr__(self):
        return '<Xml_Code id %r >' % self.id


class GameDb(Base):
    __tablename__ = 'gamedb'

    id = Column(Integer, primary_key=True)
    IsInitilized = Column(Integer, default=0, nullable=True)
    ActiveCarLevel_Capacity = Column(Unicode, default=u'1', nullable=True)
    ActiveCarLevelSpeed = Column(Unicode, default=u'1', nullable=True)
    ActiveHeliLevelCapacity = Column(Unicode, default=u'1', nullable=True)
    ActiveHeliLevelSpeed = Column(Unicode, default=u'1', nullable=True)
    ActiveBuilderLevel = Column(Unicode, default=u'1', nullable=True)
    ActiveCar = Column(Unicode, default=u'1', nullable=True)
    ActiveCharecter = Column(Unicode, default=u'0', nullable=True)
    ActiveHeli = Column(String, default=u'1', nullable=True)
    ActivePlantsLevel = Column(Unicode, default=u'1', nullable=True)
    ActiveProductionLevel = Column(Unicode, default=u'1', nullable=True)
    ActiveRepositoryLevel = Column(Unicode, default=u'1', nullable=True)
    Charecters = Column(Unicode, default=u'1,0,0,0,0,0,0,0,0,0,0,0,0,0,0', nullable=True)
    Coins = Column(Unicode, default=u'200', nullable=True)
    CurrentLevel = Column(Unicode, default=u'0', nullable=True)
    Diamonds = Column(Unicode, default=u'5', nullable=True)
    FactoryLevel = Column(Unicode,
                          default=u'T,F,F,T,T,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,T,F,F,'
                          , nullable=True)
    FarmCost = Column(Unicode, default=u'20', nullable=True)
    GiveRate = Column(Unicode, default=u'0', nullable=True)
    LastDayCounter = Column(Unicode, default=u'1', nullable=True)
    LastDayPlayed = Column(Unicode, default=u'-1', nullable=True)
    LastTempLevel = Column(Integer, default=0, nullable=True)
    LevelsStatus = Column(Unicode,
                          default=u'0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,',
                          nullable=True)
    LevelTimeStatus = Column(Unicode,
                             default=u'3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,3599,',
                             nullable=True)
    LevelTutorial1 = Column(Integer, default=0, nullable=True)
    LevelTutorial2 = Column(Integer, default=0, nullable=True)
    LevelTutorial3 = Column(Integer, default=0, nullable=True)
    MainMenuTutorial = Column(Integer, default=0, nullable=True)
    MapTutorial_1 = Column(Integer, default=0, nullable=True)
    MapTutorial_2 = Column(Integer, default=0, nullable=True)
    MusicState = Column(Integer, default=1, nullable=True)
    pickedUpItemDeletionTime = Column(Unicode, default=u'10', nullable=True)
    Prize = Column(Unicode, default=u'1', nullable=True)
    Share = Column(Unicode, default=u'0', nullable=True)
    WorkingTime = Column(Integer, default=u'0', nullable=True)
    EffectState = Column(Integer, default=u'1', nullable=True)
    username = Column(Unicode(80), nullable=True)
    Email = Column(Unicode, nullable=True)
    BuySpecialOffer = Column(Unicode, default=u'0', nullable=True)
    XP = Column(Unicode, default=u'0', nullable=True)
    XpLevel = Column(Unicode, default=u'0', nullable=True)
    XpNextLevel = Column(Unicode, default=u'300', nullable=True)
    Gandoms = Column(Unicode, default=u'200', nullable=True)
    DatabaseRestored = Column(Integer, default=0, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

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
            "DatabaseRestored": self.DatabaseRestored
        }

    def __unicode__(self):
        return self.username


class Special_Packages(Base):
    __tablename__ = 'specialpack'

    id = Column(Integer, primary_key=True)
    product_id = Column(Unicode)
    price = Column(Integer)
    number = Column(Integer)
    coin = Column(Integer)
    diamond = Column(Integer)
    discount_price = Column(Integer)
    character = Column(Boolean)
    discount = Column(Integer)
    gandom = Column(Integer)

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

    id = Column(Integer, primary_key=True)
    product_id = Column(Unicode)
    price = Column(Integer)
    number = Column(Integer)
    diamond = Column(Integer)
    discount = Column(Integer)

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

    id = Column(Integer, primary_key=True)
    version = Column(Unicode)

    def __init__(self, version=None):
        self.version = version

    def __unicode__(self):
        return self.version


'''
class SpecialOffer(Base):
    __tablename__ = 'store'

    id = Column(Integer, primary_key=True)
    cost = Column(String(30))
    discount = Column(String(30))


    def __init__(self, cost=None, discount=None):
        self.cost = cost
        self.discount = discount

    def __unicode__(self):
        return self.cost + ":" + self.discount
'''
