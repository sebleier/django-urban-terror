#!/usr/bin/env python
import md5
from django.conf import settings
from sandbox.ut.models import Game, Player, Kill, Weapon, BodyPart, Hit

class PlayerBlackListedError(Exception):
    pass

class ParserError(Exception):
    pass

class UTLogParser(object):
    players = []

    def __init__(self):
        self.actions = {
            "Kill": self.parse_kill,
            "Hit": self.parse_hit,
        }

    def parse_log(self, file_path):
        file = open(file_path)
        self.parse_games(file)

    def parse_games(self, file):
        lines = []
        for line in file:
            lines.append(line)
        for i in range(len(lines)):
            line = lines[i]
            parts = line.split()
            if len(parts) > 1 and parts[1] == "InitGame:":
                game_details = []
                game_detail = line
                while True:
                    if len(lines) == i:
                        break
                    line = lines[i]
                    parts = line.split()
                    if len(parts) > 1:
                        if parts[1] == "InitGame":
                            game_detail
                            i -= 1
                            break
                        if parts[1] != "ShutdownGame:":
                            game_details.append(line)
                        else:
                            hash = md5.new(str(game_details)).hexdigest()
                            try:
                                Game.objects.get(hash=hash)
                                print "Hash already exists: %s" % hash
                            except Game.DoesNotExist:
                                print hash
                                game = Game(details=game_detail, hash=hash)
                                game.save()
                                self.parse_game(game, game_details)
                            break
                    i += 1
                i += 1

    def parse_game(self, game, game_details):
        for detail in game_details:
            parts = detail.split()
            if len(parts) <= 1:
                continue
            try:
                action = parts[1][:-1]
                self.actions[action](game, parts)
            except (KeyError, ParserError):
                continue

    def validate_users(self, *args):
        """
        Goes through each player in the positional arguments and checks if
        they are in the BLACKLIST and if they have an alias.  If they are
        blacklisted, then an Exception is raised
        """
        players = []
        blacklist = getattr(settings, "BLACKLIST", [])
        aliases = getattr(settings, "ALIASES", {})
        for player in args:
            if player in blacklist:
                raise PlayerBlackListedError("player: %s is blacklisted" % player)
            if player in aliases.keys():
                players.append(aliases[player])
            else:
                players.append(player)
        return players

    def parse_kill(self, game, parts):
        """
        Log syntax:
            16:05 Kill: 4 2 30: spazcowz killed matt_c by UT_MOD_AK103
        """
        try:
            killer_name, victim_name, weapon_name = parts[5], parts[7], parts[9]
        except IndexError:
            raise ParserError()
        try:
            killer_name, victim_name = self.validate_users(killer_name, victim_name)
        except PlayerBlackListedError, e:
            return
        else:            
            killer, created = Player.objects.get_or_create(username=killer_name)
            victim, created = Player.objects.get_or_create(username=victim_name)
            weapon, created = Weapon.objects.get_or_create(ut_name=weapon_name)
            kill = Kill(game=game, killer=killer, victim=victim, weapon=weapon)
            kill.save()

    def parse_hit(self, game, parts):
        """
        Log Syntax:
            15:46 Hit: 4 3 0 6: djangopony hit spazcowz in the Head
        """
        print game        
        try:
            attacker_name, casualty_name, body_part_name = parts[6], parts[8], parts[11]
        except IndexError:            
            raise ParserError()
        try:
            attacker_name, casualty_name = self.validate_users(attacker_name, casualty_name)
        except PlayerBlackListedError, e:
            return
        else:
            attacker, created = Player.objects.get_or_create(username=attacker_name)
            casualty, created = Player.objects.get_or_create(username=casualty_name)
            body_part, created = BodyPart.objects.get_or_create(ut_name=body_part_name)
            hit = Hit(game=game, attacker=attacker, casualty=casualty, body_part=body_part)
            hit.save()

if __name__=='__main__':
    import os
    parser = UTLogParser()
    os.chdir(os.path.dirname(__file__))
    os.chdir("../logs")
    for file in os.listdir("."):
        if file.startswith('.') or file[-4:] != ".log":
            continue
        file_path = os.path.join(os.getcwd(), file)
        parser.parse_log(file_path)

