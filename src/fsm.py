from transitions.extensions import GraphMachine
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction

# global variable

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def start(self, event):
        text = event.message.text
        return text.lower() == "start"
    
    def move(self, event):
        text = event.message.text
        return True