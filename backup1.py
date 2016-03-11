from flask import Flask, request, abort
from database import db_session
from models import User, Level, Transaction, Xmlbase, Giftcards
from database import init_db
from flask import jsonify, json
from flask_hmac import Hmac
import datetime
from tools import Tools
from store import Store
from sqlalchemy import exc
import re
from flask_admin import Admin
import flask_wtf
from myadmin import UserView, GiftCardView, LevelView
from flask_admin.contrib.sqla import ModelView







init_db()
app = Flask(__name__)
app.config['HMAC_KEY'] = 'hBV+H7dt2aD/R3z'
hm = Hmac(app)

#app.config['CSRF_ENABLED'] = True
#flask_wtf.CsrfProtect(app)




admin = Admin(app, name='farm_web_service', template_mode='bootstrap3')
admin.add_view(UserView(User, db_session))
admin.add_view(LevelView(Level, db_session))
admin.add_view(ModelView(Transaction, db_session))
admin.add_view(ModelView(Xmlbase, db_session))
admin.add_view(GiftCardView(Giftcards, db_session))

app.secret_key = '\xa1xec[\tg`\xac\x96\xafv\xff\xf6\x04\xa2bT\x13\xb6\xca\xf9@\xf2'


@app.route('/get_time', methods=['POST'])
@hm.check_hmac
def time_server():
    time = datetime.datetime.now()
    response = jsonify({'status': '200', 'time': time})
    response.status_code = 200
    return response


@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter(User.username == request.json['username'],
                             User.password == request.json['password']).first()
    if user:
        response = jsonify({'status': '200'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'status': '401'})
        response.status_code = 401
        return response


@app.route('/register', methods=['POST'])
@hm.check_hmac
def register():
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    username_size = len(request.json['username'])
    if username_size < 5 or username_size > 20:
        abort(411)

    if not email_regex.match(request.json['email']):
        abort(410)

    u = User(request.json['username'], request.json['password'], request.json['email'])
    db_session.add(u)
    try:
        db_session.commit()
        response = jsonify({'status': '201'})
        response.status_code = 201
        return response
    except exc.SQLAlchemyError:
        response = jsonify({'status': '409', 'error': 'duplicate username'})
        response.status_code = 409
        return response


@app.route('/testreg', methods=['GET'])
def test_create():
    for i in range(1000):
        u = User(str(i), 12345, str(i)+"@gmail.com")
        db_session.add(u)

    db_session.commit()
    response = jsonify({'status': '201'})
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


@app.route('/getboard', methods=['POST'])
@hm.check_hmac
def get_score_board():
    retrieved_users = User.query.order_by(User.score.desc()).limit(10).all()

    username_list = []
    score_list = []

    for i in retrieved_users:
        username_list.append(i.username)
        score_list.append(i.score)

    if retrieved_users:
        return jsonify({'usernames': username_list, 'score': score_list, 'status': 'ok'})
    return jsonify({'status': 'not ok', 'description': 'No User Found'})


@app.route('/finish_level', methods=['POST'])
@hm.check_hmac
def finish_level():
    username = request.json['username']
    time = int(request.json['time'])
    level = int(request.json['level'])
    foreign_key = User.query.filter_by(username=username).first()
    if foreign_key:
        existence = Level.query.filter(Level.user_id == foreign_key.id, Level.level == level).first()
        if existence:
            if time < existence.time:
                existence.set_time(time)
                foreign_key.set_score(59*60 + 59 - time)
                foreign_key.recent_access_time()
                db_session.commit()
            else:
                rank = Level.query.filter(Level.time <= int(existence.time),
                                          Level.level == int(existence.level)).count()
                best_time = Level.query.filter_by(level=int(existence.level))\
                    .order_by(Level.time.asc()).first()
                best_player = User.query.filter_by(id=best_time.user_id).first()
                response = jsonify({'status': '200', 'best_time': best_time.time, 'Rank': rank,
                                    'best_username':  best_player.username})
                response.status_code = 200
                return response

        else:
            foreign_key.set_score(59*60 + 59 - time)
            new_level = Level(foreign_key.id, time, level)
            foreign_key.total_level += 1
            print "new level added"
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
    ret_level = Level.query.filter_by(level=level).order_by(Level.time.asc()).first()
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
        response = jsonify({'status': '200', 'cost': data[0], 'discount': data[1]})
        response.status_code = 200
        return response


@app.route('/top_ten/level/<int:level>/<int:offset>/<int:count>', methods=['POST'])
@hm.check_hmac
def top_ten(level, offset, count):
    ret = Level.query.join(User, User.id == Level.user_id).filter(Level.level == level).order_by(Level.time.asc()).all()
    found_users = []
    scores = []
    if offset < len(ret):
        count_picker = count if offset + count < len(ret) else offset + count - len(ret) - 1
        for i in range(count_picker):
            a = ret[offset + i]
            username = User.query.filter_by(id=a.user_id).first().username
            found_users.append(username)
            scores.append(a.time)

        found_users = json.dumps(found_users)
        scores = json.dumps(scores)
        response = jsonify({'status': '200', 'usernames': found_users, 'scores': scores})
        response.status_code = 200
        return response
    else:
        abort(404)


@app.route('/top_ten/ranking/<int:offset>/<int:count>', methods=['POST'])
@hm.check_hmac
def ranking(offset, count):
    ret = User.query.filter().order_by(User.score.asc()).all()
    found_users = []
    scores = []
    if offset < len(ret):
        count_picker = count if offset + count < len(ret) else offset + count - len(ret) - 1
        for i in range(count_picker):
            a = ret[offset + i]
            found_users.append(a.username)
            scores.append(431880 - a.score)

        found_users = json.dumps(found_users)
        scores = json.dumps(scores)

        response = jsonify({'status': '200', 'usernames': found_users, 'scores': scores})
        response.status_code = 200
        return response
    else:
        abort(404)


@app.route('/levelsStauts/<string:username>', methods=['POST'])
@hm.check_hmac
def levels_stauts(username):
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
    retrieved_user = User.query.filter_by(username=str(request.json['username'][0])).first()
    levels = request.json['levels']
    scores = request.json['times']

    for i in range(len(levels)):
        level = Level(retrieved_user.id, int(scores[i]), int(levels[i]))
        retrieved_user.set_score(59*60 + 59 - int(scores[i]))
        retrieved_user.total_level += 1
        db_session.add(level)

    db_session.commit()
    response = jsonify({'status': '201'})
    response.status_code = 201
    return response


@app.route('/getStore', methods=['POST'])
@hm.check_hmac
def get_store():
    my_store = Store()
    response = jsonify({"status": "200", 'store': my_store.get_packages()})
    response.status_code = 200
    return response


@app.route('/get_player_overall_rank/<string:username>/<int:level>', methods=['POST'])
@hm.check_hmac
def get_player_overall_rank(username, level):
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
    gift_code = int(request.json['gift_code'])
    gift_ret = Giftcards.query.filter_by(code=gift_code).first()
    if gift_ret and gift_ret.validity:
        gift_ret.count -= 1
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
    username = request.json['username']
    print "alireza sanaee"
    user = User.query.filter_by(username=username).first()
    if user:
        user.chars = character_count
        db_session.commit()
        response = jsonify({"status": "200"})
        response.status_code = 200
        return response
    abort(404)



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


@app.route('/set_gold_diamond/<string:username>/<int:gold>/<int:diamond>', methods=['POST'])
@hm.check_hmac
def set_gold_diamond(username, gold, diamond):
    retrieved_user = User.query.filter_by(username=username).first()
    if retrieved_user:
        retrieved_user.set_gold(int(gold))
        retrieved_user.set_gold_diamond(int(gold), int(diamond))
        retrieved_user.recent_access_time()
        db_session.commit()
        response = jsonify({"status": "200"})
        response.status_code = 200
        return response
    abort(404)


@app.route('/shopping/<string:username>/<int:package>', methods=['POST'])
@hm.check_hmac
def shopping(username, package):
    store = Store()
    price = store.get_package_price(package)
    temp_username = username if username != "-1" else "aghaxoo"
    retrieved_user = User.query.filter_by(username=temp_username).first()
    if retrieved_user:
        retrieved_user.shopping(int(price))
        retrieved_user.recent_access_time()
        diamond = int(store.get_package_diamond(package))
        retrieved_user.buy_diamond(diamond)
        transaction = Transaction(retrieved_user.id, int(store.get_package_dicount(package)), diamond, int(price))
        db_session.add(transaction)
        db_session.commit()
        response = jsonify({"status": "200"})
        response.status_code = 200
        return response
    abort(404)


@app.route('/get_rank/level/<int:user_level>/user/<username>/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_rank(username, user_level, offset):
    player = User.query.filter_by(username=username).first()
    if player:
        user_ranks = Level.query.filter(Level.level == user_level).order_by(Level.time.asc()).all()
        if user_ranks:
            tools = Tools()
            temp = tools.user_index_finder(user_ranks, player)
            if temp >= 0:
                user_index = tools.offset_checker(offset, temp)
                users = user_ranks[user_index:temp+offset+1]
                username_array = []
                username_scores_array = []
                counter = 0
                index = 0

                for i in users:
                    player = User.query.filter_by(id=i.user_id).first()
                    if username == player.username:
                        index = counter
                    counter += 1
                    username_array.append(player.username)
                    username_scores_array.append(i.time)
                username_array = json.dumps(username_array)
                username_scores_array = json.dumps(username_scores_array)
                ranks = Level.query.filter(Level.level == user_level, Level.time <= user_ranks[user_index].time).count()
                response = jsonify({'status': '200', 'username': username_array,
                                    'scores': username_scores_array,
                                    'rank': ranks, 'index': index})
                response.status_code = 200
                return response
    abort(404)


@app.route('/get_rank/score/user/<username>/offset/<int:offset>', methods=['POST'])
@hm.check_hmac
def get_score(username, offset):
    player = User.query.filter_by(username=username).first()
    if player:
        users = User.query.filter().order_by(User.score.asc()).all()
        tools = Tools()
        temp = tools.user_index_finder(users, player)
        if temp >= 0:
            user_index = tools.offset_checker(offset, temp)
            users = users[user_index:temp+offset+1]
            username_array = []
            username_scores_array = []
            counter = 0
            index = 0
            for i in users:
                if username == i.username:
                    index = counter
                counter += 1
                username_array.append(i.username)
                username_scores_array.append(431880 - i.score)
            username_array = json.dumps(username_array)
            username_scores_array = json.dumps(username_scores_array)
            rank = User.query.filter(User.score <= player.score).count()
            response = jsonify({'status': '200', 'username': username_array,
                                'scores': username_scores_array,
                                'rank': rank, 'index': index})
            response.status_code = 200
            return response
    abort(404)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.debug = True
    app.run(host='172.17.8.239', port=5000)
    #app.run(host='185.92.223.56', port=5001)