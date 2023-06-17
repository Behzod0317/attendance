import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from fpdf import FPDF
import os
import psycopg2

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Telegram bot token (replace 'YOUR_BOT_TOKEN' with your bot token)
TOKEN = '6082028232:AAG0tngUrjsf7HvPO_HOFddVr2Uiw2o5J8s'

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'attendance'
DB_USER = 'attendanceuser'
DB_PASSWORD = 'password1708'

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
cursor = connection.cursor()

# SQL query to create the table
create_table_query = '''
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    "came" TIMESTAMPTZ[],
    "left" TIMESTAMPTZ[]
);
'''

# Execute the query
# cursor.execute(create_table_query)

# Commit the changes and close the connection
connection.commit()
# cursor.close()
# connection.close()

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
                                This bot allows users to mark their attendance by sending "+" or "-" messages.
                                It collects attendance information such as user name, date, and arrival/departure times,
                                and stores it in a PostgreSQL database. The attendance data can be retrieved and
                                displayed as a PDF report.""")


help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)
# def collect_attendance(update: Update, context):
#     message_text = update.message.text.strip()
#     user = update.message.from_user
#     now = datetime.now()
#     current_time = now.strftime("%H:%M")
#     current_date = now.strftime("%Y-%m-%d")

#     if message_text == '+':
#         try:
#             came_time = datetime.strptime(current_time, "%H:%M")
#             with connection:
#                 with connection.cursor() as cursor:
#                     query = "INSERT INTO attendance (name, date, came) VALUES (%s, %s, ARRAY[%s]::TIMESTAMPTZ[])"
#                     cursor.execute(query, (user.first_name, current_date, came_time))

#             # context.bot.send_message(chat_id=update.effective_chat.id,
#             #                          text="Attendance recorded successfully.")
#         except (Exception, psycopg2.Error) as error:
#             logging.error("Error while recording attendance: %s", str(error))
#             # context.bot.send_message(chat_id=update.effective_chat.id,
#             #                          text="Failed to record attendance.")


#     elif message_text == '-':
#         try:
#             left_time = datetime.strptime(current_time, "%H:%M")
#             with connection:
#                 with connection.cursor() as cursor:
#                     #query = "UPDATE attendance SET left = ARRAY[%s]::TIMESTAMPTZ[] WHERE name = %s AND date = %s"
#                     query = 'UPDATE attendance SET "left" = ARRAY[%s]::TIMESTAMPTZ[] WHERE name = %s AND date = %s'

#                     cursor.execute(query, (left_time, user.first_name, current_date))

#             # context.bot.send_message(chat_id=update.effective_chat.id,
#             #                          text="Exit time recorded successfully.")
#         except (Exception, psycopg2.Error) as error:
#             logging.error("Error while recording exit time: %s", str(error))
#             # context.bot.send_message(chat_id=update.effective_chat.id,
#             #                          text="Failed to record exit time.")
# def collect_attendance(update: Update, context):
#     message_text = update.message.text.strip()
#     user = update.message.from_user
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     current_date = now.strftime("%Y-%m-%d")
def collect_attendance(update: Update, context):
    message_text = update.message.text.strip()
    user = update.message.from_user
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if message_text == '+':
        try:
            came_time = datetime.strptime(current_time, "%H:%M")
            with connection.cursor() as cursor:
                query = "INSERT INTO attendance (name, date, came) VALUES (%s, %s::date, ARRAY[%s]::TIMESTAMPTZ[])"
                cursor.execute(query, (user.first_name, current_date, came_time))

            connection.commit()  # Commit the changes to the database
            # context.bot.send_message(chat_id=update.effective_chat.id,
            #                          text="Attendance recorded successfully.")
        except (Exception, psycopg2.Error) as error:
            logging.error("Error while recording attendance: %s", str(error))
            # context.bot.send_message(chat_id=update.effective_chat.id,
            #                          text="Failed to record attendance.")

    elif message_text == '-':
        try:
            left_time = datetime.strptime(current_time, "%H:%M")
            with connection.cursor() as cursor:
                query = 'UPDATE attendance SET "left" = ARRAY[%s]::TIMESTAMPTZ[] WHERE name = %s AND date = %s::date'
                cursor.execute(query, (left_time, user.first_name, current_date))

            connection.commit()  # Commit the changes to the database
            # context.bot.send_message(chat_id=update.effective_chat.id,
            #                          text="Exit time recorded successfully.")
        except (Exception, psycopg2.Error) as error:
            logging.error("Error while recording exit time: %s", str(error))
            # context.bot.send_message(chat_id=update.effective_chat.id,
            #                          text="Failed to record exit time.")


collect_attendance_handler = MessageHandler(Filters.text & (~Filters.command), collect_attendance)
dispatcher.add_handler(collect_attendance_handler)

def generate_attendance_table(update: Update, context):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    # Generate the PDF table
    pdf = UnicodePDF()
    pdf.add_page()
    # pdf.set_font('Arial', 'B', 12)
    font_path = os.path.join(os.path.dirname(__file__), 'dejavu-sans-ttf-2.37', 'DejaVuSans.ttf')
    pdf.add_font('DejaVuSans', '', font_path, uni=True)
    pdf.set_font('DejaVuSans', '', 15)

    pdf.cell(15, 15, 'ID')
    pdf.cell(30, 15, 'User')
    pdf.cell(40, 15, 'Date')
    pdf.cell(35, 15, 'Entry Time')
    pdf.cell(35, 15, 'Exit Time', ln=True)

    try:
        # Fetch attendance data from the database
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT * FROM attendance WHERE date = %s"
                cursor.execute(query, (current_date,))
                rows = cursor.fetchall()

        for row in rows:
            pdf.cell(15, 15, str(row[0]))  # Assuming the ID column is the first column
            pdf.cell(30, 15, row[2])
            pdf.cell(40, 15, row[3])
            came_times = [dt.strftime("%H:%M:%S") for dt in row[4]]
            pdf.cell(35, 15, ', '.join(came_times))
            left_times = [dt.strftime("%H:%M:%S") for dt in row[5]]
            pdf.cell(35, 15, ', '.join(left_times), ln=True)

        # Save the PDF file
        filename = f"attendance_{current_date}.pdf"
        pdf.output(filename)

        # Send the PDF file to the user
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(filename, 'rb'))

        # Delete the PDF file
        os.remove(filename)
    except (Exception, psycopg2.Error) as error:
        logging.error("Error while generating attendance table: %s", str(error))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to generate table.")


generate_attendance_table_handler = CommandHandler('hisob', generate_attendance_table)
dispatcher.add_handler(generate_attendance_table_handler)


def main():
    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
 