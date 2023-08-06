# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cada import db

PARTS = {
    1: {'label': 'Présentiel', 'help': "L'administration s'est déplacée à la séance"},
    2: {'label': 'Etudié', 'help': "Etude et avis sur de nouveaux cas"},
    3: {'label': 'Récurrent', 'help': "Avis sur des cas récurrents"},
}


class Advice(db.Document):
    id = db.StringField(primary_key=True)
    administration = db.StringField()
    type = db.StringField()
    session = db.DateTimeField()
    subject = db.StringField()
    topics = db.ListField(db.StringField())
    tags = db.ListField(db.StringField())
    meanings = db.ListField(db.StringField())
    part = db.IntField()
    content = db.StringField()

    def __unicode__(self):
        return self.subject
