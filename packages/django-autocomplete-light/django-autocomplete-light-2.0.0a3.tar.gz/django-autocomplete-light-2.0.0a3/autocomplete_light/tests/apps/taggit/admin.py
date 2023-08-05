from django.contrib import admin

import autocomplete_light


class FoodAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(FoodAdmin)
admin.site.register(FoodAdmin)
