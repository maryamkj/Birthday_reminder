from pyrogram import *
from pyrogram.types import *
import constants as keys
import const as key
import psycopg2
from persiantools.jdatetime import JalaliDate, timedelta
import numpy as np
from unidecode import unidecode


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
            

async def second_state_recieve_year(message) :
    'Recieving year of birth'
    
    user_id = message.from_user.id
    year = unidecode(message.text)
    current_year = JalaliDate.today().year
    
    if (len(year) != 4) or (int(year) > current_year) or (int(year) < 1300):
        await app.send_message(user_id ,"سال تولد معتبر نیست، دوباره سال تولد را وارد کنید.")
        return
       
    month_list = np.array([])
    for i in range(1,13):
        i = str(i).zfill(2)
        month_list = np.append(month_list,[InlineKeyboardButton(text = f"{key.month_dic_key_value[str(i)]}",callback_data = f"{i}")])
    
    month_list = month_list.reshape(6,2)
    
    mark  = InlineKeyboardMarkup(month_list)

    message = await app.send_message(user_id ,"ماه تولد ایشان را انتخاب کنید.",reply_markup=mark)
    message_id = message.message_id

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE users SET state = 3 WHERE user_id = {user_id};")     
            cursor.execute(f"UPDATE events_buffer SET year = '{year}' WHERE user_id = {user_id};")
            cursor.execute(f"UPDATE events_buffer SET month_id = '{message_id}' WHERE user_id = {user_id};")


async def third_state_recieve_month(client, callback_query):
    'Recieving month of birth'
    
    user_id = callback_query.from_user.id
    month = callback_query.data 
    
    message_id = callback_query.message.message_id
    await app.delete_messages(user_id ,message_id)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT state FROM users WHERE user_id = {user_id};")
            user_state = cursor.fetchall()
            if user_state[0][0] != 3:
                await app.send_message(user_id ,f"در زمان اشتباهی از کلید های شیشه ای استفاده کردید، دوباره از ابتدا مراحل را آغاز کنید", reply_markup=key.mark)
                empty_buffer(user_id, cursor)
                return
            cursor.execute(f"SELECT month_id FROM events_buffer WHERE user_id = {user_id};")
            month_message_id = cursor.fetchall() 
            if message_id != month_message_id[0][0]:
                await app.send_message(user_id ,f"برای انتخاب کردن ماه تولد لطفا از آخرین کلید شیشه ای تولید شده استفاده کنید.", reply_markup=key.mark)
                return
            cursor.execute(f"UPDATE users SET state = 4 WHERE user_id = {user_id};")  
            cursor.execute(f"UPDATE events_buffer SET month = '{month}' WHERE user_id = {user_id};")  

    
    await app.send_message(user_id ,f"ماه {key.month_dic_key_value[month]} انتخاب شد.")
    days_list = np.array([])
    for i in range(1,31):
        days_list = np.append(days_list,[InlineKeyboardButton(text = f"{i}",callback_data = f"{i}")])
    days_list = days_list.reshape(5,6)

    if(int(month) <= 6):
        
        days_mark = InlineKeyboardMarkup([
            days_list[0],
            days_list[1],
            days_list[2],
            days_list[3],
            days_list[4],
            [InlineKeyboardButton(text = "31",callback_data="31")] 
        ])
    else:
        days_mark= InlineKeyboardMarkup(days_list)
    message = await app.send_message(user_id ,f"روز تولد ایشان را انتخاب کنید.", reply_markup=days_mark)
    message_id = message.message_id
    
    with connection:
        with connection.cursor() as cursor:  
            cursor.execute(f"UPDATE events_buffer SET day_id = '{message_id}' WHERE user_id = {user_id};")  
            

@app.on_callback_query()
async def callback_query_handler(client, callback_query):
    
    text = callback_query.message.text
    
    if text == "ماه تولد ایشان را انتخاب کنید.":
        await third_state_recieve_month(client, callback_query)
        return


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
    
    if user_state[0][0] == 2:
        await second_state_recieve_year(message)  
        return
    
    if user_state[0][0] == 3:
        await app.send_message(user_id ,".برای وارد کردن ماه تولد از دکمه های شیشه ای استفاده کنید",reply_markup=mark)
        return

app.run()
