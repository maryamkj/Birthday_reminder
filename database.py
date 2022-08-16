import psycopg2
import constants as keys

CONN = None

def connect_to_db():
    
    global CONN
    if CONN is None or CONN.closed:
        CONN = psycopg2.connect(user=keys.user, password=keys.password, host=keys.host, port=keys.port, database=keys.database)
    return CONN

def delete_row(user_id,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name} WHERE user_id = {user_id};")
    CONN.commit()
    CONN.close()
        
def delete_row_where(user_id,table_name,variable,value):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name} WHERE user_id = {user_id} AND {variable} = '{value}';")
    CONN.commit()
    CONN.close()

def select_count(user_id,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(user_id) FROM {table_name} WHERE user_id = {user_id};")
        return_value = cursor.fetchall()
    CONN.close()
    return return_value

def select_one_parameter(user_id,variable,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"SELECT {variable} FROM {table_name} WHERE user_id = {user_id};")
        return_value = cursor.fetchall()
    CONN.close()
    return return_value

def select_one_parameter_where(user_id,s_value,variable,value,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"SELECT {s_value} FROM {table_name} WHERE  {variable} = '{value}' AND user_id = {user_id};")
        return_value = cursor.fetchall()
    CONN.close()
    return return_value

def select_star(user_id,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} WHERE user_id = {user_id};")
        return_value = cursor.fetchall()
    CONN.close()
    return return_value


def create_new_user(user_id,date):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"INSERT INTO users (user_id, joined_date, is_vip, state) VALUES ({user_id},'{date}','no',0);")
    CONN.commit()
    CONN.close()
    
def create_new_event(user_id,birthday_person_name,date):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"INSERT INTO events (user_id, birthday_person_name, date_of_birth) VALUES ({user_id},'{birthday_person_name}','{date}');") 
    CONN.commit()
    CONN.close()
    
def create_new_event_buffer(user_id,birthday_person_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"INSERT INTO events_buffer (user_id,birthday_person_name) VALUES ({user_id},'{birthday_person_name}');")
    CONN.commit()
    CONN.close()
    

def update_one_parameter(user_id,variable,value,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"UPDATE {table_name} SET {variable} = {value} WHERE user_id = {user_id};")
    CONN.commit()
    CONN.close()
    
    
def select_true_if_exist(user_id,variable,value,table_name):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"SELECT TRUE FROM {table_name} WHERE {variable} = '{value}' and user_id = '{user_id}';")
        return_value = cursor.fetchall()
    CONN.close()
    return return_value

def select_near_birthday(next_month,next_day):
    CONN = connect_to_db()
    with CONN.cursor() as cursor:
        cursor.execute(f"SELECT birthday_person_name, user_id FROM events WHERE (SELECT substring(date_of_birth,6,2)) = '{next_month}' and (SELECT substring(date_of_birth,9,2)) = '{next_day}';")
        return_value = cursor.fetchall()
    CONN.close()
    return return_value
    