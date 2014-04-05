from django.contrib import admin
from django_hello_world.hello.models import PriorityRule


def apply_rule(modeladmin, request, queryset):
    for rule in queryset:
        rule.apply_to_existed()
apply_rule.short_description = "Apply selected rules to all requests"


class PriorityRuleAdmin(admin.ModelAdmin):
    actions = [apply_rule]
admin.site.register(PriorityRule, PriorityRuleAdmin)
