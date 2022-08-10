from pyrogram.types import *

mark = ReplyKeyboardMarkup(
    [
        [KeyboardButton("ثبت تاریخ تولد جدید")],
        [KeyboardButton("مشاهده تاریخ تولد های ثبت شده")],
        [KeyboardButton("حذف یک تاریخ تولد")]
    ],resize_keyboard=True, one_time_keyboard=True)

first_mark = ReplyKeyboardMarkup(
    [
        [KeyboardButton("ثبت تاریخ تولد جدید")]
    ],resize_keyboard=True, one_time_keyboard=True)

month_dic_key_value = {'01':'فروردین', '02':'اردیبهشت', '03':'خرداد','04':'تیر', '05':'مرداد', '06':'شهریور','07':'مهر', '08':'آبان', '09':'آذر','10':'دی', '11':'بهمن', '12':'اسفند'}