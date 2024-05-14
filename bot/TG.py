import logging
import re
import os
import paramiko
from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error
from pathlib import Path
import shutil
import subprocess
load_dotenv()

TOKEN = os.getenv('TOKEN')
# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')
##########################PHONEEEEEE

def TryToSavePhones(update: Update, context):
    user_input = update.message.text # Получаем ответ пишем или нет в бд номера телефонов
    if user_input == 'да':
        update.message.reply_text('Сейчас сохраним ')
        try:
            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                      password=os.getenv('DB_PASSWORD'),
                                      host=os.getenv('DB_HOST'),
                                      port=os.getenv('DB_PORT'), 
                                      database=os.getenv('DB_DATABASE'))
            user_id = str(update.message.from_user.id) #получаем для уникального имя файа
            filename = user_id+'.tmpNUMS.txt' #Уникальный файл для чтения запросов номеров =\
            tmpFIle=open('/tmp/'+filename, 'r')
            cursor = connection.cursor()
            line = tmpFIle.readline()
            cursor.execute(line)
            connection.commit()
            while line:
                line = tmpFIle.readline()
                cursor.execute(line)
                connection.commit()
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            return ConversationHandler.END 
        finally:
            if connection:
                cursor.close()
                connection.close()
            update.message.reply_text("все сохранилось")
            tmpFIle.close() 
            os.unlink('/tmp/'+filename)
            return ConversationHandler.END

    if user_input == 'нет':
        update.message.reply_text('Не сохраняем')
        user_id = str(update.message.from_user.id) #получаем для уникального имя файа
        filename = user_id+'.tmpNUMS.txt' #Уникальный файл для чтения запросов номеров =\
        os.unlink('/tmp/'+filename)

    return ConversationHandler.END # Завершаем работу обработчика диалога


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    phoneNumRegex =  re.compile(r'(?:\+7|8)(?: \(\d{3}\) \d{3}-\d{2}-\d{2}|\d{10}|\(\d{3}\)\d{7}| \d{3} \d{3} \d{2} \d{2}| \(\d{3}\) \d{3} \d{2} \d{2}|-\d{3}-\d{3}-\d{2}-\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    user_id = str(update.message.from_user.id) #получаем для уникального имя файа
    filename = user_id+'.tmpNUMS.txt' #Уникальный файл для записи номеров =\
    tmpFIle=open('/tmp/'+filename, 'w')
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        tmpFIle.write('INSERT INTO phone_num (phone_num) VALUES (\''+ phoneNumberList[i]+'\');'+'\n') #сохранили нужные запросы в файл
    tmpFIle.close()
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text('Записать  бд? (да/нет)')

    return 'TryToSavePhones'
#############################################
##############################Mail
def TryToSaveMails(update: Update, context):
    user_input = update.message.text # Получаем ответ пишем или нет в бд имейлы
    if user_input == 'да':
        update.message.reply_text('Сейчас сохраним ')
        try:
            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                      password=os.getenv('DB_PASSWORD'),
                                      host=os.getenv('DB_HOST'),
                                      port=os.getenv('DB_PORT'), 
                                      database=os.getenv('DB_DATABASE'))
            user_id = str(update.message.from_user.id) #получаем для уникального имя файа
            filename = user_id+'.tmpMAILS.txt' #Уникальный файл для чтения запросов номеров =\
            tmpFIle=open('/tmp/'+filename, 'r')
            cursor = connection.cursor()
            line = tmpFIle.readline()
            update.message.reply_text(line)
            cursor.execute(line)
            connection.commit()
            while line:
                line = tmpFIle.readline()
                update.message.reply_text(line)
                cursor.execute(line)
                connection.commit()
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            return ConversationHandler.END 
        finally:
            if connection:
                cursor.close()
                connection.close()
            update.message.reply_text("все сохранилось")
            tmpFIle.close() 
            os.unlink('/tmp/'+filename)
            return ConversationHandler.END

    if user_input == 'нет':
        update.message.reply_text('Не сохраняем')
        user_id = str(update.message.from_user.id) #получаем для уникального имя файа
        filename = user_id+'.tmpMAILS.txt' #Уникальный файл для чтения запросов номеров =\
        os.unlink('/tmp/'+filename)

    return ConversationHandler.END # Завершаем работу обработчика диалога
def findMailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email: ')

    return 'findMail'

def findMail (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email

    mailRegex =  re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    mailList = mailRegex.findall(user_input) # Ищем  mail

    if not mailList: # Обрабатываем случай, когда emal none
        update.message.reply_text('Email не найдены')
        return # Завершаем выполнение функции
    
    mails = '' # Создаем строку, в которую будем записывать email
    user_id = str(update.message.from_user.id) #получаем для уникального имя файа
    filename = user_id+'.tmpMAILS.txt' #Уникальный файл для записи номеров =\
    tmpFIle=open('/tmp/'+filename, 'w')
    for i in range(len(mailList)):
        mails += f'{i+1}. {mailList[i]}\n' # Записываем очередной mail
        tmpFIle.write('INSERT INTO mails_s (mails_s) VALUES (\''+ mailList[i]+'\');'+'\n') #сохранили нужные запросы в файл
    tmpFIle.close()      
    update.message.reply_text(mails) # Отправляем сообщение пользователю
    update.message.reply_text('Записать  бд? (да/нет)')
    return 'TryToSaveMails' # Переходим к сохранению

###########################################
######################################PASS
def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности: ')

    return 'verify_password'

def verify_password (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email

    passwordRegex =  re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$') #Проверка сложности
    
    mailList = passwordRegex.findall(user_input) # Ищем  совпадения, если совпало то гуд пасс

    if not mailList: # Обрабатываем случай, когда emal none
        update.message.reply_text('Pass слабый')
        return # Завершаем выполнение функции
    update.message.reply_text('Pass отличный') #если нет совпадений то пас слабый

    return ConversationHandler.END # Завершаем работу обработчика диалога
#######################################
######################################get_release
def get_release (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /etc/*-release')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_uname
def get_uname (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_uptime
def get_uptime (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_df
def get_df (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_free
def get_free (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_mpstat
def get_mpstat (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_w
def get_w (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_auths
def get_auths (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_critical
def get_critical (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -p 2')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    if not data: # Обрабатываем случай, когда нет даты 
        update.message.reply_text('CriticalNoFound')
        return # Завершаем выполнение функции
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_ps
def get_ps (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_ss
def get_ss (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss | head -n 10')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_apt_list
def get_apt_list (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('apt list --installed | head -n 10')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_apt_list
def get_apt_list_comm(update: Update, context):
    update.message.reply_text('Введите пакет для поиска конкретного пакета или все ')

    return 'get_apt_list'
	

def get_apt_list (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
	
    user_input = update.message.text # Получаем текст, содержащий(или нет) имя пакета
    if user_input == 'все':
        stdin, stdout, stderr = client.exec_command('apt list --installed | head -n 15')
        data = stdout.read() + stderr.read()
        stdin.close()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data) # Отправляем сообщение пользователю
        return ConversationHandler.END # Завершаем работу обработчика диалога

    stdin, stdout, stderr = client.exec_command('apt list --installed | grep ' + user_input)
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_services
def get_services_comm(update: Update, context):
    update.message.reply_text('Введите сервис для отображения')

    return 'get_services'
	

def get_services (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
	
    user_input = update.message.text # Получаем текст, содержащий(или нет) имя пакета
    if user_input == '':
        update.message.reply_text('так не бывает') # Отправляем сообщение пользователю
        return ConversationHandler.END # Завершаем работу обработчика диалога

    stdin, stdout, stderr = client.exec_command('apt list --installed | grep ' + user_input)
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
#########################################
######################################get_repl_logs
def get_repl_logs (update: Update, context):
#    stdin, stdout, stderr = os.system('cat /tmp/logs/postgresql.log | grep replication | head -n 10')
#    data = stdout.read() + stderr.read()
#   data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    batcmd="cat /tmp/logs/postgresql.log | grep replication | head -n 10"
    result = subprocess.check_output(batcmd, shell=True)
    result = str(result).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text('nyyyy gdez e logi, ny gde ze nashi logi, davai mne syda ligi, i bydem vividit')
    update.message.reply_text(result) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога
def get_repl_logs_not_docker (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /tmp/logs/postgresql.log | grep replication | head -n 10')
    data = stdout.read() + stderr.read()
    stdin.close()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
#########################################
######################################get_emails
def get_emails (update: Update, context):
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv('DB_PASSWORD'),
                                  host=os.getenv('DB_HOST'),
                                  port=os.getenv('DB_PORT'), 
                                  database=os.getenv('DB_DATABASE'))

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM mails_s;")
        connection.commit()
        results = cursor.fetchall() 
        for row in results: 
            data= "ID: {}".format(row[0])+"  "+"Mail: {}".format(row[1])
            update.message.reply_text(data) 
    except (Exception, Error) as error:
        update.message.reply_text("Ошибка при работе с PostgreSQL: %s", error)
    finally:
	    if connection is not None:
                cursor.close()
                connection.close()
#########################################
######################################get_phone_numbers
def get_phone_numbers (update: Update, context):
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv('DB_PASSWORD'),
                                  host=os.getenv('DB_HOST'),
                                  port=os.getenv('DB_PORT'), 
                                  database=os.getenv('DB_DATABASE'))

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_num;")
        connection.commit()
        results = cursor.fetchall() 
        for row in results: 
            data= "ID: {}".format(row[0])+"  "+"PhoneNum: {}".format(row[1])
            update.message.reply_text(data) 
    except (Exception, Error) as error:
        update.message.reply_text("Ошибка при работе с PostgreSQL: %s", error)
    finally:
	    if connection is not None:
                cursor.close()
                connection.close()
#########################################

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'TryToSavePhones': [MessageHandler(Filters.text & ~Filters.command, TryToSavePhones)],
        },
        fallbacks=[]
    )

    convHandlerfindMail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findMailCommand)],
        states={
            'TryToSaveMails': [MessageHandler(Filters.text & ~Filters.command, TryToSaveMails)],
            'findMail': [MessageHandler(Filters.text & ~Filters.command, findMail)],
        },
        fallbacks=[]
    )

    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
    convHandlerget_release = ConversationHandler(
        entry_points=[CommandHandler('get_release', get_release)],
        states={
            'get_release': [MessageHandler(Filters.text & ~Filters.command, get_release)],
        },
        fallbacks=[]
    )
    convHandlerget_uname = ConversationHandler(
        entry_points=[CommandHandler('get_uname', get_uname)],
        states={
            'get_uname': [MessageHandler(Filters.text & ~Filters.command, get_uname)],
        },
        fallbacks=[]
    )
    convHandlerget_uptime = ConversationHandler(
        entry_points=[CommandHandler('get_uptime', get_uptime)],
        states={
            'get_uptime': [MessageHandler(Filters.text & ~Filters.command, get_uptime)],
        },
        fallbacks=[]
    )
    convHandlerget_df = ConversationHandler(
        entry_points=[CommandHandler('get_df', get_df)],
        states={
            'get_df': [MessageHandler(Filters.text & ~Filters.command, get_df)],
        },
        fallbacks=[]
    )
    convHandlerget_free = ConversationHandler(
        entry_points=[CommandHandler('get_free', get_free)],
        states={
            'get_free': [MessageHandler(Filters.text & ~Filters.command, get_free)],
        },
        fallbacks=[]
    )
    convHandlerget_mpstat = ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', get_mpstat)],
        states={
            'get_mpstat': [MessageHandler(Filters.text & ~Filters.command, get_mpstat)],
        },
        fallbacks=[]
    )
    convHandlerget_w = ConversationHandler(
        entry_points=[CommandHandler('get_w', get_w)],
        states={
            'get_w': [MessageHandler(Filters.text & ~Filters.command, get_w)],
        },
        fallbacks=[]
    )
    convHandlerget_auths = ConversationHandler(
        entry_points=[CommandHandler('get_auths', get_auths)],
        states={
            'get_auths': [MessageHandler(Filters.text & ~Filters.command, get_auths)],
        },
        fallbacks=[]
    )
    convHandlerget_critical = ConversationHandler(
        entry_points=[CommandHandler('get_critical', get_critical)],
        states={
            'get_critical': [MessageHandler(Filters.text & ~Filters.command, get_critical)],
        },
        fallbacks=[]
    )
    convHandlerget_ps = ConversationHandler(
        entry_points=[CommandHandler('get_ps', get_ps)],
        states={
            'get_ps': [MessageHandler(Filters.text & ~Filters.command, get_ps)],
        },
        fallbacks=[]
    )
    convHandlerget_ss = ConversationHandler(
        entry_points=[CommandHandler('get_ss', get_ss)],
        states={
            'get_ss': [MessageHandler(Filters.text & ~Filters.command, get_ss)],
        },
        fallbacks=[]
    )
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_comm)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    convHandlerget_services = ConversationHandler(
        entry_points=[CommandHandler('get_services', get_services_comm)],
        states={
            'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services)],
        },
        fallbacks=[]
    )
    convHandlerget_repl_logs = ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', get_repl_logs)],
        states={
            'get_repl_logs': [MessageHandler(Filters.text & ~Filters.command, get_repl_logs)],
        },
        fallbacks=[]
    )
    convHandlerget_emails = ConversationHandler(
        entry_points=[CommandHandler('get_emails', get_emails)],
        states={
            'get_emails': [MessageHandler(Filters.text & ~Filters.command, get_emails)],
        },
        fallbacks=[]
    )
    convHandlerget_phone_numbers = ConversationHandler(
        entry_points=[CommandHandler('get_phone_numbers', get_phone_numbers)],
        states={
            'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, get_phone_numbers)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerfindMail)
    dp.add_handler(convHandlerverify_password)
    dp.add_handler(convHandlerget_release)
    dp.add_handler(convHandlerget_uname)
    dp.add_handler(convHandlerget_uptime)
    dp.add_handler(convHandlerget_df)
    dp.add_handler(convHandlerget_free)
    dp.add_handler(convHandlerget_mpstat)
    dp.add_handler(convHandlerget_w)
    dp.add_handler(convHandlerget_auths)
    dp.add_handler(convHandlerget_critical)
    dp.add_handler(convHandlerget_ps)
    dp.add_handler(convHandlerget_ss)
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(convHandlerget_services)
    dp.add_handler(convHandlerget_repl_logs)
    dp.add_handler(convHandlerget_emails)
    dp.add_handler(convHandlerget_phone_numbers)


	# Регистрируем обработчик текстовых сообщений
    #dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
