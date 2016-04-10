# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from database import db_session
from models import User, Level, Transaction, Xmlbase, Giftcards, AdminUsers, Store, \
    GameDb, Special_Packages, Api
from database import init_db, Base
from flask import jsonify, json
from flask_hmac import Hmac
import datetime
import re
from celery import Celery
from flask_admin import Admin
from flask.ext import login
from myadmin import UserView, GiftCardView, LevelView, \
    MyAdminIndexView, AdminUsersView, XmlBaseView, \
    TransactionView, StoreView, GameDbView, SpecialPackView, ApiView
from jsonScheme import gameDbJsonScheme
from werkzeug.contrib.cache import SimpleCache
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import requests

cache = SimpleCache()
init_db()
app = Flask(__name__)
app.config['HMAC_KEY'] = 'hBV+H7dt2aD/R3z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yokohama@localhost/FarmBase'
migrate = Migrate(app, Base)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
app.debug = True
hm = Hmac(app)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db_session.query(AdminUsers).get(user_id)


init_login()


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)

# app.config['CSRF_ENABLED'] = True
# flask_wtf.CsrfProtect(app)

packages = {"Diamonds_G": 7, "Diamonds_F": 6, "Diamonds_E": 5, "Diamonds_D": 4, "Diamonds_C": 3, "Diamonds_B": 2,
            "Diamonds_A": 1}

gameDbSchemeConverter = gameDbJsonScheme()

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, (User, Level, int, str)):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)


admin = Admin(app, name='farm_web_service', index_view=MyAdminIndexView(), base_template='my_master.html')

admin.add_view(UserView(User, db_session))
admin.add_view(LevelView(Level, db_session))
admin.add_view(TransactionView(Transaction, db_session))
admin.add_view(XmlBaseView(Xmlbase, db_session))
admin.add_view(GiftCardView(Giftcards, db_session))
admin.add_view(AdminUsersView(AdminUsers, db_session))
admin.add_view(StoreView(Store, db_session))
admin.add_view(GameDbView(GameDb, db_session))
admin.add_view(SpecialPackView(Special_Packages, db_session))
admin.add_view(ApiView(Api, db_session))

app.secret_key = '\xa1xec[\tg`\xac\x96\xafv\xff\xf6\x04\xa2bT\x13\xb6\xca\xf9@\xf2'
cafebazaar_access_token = ""


@app.route('/get_time', methods=['POST'])
@hm.check_hmac
def time_server():
    time = datetime.datetime.now()
    response = jsonify({'status': '200', 'time': time})
    response.status_code = 200
    return response

@app.route('/v1/get_time', methods=['GET'])
def get_time_server():
    time = datetime.datetime.now()
    response = jsonify({'status': '200', 'time': time})
    response.status_code = 200
    return response


@app.route('/dailyreward/<int:id>', methods=['GET'])
def daily_reward(id):
    retrieved_user = User.query.filter_by(id=id).first()
    if retrieved_user:
        b = datetime.datetime.now()
        delta = b - retrieved_user.last_daily_reward_date
        if (delta.total_seconds() > 10):#3599):
            retrieved_user.last_daily_reward_date = datetime.datetime.now()
            db_session.commit()
            response = jsonify({"status": "Ok"})
            response.status_code = 200
            return response
        abort(403)
    abort(404)


@app.route('/editprofile', methods=['POST'])
@hm.check_hmac
def edit_profile():
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
    for i in users:
        i.is_banned = False
        i.wins = 0
        i.last_daily_reward_date = datetime.datetime.now()
    db_session.commit()
    return "finished"


'''
@app.route('/V2/coin/<int:id>', methods=['GET'])
def get_gold(id):
    gamedb = GameDb.query.filter_by(user_id=id).first()
    if gamedb:
        response = jsonify({"gold": gamedb.Coins})
        response.status_code = 200
        return response
    abort(404)

@app.route('/V2/coin/<int:id>', methods=['POST'])
def set_gold(id):
    gamedb = GameDb.query.filter_by(user_id=id).first()
    if gamedb:
        gamedb.Coins = request.json["coin"]
        gamedb.commit()
        response = jsonify({"gold": gamedb.Coins, "status": "updated"})
        response.status_code = 200
        return response
    abort(404)
'''

@app.route('/version', methods=['GET'])
def get_last_version():
    version = Api.query.first().version
    response = jsonify({"version": version})
    response.status_code = 200
    return response

@app.route('/V1/purchase_log', methods=['POST'])
@hm.check_hmac
def client_logs():
    if request.json.get("log"):
        log = request.json.get("log")
        print("Client Log", log)
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
    '''
    try:
        gamedb = GameDb(request.json)
        db_session.add(gamedb)
        db_session.commit()
        response = jsonify({"status": "ok"})
        response.status_code = 201
    except Exception:
        response = jsonify({"status": "No User Found"})
        response.status_code = 404

    '''

    gamedb = GameDb.query.filter_by(user_id=request.json["id"]).first()
    if gamedb:
        gamedb.update_data(request.json)
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


@app.route('/gamedb', methods=['POST'])
@hm.check_hmac
def set_player_db():
    gamedb = GameDb.query.filter_by(user_id=request.json["id"]).first()
    for i in request.json.keys():
         setattr(gamedb, gameDbSchemeConverter.get_correspond(i), request.json[i])
    db_session.commit()
    response = jsonify({"status": "updated"})
    return response


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

    #generating proper game db for new user
    new_gamedb = GameDb(None, u.id) # creating new game db for new user
    db_session.add(u)
    db_session.commit()

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
        gift_ret.count -= 1
        gift_ret.username = request.json['username']
        if gift_ret.count == 0:
            gift_ret.validity = 0
        db_session.commit()
        response = jsonify({"status": "200", 'count': gift_ret.diamond_count})
        response.status_code = 200
        return response
    abort(404)


@app.route('/aghax/set_giftcard', methods=['POST'])
def set_gift_card():
    gift_code = request.json['gift_code']
    gift_count = request.json['gift_count']
    gift_ret = Giftcards(gift_code, gift_count)
    db_session.add(gift_ret)
    db_session.commit()
    response = jsonify({"status": "200"})
    response.status_code = 200
    return response


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
    retrieved_user = User.query.filter_by(username=request.json["winner"]).first()
    if retrieved_user:
        retrieved_user.win()
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


@app.route('/getHash', methods=['POST'])
@hm.check_hmac
def get_hash():
    api_ver = request.json['api_version']
    xml_ret = Xmlbase.query.filter_by(api_version=api_ver).first()
    if xml_ret:
        response = jsonify({"status": "200", 'hash': xml_ret.xml_code})
        response.status_code = 200
        return response
    abort(404)


@app.route('/aghax/setHash', methods=['POST'])
def set_hash():
    api_ver = request.json['api_version']
    code = request.json['code']
    xml_ret = Xmlbase(code, api_ver)
    db_session.add(xml_ret)
    db_session.commit()
    response = jsonify({"status": "200"})
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


@app.route('/shopping/<int:package>', methods=['POST'])
@hm.check_hmac
def shopping(package):
    response = jsonify({"status": "200"})
    response.status_code = 200
    return response


@app.route('/V1/get_rank/level/<int:user_level>/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_rank_v1(user_level, offset):
    '''
    a = cache.get('V1_level_user_join_' + str(user_level))
    if a is None:
        a = db_session.query(User, Level).join(Level).add_columns(User.score, Level.level, Level.time, User.username). \
            filter(Level.level == user_level).order_by(Level.time.asc()).all()  # TODO: this function must be cached
        cache.set('V1_level_user_join_' + str(user_level), a, timeout=5 * 60)
    '''
    # a = db_session.query(User, Level).join(Level).add_columns(User.score, Level.level, Level.time, User.username). \
    #            filter(Level.level == user_level).order_by(Level.time.asc()).all()

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
    # a = db_session.query(User, Level).join(Level).add_columns(User.score, Level.level, Level.time, User.username). \
    #    filter(Level.level == user_level).order_by(Level.time.asc()).all() # TODO: this function must be cached
    '''
    a = cache.get('level_user_join_' + str(user_level))
    if a is None:
        a = db_session.query(User, Level).join(Level).add_columns(User.score, Level.level, Level.time, User.username). \
            filter(Level.level == user_level).order_by(Level.time.asc()).all()  # TODO: this function must be cached
        cache.set('level_user_join_' + str(user_level), a, timeout=5 * 60)
    '''

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

        anar = json.dumps(usernames_list, cls=SetEncoder, ensure_ascii=False)
        response = jsonify({'status': '200', 'username': anar, 'scores': time_list, 'index': index - start_index,
                            'rank': index + 1})
        response.status_code = 200
        return response
    abort(404)


@app.route('/get_rank/score/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_score(offset):
    # player = db_session.query(User).filter_by().order_by(User.score.asc()).all() ## TODO: this function must be cached
    ''''
    player = cache.get('user_sorted_by_score')
    if player is None:
        player = db_session.query(User).filter_by().order_by(
            User.score.asc()).all()  ## TODO: this function must be cached
        cache.set('user_sorted_by_score', player, timeout=5 * 60)
    '''
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
    # player = db_session.query(User).filter_by().order_by(User.score.asc()).all() ## TODO: this function must be cached


    '''
    player = cache.get('user_sorted_by_score')
    if player is None:
        player = db_session.query(User).filter_by().order_by(
            User.score.asc()).all()  ## TODO: this function must be cached
        cache.set('user_sorted_by_score', player, timeout=5 * 60)
    '''
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


@app.route('/bazzar', methods=['GET', 'POST'])
def get_bazzar_token():
    return request.data


@app.route('/v1/validate_transaction', methods=['POST'])
@hm.check_hmac
def v1_validate_transaction():
    #abort(500)
    product_id = request.json["product_id"]
    purchase_token = request.json["purchase_token"]
    request_validate = cafebazaar_send_validation_request(product_id, purchase_token)
    is_repeated_token = db_session.query(Transaction).filter_by(token=purchase_token).all()
    result = request_validate and len(is_repeated_token) == 0
    if result:
        store_product_ids = db_session.query(Store.product_id).all()
        special_packages_product_ids = db_session.query(Special_Packages.product_id).all()

        for i in store_product_ids:
            if product_id in i:
                store = Store.query.filter_by(product_id=product_id).first()
                transaction = Transaction(request.json.get("id"), store.discount, store.diamond, store.price,
                                          purchase_token, product_id)
                db_session.add(transaction)
                break

        for i in special_packages_product_ids:
            if product_id in i:
                special_packages = Special_Packages.query.filter_by(product_id=product_id).first()
                transaction = Transaction(request.json.get("id"), special_packages.discount, special_packages.diamond,
                                          special_packages.price, purchase_token, product_id)
                db_session.add(transaction)
                break

        db_session.commit()

    response = jsonify({"status": result})
    response.status_code = 200
    return response


@app.route('/check_validatation_testing', methods=['POST'])
@hm.check_hmac
def testing_validation1():
    product_id = request.json["product_id"]
    purchase_token = request.json["purchase_token"]
    request_validate = cafebazaar_send_validation_request(product_id, purchase_token, 1)
    response = jsonify({"status": request_validate})
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
    bazzar_access_token = cafebazaar_refresh_auth()
    url = "https://pardakht.cafebazaar.ir/devapi/v2/api/validate/" + \
          "com.ElmoGame.Farmuler/inapp/" + str(product_id) + "/purchases/" + \
          str(purchase_token) + "/?access_token={access_token}" \
              .format(access_token=bazzar_access_token)
    r = requests.get(url, verify=False)
    return_json = json.loads(r.text)
    result = return_json.get('error') is None
    return result


if __name__ == '__main__':
    app.debug = True
    #manager.run()
    app.run(host='0.0.0.0', port=6789)

'''
print("koscher")
is_repeated_token = db_session.query(Transaction).filter_by(token=purchase_token).all()
if request_validate and not is_repeated_token:
    product_ids = db_session.query(Store.product_id).all()
    special_packages_product_ids = db_session.query(Special_Packages.product_id).all()
    user_db = GameDb.query.filter_by(user_id=request.json.get("id")).first()

    for i in product_ids:
        if product_id in i:
            store = Store.query.filter_by(product_id=product_id).first()
            user_db.Diamonds = store.diamond + user_db.Diamonds
            transaction = Transaction(request.json.get("id"), store.discount, store.diamond, store.price, purchase_token, product_id)
            db_session.add(transaction)
            break
    for i in special_packages_product_ids:
        if product_id in i:
            special_packages = Special_Packages.query.all()
            user_db.Charecters = special_packages.charactor
            user_db.Diamonds = special_packages.diamond + user_db.Diamonds
            user_db.Coins = special_packages.coin + user_db.Coins
            transaction = Transaction(request.json.get("id"), special_packages.discount, special_packages.diamond, special_packages.price, purchase_token, product_id)
            db_session.add(transaction)
            break

'''
