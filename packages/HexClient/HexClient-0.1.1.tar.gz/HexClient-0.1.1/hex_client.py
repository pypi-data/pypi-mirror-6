import argparse
import os
import json
import requests
from hex_connection import HexConnection, HexCommunicationError
import spellbook

class Quit(Exception):
    pass

class HexClient(object):

    def __init__(self, hex_server='http://localhost:6543'):
        self.conn = HexConnection(hex_server=hex_server)

    def start(self):
        try:
            print self.messages['hex']
            print self.messages['welcome']
            username = self._get_user_name()
            if username: 
                print self.messages['logged_in'] % {'name':username}
            else:
                print self.messages['not_logged_in']
            self.show_options()
        except Quit:
            print self.messages['goodbye']
        except HexCommunicationError:
            print self.messages['server_error']
        
    def show_options(self):
        options = self._get_options()
        print self.messages['present_options']
        for option in options:
            print self.messages[option]
        while True:
            choice = raw_input(self.messages['prompt_option']).upper()
            if choice in options:
                self._perform_action(choice)
                return True
            else:
                print self.messages['invalid_option']

    def _get_options(self):
        options = []
        if self._get_user_name():
            options.append("SPELL")
            options.append("STATUS")
            options.append("LOGOUT")
        else:
            options.append("SIGNUP")
            options.append("LOGIN")
        options.append("QUIT")
        return options
    
    def _perform_action(self, action):
        {
            "STATUS": self.get_account_status,
            "LOGOUT": self.log_out,
            "SIGNUP": self.sign_up,
            "LOGIN" : self.log_in,
            "SPELL" : self.show_spell_menu,
            "QUIT"  : self.quit
        }[action]()
        self.show_options()

    def show_spell_menu(self):
        spellOptions = self._get_spell_options()
        print self.messages['present_spell_options']
        for option in spellOptions:
            print self.messages[option]
        while True:
            choice = raw_input(self.messages['prompt_option']).upper()
            if choice in spellOptions:
                self.cast_spell(choice)
                return True
            else:
                print self.messages['invalid_option']

    def _get_spell_options(self):
        response = self.conn.get_user(self._get_user_name())
        points = response['user']['points']
        spells = ["COLOR"]
        if points > 2:
            spells.append("SPIRIT")
        spells.append("FLAME")
        spells.append("BACK")
        return spells

    # TODO Pull out these strings
    def cast_spell(self, spell):
        if spell == 'BACK':
            return False
        if spell == 'COLOR':
            self.cast_spell_color()
        if spell == 'FLAME':
            self.cast_spell_flame()
        if spell == 'SPIRIT':
            self.cast_spell_spirit()
        self.show_spell_menu()

    def cast_spell_color(self):
        color = self._get_color()
        account = self._get_saved_credentials()
        self._create_spell(account['name'], account['animal'], 
                'Color', spellbook.spell_color(color))

    def cast_spell_spirit(self):
        print "Choose a background color:"
        background = self._get_color()
        print "And now choose a color for the spirit"
        spirit = self._get_color()
        account = self._get_saved_credentials()
        self._create_spell(account['name'], account['animal'], 
                'Spirit', spellbook.spell_spirit(background, spirit))

    def cast_spell_flame(self):
        print "Choose a background color:"
        background  = self._get_color(intensity=100)
        print "And now choose a color for the flame"
        flame = self._get_color(intensity=240)
        account = self._get_saved_credentials()
        self._create_spell(account['name'], account['animal'], 
                'Flame', spellbook.spell_flame(background, flame))

    def _create_spell(self, username, animal, name, spell):
        spellCreation = self.conn.create_spell(username, animal, 
                name, spell)
        if spellCreation['result'] == 'OK':
            print "Your spell has been cast."
        else:
            print "Error creating your spell"

    def _get_color(self, intensity=200):
        colors = []
        for color in ['red', 'green', 'blue']:
            while True:
                userInput = raw_input("How much %s do you want? (0-15) " % color)
                if userInput.isdigit():
                    colorValue = int(userInput)
                    if 0 <= colorValue and colorValue <= 15:
                        colors.append(colorValue)
                        break
                print "Sorry, please enter a number between 0 and 15..."  
        colors.append(intensity)
        return colors

    def log_in(self):
        name = raw_input(self.messages['prompt_name'])
        animal = raw_input(self.messages['prompt_animal'])
        self._log_in(name, animal)

    def _log_in(self, name, animal):
        if self.conn.authenticate(name, animal):
            try:
                with open(self._hexfile(), 'w') as hexfile:
                    hexfile.write(json.dumps({'name': name, 'animal': animal}))
                print self.messages['logged_in'] % {'name': self._get_user_name()}
            except:
                print self.messages['login_error'] 
        else:
            print self.messages['invalid_login'] % {'name': name, 'animal': animal}

    def log_out(self):
        os.remove(self._hexfile())
        print self.messages['not_logged_in']

    def sign_up(self):
        username = None
        while not username: 
            proposedName = raw_input(self.messages['choose_username'])
            if self.conn.get_user(proposedName)['result'] == 'ERROR':
                username = proposedName
            else:
                print self.messages['name_not_available']
        animal = raw_input(self.messages['choose_animal'])
        creation = self.conn.create_user(username, animal)
        if creation['result'] == 'OK':
            print self.messages['user_created'] % creation['user']['name']
            self._log_in(username, animal)
        else:
            print self.messages['account_creation_error']
            
    def quit(self):
        raise Quit()
    
    def get_account_status(self):
        response = self.conn.get_user(self._get_user_name())
        if response['result'] == 'OK':
            print self.messages['account_status'] % response['user']
        

    def _hexfile(self):
        return os.path.join('/users', os.getlogin(), '.hexfile')

    def _get_user_name(self):
        "Look up the username from the saved login credentials"
        account = self._get_saved_credentials()
        if account: 
            return account['name']
        else:
            return False

    def _get_saved_credentials(self):
        "Look up the saved login credentials"
        try:
            with open(self._hexfile()) as hexfile:
                return json.loads(hexfile.read())
        except:
            return False
        
    messages = {
        "welcome"           : "Welcome to the hex. You can cast spells here.",
        "logged_in"         : "You are currently logged in as %(name)s.",
        "not_logged_in"     : "You are not logged in.",
        "invalid_login"     : "Sorry, we don't know any wizards named %(name)s with a %(animal)s for a spirit animal.",
        "name_not_available": "Sorry, there's already a wizard with that name",
        "prompt_name"       : "What is your wizard name? ",
        "prompt_animal"     : "What is your spirit animal? ",
        "prompt_option"     : "Please choose an option: ",
        "login_error"       : "Sorry, there was an error logging in",
        "present_options"   : "\nPlease choose from the following options:",
        "present_spell_options"   : "You know how to cast the following spells:",
        "invalid_option"    : "Sorry, that's not an option.",
        "choose_username"   : "Choose your new wizard name: ",
        "choose_animal"     : "All wizards have spirit animals. What's yours? ",
        "user_created"      : "Wizard %s has been created",
        "goodbye"           : "We'll see you later.",
        "account_status"    : "Your name is %(name)s and you currently have %(points)s points. You can currently cast spells lasting %(spell_duration)s seconds. Keep casting to unlock more powerful spells.",
        "server_error"      : "Sorry, there was a problem talking to the hex server",
        "account_creation_error": "There was a problem creating your account",
        "account_lookup_err": "There was a problem looking up your account",
        "STATUS"            : "  STATUS  Show your account status",
        "LOGOUT"            : "  LOGOUT  Log out",
        "LOGIN"             : "  LOGIN   Log in",
        "SIGNUP"            : "  SIGNUP  Sign up as a new wizard",
        "SPELL"             : "  SPELL   Cast a spell",
        "QUIT"              : "  QUIT    Exit hex client",
        "BACK"              : "  BACK    Don't cast a spell right now",
        "COLOR"             : "  COLOR   Cast the color spell",
        "SPIRIT"            : "  SPIRIT  Cast the spirit spell",
        "FLAME"             : "  FLAME   Cast the flame spell",
         "hex"              : """
           / \ / \ / \ / \ 
          |   |   |   |   |
         / \ / \ / \ / \ / \ 
        |   |   |   |   |   |
       / \ / \ / \ / \ / \ / \ 
      |   |   |   |   |   |   |
     / \ / \ / \ / \ / \ / \ / \ 
    |   |   |   |   |   |   |   |
     \ / \ / \ / \ / \ / \ / \ /
      |   |   |   |   |   |   |
       \ / \ / \ / \ / \ / \ /
        |   |   |   |   |   |
         \ / \ / \ / \ / \ / 
          |   |   |   |   |
           \ / \ / \ / \ / 
"""      
    }

if __name__ == '__main__':
    hexClient = HexClient(hex_server='http://hex.local')
    hexClient.start()









