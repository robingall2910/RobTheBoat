import os
import shutil
import traceback
import configparser

from .exceptions import HelpfulError


class ConfigDefaults:
    email = None
    password = None
    token = None

    owner_id = None
    command_prefix = '.'
    bound_channels = set()
    autojoin_channels = set()

    default_volume = 0.15
    white_list_check = False
    skips_required = 4
    skip_ratio_required = 0.5
    save_videos = True
    now_playing_mentions = False
    auto_summon = True
    auto_playlist = True
    auto_pause = True
    delete_messages = True
    delete_invoking = False
    log_masterchannel = None
    log_subchannels = set()
    log_exceptions = False
    log_interaction = False
    log_downloads = False
    log_timeformat = '%H:%M:%S'
    options_file = 'config/login.ini'
    blacklist_file = 'config/blacklist.txt'
    whitelist_file = 'config/whitelist.txt'
    excel_file = 'config/excel/discord-auto-login-c480a18f18c9.json'
    challonge_file = 'config/challonge/challonge.ini'
    saying_file = 'config/jokes/funny.ini'

    options_file = 'config/options.ini'
    blacklist_file = 'config/blacklist.txt'
    whitelist_file = 'config/whitelist.txt'
    auto_playlist_file = 'config/autoplaylist.txt' # this will change when I add playlists

class ChallongeGroup:
    def __init__(self, name, section_data):
        self.name = name

        self.username = section_data.get('Username', fallback=None)
        self.Api_Key = section_data.get('API_Key', fallback=None)
    
class ChallongeConfig(object):
    def __init__(self, config_file):
        self.challonge_config_file = config_file
        self.challonge_config = configparser.ConfigParser()
        if not self.challonge_config.read(config_file):
            print('[config] Config file not found, copying example_challonge.ini')
            import os, shutil, traceback
             
            try:
                shutil.copy('config/challonge/example_challonge.ini', config_file)

                print("\nPlease configure config/challonge/example_challonge.ini and restart the bot.", flush=True)
                os._exit(1)

            except FileNotFoundError as e:
                traceback.print_exc()
                print("\nWhat happened to your configs?", flush=True)
                os._exit(2)

            except Exception as e:
                traceback.print_exc()
                print("\nUnable to copy config/challonge/example_challonge.ini to %s: %s" % (config_file, e), flush=True)
                os._exit(3)
        print('Reading challonge config file')
        self.challonge_default_group = ChallongeGroup('Default', self.challonge_config['Default'])
        self.challonge_groups = set()

        for section in self.challonge_config.sections():
            self.challonge_groups.add(ChallongeGroup(section, self.challonge_config[section]))
    
    def for_user(self, user):
        '''
        Returns the first PermissionGroup a user belongs to
        :param user: A discord User or Member object
        '''

        for group in self.challonge_groups:
            if str(user) in group.name:
                return group

        # The only way I could search for roles is if I add a `server=None` param and pass that too
        if type(user) == discord_User:
            return self.challonge_default_group

        return self.challonge_default_group

    def create_group(self, name, **kwargs):
        self.config.read_dict({name:kwargs})
        self.groups.add(PermissionGroup(name, self.config[name]))
        # TODO: Test this
    
    def configSectionsExist(self, _section):
        """ configSectionsExist: 
                If true, section does exist in config file
                If false, section does not exist in config file
        """
        return self.challonge_config.has_section(_section)

    def getBySection(self, _sectionName, _sectionContent):
        if(self.configSectionsExist(_sectionName)):
            if self.challonge_config.get(_sectionName, _sectionContent):
                arrayLst = self.challonge_config.get(_sectionName, _sectionContent)
                return arrayLst
            else:
                return "Option does not exist"
        else:
            return "Section does not exist"

class Organization():
    def __init__(self):
        self.organization = None
        self.name = None
        self.website = None
        self.rules = None
        self.checkin_guidelines = None
        self.faq = None
        self.twitch = None
        self.streamme = None
        self.server_id = None
    def setServerId(self, _id):
        self.server_id = _id
    def getServerId(self):
        return self.server_id
    def setOrganization(self, _organization):
        self.organization = _organization
    def getOrganization(self):
        return self.organization
    def setName(self, _name):
        self.name = _name
    def setWebsite(self, _website):
        self.website = _website
    def getWebsite(self):
        return self.website
    def setRules(self, _rules):
        self.rules = _rules
    def getRules(self):
        return self.rules
    def setCheckinGuidelines(self, _guide):
        self.checkin_guidelines = _guide
    def getCheckinGuidelines(self):
        return self.checkin_guidelines
    def setFAQ(self, _faq):
        self.faq = _faq
    def getFAQ(self):
        return self.faq
    def setTwitch(self, _twitch):
        self.twitch = _twitch
    def getTwitch(self):
        return self.twitch
    def setStreamme(self, _streamme):
        self.streamme = _streamme
    def getStreamme(self):
        return self.streamme

class Saying:
    def __init__(self, _saying_file):
        self.saying_file = _saying_file
        sayingConfig = configparser.ConfigParser()
        if not sayingConfig.read(_saying_file):
            print('[config] Config file not found, copying example_login.ini')
            import os, shutil, traceback
            try:
                shutil.copy('config/jokes/example_funny.ini', _saying_file)

                print("\nPlease configure config/jokes/funny.ini and restart the bot.", flush=True)
                os._exit(1)

            except FileNotFoundError as e:
                traceback.print_exc()
                print("\nWhat happened to your configs?", flush=True)
                os._exit(2)

            except Exception as e:
                traceback.print_exc()
                print("\nUnable to copy config/jokes/example_funny.ini to %s: %s" % (_saying_file, e), flush=True)
                os._exit(3)
        sayingConfig.read(_saying_file)
        self.nudes = sayingConfig.get('Sayings', 'nudes', fallback=0)
        self.config = sayingConfig
    def setNudes(self, _nudes):
        self.nudes = _nudes
    def getNudes(self):
        return self.nudes
    def writeFunnyConfigLst(self, PATH = 'config/jokes/funny.ini'):
        print("Path Name: " + PATH)
        #print("Path OS: " + str(os.path.dirname(PATH)))
        #print("Path exist: " + str(os.path.exists(os.path.dirname(PATH))))
        if not os.path.exists(os.path.dirname(PATH)):
            print("Path does not exists")
            os.makedirs(os.path.dirname(PATH), exist_ok=True)
            with open(PATH, 'w') as configfile:
                self.config.write(configfile)
        else:
            if not os.path.exists(PATH):
                with open(PATH, 'w') as configfile:
                    self.config.write(configfile)
            else:
                if not os.path.isfile(PATH) or not os.access(PATH, os.R_OK):
                    PATH = './config/jokes/funny.ini'
                with open(PATH, 'w+') as configfile:
                    self.config.write(configfile)

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        config = configparser.ConfigParser()

        if not config.read(config_file, encoding='utf-8'):
            print('[config] Config file not found, copying example_options.ini')

            try:
                shutil.copy('config/example_options.ini', config_file)

                # load the config again and check to see if the user edited that one
                c = configparser.ConfigParser()
                c.read(config_file, encoding='utf-8')

                if not int(c.get('Permissions', 'OwnerID', fallback=0)): # jake pls no flame
                    print("\nPlease configure config/options.ini and restart the bot.", flush=True)
                    os._exit(1)

            except FileNotFoundError as e:
                raise HelpfulError(
                    "Your config files are missing.  Neither options.ini nor example_options.ini were found.",
                    "Grab the files back from the archive or remake them yourself and copy paste the content "
                    "from the repo.  Stop removing important files!"
                )

            except ValueError: # Config id value was changed but its not valid
                print("\nInvalid value for OwnerID, config cannot be loaded.")
                # TODO: HelpfulError
                os._exit(4)

            except Exception as e:
                print(e)
                print("\nUnable to copy config/example_options.ini to %s" % config_file, flush=True)
                os._exit(2)

        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file, encoding='utf-8')

        confsections = {"Credentials", "Permissions", "Chat", "MusicBot", "Logging"}.difference(config.sections())
        if confsections:
            raise HelpfulError(
                "One or more required config sections are missing.",
                "Fix your config.  Each [Section] should be on its own line with "
                "nothing else on it.  The following sections are missing: {}".format(
                    ', '.join(['[%s]' % s for s in confsections])
                ),
                preface="An error has occured parsing the config:\n"
            )

        self._email = config.get('Credentials', 'Email', fallback=ConfigDefaults.email)
        self._password = config.get('Credentials', 'Password', fallback=ConfigDefaults.password)
        self._login_token = config.get('Credentials', 'Token', fallback=ConfigDefaults.token)

        self.auth = None

        #generic stuff
        self.owner_id = config.get('Permissions', 'OwnerID', fallback=ConfigDefaults.owner_id)
        self.command_prefix = config.get('Chat', 'CommandPrefix', fallback=ConfigDefaults.command_prefix)
        self.bound_channels = config.get('Chat', 'BindToChannels', fallback=ConfigDefaults.bound_channels)
        self.autojoin_channels = config.get('Chat', 'AutojoinChannels', fallback=ConfigDefaults.autojoin_channels)

        #default musicbot settings
        self.default_volume = config.getfloat('MusicBot', 'DefaultVolume', fallback=ConfigDefaults.default_volume)
        self.white_list_check = config.getboolean('MusicBot', 'WhiteListCheck', fallback=ConfigDefaults.white_list_check)
        self.skips_required = config.getint('MusicBot', 'SkipsRequired', fallback=ConfigDefaults.skips_required)
        self.skip_ratio_required = config.getfloat('MusicBot', 'SkipRatio', fallback=ConfigDefaults.skip_ratio_required)
        self.save_videos = config.getboolean('MusicBot', 'SaveVideos', fallback=ConfigDefaults.save_videos)
        self.now_playing_mentions = config.getboolean('MusicBot', 'NowPlayingMentions', fallback=ConfigDefaults.now_playing_mentions)
        self.auto_summon = config.getboolean('MusicBot', 'AutoSummon', fallback=ConfigDefaults.auto_summon)
        self.auto_playlist = config.getboolean('MusicBot', 'UseAutoPlaylist', fallback=ConfigDefaults.auto_playlist)
        self.auto_pause = config.getboolean('MusicBot', 'AutoPause', fallback=ConfigDefaults.auto_pause)
        self.delete_messages  = config.getboolean('MusicBot', 'DeleteMessages', fallback=ConfigDefaults.delete_messages)
        self.delete_invoking = config.getboolean('MusicBot', 'DeleteInvoking', fallback=ConfigDefaults.delete_invoking)

        #blacklisting files
        self.blacklist_file = config.get('Files', 'BlacklistFile', fallback=ConfigDefaults.blacklist_file)
        self.whitelist_file = config.get('Files', 'WhitelistFile', fallback=ConfigDefaults.whitelist_file)
        self.auto_playlist_file = config.get('Files', 'AutoPlaylistFile', fallback=ConfigDefaults.auto_playlist_file)

        #logging
        self.log_masterchannel = config.get('Logging', 'MasterChannel', fallback=ConfigDefaults.log_masterchannel)
        self.log_subchannels = config.get('Logging', 'SubChannels', fallback=ConfigDefaults.log_subchannels)
        self.log_exceptions = config.getboolean('Logging', 'Exceptions', fallback=ConfigDefaults.log_exceptions)
        self.log_interaction = config.getboolean('Logging', 'Interaction', fallback=ConfigDefaults.log_interaction)
        self.log_downloads = config.getboolean('Logging', 'Downloads', fallback=ConfigDefaults.log_downloads)
        self.log_timeformat = config.get('Logging', 'TimeFormat', fallback=ConfigDefaults.log_timeformat)

        #blacklist
        self.userslist = config.get('Security', 'users', fallback=None)
        self.userslist_check = config.getboolean('Security', 'whitelist', fallback=False)
        self.admins = config.get('Security', 'admins', fallback=self.owner_id)
        
        #Channels
        self.channels = config.get('Channel', 'channels', fallback=None)
        self.whitelistchannels = config.getboolean('Channel', 'whitelist', fallback=False)
        
        #Excel
        self.excel_email = config.get('Excel', 'Email', fallback=None)
        
        #Files
        self.blacklist_file = config.get('Files', 'BlacklistFile', fallback=ConfigDefaults.blacklist_file)
        self.whitelist_file = config.get('Files', 'WhitelistFile', fallback=ConfigDefaults.whitelist_file)
        self.excel_file = config.get('Files', 'ExcelFile', fallback=ConfigDefaults.excel_file)
        self.challonge_file = config.get('Files', 'ChallongeFile', fallback=ConfigDefaults.challonge_file)
        self.saying_file = config.get('Files', 'SayingFile', fallback=ConfigDefaults.saying_file)

        #Organization
        self.organization = Organization()
        self.organization.organization = config.get('Organization',
                                                    'organization',
                                                    fallback=None)
        self.organization.name = config.get('Organization',
                                            'organization_name',
                                            fallback=None)
        self.organization.website = config.get('Organization',
                                               'organization_website',
                                               fallback=None)
        self.organization.rules = config.get('Organization',
                                             'organization_website_rules',
                                             fallback=None)
        self.organization.checkin_guidelines = config.get('Organization',
                                                          'organization_checkin_guidelines',
                                                          fallback=None)
        self.organization.faq = config.get('Organization',
                                           'organization_faq',
                                           fallback=None)
        self.organization.twitch = config.get('Organization',
                                              'organization_twitch',
                                              fallback=None)
        self.organization.streamme = config.get('Organization',
                                                'organization_streamme',
                                                fallback=None)
        self.organization.server_id = config.get('Organization',
                                                 'organization_server_id',
                                                 fallback=None)
        self.organization.prohibit_channels = config.get('Organization',
                                                         'organization_prohibit_channels',
                                                         fallback = set())
        #Tournament
        self.casters = config.get('Tournament', 'casters', fallback=None)#self.manipulateSettings('Tournament', 'casters')
        #self.caster1 = config.get('Tournament', 'caster1', fallback=None)
        #self.caster2 = config.get('Tournament', 'caster2', fallback=None)
        #self.caster3 = config.get('Tournament', 'caster3', fallback=None)
        self.tourneychannel = config.get('Tournament', 'tourneychannel', fallback=None)
        self.tourneylobby = config.get('Tournament', 'lobby', fallback=None)
        
        #Funny catch phrases
        self.funny = Saying(self.saying_file)

        self.run_checks()


    def run_checks(self):
        """
        Validation logic for bot settings.
        """
        confpreface = "An error has occurred reading the config:\n"

        if self._email or self._password:
            if not self._email:
                raise HelpfulError(
                    "The login email was not specified in the config.",

                    "Please put your bot account credentials in the config.  "
                    "Remember that the Email is the email address used to register the bot account.",
                    preface=confpreface)

            if not self._password:
                raise HelpfulError(
                    "The password was not specified in the config.",

                    "Please put your bot account credentials in the config.",
                    preface=confpreface)

            self.auth = (self._email, self._password)

        elif not self._login_token:
            raise HelpfulError(
                "No login credentials were specified in the config.",

                "Please fill in either the Email and Password fields, or "
                "the Token field.  The Token field is for Bot accounts only.",
                preface=confpreface
            )

        else:
            self.auth = (self._login_token,)


        if self.owner_id and self.owner_id.isdigit():
            if int(self.owner_id) < 10000:
                raise HelpfulError(
                    "OwnerID was not set.",

                    "Please set the OwnerID in the config.  If you "
                    "don't know what that is, use the %sid command" % self.command_prefix,
                    preface=confpreface)

        else:
            raise HelpfulError(
                "An invalid OwnerID was set.",

                "Correct your OwnerID.  The ID should be just a number, approximately "
                "18 characters long.  If you don't know what your ID is, "
                "use the %sid command.  Current invalid OwnerID: %s" % (self.command_prefix, self.owner_id),
                preface=confpreface)

        if self.bound_channels:
            try:
                self.bound_channels = set(x for x in self.bound_channels.split() if x)
            except:
                print("[Warning] BindToChannels data invalid, will not bind to any channels")
                self.bound_channels = set()

        if self.autojoin_channels:
            try:
                self.autojoin_channels = set(x for x in self.autojoin_channels.split() if x)
            except:
                print("[Warning] AutojoinChannels data invalid, will not autojoin any channels")
                self.autojoin_channels = set()

        if self.log_subchannels:
            try:
                self.log_subchannels = set(x for x in self.log_subchannels.split() if x)
            except:
                print("[Warning] LogSubChannels data invalid, will not log to any subchannels")
                self.log_subchannels = set()

        self.delete_invoking = self.delete_invoking and self.delete_messages

    def setCommandPrefix(self, _prefix):
        self.command_prefix = _prefix

    def getCommandPrefix(self):
        return self.command_prefix

    def discord_user_email(self):
        """ email: the discord login email address of the bot """
        return self.username

    def discord_user_password(self):
        """ password: the bot's discord password """
        return self.password
        
    def UserWhiteList(self):
        """ 
        whitelist: If true, only Users and Admins will be able to issue non-admin
        commands to the bot; if false, Users are prohibited from issuing commands
        but all others may issue non-admin commands. Default: True
        """
        return self.userslist_check #config.get("Security", "whitelist")

    def userList(self):
        """ Users: A list of users; behaviour determined by whitelist setting """
        return self.userslist #config.get("Security", "Users")

    def adminList(self):
        """ Admins: A list of users who will have admin access to the bot """
        return self.admins #config.get("Security", "Admins")
        
    def channelList(self):
        """ Channel: A list of channels accessable to the bot """
        return self.channels #config.get("Channel", "channels")
        
    def getTourneyChannel(self):
        """ Channel: the Tourney Channel id """
        return self.tourneychannel #config.get('Tournament', 'tourneychannel')

    def casterLst(self):
        return self.casters #config.get('Tournament', 'casters')

    def getOwner(self):
        """ User: the owner of the bot """
        return self.owner_id #getOwnerId("login", "ownerId")

    def getLobbyChannel(self):
        """ Channel: the lobby Channel id """
        return self.tourneylobby #config.get('Tournament', 'lobby')

    def getDebugBool(self):
        return self.debug_mode #config.get('Debug', 'debugToggle')

    def ChannelWhiteList(self):
        """
        whitelist: If true, bot will join the channels listed, if False, will join all except those listed
        """
        return self.whitelistchannels #config.get("Channel", "whitelist")

    def configSectionList(self):
        return self.config.sections()
        
    def configSectionsExist(self, _section):
        """ configSectionsExist: 
                If true, section does exist in config file
                If false, section does not exist in config file
        """
        return self.config.has_section(_section)

    
    def getSettings(self, PATH='./config/login.ini'):
        """ Reads in the config file """
        self.__init__(PATH)
    
    def manipulateSettings(self, _sectionName, _sectionContent):
        if(self.configSectionsExist(_sectionName)):
            if self.config.get(_sectionName, _sectionContent):
                arrayLst = self.config.get(_sectionName, _sectionContent).split("\n")
                #pop first arrayLst
                arrayLst.pop(0)
                return arrayLst
            else:
                print('Option is not existent')
                return None
        else:
            print('Section is not existing')
            return None

    def getOwnerId(_sectionName, _sectionContent):
        if(configSectionsExist(_sectionName)):
            if self.config.get(_sectionName, _sectionContent):
                return self.config.get(_sectionName, _sectionContent)
            else:
                return "Option does not exist"
        else:
            return "Section does not exist"
            
    def addToList(_sectionName, _sectionContent, _contentID):
        #validating to see if sectionName and sectionContent exist
        manSectionHolder = manipulateSettings(_sectionName, _sectionContent)
        if type(manSectionHolder) is list:
            #valid response
            if _contentID not in manSectionHolder:
                manSectionHolder.append(_contentID)
                config.set(_sectionName, _sectionContent, "\n".join(manSectionHolder))
                return "Configuration has been modified and has been overwritten."
            else:
                if(_sectionContent == ("Channels")):
                    return "<#" + _contentID + "> already exists in the " + _sectionContent + " list."
                else:
                    return "<@" + _contentID + "> already exists in the " + _sectionContent + " list."
        else:
            return manSectionHolder
        #return "Validating to see if ID is already in list"
    def removeToList(_sectionName, _sectionContent,_contentID):
        manSectionHolder = manipulateSettings(_sectionName, _sectionContent)
        if type(manSectionHolder) is list:
            #valid response
            if (_contentID in manSectionHolder):
                userOwnerId = getOwnerId("login", "ownerId")
                if userOwnerId == _contentID and (_sectionContent == ("Admins")):
                    return "<@" + userOwnerId + "> cannot be removed from the " + _sectionContent + " list due to ownership of the bot."
                else:
                    manSectionHolder.remove(_contentID)
                    config.set(_sectionName, _sectionContent, "\n".join(manSectionHolder))
                return "Configuration has been modified and has been overwritten."
            else:
                if(_sectionContent == ("Channels")):
                    return "<#" + _contentID + "> is not in the " + _sectionContent + " list."
                else:
                    return "<@" + _contentID + "> is not in the " + _sectionContent + " list."
        else:
            return manSectionHolder

    def writeConfigLst(PATH = '.\config\options.ini'):
        #print("Path Name: " + PATH)
        #print("Path OS: " + str(os.path.dirname(PATH)))
        #print("Path exist: " + str(os.path.exists(os.path.dirname(PATH))))
        if not os.path.exists(os.path.dirname(PATH)):
            print("Path does not exists")
            os.makedirs(os.path.dirname(PATH), exist_ok=True)
            with open(PATH, 'w') as configfile:
                config.write(configfile)
        else:
            if not os.path.exists(PATH):
                with open(PATH, 'w') as configfile:
                    config.write(configfile)
            else:
                if not os.path.isfile(PATH) or not os.access(PATH, os.R_OK):
                    PATH = '.\config\options.ini'
                with open(PATH, 'w+') as configfile:
                    config.write(configfile)

    # TODO: Add save function for future editing of options with commands
    #       Maybe add warnings about fields missing from the config file

    def write_default_config(self, location):
        pass


# These two are going to be wrappers for the id lists, with add/remove/load/save functions
# and id/object conversion so types aren't an issue
class Blacklist:
    pass

class Whitelist:
    pass
