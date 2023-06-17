import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from fpdf import FPDF
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Telegram bot token (replace 'YOUR_BOT_TOKEN' with your bot token)
TOKEN = '6082028232:AAG0tngUrjsf7HvPO_HOFddVr2Uiw2o5J8s'

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

def help(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
                                This bot allows users to mark their attendance by sending "+" or "-" messages.
                                It collects attendance information such as user name, date, and arrival/departure times,
                                and stores it in a PostgreSQL database. The attendance data can be retrieved and
                                displayed as a PDF report.""")

help_handler = CommandHandler('help', help)

def collect_attendance(update: Update, context):
    message_text = update.message.text.strip()
    user = update.message.from_user
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if message_text == '+':
        try:
            # Store the attendance record
            # You can add your logic here to store the data in the desired format or database
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Attendance recorded successfully.")
        except Exception as error:
            logging.error("Error while recording attendance: %s", str(error))
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Failed to record attendance.")

    elif message_text == '-':
        try:
            # Store the exit time record
            # You can add your logic here to store the data in the desired format or database
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Exit time recorded successfully.")
        except Exception as error:
            logging.error("Error while recording exit time: %s", str(error))
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Failed to record exit time.")

collect_attendance_handler = MessageHandler(Filters.text & (~Filters.command), collect_attendance)

def generate_attendance_table(update: Update, context):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    # Generate the PDF table
    pdf = UnicodePDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'User')
    pdf.cell(40, 10, 'Date')
    pdf.cell(40, 10, 'Entry Time')
    pdf.cell(40, 10, 'Exit Time', ln=True)

    try:
        # Fetch attendance data from the database or any other source
        # You can add your logic here to fetch the attendance data
        # and populate the PDF table

        # Save the PDF file
        filename = f"attendance_{current_date}.pdf"
        pdf.output(filename)

        # Send the PDF file to the user
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filename, 'rb'))

        # Delete the PDF file
        os.remove(filename)
    except Exception as error:
        logging.error("Error while generating attendance table: %s", str(error))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to generate table.")

generate_attendance_table_handler = CommandHandler('generate_table', generate_attendance_table)

def main():
    # Create an instance of the Updater class
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register the handlers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(collect_attendance_handler)
    dispatcher.add_handler(generate_attendance_table_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
