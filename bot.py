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
                    await app.send_message(user_id ,f"کاربر {message.from_user.first_name} عزیز تعداد تاریخ تولد های ذخیره شده شما به اتمام رسیده است، شما تنها میتوانید ۱۵ تاریخ تولد را در اکانت خود ذخیره نمایید، میتوانید با حذف یکی از تاریخ تولد ها، تاریخ تولد دیگری را جایگزین آن کنید.")
                    return
                else :
                    await app.send_message(user_id, f"سلام {message.from_user.first_name} عزیز لطفا عملیات خود را انتخاب کنید", reply_markup=key.mark)
                    return          
            else:
                date = JalaliDate.today()
                cursor.execute(f"INSERT INTO users (user_id, joined_date, is_vip, state) VALUES ({user_id},'{date}','no',0);") 
    
    await app.send_message(user_id, f"سلام {message.from_user.first_name} عزیز لطفا عملیات خود را انتخاب کنید", reply_markup=key.first_mark)


async def new_event(message):
    'Initialization of new event'
    user_id = message.from_user.id
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(user_id) FROM events WHERE user_id = {user_id};")
            number_of_events = cursor.fetchall() 
            if((number_of_events[0][0] > 15)):
                await app.send_message(user_id ,f"کاربر {message.from_user.first_name} عزیز تعداد تاریخ تولد های ذخیره شده شما به اتمام رسیده است، شما تنها میتوانید ۱۵ تاریخ تولد را در اکانت خود ذخیره نمایید، میتوانید با حذف یکی از تاریخ تولد ها، تاریخ تولد دیگری را جایگزین آن کنید.")
                return
            cursor.execute(f"SELECT state FROM users WHERE user_id = {user_id};")
            state = cursor.fetchall()[0][0]        
            if int(state) in [1,2,3,4] :
                cursor.execute(f"DELETE FROM events_buffer WHERE user_id = {user_id};")
            await app.send_message(user_id ,"نام کسی که میخواهید تولدش را ذخیره کنید وارد کنید")
            cursor.execute(f"UPDATE users SET state = 1 WHERE user_id = {user_id};")


async def first_state_recieve_name(message):
    'Recieving birthday person name'
    user_id = message.from_user.id
    birthday_person_name = message.text
    if len(birthday_person_name) > 30 :
        await app.send_message(user_id ,"نام شخص نهایتا میتواند ۳۰ کاراکتر باشد، یک بار دیگر نام ایشان را خلاصه تر وارد کنید.")
        return
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT TRUE FROM events WHERE birthday_person_name = '{birthday_person_name}' and user_id = '{user_id}';")
            is_repeated = cursor.fetchall()
            try:
                if is_repeated[0][0] == True:
                    await app.send_message(user_id ,"قبلا برای این اسم یک تاریخ تولد ثبت کردید. اسم ایشان را خلاصه تر یا به همراه یک ایموجی وارد کنید.")
                    return
            except:
                pass
            cursor.execute(f"SELECT COUNT(user_id) FROM events_buffer WHERE user_id = {user_id};")
            has_unfinished = cursor.fetchall()
            if has_unfinished[0][0] == 0:
                cursor.execute(f"INSERT INTO events_buffer (user_id,birthday_person_name) VALUES ({user_id},'{birthday_person_name}');")
            else:
                cursor.execute(f"UPDATE events_buffer SET birthday_person_name = '{birthday_person_name}' WHERE user_id = {user_id};")
            cursor.execute(f"UPDATE users SET state = 2 WHERE user_id = {user_id};")
            
    await app.send_message(user_id ,"سال تولد ایشان را ۴ رقمی وارد کنید. برای مثال ۱۳۷۳")
            


@app.on_message()
async def data_gathering(client, message):

    user_id = message.from_user.id
    
    if message.text == "ثبت تاریخ تولد جدید":
        await new_event(message)
        return 
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT state FROM users WHERE user_id = {user_id};")
            user_state = cursor.fetchall()
    
    if user_state[0][0] == 0:
        await app.send_message(user_id ,"نمیفهمم چی میگید از دکمه های شیشه ای استفاده کنید. ",reply_markup=key.mark)
        return
    
    if user_state[0][0] == 1:
        await first_state_recieve_name(message)
        return

app.run()
