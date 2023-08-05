from django.contrib import admin


class ModelAdmin(admin.ModelAdmin):
    @property
    def form(cls):
        import ipdb; ipdb.set_trace()
