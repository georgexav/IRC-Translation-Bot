# IRC Translation Bot

IRC Translation Bot translates PRIVMSG messages received in a specified IRC channel (the ___source___ channel) and sends them to another specified IRC channel (the ___target___ channel).

Sometimes you want to participate in the source channel conversation but the primary language used there may not be a language you know.
IRC Translation Bot helps with this by sending the translated messages to the target channel.
This enables you to get the gist of the conversation.  At the same time, since the translated messages go to a separate channel, there is no extra message traffic in the source channel on account of the translation.

This project was started in the __#nightfly__ channel on Dalnet where the primary language is Swedish. However, since the source and destination channels are configurable, the bot can be used elsewhere too.

IRC Translation Bot uses a locally running LibreTranslate server to do the translation. These are the dependencies:

* Python 3.10.*
* LibreTranslate
* langcodes
* langdetect

Use _pip_ to install dependencies.

___Note___
LibreTranslate currently works with Python 3.8 thru 3.10.  At the time of this writing, more recent versions of Python do not work.

## Configuration file

IRC Translation Bot uses a JSON-format configuration file as shown below:

{  
  "server" : "bitcoin.uk.eu.dal.net",  
  "port" : "6697",  
  "nickname" : "bot9",  
  "password" : "",  
  "real_name" : "asi9''s translation bot",  
  "source_channel" : "nightfly",  
  "target_channel" : "nightfly_en",  
  "target_lang" : "en",  
  "libre_translate_url" : "http://127.0.0.1:5000/translate",  
  "max_seconds_without_ping" : "600",  
  "max_ping_tries" : "3"  
}


## Usage

_python irc_client.py [configuration_file_path]_

The configuration file path can be specified as the first command line argument to the program.
If no argument is specified on the command line, the program will look for a file named TranslationBotConfig.json in the user's home directory.

## Bot Commands

__About__ command

Type _!botnick about_ in the channel to display information about the bot.  botnick is the nick assigned to the bot in the configuration file.

__Stats__ command  

Type _!botnick stats_ in the channel to display basic statistics about bot activity.  botnick is the nick assigned to the bot in the configuration file.
