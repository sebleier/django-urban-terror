from django.shortcuts import render_to_response
from django.db import models
from django.http import HttpResponse
from django.template import Template
from django.utils import simplejson as json
from django.views.generic import list_detail
from sandbox.ut.models import Player, Game, Weapon

def stats(request):
    killers = Player.objects.all()
    victims = Player.objects.all()
    games = Game.objects.all().order_by("-id")[0:20]
    context = {
        'games': games,        
    }
    return render_to_response("ut/stats.html", context)

def player_kill_to_death_ratio(request, username):
    return render_to_response("ut/graph.html", {"username": username })

def player_kill_to_death_ratio_ave(request, username):
    return render_to_response("ut/graph.html", {"username": username })

def player_kill_to_death_ratio_json(request, username):
    games = Game.objects.get_games_with_player(username)
    points = []
    xLim = [0, len(games)]    
    for game in games:
        kills = game.kills.filter(killer__username=username).count()
        deaths = game.kills.filter(victim__username=username).count()
        points.append(float(kills + 1) / float(deaths + 1))
    yLim = [min(points), max(points)]
    data = {
        "values": points,
        "xLim": xLim,
        "yLim": yLim,
        "inc": [1, .01],
    }
    return HttpResponse(json.dumps(data), mimetype="text/plain")

def player_kill_to_death_ratio_ave_json(request, username):
    games = Game.objects.get_games_with_player(username)
    points = []
    xLim = [0, len(games)]   
    i = 0.0 
    running_ave = 0.0
    for game in games:
        kills = game.kills.filter(killer__username=username).count()
        deaths = game.kills.filter(victim__username=username).count()
        ratio = float(kills + 1) / float(deaths + 1)
        running_ave = ((running_ave * i) + ratio) / (i + 1)
        i += 1
        points.append(running_ave)
        
    yLim = [min(points), max(points)]
    data = {
        "values": points,
        "xLim": xLim,
        "yLim": yLim,
        "inc": [1, .01],
    }
    return HttpResponse(json.dumps(data), mimetype="text/plain")

def game_detail(request, hash, template_name='ut/game_detail.html'):
    return list_detail.object_detail(
        request,
        queryset=Game.objects.all(),
        slug_field='hash',
        slug=hash,
        template_name=template_name,
    )


def game_list(request, template_name='ut/game_list.html'):
    return list_detail.object_list(
        request,
        queryset=Game.objects.all().order_by('-id'),
        template_name=template_name,
    )


def player_detail(request, username, template_name='ut/player_detail.html'):
    return list_detail.object_detail(
        request,
        queryset=Player.objects.all(),
        slug_field='username',
        slug=username,
        template_name=template_name,
    )


def player_list(request, template_name='ut/player_list.html'):
    return list_detail.object_list(
        request,
        queryset=Player.objects.all().order_by('username'),
        template_name=template_name,
    )


def weapon_detail(request, ut_name, template_name='ut/weapon_detail.html'):
    return list_detail.object_detail(
        request,
        queryset=Weapon.objects.all(),
        slug_field='ut_name',
        slug=ut_name,
        template_name=template_name,
    )


def weapon_list(request, template_name='ut/weapon_list.html'):
    return list_detail.object_list(
        request,
        queryset=Weapon.objects.filter(ut_name__startswith='UT_MOD_').order_by('ut_name'),
        template_name=template_name,
    )