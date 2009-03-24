from django import template
register = template.Library()
from sandbox.ut.models import Player, Game, Kill

class GetKillsNode(template.Node):
    def __init__(self, killer, victim, game=None):
       self.killer, self.victim, self.game = killer, victim, game    

    def render(self, context):
        try:
            killer = template.resolve_variable(self.killer, context)
            victim = template.resolve_variable(self.victim, context)
        except template.VariableDoesNotExist:
            return ''
        if self.game is not None:
            game = template.resolve_variable(self.game, context)        
            return Kill.objects.filter(killer=killer, victim=victim, game=game).count()        
        else:
            return Kill.objects.filter(killer=killer, victim=victim).count()
        
        
def do_kills(parser, token):
    """
    Syntax::
        {% get_kills killer victim [game] %}

    Example usage::

        {% get_kills killer victim %}
    """
    bits = token.contents.split()
    if len(bits) != 3 and len(bits) != 4:
        raise template.TemplateSyntaxError, "'%s' tag takes 2 or 3 arguments" % bits[0]    
    if len(bits) == 3:
        return GetKillsNode(bits[1], bits[2])
    return GetKillsNode(bits[1], bits[2], bits[3])

class GetTotalKillsNode(template.Node):
    def __init__(self, killer, game=None):
       self.killer, self.game = killer, game    

    def render(self, context):
        try:
            killer = template.resolve_variable(self.killer, context)
        except template.VariableDoesNotExist:
            return ''
        if self.game is not None:
            game = template.resolve_variable(self.game, context)        
            return Kill.objects.filter(killer=killer, game=game).count()        
        else:
            return Kill.objects.filter(killer=killer).count()
        
        
def do_total_kills(parser, token):
    """
    Syntax::
        {% get_total_kills killer [game] %}
    """
    bits = token.contents.split()
    if len(bits) != 2 and len(bits) != 3:
        raise template.TemplateSyntaxError, "'%s' tag takes 1 or 2 arguments" % bits[0]    
    if len(bits) == 2:
        return GetTotalKillsNode(bits[1])
    return GetTotalKillsNode(bits[1], bits[2])

class GetTotalDeathsNode(template.Node):
    def __init__(self, victim, game=None):
       self.victim, self.game = victim, game    

    def render(self, context):
        try:
            victim = template.resolve_variable(self.victim, context)
        except template.VariableDoesNotExist:
            return ''
        if self.game is not None:
            game = template.resolve_variable(self.game, context)        
            return Kill.objects.filter(victim=victim, game=game).count()        
        else:
            return Kill.objects.filter(victim=victim).count()
        
        
def do_total_deaths(parser, token):
    """
    Syntax::
        {% get_total_deaths victim [game] %}
    """
    bits = token.contents.split()
    if len(bits) != 2 and len(bits) != 3:
        raise template.TemplateSyntaxError, "'%s' tag takes 1 or 2 arguments" % bits[0]    
    if len(bits) == 2:
        return GetTotalDeathsNode(bits[1])
    return GetTotalDeathsNode(bits[1], bits[2])


class GetKillRatioNode(template.Node):
    def __init__(self, player, game=None):
       self.player, self.game = player, game    

    def render(self, context):
        try:
            player = template.resolve_variable(self.player, context)            
        except template.VariableDoesNotExist:
            return ''
        if self.game is not None:
            try:
                game = template.resolve_variable(self.game, context)
            except template.VariableDoesNotExist:
                return ''
            else:
                try:
                    return float(Kill.objects.filter(killer=player, game=game).count()) / float(Kill.objects.filter(victim=player, game=game).count())
                except ZeroDivisionError:
                    return "NaN"
        else:
            try:
                return float(Kill.objects.filter(killer=player).count()) / float(Kill.objects.filter(victim=player).count())
            except ZeroDivisionError:
                return "NaN"

def do_kill_ratio(parser, token):
    """
    Syntax::
        {% get_kill_ratio player [game] %}

    """
    bits = token.contents.split()
    if len(bits) != 2 and len(bits) != 3:
        raise template.TemplateSyntaxError, "'%s' tag takes 1 or 2 arguments" % bits[0]    
    if len(bits) == 2:
        return GetKillRatioNode(bits[1])
    else:
        return GetKillRatioNode(bits[1], bits[2])

class GetPlayersNode(template.Node):
    def __init__(self, killers, victims, game=None):
       self.killers, self.victims, self.game = killers, victims, game    

    def render(self, context):
        try:
            if self.game is not None:
                game = template.resolve_variable(self.game, context)                
                kills = Kill.objects.filter(game=game)
                victims = [kill.victim for kill in kills]
                killers = [kill.killer for kill in kills]
                context[self.killers] = context[self.victims] = list(set(victims + killers))
            else:
                context[self.killers] = context[self.victims] = Player.objects.all()
        except template.VariableDoesNotExist:
            return ''
        return ''
        

def do_players(parser, token):
    """
    Syntax::
        {% get_players [game] as killers victims %}

    """
    bits = token.contents.split()
    if len(bits) != 4 and len(bits) != 5:
        raise template.TemplateSyntaxError, "'%s' tag takes 3 or 4 arguments" % bits[0]    
    if len(bits) == 4:
        return GetPlayersNode(bits[2], bits[3])
    else:
        return GetPlayersNode(bits[3], bits[4], bits[1])
    
    
register.tag('get_kills', do_kills)
register.tag('get_total_deaths', do_total_deaths)
register.tag('get_total_kills', do_total_kills)
register.tag('get_kill_ratio', do_kill_ratio)
register.tag('get_players', do_players)
