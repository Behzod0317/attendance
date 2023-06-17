import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from fpdf import FPDF
import unicodedata
import os
import psycopg2


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Telegram bot token (replace 'YOUR_BOT_TOKEN' with your bot token)
TOKEN = '6082028232:AAG0tngUrjsf7HvPO_HOFddVr2Uiw2o5J8s'

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'bot'
DB_USER = 'botuser'
DB_PASSWORD = 'password1721'

# Create an instance of the Updater class
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

connection = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)


class UnicodePDF(FPDF):
    def header(self):
        
        pass

    def footer(self):
        
        pass


def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Attendance Bot!")


# Register the start command handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def help(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
                                Bu bot foydalanuvchilarga botga “+” yoki “-” 
                                xabarini yuborish orqali o‘z ishtirokini
                                belgilash imkonini beradi. Bot ishtirokchilar 
                                haqidagi ma'lumotlarni, jumladan,
                                foydalanuvchining ismi, sanasi va kelish yoki
                                ketish vaqtini pdf formatda qaytaradi.""")


help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)
# Dictionary to store attendance information
attendance_data = {}

cursor = connection.cursor()


# def collect_attendance(update: Update, context):
#     message_text = update.message.text.strip()
#     user = update.message.from_user
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     current_date = now.strftime("%Y-%m-%d")

#     if message_text == '+':
#         if user.id not in attendance_data:
#             attendance_data[user.id] = {
#                 'name': user.first_name, 'coming_time': current_time}
#     elif message_text == '-':
#         if user.id in attendance_data:
#             attendance_data[user.id]['leaving_time'] = current_time


def collect_attendance(update: Update, context):
    message_text = update.message.text.strip()
    user = update.message.from_user
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")

    if message_text == '+':
        if user.id not in attendance_data:
            attendance_data[user.id] = {
                'name': user.first_name, 'coming_time': current_time}
        elif 'coming_time' in attendance_data[user.id] and 'to_lunch' not in attendance_data[user.id]:
            attendance_data[user.id]['to_lunch'] = current_time
        elif 'coming_time' in attendance_data[user.id] and 'to_lunch' in attendance_data[user.id] and 'from_lunch' not in attendance_data[user.id]:
            attendance_data[user.id]['from_lunch'] = current_time
        elif 'coming_time' in attendance_data[user.id] and 'to_lunch' in attendance_data[user.id] and 'from_lunch' in attendance_data[user.id] and 'leaving_time' not in attendance_data[user.id]:
            attendance_data[user.id]['leaving_time'] = current_time
    elif message_text == '-':
        if user.id in attendance_data:
            if 'coming_time' in attendance_data[user.id] and 'to_lunch' not in attendance_data[user.id]:
                attendance_data[user.id]['to_lunch'] = current_time
            elif 'to_lunch' in attendance_data[user.id] and 'from_lunch' not in attendance_data[user.id]:
                attendance_data[user.id]['from_lunch'] = current_time
            elif 'from_lunch' in attendance_data[user.id] and 'leaving_time' not in attendance_data[user.id]:
                attendance_data[user.id]['leaving_time'] = current_time


message_handler = MessageHandler(
    Filters.text & ~Filters.command, collect_attendance)
dispatcher.add_handler(message_handler)

# def generate_attendance_table(update: Update, context):
#     now = datetime.now()
#     current_date = now.strftime("%Y-%m-%d")

#     # Initialize PDF object and set up the page
#     pdf = UnicodePDF()
#     pdf.add_page()
#     font_path = os.path.join(os.path.dirname(__file__), 'dejavu-sans-ttf-2.37', 'DejaVuSans.ttf')
#     pdf.add_font('DejaVuSans', '', font_path, uni=True)
#     pdf.set_font('DejaVuSans', '', 12)

#     pdf.cell(15, 15, 'ID')
#     pdf.cell(30, 15, 'User')
#     pdf.cell(40, 15, 'Date')
#     pdf.cell(30, 15, 'Came')
#     pdf.cell(30, 15, 'To Lunch')
#     pdf.cell(30, 15, 'From Lunch')
#     pdf.cell(30, 15, 'Left')
#     pdf.ln()

#     for id_counter, (user_id, data) in enumerate(attendance_data.items(), start=1):
#         user_name = data.get('name', '')
#         coming_time = data.get('coming_time', '')
#         to_lunch = data.get('to_lunch', '')
#         from_lunch = data.get('from_lunch', '')
#         leaving_time = data.get('leaving_time', '')

#         insert_query = '''
#         INSERT INTO attendance (name, date, coming_time, to_lunch, from_lunch, leaving_time)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         '''
#         cursor.execute(insert_query, (user_name, current_date, coming_time, to_lunch, from_lunch, leaving_time))

#         # Add data to the PDF
#         pdf.cell(15, 15, str(id_counter))
#         pdf.cell(30, 15, str(user_name))
#         pdf.cell(40, 15, str(current_date))
#         pdf.cell(30, 15, str(coming_time))
#         pdf.cell(30, 15, str(to_lunch))
#         pdf.cell(30, 15, str(from_lunch) if to_lunch and from_lunch != '' else '')
#         pdf.cell(30, 15, str(leaving_time) if to_lunch and from_lunch and leaving_time != '' else '')
#         pdf.ln()

#     # Commit the database changes and close the connection
#     connection.commit()
#     cursor.close()
#     connection.close()

#     # Save the PDF file
#     pdf_file = 'Attendance.pdf'
#     pdf.output(pdf_file)

#     # Send the PDF file to the user
#     with open(pdf_file, 'rb') as file:
#         context.bot.send_document(chat_id=update.effective_chat.id, document=file, caption='Davomod hisoboti')

#     # Remove the PDF file
#     os.remove(pdf_file)

#     # Send a message to notify the user
#     context.bot.send_message(chat_id=update.effective_chat.id, text='Attendance data inserted into the database and PDF sent')


def generate_attendance_table(update: Update, context):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    # Initialize PDF object and set up the page
    pdf = UnicodePDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(
        __file__), 'dejavu-sans-ttf-2.37', 'DejaVuSans.ttf')
    pdf.add_font('DejaVuSans', '', font_path, uni=True)
    pdf.set_font('DejaVuSans', '', 12)

    pdf.cell(15, 15, 'ID')
    pdf.cell(30, 15, 'User')
    pdf.cell(40, 15, 'Date')
    pdf.cell(30, 15, 'Came')
    pdf.cell(30, 15, 'To Lunch')
    pdf.cell(30, 15, 'From Lunch')
    pdf.cell(30, 15, 'Left')
    pdf.ln()

    # Open a new cursor
    with connection.cursor() as cursor:
        for id_counter, (user_id, data) in enumerate(attendance_data.items(), start=1):
            user_name = data.get('name', '')
            coming_time = data.get('coming_time', '')
            to_lunch = data.get('to_lunch', '')
            from_lunch = data.get('from_lunch', '')
            leaving_time = data.get('leaving_time', '')

            insert_query = '''
            INSERT INTO attendance (name, date, coming_time, to_lunch, from_lunch, leaving_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (user_name, current_date,
                           coming_time, to_lunch, from_lunch, leaving_time))

            # Add data to the PDF
            pdf.cell(15, 15, str(id_counter))
            pdf.cell(30, 15, str(user_name))
            pdf.cell(40, 15, str(current_date))
            pdf.cell(30, 15, str(coming_time))
            pdf.cell(30, 15, str(to_lunch))
            pdf.cell(30, 15, str(from_lunch)
                     if to_lunch and from_lunch != '' else '')
            pdf.cell(30, 15, str(leaving_time)
                     if to_lunch and from_lunch and leaving_time != '' else '')
            pdf.ln()

        # Commit the database changes
        connection.commit()

    
    pdf_file = 'Attendance.pdf'
    pdf.output(pdf_file)

   
    with open(pdf_file, 'rb') as file:
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=file, caption='Davomod hisoboti')

   
    os.remove(pdf_file)

    
    # context.bot.send_message(chat_id=update.effective_chat.id,
    #                          text='data inserted to database')


hisob_handler = CommandHandler('hisob', generate_attendance_table)
dispatcher.add_handler(hisob_handler)


def show_menu(update: Update, context):
    menu_options = [
        ['/start', '/menu'],
        ['/help'],
        ['+'],
        ['-'],
        ['/hisob'],
    ]
    reply_markup = ReplyKeyboardMarkup(menu_options, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please select an option:", reply_markup=reply_markup)


# Register the menu command handler
menu_handler = CommandHandler('menu', show_menu)
dispatcher.add_handler(menu_handler)

updater.start_polling()
updater.idle()
