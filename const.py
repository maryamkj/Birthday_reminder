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
