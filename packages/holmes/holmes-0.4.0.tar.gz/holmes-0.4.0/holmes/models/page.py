#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from holmes.models import Base


class Page(Base):
    __tablename__ = "pages"

    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column('url', sa.String(2000), nullable=False)
    url_hash = sa.Column('url_hash', sa.String(128), nullable=False)
    uuid = sa.Column('uuid', sa.String(36), default=uuid4, nullable=False)
    created_date = sa.Column('created_date', sa.DateTime, default=datetime.utcnow, nullable=False)

    last_review_date = sa.Column('last_review_date', sa.DateTime, nullable=True)

    domain_id = sa.Column('domain_id', sa.Integer, sa.ForeignKey('domains.id'))

    reviews = relationship("Review", backref="page", foreign_keys='[Review.page_id]')

    last_review_id = sa.Column('last_review_id', sa.Integer, sa.ForeignKey('reviews.id'))
    last_review = relationship("Review", foreign_keys=[last_review_id])

    last_modified = sa.Column('last_modified', sa.DateTime, nullable=True)
    expires = sa.Column('expires', sa.DateTime, nullable=True)

    def to_dict(self):
        return {
            'uuid': str(self.uuid),
            'url': self.url,
            'lastModified': self.last_modified,
            'expires': self.expires,
        }

    def __str__(self):
        return str(self.uuid)

    def __repr__(self):
        return str(self)

    def get_violations_per_day(self, db):
        from holmes.models import Review, Violation  # Prevent circular dependency

        violations = db \
            .query(
                sa.func.year(Review.completed_date).label('year'),
                sa.func.month(Review.completed_date).label('month'),
                sa.func.day(Review.completed_date).label('day'),
                sa.func.count(Violation.id).label('violation_count'),
                sa.func.sum(Violation.points).label('violation_points')
            ).join(
                Page, Page.id == Review.page_id
            ).join(
                Violation, Violation.review_id == Review.id
            ).filter(Review.is_complete == True).filter(Review.page_id == self.id) \
            .group_by(
                sa.func.year(Review.completed_date),
                sa.func.month(Review.completed_date),
                sa.func.day(Review.completed_date),
            ) \
            .order_by(Review.completed_date) \
            .all()

        result = []

        for day in violations:
            dt = "%d-%d-%d" % (day.year, day.month, day.day)
            result.append({
                "completedAt": dt,
                "violation_count": int(day.violation_count),
                "violation_points": int(day.violation_points)
            })

        return result

    @classmethod
    def by_uuid(cls, uuid, db):
        return db.query(Page).filter(Page.uuid == uuid).first()
