from pyrogram import *
from pyrogram.types import *
import constants as keys
import const as key
import psycopg2
from persiantools.jdatetime import JalaliDate, timedelta


app = Client("session", config_file="config.ini")
connection = psycopg2.connect(
    user=keys.user, password=keys.password, host=keys.host, port=keys.port, database=keys.database)


def empty_buffer(user_id,cursor):
    cursor.execute(f"DELETE FROM events_buffer WHERE user_id = {user_id};")
    cursor.execute(f"UPDATE users SET state = 0 WHERE user_id = {user_id};")
    

@app.on_message(filters.command("start"))
async def start_command(Client, message):

    user_id = message.from_user.id
 
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(user_id) FROM users WHERE user_id = {user_id};")
            has_already_started = cursor.fetchall()
            if has_already_started[0][0] > 0 :
                empty_buffer(user_id, cursor)
                cursor.execute(f"SELECT COUNT(user_id) FROM events WHERE user_id = {user_id};")
                number_of_events = cursor.fetchall()
                
                if number_of_events[0][0] > 15:
                    await app.send_message(user_id, f"سلام {message.from_user.first_name} \nتعداد تاریخ تولد هایی که میتوانید ذخیره کنید تمام شده است.")
                    return
                else :
                    await app.send_message(user_id, f"سلام {message.from_user.first_name} عزیز لطفا عملیات خود را انتخاب کنید", reply_markup=key.mark)
                    return          
            else:
                date = JalaliDate.today()
                cursor.execute(f"INSERT INTO users (user_id, joined_date, is_vip, state) VALUES ({user_id},'{date}','no',0);") 
    
    await app.send_message(user_id, f"سلام {message.from_user.first_name} عزیز لطفا عملیات خود را انتخاب کنید", reply_markup=key.first_mark)


app.run()
