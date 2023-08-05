from django.contrib import admin

from .models import Character, CharacterGroup, Nickname


class CharacterAdmin(admin.ModelAdmin):
    pass


class CharacterGroupAdmin(admin.ModelAdmin):
    pass


class NicknameAdmin(admin.ModelAdmin):
    pass


admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterGroup, CharacterGroupAdmin)
admin.site.register(Nickname, NicknameAdmin)


