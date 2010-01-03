from django.db import models
from django.db.models import permalink


class GameManager(models.Manager):
    def get_games_with_player(self, username):
        return self.filter(models.Q(kills__victim__username=username) | models.Q(kills__killer__username=username)).distinct()

class Game(models.Model):
    details = models.TextField()
    hash = models.TextField()

    objects = GameManager()

    _players = None

    @property
    def players(self):
        if self._players is None:
            kills = Kill.objects.filter(game=self)
            for kill in kills:
                players.append(kill.killer)
                players.append(kill.victim)
            self._players = list(set(players))
        return self._players

    def __unicode__(self):
        return self.hash

    @permalink
    def get_absolute_url(self):
        return ('game_detail', None, {
            'hash': self.hash,
        })

class Weapon(models.Model):
    name = models.CharField(max_length=255, null=True)
    ut_name = models.CharField(max_length=255)

    _kill_counts = None

    def __unicode__(self):
        return self.ut_name

    @permalink
    def get_absolute_url(self):
        return ('weapon_detail', None, {
            'ut_name': self.ut_name,
        })

    def get_kills_by_player(self):
        if self._kill_counts is None:
            kill_counts = []
            players = Player.objects.all().order_by('username')
            for player in players:
                kills = Kill.objects.filter(weapon=self, killer=player).count()
                if kills:
                    kill_counts.append({
                        'killer': player,
                        'username': player.username,
                        'count': kills,
                    })
        return self.kill_counts

class Player(models.Model):
    username = models.CharField(max_length=255)
    kills = models.ManyToManyField("self", through="Kill", symmetrical=False)

    _victims = None
    _weapon_counts = None

    def __unicode__(self):
        return self.username

    @permalink
    def get_absolute_url(self):
        return ('player_detail', None, {
            'username': self.username,
        })

    def get_games_played(self):
        return -1

    def get_kill_ratio(self):
        return float(Kill.objects.filter(killer=self).count() + 1) / float(Kill.objects.filter(victim=self).count() + 1)

    def get_victims(self):
        if self._victims_count is None:
            victim_count = []
            players = Player.objects.all().order_by('username')
            for player in players:
                kills = Kill.objects.filter(killer=self, victim=player).count()
                if kills:
                    victim_count.append(
                        {
                            'victim': player,
                            'count': kills,
                        }
                    )
        return self._victim_count

    def get_kills_by_weapon(self):
        if self._weapon_counts is None:
            weapon_counts = []
            weapons = Weapon.objects.all()
            for weapon in weapons:
                kills = Kill.objects.filter(killer=self, weapon=weapon).count()
                if kills:
                    weapon_counts.append({
                        'weapon': weapon,
                        'count': kills,
                    })
        return self._weapon_counts

class Kill(models.Model):
    killer = models.ForeignKey(Player, related_name="victims")
    victim = models.ForeignKey(Player, related_name="killers")
    weapon = models.ForeignKey(Weapon)
    game = models.ForeignKey(Game, related_name="kills")

    def __unicode__(self):
        return "%s killed by %s with %s" % (self.victim, self.killer, self.weapon)

class BodyPart(models.Model):
    name = models.CharField(max_length=255, null=True)
    ut_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.ut_name

class Hit(models.Model):
    attacker = models.ForeignKey(Player, related_name="hits_made")
    casualty = models.ForeignKey(Player, related_name="hits_incurred")
    body_part = models.ForeignKey(BodyPart)
    game = models.ForeignKey(Game, related_name="hits_per_game")

    def __unicode__(self):
        return "%s was hit by %s in the %s" % (self.victim.username, self.attacker.username, self.body_part_ut_name)
