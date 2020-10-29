# welcome
import importlib as imp  
import os
import gtts
import getpass
import playsound as ps; imp.reload(ps)

from gtts import gTTS

def Speak(var):
    if var == 'hello':
        try:
            t1 = 'Hello' + getpass.getuser()
            t2 = '..........Welcome to Investment R......deep.'
            t3 = '.........You can start by pressing Auto or Manual button'
            T = t1 + t2 + t3        
            language = 'en'
            welcomeObj = gTTS(text=T, lang=language, slow=False)
            welcomeObj.save('hello.mp3')
            #os.system('mpg321 welcome.mp3')
            ps.playsound('hello.mp3', block=False)
        except:
            print('cannot play hello.mp3')
        return
    elif var == 'adv':
        try:
            t1 = 'Advance Settings Menu..........'
            t2 = '..........Window.......... length........... is how long you intend to look back...........'
            t3 = '..........Window.......... future........... is how far you intend to look forward...........'
            t4 = '..........If you are unsure.......... reset to default'
            T = t1 + t2 + t3 + t4      
            language = 'en'
            welcomeObj = gTTS(text=T, lang=language, slow=False)
            welcomeObj.save('adv.mp3')
            #os.system('mpg321 welcome.mp3')
            ps.playsound('adv.mp3', block=False)
        except:
            print('cannot play adv.mp3')
    elif var == 'Buy':
        try:
            t1 = 'Buy recommended'
            T = t1 
            language = 'en'
            welcomeObj = gTTS(text=T, lang=language, slow=False)
            welcomeObj.save('buy.mp3')
            #os.system('mpg321 welcome.mp3')
            ps.playsound('buy.mp3', block=False)
        except:
            print('cannot play buy.mp3')
    elif var == 'Hold':
        try:
            t1 = 'Hold recommended'
            T = t1 
            language = 'en'
            welcomeObj = gTTS(text=T, lang=language, slow=False)
            welcomeObj.save('hold.mp3')
            #os.system('mpg321 welcome.mp3')
            ps.playsound('hold.mp3', block=False)
        except:
            print('cannot play hold.mp3')
    return