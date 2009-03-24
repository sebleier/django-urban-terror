from django.conf.urls.defaults import *
from sandbox.ut.views import *

urlpatterns = patterns('',
    url(r'games/(?P<hash>[-\w]+)/$',
        view=game_detail,
        name='game_detail'),

    url(r'games/$',
        view=game_list,
        name='game_list'),

    url(r'players/(?P<username>[-\w]+)/$',
        view=player_detail,
        name='player_detail'),

    url(r'players/(?P<username>[-\w]+)/kd/$',
        view=player_kill_to_death_ratio,
        name='player_kill_to_death_ratio'),

    url(r'players/(?P<username>[-\w]+)/kd/json/$',
        view=player_kill_to_death_ratio_json,
        name='player_kill_to_death_ratio_json'),

    url(r'players/$',
        view=player_list,
        name='player_list'),

    url(r'weapons/(?P<ut_name>[-\w]+)/$',
        view=weapon_detail,
        name='weapon_detail'),

    url(r'weapons/$',
        view=weapon_list,
        name='weapon_list'),
)
