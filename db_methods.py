from bot import conn, curs


def get_user_list():
    users = curs.execute('SELECT * FROM users')
    users = users.fetchall()
    return users


def get_user_detail(q_param: list):
    user = curs.execute('SELECT * FROM users WHERE {}="{}"'.format(q_param[0], q_param[1]))
    user = user.fetchall()
    if user:
        user = user[0]
    return user


def create_user(data: dict):
    curs.execute('INSERT INTO users (name, tg_id, phone) VALUES ("{}", "{}", "{}")'.format(
        data['name'],
        data['contact']['user_id'],
        data['contact']['phone_number']
    ))
    conn.commit()
    return True
