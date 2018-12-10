import sys
from calendarbot import Chatbot

    def test_welcome():
        Chatbot.welcome()  #since this method will only print it will not return any value, so we will aseert None, and just check if this method was excuted or not
        assert Chatbot.welcome() == None
