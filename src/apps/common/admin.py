from unfold.admin import ModelAdmin


class BaseAdmin(ModelAdmin):
    list_per_page = 25
    search_help_text = "Qidirish uchun kalit so'z kiriting"
