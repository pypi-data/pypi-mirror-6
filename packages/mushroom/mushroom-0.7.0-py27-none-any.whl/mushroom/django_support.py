

class RunserverCommand(BaseCommand):
    server_class = None




class Command(RunserverCommand):
    server_class = Gameserver
