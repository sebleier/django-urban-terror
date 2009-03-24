from django.contrib import admin
from sandbox.ut.models import *


class GameAdmin(admin.ModelAdmin):
    list_display  = ('id', 'hash')

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('username',)
    ordering = ('username',)

class KillAdmin(admin.ModelAdmin):
    pass

class WeaponAdmin(admin.ModelAdmin):
    pass

admin.site.register(Game, GameAdmin)
admin.site.register(Kill, KillAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Weapon, WeaponAdmin)
