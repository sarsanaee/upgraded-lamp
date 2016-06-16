# -*- coding: utf-8 -*-
import datetime
import re
from flask import request, abort
from flask import jsonify, json
from Api.database import db_session
from Api.models import User, Level, Transaction, Giftcards, AdminUsers, Store, \
    GameDb, Special_Packages, Api, OnlineServer
from Api.database import init_db, Base
from Api.flask_hmac import Hmac
from flask_admin import Admin
import flask_login as login
from Api.myadmin import UserView, GiftCardView, LevelView, \
    MyAdminIndexView, AdminUsersView, \
    TransactionView, StoreView, GameDbView, SpecialPackView, \
    ApiView, OnlineServerView
from Api.jsonScheme import gameDbJsonScheme
from werkzeug.contrib.cache import SimpleCache
import requests
from Api import app
from flask_cors import CORS

CORS(app)
cache = SimpleCache()
init_db()
hm = Hmac(app)
gameDbSchemeConverter = gameDbJsonScheme()


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, (User, Level, int, str)):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db_session.query(AdminUsers).get(user_id)


init_login()

# it has to be deleted until special amount of time because it is bas for project structure
packages = {"Diamonds_G": 7, "Diamonds_F": 6, "Diamonds_E": 5, "Diamonds_D": 4, "Diamonds_C": 3, "Diamonds_B": 2,
            "Diamonds_A": 1}

admin = Admin(app, name='farm_web_service', index_view=MyAdminIndexView(), base_template='my_master.html')

admin.add_view(UserView(User, db_session))
admin.add_view(LevelView(Level, db_session))
admin.add_view(TransactionView(Transaction, db_session))
admin.add_view(GiftCardView(Giftcards, db_session))
admin.add_view(AdminUsersView(AdminUsers, db_session))
admin.add_view(StoreView(Store, db_session))
admin.add_view(GameDbView(GameDb, db_session))
admin.add_view(SpecialPackView(Special_Packages, db_session))
admin.add_view(ApiView(Api, db_session))
admin.add_view(OnlineServerView(OnlineServer, db_session))


@app.route('/get_time', methods=['POST'])
@hm.check_hmac
def time_server():
    """
    @api {POST} /get_time/ Getting the time of server - Protected
    @apiName time_server
    @apiVersion 0.0.0
    @apiGroup Time


    @apiDescription It generates time of server in UTC.

    @apiSuccess (Success 200) {string} status status of request
    @apiSuccess (Success 200) {time} time    time generated for user

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "200",
            "time": Sun, 22 May 2016 15:00:40 GMT
        }
    """
    time = datetime.datetime.now()
    response = jsonify({'status': '200', 'time': time})
    response.status_code = 200
    return response


@app.route('/v1/get_time', methods=['GET'])
def get_time_server():
    """
    @api {GET} /v1/get_time/ Getting the time of server
    @apiName V1_time_server
    @apiGroup Time
    @apiVersion 0.0.1
    @apiDescription It generates time of server in UTC.

    @apiSuccess (Success 200) {string} status status of request
    @apiSuccess (Success 200) {time} time    time generated for user


    @apiSampleRequest /v1/get_time

        @apiExample cURL example
    $ curl /v1/get_time

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "200",
            "time": Sun, 22 May 2016 15:00:40 GMT
        }
    """
    time = datetime.datetime.now()
    response = jsonify({'status': '200', 'time': time})
    response.status_code = 200
    return response


@app.route('/dailyreward/<int:id>', methods=['GET'])
def daily_reward(id):
    """
    @api {GET} /dailyreward/:id Getting the daily reward of a player
    @apiName daily reward
    @apiGroup Daily Rewards
    @apiVersion 0.0.1

    @apiDescription It generates proper daily reward based on previous daily rewards of player

    @apiParam {int} id Users unique ID.

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "Ok",
        }
    """
    retrieved_user = User.query.filter_by(id=id).first()
    if retrieved_user:
        b = datetime.datetime.now()
        delta = b - retrieved_user.last_daily_reward_date
        if delta.total_seconds() > app.config["DAILY"]:
            retrieved_user.last_daily_reward_date = datetime.datetime.now()
            db_session.commit()
            response = jsonify({"status": "Ok"})
            response.status_code = 200
            return response
        abort(403)
    abort(404)


@app.route('/dailyreward/price/<int:id>', methods=['GET'])
def daily_reward_price(id):
    """
    @api {GET} /dailyreward/price/:id Getting daily reward by money everyday
    @apiName daily reward price
    @apiGroup Daily Rewards
    @apiVersion 0.0.1

    @apiDescription It generates proper daily reward money based on previous daily rewards of player

    @apiParam {int} id Users unique ID.

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "Ok",
            "count": 10
        }
    """
    retrieved_user = User.query.filter_by(id=id).first()
    if retrieved_user:
        b = datetime.datetime.now()
        delta = b - retrieved_user.daily_reward_with_price_date

        if retrieved_user.daily_reward_with_price_count <= 5:
            retrieved_user.daily_reward_with_price_date = datetime.datetime.now()
            retrieved_user.daily_reward_with_price_count = retrieved_user.daily_reward_with_price_count + 1
            db_session.commit()
            response = jsonify({"status": "Ok", "count": retrieved_user.daily_reward_with_price_count})
            response.status_code = 200
            return response

        elif delta.total_seconds() > 86399:
            retrieved_user.daily_reward_with_price_date = datetime.datetime.now()
            retrieved_user.daily_reward_with_price_count = 1
            db_session.commit()
            response = jsonify({"status": "Ok", "count": retrieved_user.daily_reward_with_price_count})
            response.status_code = 200
            return response

        abort(403)
    abort(404)


@app.route('/username/taksos', methods=['POST'])
def get_username_info():
    retrieved_user = User.query.filter_by(username=request.json["username"]).first()
    if retrieved_user:
        response = jsonify({'username':retrieved_user.username ,'id': retrieved_user.id, 'password': retrieved_user.password, 'email': retrieved_user.email})
        response.status_code = 200
        return response
    abort(404)


@app.route('/dailyreward/price/count/<int:id>', methods=['GET'])
def daily_reward_price_count(id):
    """
    @api {GET} /dailyreward/price/count/:id Getting number of daily rewards
    @apiName daily reward price count
    @apiGroup Daily Rewards
    @apiVersion 0.0.1

    @apiDescription This Api returns nubmer of daily rewards that a use has collected
    @apiParam {int} id Users unique ID.

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "Ok",
            "count": 10
        }
    """
    retrieved_user = User.query.filter_by(id=id).first()

    if retrieved_user:
        response = jsonify({"status": "Ok", "count": retrieved_user.daily_reward_with_price_count})
        response.status_code = 200
        return response

    abort(404)


@app.route('/editprofile', methods=['POST'])
@hm.check_hmac
def edit_profile():
    """
    @api {post} /editprofile Editing profile
    @apiName edit_profile
    @apiGroup Profile
    @apiVersion 0.0.1

    @apiDescription Users can edit their profile with this Api
    @apiParam {int} id Users unique ID.
    @apiParam {email} id Users Email.
    @apiParam {password} id Users Password.

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "updated"
        }

    @apiParamExample {json} Request-Example:
    {
        "id": 4711,
        "email": "sarsanaee@gmail.com",
        "password": "password"
    }
    """
    retrieved_user = User.query.filter_by(id=request.json.get('id')).first()
    if retrieved_user:
        retrieved_user.update_profile(request.json.get('email'), request.json.get('password'))
        db_session.commit()
        response = jsonify({'status': 'updated'})
        response.status_code = 200
        return response
    abort(404)


@app.route('/V1/getid', methods=['POST'])
@hm.check_hmac
def get_id():
    """
    @api {post} /V1/getid getting UUID
    @apiName get_id
    @apiGroup Profile
    @apiVersion 0.0.1

    @apiDescription Getting id from unique username
    @apiParam {string} username Users unique Username.

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "200",
            "id": 10
        }

    @apiParamExample {json} Request-Example:
    {
        "username": "sarsanaee"
    }
    """
    if request.json.get('username'):
        retrieved_user = User.query.filter_by(username=request.json.get('username')).first()
        if retrieved_user:
            response = jsonify({'status': '200', 'id': retrieved_user.id})
            response.status_code = 200
            return response
    abort(404)


@app.route('/login', methods=['POST'])
@hm.check_hmac
def login():
    """
    @api {post} /login Authentication
    @apiName login
    @apiGroup Authentication
    @apiVersion 0.0.0

    @apiDescription logging into your account
    @apiParam {string} username Users unique Username.
    @apiParam {string} password Users password.

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "status": "OK",
            "id": 10,
            "email": "sarsanaee@gmail.com",
            "password": "password"
        }

    @apiParamExample {json} Request-Example:
    {
        "username": "sarsanaee",
        "password": "password"
    }
    """
    retrieved_user = User.query.filter_by(username=request.json.get('username')).first()
    if retrieved_user and retrieved_user.password == request.json.get('password'):
        response = jsonify({'status': 'OK',
                            'email': retrieved_user.email,
                            'id': retrieved_user.id,
                            'password': retrieved_user.password})
        response.status_code = 200
        return response
    abort(401)


@app.route('/level_creator', methods=['GET'])
def level_creator():
    for i in range(1, 121):
        from random import randint
        random_number = randint(600, 1500)
        level_t = Level(9, random_number, i)
        db_session.add(level_t)
    db_session.commit()

    response = jsonify({'status': '200'})
    response.status_code = 200
    return response


@app.route('/V2/datacorrector', methods=['GET'])
def datacorrector():
    users = User.query.all()
    #print(users)
    for i in users:
        #print(i.lose)
        #i.is_banned = False
        #i.wins = 0
        i.lose = 0
        #i.last_daily_reward_date = datetime.datetime.now()
        #i.daily_reward_with_price_count = 0
        #i.daily_reward_with_price_date = datetime.datetime.now()
    db_session.commit()
    return "finished"

@app.route('/V2/gamedbcorrector', methods=['GET'])
def gamedbcorrector():
    gamedb = GameDb.query.all()
    for i in gamedb:
        i.ActiveSex = 0
        i.WomanCharecters = ""
    db_session.commit()
    return "finished"



@app.route('/version', methods=['GET'])
def get_last_version():
    """
    @api {get} /version Getting version
    @apiName versions
    @apiGroup General

    @apiDescription getting latest version of the game published in cafebazzar

    @apiSuccess (Success 200) {status} string status of request

    @apiSampleRequest off

    @apiSuccessExample {js} Success-Response:
        HTTP/1.0 200 OK
        {
            "version": "OK",
            "online_status": True
        }
    """
    version = Api.query.first().version
    online = OnlineServer.query.first().status
    response = jsonify({"version": version, "online_status": online})
    response.status_code = 200
    return response


@app.route('/V1/purchase_log', methods=['POST'])
@hm.check_hmac
def client_logs():
    if request.json.get("log"):
        log = request.json.get("log")
        print("Client Log", log)
        token = request.json.get('token')
        if token:
            transaction = db_session.query(Transaction).filter_by(token=token).first()
            if transaction:
                transaction.complete = True
                db_session.commit()
            else:
                print("Complete Purchase in with failed transaction ", token)
    response = jsonify({'status': '200'})
    response.status_code = 200
    return response


@app.route('/gamedb/<int:id>', methods=['GET'])
def get_player_db(id):
    gamedb = GameDb.query.filter_by(user_id=id).first()
    if gamedb:
        response = jsonify(gamedb.to_dict())
        response.status_code = 200
        return response
    abort(404)


@app.route('/allgamedb', methods=['POST'])
@hm.check_hmac
def set_player_all_db():
    gamedb = GameDb.query.filter_by(user_id=request.json["id"]).first()
    if gamedb:
        gamedb.update_data(gameDbSchemeConverter.add_diff_keys(request.json))
        db_session.commit()
        response = jsonify({"status": "updated"})
        response.status_code = 200
    else:
        gamedb = GameDb(request.json)
        db_session.add(gamedb)
        db_session.commit()
        response = jsonify({"status": "created"})
        response.status_code = 201
    return response


@app.route('/collect_statistics', methods=['GET'])
def collect_statistics():
    users = User.query.filter_by().all()
    for i in users:
        i.periodic_win = i.wins
    db_session.commit()
    response = jsonify({"status": "updated"})
    return response


@app.route('/gamedb', methods=['POST'])
@hm.check_hmac
def set_player_db():
    gamedb = GameDb.query.filter_by(user_id=request.json["id"]).first()
    if (gamedb):
        for i in request.json.keys():
            setattr(gamedb, gameDbSchemeConverter.get_correspond(i), request.json[i])
        db_session.commit()
        response = jsonify({"status": "updated"})
        return response
    abort(404)


@app.route('/register', methods=['POST'])
@hm.check_hmac
def register():
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    username_size = len(request.json['username'])
    if username_size < 5 or username_size > 20:
        # abort(411)
        response = jsonify({'status': 1, 'id': ''})
        response_status_code = 200
        return response

    if not email_regex.match(request.json['email']):
        # abort(410)
        response = jsonify({'status': 2, 'id': ''})
        response_status_code = 200
        return response

    retrieved_user = User.query.filter_by(username=request.json['username']).first()
    if retrieved_user:
        response = jsonify({'status': 3, 'id': ''})
        response_status_code = 200
        return response
        # abort(409)
    u = User(request.json['username'], request.json['password'], request.json['email'])

    # generating proper game db for new user
    db_session.add(u)
    db_session.commit()

    new_gamedb = GameDb(None, u.id)  # creating new game db for new user
    new_gamedb.username = u.username
    new_gamedb.Email = u.email
    db_session.add(new_gamedb)
    db_session.commit()

    response = jsonify({'status': 201, 'id': u.id})
    response.status_code = 201
    return response


@app.route('/getmyscore', methods=['POST'])
@hm.check_hmac
def get_my_score():
    username = request.json['username']
    retrieved_user = User.query.filter_by(username=username).first()
    if retrieved_user:
        return jsonify({'score': retrieved_user.score, 'status': 'ok'})
    return jsonify({'status': 'not ok', 'description': 'No User Found'})


@app.route('/finish_level', methods=['POST'])
@hm.check_hmac
def finish_level():
    id = None
    if request.json.get("id"):
        if request.json.get("id").isdigit():
            id = int(request.json.get("id"))
            foreign_key = User.query.filter_by(id=id).first()
        else:
            foreign_key = User.query.filter_by(username=request.json.get("id")).first()

    else:
        username = request.json['username']
        foreign_key = User.query.filter_by(username=username).first()
    time = int(request.json['time'])
    level = int(request.json['level'])
    if foreign_key:
        existence = Level.query.filter(Level.user_id == foreign_key.id, Level.level == level).first()
        if existence:
            if time < existence.time:
                # foreign_key.set_score(59 * 60 + 59 - time)
                foreign_key.update_score(existence.time, time)
                existence.set_time(time)
                foreign_key.recent_access_time()
                db_session.commit()
            else:
                rank = Level.query.filter(Level.time <= int(existence.time),
                                          Level.level == int(existence.level)).count()
                best_time = Level.query.filter_by(level=int(existence.level)) \
                    .order_by(Level.time.asc()).first()
                best_player = User.query.filter_by(id=best_time.user_id).first()
                response = jsonify({'status': '200', 'best_time': best_time.time, 'Rank': rank,
                                    'best_username': best_player.username})
                response.status_code = 200
                return response

        else:
            foreign_key.set_score(59 * 60 + 59 - time)
            new_level = Level(foreign_key.id, time, level)
            foreign_key.total_level += 1
            db_session.add(new_level)
            db_session.commit()

        rank = Level.query.filter(Level.time <= time, Level.level == level).count()
        best_time = Level.query.filter_by(level=level).order_by(Level.time.asc()).first()
        if best_time:
            best_player = User.query.filter_by(id=best_time.user_id).first()
            response = jsonify({'status': '200', 'best_time': best_time.time,
                                'Rank': rank, 'best_username': best_player.username})
            response.status_code = 200
            return response
    abort(404)


@app.route('/top_player_level/level/<int:level>', methods=['POST'])
@hm.check_hmac
def top_player_level(level):
    ret_level = cache.get("first_player_in_level_" + str(level))
    if ret_level is None:
        ret_level = Level.query.filter_by(level=level).order_by(Level.time.asc()).first()
        cache.set("first_player_in_level_" + str(level), ret_level, timeout=5 * 60)
    if ret_level:
        ret_user = User.query.filter_by(id=ret_level.user_id).first()
        if ret_user:
            response = jsonify({'status': '200', 'username': ret_user.username, 'time': ret_level.time})
            response.status_code = 200
            return response
    abort(404)


@app.route('/get_special_offer', methods=['POST'])
@hm.check_hmac
def get_special_offer():
    with open("special_offer.txt", 'r') as f:
        packages = f.read()
        data = packages.split(':')
        response = jsonify({'status': '200', 'cost': data[0], 'discount': data[1], 'final': data[2], 'coin': data[3]})
        response.status_code = 200
        return response


@app.route('/score_corrector', methods=['GET'])
def score_corrector():
    users = User.query.filter_by().all()
    for i in users:
        levels = Level.query.filter(Level.user_id == i.id).all()
        if levels:
            sum = 0
            for j in levels:
                sum = sum + 59 * 60 + 59 - j.time
            i.score = 431880 - sum
    db_session.commit()
    response = jsonify({'status': '200'})
    response.status_code = 200
    return response


@app.route('/levelsStauts/', methods=['POST'])
@hm.check_hmac
def levels_stauts():
    id = None
    if request.json.get("id"):
        if request.json.get("id").isdigit():
            id = int(request.json.get("id"))
            retrieved_user = User.query.filter_by(id=id).first()
        else:
            retrieved_user = User.query.filter_by(username=request.json.get("id")).first()
    else:
        username = request.json['username']
        retrieved_user = User.query.filter_by(username=username).first()
    if retrieved_user:
        retrieved_info = Level.query.filter_by(user_id=retrieved_user.id).all()
        levels = []
        scores = []
        for i in retrieved_info:
            levels.append(i.level)
            scores.append(i.time)
        levels = json.dumps(levels)
        scores = json.dumps(scores)
        response = jsonify({'status': '200', 'levels': levels, 'scores': scores})
        response.status_code = 200
        return response
    abort(404)


@app.route('/updateMylevels', methods=['POST'])
@hm.check_hmac
def updatemylevels():
    id = None
    if request.json.get("id"):
        if request.json.get("id")[0].isdigit():
            id = int(request.json.get("id")[0])
            retrieved_user = User.query.filter_by(id=id).first()
        else:
            retrieved_user = User.query.filter_by(username=request.json.get("id")[0]).first()

    else:
        username = request.json['username'][0]
        retrieved_user = User.query.filter_by(username=username).first()

    levels = request.json['levels']
    times = request.json['times']

    for i in range(len(levels)):
        time = int(times[i])
        level = int(levels[i])
        instance = db_session.query(Level).filter(Level.user_id == retrieved_user.id, Level.level == level). \
            first()
        if instance:
            retrieved_user.update_score(instance.time, time)
            instance.time = time
        else:
            new_level = Level(retrieved_user.id, time, level)
            retrieved_user.set_score(59 * 60 + 59 - time)
            retrieved_user.total_level += 1
            db_session.add(new_level)

    db_session.commit()
    response = jsonify({'status': '201'})
    response.status_code = 201
    return response


@app.route('/getStore', methods=['POST'])
@hm.check_hmac
def get_store():
    store = cache.get('store')
    version = cache.get('version')
    if store is None and version is None:
        store = db_session.query(Store).all()
        version = Api.query.first().version
        cache.set('store', store, timeout=5 * 60)
        cache.set('version', version, timeout=5 * 60)
    store = db_session.query(Store).all()
    message = ''
    for i in store:
        message += str(i.number) + ':' + str(i.price) + ":" + str(i.diamond) + ":" + str(i.discount) + '\n'
    message = message[:len(message) - 1]
    response = jsonify({"status": "200", 'store': message, 'version': version})
    response.status_code = 200
    return response


@app.route('/get_player_overall_rank/<int:level>', methods=['POST'])
@hm.check_hmac
def get_player_overall_rank(level):
    id = None
    if request.json.get("id"):
        if request.json.get("id").isdigit():
            id = int(request.json.get("id"))
            user_requester = User.query.filter_by(id=id).first()
        else:
            user_requester = User.query.filter_by(username=request.json.get("id")).first()

    else:
        username = request.json['username']
        user_requester = User.query.filter_by(username=username).first()

    if user_requester:
        rank = User.query.filter(User.score < user_requester.score).count() + 1
        user_level_status = Level.query.filter(Level.user_id == user_requester.id, Level.level == level).first()
        if user_level_status:
            in_level_ranking = Level.query.filter(Level.time < user_level_status.time, Level.level == level).count() + 1
            response = jsonify({"status": "200", 'levelRank': in_level_ranking, 'GlobalRank': rank})
            response.status_code = 200
            return response
    abort(404)


@app.route('/valid_giftcard', methods=['POST'])
@hm.check_hmac
def valid_giftcard():
    try:
        gift_code = int(request.json['gift_code'])
    except:
        abort(404)
    gift_ret = Giftcards.query.filter_by(code=gift_code).first()
    if gift_ret and gift_ret.validity:
        if gift_ret.username:
            if gift_ret.username == request.json['username']:
                gift_ret.count -= 1
                if gift_ret.count == 0:
                    gift_ret.validity = 0
            else:
                abort(403)
        else:
            gift_ret.count -= 1
            gift_ret.username = request.json['username']
            if gift_ret.count == 0:
                gift_ret.validity = 0


        db_session.commit()
        response = jsonify({"status": "200", 'count': gift_ret.diamond_count})
        response.status_code = 200
        return response
    abort(404)


@app.route('/set_character_bought', methods=['POST'])
@hm.check_hmac
def set_char_bought():
    character_count = request.json['char_numbers']
    id = None
    if request.json.get("id"):
        if request.json.get("id").isdigit():
            id = int(request.json.get("id"))
            user = db_session.query(User).filter_by(id=id).first()
        else:
            user = User.query.filter_by(username=request.json.get("id")).first()


    else:
        username = request.json['username']
        user = User.query.filter_by(username=username).first()

    if user:
        user.chars = character_count
        db_session.commit()
        response = jsonify({"status": "200"})
        response.status_code = 200
        return response
    abort(404)


@app.route('/wins/<int:id>', methods=['GET'])
def wins_number(id):
    retrieved_user = User.query.filter_by(id=id).first()
    if retrieved_user:
        response = jsonify({"status": "OK", "wins": retrieved_user.wins})
        response.status_code = 200
        return response
    abort(404)


@app.route('/wins/taksossharamje', methods=['POST'])
def win_game():
    retrieved_user_winner = User.query.filter_by(username=request.json["winner"]).first()
    retrieved_user_looser = User.query.filter_by(username=request.json["looser"]).first()
    if retrieved_user_winner and retrieved_user_looser:
        retrieved_user_winner.win()
        retrieved_user_looser.lose_game()
        db_session.commit()
        response = jsonify({"status": "Ok"})
        response.status_code = 201
        return response
    abort(404)


@app.route('/special_package', methods=['GET'])
def get_special_package():
    packages = Special_Packages.query.all()
    packages_list = []
    for i in packages:
        packages_list.append(i.to_dict())
    response = jsonify({"packages": packages_list})
    response.status_code = 200
    return response


@app.route('/set_gold_diamond/<int:gold>/<int:diamond>', methods=['POST'])
@hm.check_hmac
def set_gold_diamond(gold, diamond):
    id = None
    if request.json.get("id"):
        if request.json.get("id").isdigit():
            id = int(request.json.get("id"))
            retrieved_user = User.query.filter_by(id=id).first()
        else:
            retrieved_user = User.query.filter_by(username=request.json.get("id")).first()

    else:
        username = request.json['username']
        retrieved_user = User.query.filter_by(username=username).first()

    if retrieved_user:
        retrieved_user.set_gold_diamond(int(gold), int(diamond))
        retrieved_user.recent_access_time()
        db_session.commit()
        response = jsonify({"status": "200"})
        response.status_code = 200
        return response
    abort(404)


@app.route('/V1/get_rank/level/<int:user_level>/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_rank_v1(user_level, offset):
    a = db_session.query(User, Level).join(Level).add_columns(User.score, Level.level, Level.time, User.username). \
        filter(Level.level == user_level).order_by(Level.time.asc()).all()  # TODO: this function must be cached

    if request.json.get("id").isdigit():
        id = int(request.json.get("id"))
        current_user = db_session.query(User).filter_by(id=id).first()
    else:
        current_user = User.query.filter_by(username=request.json.get("id")).first()

    if current_user:
        index = 0
        for i in a:
            if i[0].id == current_user.id:
                break
            index += 1
        start_index = 0
        if index - offset > 0:
            start_index = index - offset
        end_index = len(a) - 1
        if index + offset < end_index:
            end_index = index + offset
        usernames_list = []
        time_list = []

        for i in range(start_index, end_index + 1):
            usernames_list.append(a[i][5])
            time_list.append(a[i][4])

        # anar = json.dumps(usernames_list, cls=SetEncoder, ensure_ascii=False)
        response = jsonify(
            {'status': '200', 'username': usernames_list, 'scores': time_list, 'index': index - start_index,
             'rank': index + 1})
        response.status_code = 200
        return response
    abort(404)


@app.route('/get_rank/level/<int:user_level>/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_rank(user_level, offset):
    a = db_session.query(User, Level).join(Level).add_columns(User.score, Level.level, Level.time, User.username). \
        filter(Level.level == user_level).order_by(Level.time.asc()).all()  # TODO: this function must be cached

    username = request.json['username']
    current_user = db_session.query(User).filter_by(username=username).first()

    if current_user:
        index = 0
        for i in a:
            if i[0].id == current_user.id:
                break
            index += 1
        start_index = 0
        if index - offset > 0:
            start_index = index - offset
        end_index = len(a) - 1
        if index + offset < end_index:
            end_index = index + offset
        usernames_list = []
        time_list = []

        for i in range(start_index, end_index + 1):
            usernames_list.append(a[i][5])
            time_list.append(a[i][4])

        # anar = json.dumps(usernames_list, cls=SetEncoder, ensure_ascii=False)
        anar = json.dumps(usernames_list, ensure_ascii=False)
        response = jsonify({'status': '200', 'username': anar, 'scores': time_list, 'index': index - start_index,
                            'rank': index + 1})
        response.status_code = 200
        return response
    abort(404)


@app.route('/get_rank/score/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_score(offset):
    player = db_session.query(User).filter_by().order_by(
        User.score.asc()).all()  ## TODO: this function must be cached

    username = request.json.get("username")
    current_user = db_session.query(User).filter_by(username=username).first()

    if current_user:
        index = 0
        for i in player:
            if i.id == current_user.id:
                break
            index += 1
        start_index = 0
        if index - offset > 0:
            start_index = index - offset
        end_index = len(player) - 1
        if index + offset < end_index:
            end_index = index + offset

        usernames_list = []
        scores_list = []

        for i in range(start_index, end_index + 1):
            temp_username = player[
                i].username  # if all(ord(c) < 128 for c in player[i].username) else player[i].username[::-1]
            usernames_list.append(temp_username)
            scores_list.append(431880 - player[i].score)

        converted_usernames_list = json.dumps(usernames_list, cls=SetEncoder, ensure_ascii=False)
        response = jsonify({'status': '200', 'username': converted_usernames_list,
                            'scores': scores_list,
                            'rank': index + 1, 'index': index - start_index})
        response.status_code = 200
        return response
    abort(404)


@app.route('/V1/get_rank/score/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_score_v1(offset):
    player = db_session.query(User).filter_by().order_by(
        User.score.asc()).all()  ## TODO: this function must be cached

    if request.json.get("id").isdigit():
        id = int(request.json.get("id"))
        current_user = db_session.query(User).filter_by(id=id).first()
    else:
        current_user = User.query.filter_by(username=request.json.get("id")).first()

    if current_user:
        index = 0
        for i in player:
            if i.id == current_user.id:
                break
            index += 1
        start_index = 0
        if index - offset > 0:
            start_index = index - offset
        end_index = len(player) - 1
        if index + offset < end_index:
            end_index = index + offset

        usernames_list = []
        scores_list = []

        for i in range(start_index, end_index + 1):
            temp_username = player[
                i].username  # if all(ord(c) < 128 for c in player[i].username) else player[i].username[::-1]
            usernames_list.append(temp_username)
            scores_list.append(431880 - player[i].score)


        # converted_usernames_list = json.dumps(usernames_list)#, ensure_ascii=False)
        response = jsonify({'status': '200', 'username': usernames_list,  # converted_usernames_list,
                            'scores': scores_list,
                            'rank': index + 1, 'index': index - start_index})
        response.status_code = 200
        return response
    abort(404)


@app.route('/v1/validate_transaction', methods=['POST'])
#@hm.check_hmac
def v1_validate_transaction():
    product_id = request.json["product_id"]
    purchase_token = request.json["purchase_token"]
    request_validate = cafebazaar_send_validation_request(product_id, purchase_token)
    is_repeated_token = db_session.query(Transaction).filter_by(token=purchase_token).all()
    result = request_validate and len(is_repeated_token) == 0
    if result:
        store_product_ids = db_session.query(Store.product_id).all()
        special_packages_product_ids = db_session.query(Special_Packages.product_id).all()
        user = db_session.query(User).filter_by(id=request.json.get("id")).first()
        for i in store_product_ids:
            if product_id in i:
                store = Store.query.filter_by(product_id=product_id).first()
                transaction = Transaction(request.json.get("id"), store.discount, store.diamond, store.price,
                                          purchase_token, product_id)

                if user:
                    user.shopping(store.price, store.discount)
                db_session.add(transaction)
                break
        for i in special_packages_product_ids:
            if product_id in i:
                special_packages = Special_Packages.query.filter_by(product_id=product_id).first()
                transaction = Transaction(request.json.get("id"), special_packages.discount, special_packages.diamond,
                                          special_packages.price, purchase_token, product_id)
                if user:
                    user.shopping(special_packages.price, special_packages.discount)
                db_session.add(transaction)
                break
        db_session.commit()
    print(result, product_id, purchase_token)
    response = jsonify({"status": result})
    response.status_code = 200
    return response


@app.route('/validate_transaction', methods=['POST'])
@hm.check_hmac
def v0_validation():
    try:
        product_id = request.json["product_id"]
        purchase_token = request.json["purchase_token"]
        print("token Rec", product_id, purchase_token)
        id = None
        if request.json.get("id"):
            if request.json.get("id").isdigit():
                id = int(request.json.get("id"))
        request_validate = -1
        for i in range(3):
            request_validate = cafebazaar_send_validation_request(product_id, purchase_token)
            if request_validate != -1:
                break

        if request_validate:
            if packages.has_key(product_id):
                store = Store.query.filter_by(number=packages[product_id]).first()
                retrieved_user = None
                if id:
                    retrieved_user = User.query.filter_by(id=id).first()
                    if not retrieved_user:
                        retrieved_user = User.query.filter_by(username="aghaxoo").first()

                else:
                    retrieved_user = User.query.filter_by(username="aghaxoo").first()

                if retrieved_user:
                    retrieved_user.shopping(store.price)
                    retrieved_user.recent_access_time()
                    diamond = store.diamond
                    retrieved_user.buy_gold_diamond(diamond)
                    transaction = Transaction(retrieved_user.id, store.discount, diamond, store.price, purchase_token,
                                              product_id)
                    db_session.add(transaction)
                    db_session.commit()
            else:
                retrieved_user = None
                if id:
                    retrieved_user = User.query.filter_by(id=id).first()

                else:
                    retrieved_user = User.query.filter_by(username="aghaxoo").first()

                if retrieved_user:
                    retrieved_user.shopping(25000)
                    retrieved_user.recent_access_time()
                    diamond = 0
                    retrieved_user.buy_gold_diamond(diamond)
                    transaction = Transaction(retrieved_user.id, 0, diamond, 25000, purchase_token, product_id)
                    db_session.add(transaction)
                    db_session.commit()
        response = jsonify({"status": request_validate})
        response.status_code = 200
        return response

    except:
        print("database insertion broken")
        abort(500)


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def cafebazaar_refresh_auth():
    r = requests.post("https://pardakht.cafebazaar.ir/auth/token/", data={
        'grant_type': "refresh_token",
        'client_id': "YBOUKMX8lkn15zJUSRMDLECpMlO0nJjhuH8keG3Q",
        'client_secret': "JXd7jpqluUCqfpMX9ZxyrKTT2htA5NqAtdACyXgSW91p8eJXDbauZoDonyk2",
        'refresh_token': "8KkfCgsd0BqS7TqG4PNaDT3eQ6gKQR"
    }, verify=False)
    return json.loads(r.text)["access_token"]


# @celery.task(name='req')
def cafebazaar_send_validation_request(product_id, purchase_token):
    '''
    bazzar_access_token = cafebazaar_refresh_auth()
    url = "https://pardakht.cafebazaar.ir/devapi/v2/api/validate/" + \
          "com.ElmoGame.Farmuler/inapp/" + str(product_id) + "/purchases/" + \
          str(purchase_token) + "/?access_token={access_token}" \
              .format(access_token=bazzar_access_token)
    '''

    while True:
        bazzar_access_token = cafebazaar_refresh_auth()
        url = "https://pardakht.cafebazaar.ir/devapi/v2/api/validate/" + \
          "com.ElmoGame.Farmuler/inapp/" + str(product_id) + "/purchases/" + \
          str(purchase_token) + "/?access_token={access_token}" \
              .format(access_token=bazzar_access_token)
        r = requests.get(url, verify=False)
        return_json = json.loads(r.text)
        print("Cafe Answer ", return_json)
        if(return_json.get('error') != 'invalid_credentials'):
            break

    #r = requests.get(url, verify=False)
    #return_json = json.loads(r.text)



    result = r.status_code == 200 and return_json.get('error') is None
    return result


'''
if __name__ == '__main__':
    app.debug = True
    #manager.run()
    app.run(host='0.0.0.0', port=6789)

'''
