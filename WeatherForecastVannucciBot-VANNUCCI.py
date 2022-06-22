import requests, json, datetime, telebot

class WeatherAPI():

    def __init__(self, apiKey:str):
        self.APIKey = apiKey
        self.CurrentCity = 'Montevideo'

    def getCurrentCity(self):
        return self.CurrentCity
    
    def setCurrentCity(self, cityName):
        self.CurrentCity = cityName

    def getWeather(self):
        APIURL = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'.format(self.CurrentCity ,self.APIKey)
        apiRequest = requests.get(APIURL)
        JSONFile = json.loads(apiRequest.content)
        if JSONFile['cod'] == '404':#API Error: {"cod":"404","message":"city not found"}
            return ['APIError']
        else:
            hora_UTC = datetime.datetime.fromtimestamp(JSONFile['dt'])
            #Search time, Current Temperature, Thermal sensation, Minimum temperature, Maximum temperature and Country code
            return [hora_UTC.strftime('%d-%m-%Y %H:%M:%S'), JSONFile['main']['temp'], JSONFile['main']['feels_like'], JSONFile['main']['temp_min'], JSONFile['main']['temp_max'], JSONFile['sys']['country']]


#Wather API and TelegramBot object initialization
WEATHERTOKEN = 'IngresarToken'
weatherAPI = WeatherAPI(WEATHERTOKEN)
BOTTOKEN = 'IngresarToken'
telegramBot = telebot.TeleBot(BOTTOKEN)
#Create our required counters
messagesCounter = 0
weatherCallsCounter = 0
#Stored time which bot was a first time called
initialBotDateTime:str = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')

#Answer to /start command
@telegramBot.message_handler(commands=['start'])
def WelcomeMessage(message):
    global messagesCounter
    #Counter increased
    messagesCounter += 1
    contactMethod = ''
    if message.chat.type == "private":
        contactMethod = 'Private chat'
    elif message.chat.type == "group":
        contactMethod = 'Group chat'
    elif message.chat.type == "supergroup":
        contactMethod = 'Super Group chat'
    elif message.chat.type == "channel":
        contactMethod = 'Channel'
    telegramBot.reply_to(message, "Hello! Nice to meet you!\nI hope you are doing well!\nThank you for reaching me out via this {}\nI will be glad to assist you.\nPlease type 'WeatherForecast' or 'CounterMessages'.".format(contactMethod))
    

#Answer to /end command
@telegramBot.message_handler(commands=['end'])
def ClosureMessage(message):
    global messagesCounter
    #Counter increased
    messagesCounter += 1
    telegramBot.reply_to(message, 'Bye!\nI really have enjoyed our time together')

#Possible user messages related to greetings or farewalls
greetingsMessagesList:list = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening']
farewallsMessagesList:list = ['goodbye', 'bye', 'good night', 'see you']
#Predifine answer to user greetings or farewalls
def GreetingMessage():
    return 'Hi!\nHow are you today?'
def FarewallMessage():
    return '\nSee you later\nHave a great day!'

#Answers to user messages
@telegramBot.message_handler(func=lambda message: True)
def Handle_all_message(message):
    global messagesCounter
    #Counter increased
    messagesCounter += 1
    botUserMessage:str = message.text
    if 'weatherforecast' in botUserMessage.lower():
        weatherCity = telegramBot.reply_to(message, 'Do you want to know current weather information in some place?\nPlease type your desired city.')
        telegramBot.register_next_step_handler(weatherCity, CallWeatherApi)
    elif 'countermessages' in botUserMessage.lower():
        telegramBot.reply_to(message, ShowCountersInformation())
    elif botUserMessage.lower() in greetingsMessagesList:
        telegramBot.reply_to(message, GreetingMessage())
    elif botUserMessage.lower() in farewallsMessagesList:
        telegramBot.reply_to(message, FarewallMessage())
    else:
        telegramBot.reply_to(message, "I\'m so sorry but I could not understand your last message\nPlease type 'WeatherForecast' or 'CounterMessages'")#:changed,{}'.format(message.text))

def ShowCountersInformation():
    currentTime:str = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    return "From {} to {}\nyou have sent me {} messages and have asked {} times for Weather Forecast information.\nPlease type 'WeatherForecast' or 'CounterMessages'".format(initialBotDateTime, currentTime, messagesCounter, weatherCallsCounter)

def CallWeatherApi(cityReceived):
    global weatherCallsCounter
    #Counter increased
    weatherCallsCounter += 1
    botUserCity = cityReceived.text
    weatherAPI.setCurrentCity(botUserCity)
    apiRequest:list = weatherAPI.getWeather()
    botAnswer = ''
    if apiRequest[0] == 'APIError':
        botAnswer = 'Ops!\nSorry, but \"{}\" is not a valid city to search for data.'.format(botUserCity)
    else:
        botAnswer = "Weather conditions of {}.\nSearch time: {}\nCurrent Temperature: {}\nThermal sensation: {}\nMinimum temperature: {}\nMaximum temperature: {}\nCountry code: {}\nPlease type 'WeatherForecast' or 'CounterMessages'".format(botUserCity, apiRequest[0], apiRequest[1], apiRequest[2], apiRequest[3], apiRequest[4], apiRequest[5])
    telegramBot.reply_to(cityReceived, botAnswer)

telegramBot.polling()
