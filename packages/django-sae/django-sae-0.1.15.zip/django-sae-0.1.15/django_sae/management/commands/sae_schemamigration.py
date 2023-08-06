# coding=utf-8
from south.management.commands import schemamigration
from django_sae.management.commands import patch_for_sae_restful_mysql


class Command(schemamigration.Command):
    def handle(self, *args, **kwargs):
        patch_for_sae_restful_mysql()
        super(Command, self).handle(*args, **kwargs)
