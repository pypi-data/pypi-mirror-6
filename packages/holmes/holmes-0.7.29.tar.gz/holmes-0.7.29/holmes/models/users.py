#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlalchemy as sa

from holmes.models import Base


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String(2000), nullable=False)
    email = sa.Column('email', sa.String(2000), nullable=False)

    def to_dict(self):
        return {
            'name': str(self.name),
            'email': str(self.email)
        }

    def __str__(self):
        return str(self.email)

    def __repr__(self):
        return str(self)
