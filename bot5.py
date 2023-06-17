import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from fpdf import FPDF
import unicodedata
import os
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Telegram bot token (replace 'YOUR_BOT_TOKEN' with your bot token)
TOKEN = '6082028232:AAG0tngUrjsf7HvPO_HOFddVr2Uiw2o5J8s'
# Create an instance of the Updater class
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


class UnicodePDF(FPDF):
    def header(self):
        # Add a custom header if needed
        pass

    def footer(self):
        # Add a custom footer if needed
        pass


def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Attendance Bot!")


# Register the start command handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def help(update:Update, context):
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


def collect_attendance(update: Update, context):
    message_text = update.message.text.strip()
    user = update.message.from_user
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if message_text == '+':
        if user.id not in attendance_data:
            attendance_data[user.id] = {
                'name': user.first_name, 'coming_time': current_time}
    elif message_text == '-':
        if user.id in attendance_data:
            attendance_data[user.id]['leaving_time'] = current_time


# Register the message handler to collect attendance
message_handler = MessageHandler(
    Filters.text & ~Filters.command, collect_attendance)
dispatcher.add_handler(message_handler)


def generate_attendance_table(update: Update, context):
    pdf = UnicodePDF()
    pdf.add_page() 
    #pdf.set_font('Arial', 'B', 15)
   
    font_path = os.path.join(os.path.dirname(__file__), 'dejavu-sans-ttf-2.37', 'DejaVuSans.ttf')
    pdf.add_font('DejaVuSans', '', font_path, uni=True)
    pdf.set_font('DejaVuSans', '', 15)

    pdf.cell(15, 15, 'ID')
    pdf.cell(50, 15, 'User')    
    pdf.cell(50, 15, 'Date')
    pdf.cell(50, 15, 'Coming Time')
    pdf.cell(50, 15, 'Leaving Time')
    pdf.ln()

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")  # Define current_date here

    id_counter = 1 
    for user_id, data in attendance_data.items():
        user_name = data.get('name', '')
        coming_time = data.get('coming_time', '')
        leaving_time = data.get('leaving_time', '')

        # user_name = unicodedata.normalize('NFKD', user_name).encode(
        #     'ascii', 'ignore').decode('utf-8')
        user_name = str(user_name)

        pdf.cell(15, 15, str(id_counter)) 
        pdf.cell(50, 15, user_name or '')
        pdf.cell(50, 15, current_date)
        pdf.cell(50, 15, coming_time or '')
        pdf.cell(50, 15, leaving_time or '')
        pdf.ln()
        id_counter += 1

    pdf_file = 'Attendance.pdf'
    pdf.output(pdf_file)

    # Send the PDF file to the user who requested it
    with open(pdf_file, 'rb') as file:
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=file, caption='Davomod hisoboti')


hisob_handler = CommandHandler('hisob', generate_attendance_table)
dispatcher.add_handler(hisob_handler)
def show_menu(update: Update, context):
    menu_options = [
        ['/start', '/menu'],  # List of available commands/options
        ['/help'],# to give information
        ['+'],  # Attend
        ['-'],  # Leave
        ['/hisob'],  # Generate attendance table
    ]
    reply_markup = ReplyKeyboardMarkup(menu_options, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please select an option:", reply_markup=reply_markup)


# Register the menu command handler
menu_handler = CommandHandler('menu', show_menu)
dispatcher.add_handler(menu_handler)
updater.start_polling()
updater.idle()
