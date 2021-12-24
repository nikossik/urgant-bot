import telebot

import warnings
warnings.filterwarnings('ignore')

import config
from qg import *


TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)

qg = QgTrans(GoogleTranslator(source='russian', target='english'), 
				GoogleTranslator(source='english', target='russian'), 
				pipeline("e2e-qg", model="valhalla/t5-base-e2e-qg")) 


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello, this bot generates question about specific celebrity. Send me the name of celebrity on the russian language!')

@bot.message_handler(content_types=['text'])
def load_celeb(message):
	celebrity = message.text
	bot.send_message(message.chat.id ,f'Got celebrity name: {celebrity}')

	preds = qg.predict(celebrity)

<<<<<<< HEAD
	try:
		if len(preds) == 0:
			bot.send_message(message.chat.id, 'Error, nothing was generated!')
		else:
			bot.send_message(message.chat.id , 'Successfully generated questions!')
			print(preds[:10])

			text = ''
			i = 0	

			for corpus in enumerate(preds):
				for question in corpus:
					text += f'{i+1}. {question} \n'
					i+=1

			bot.send_message(message.chat.id, text)
	except:
		bot.send_message(message.chat.id, 'Something went wrong!')
=======
	if len(preds) == 0:
		bot.send_message(message.chat.id, 'Error, nothing was generated!')
	else:
		bot.send_message(message.chat.id , 'Successfully generated questions!')
		print(preds[:10])

		text = ''

		for i, question in enumerate(preds[:10]):
			text += f'{i+1}. {question} \n'

		bot.send_message(message.chat.id, text)

>>>>>>> 2fa13066d55c29dc6b495650edc1cd1eda36c7f0

print('Bot started!')
bot.polling()

