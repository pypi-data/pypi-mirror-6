#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import UUID, uuid4

from ujson import loads, dumps

from holmes.models import Review, Page
from holmes.handlers import BaseHandler


class BaseReviewHandler(BaseHandler):
    def _parse_uuid(self, uuid):
        try:
            return UUID(uuid)
        except ValueError:
            return None


class ReviewHandler(BaseReviewHandler):
    def get(self, page_uuid, review_uuid):
        review = None
        if self._parse_uuid(review_uuid):
            review = Review.by_uuid(review_uuid, self.db)

        if not review:
            self.set_status(404, 'Review with uuid of %s not found!' % review_uuid)
            return

        if review.completed_date:
            completed_data_iso = review.completed_date.isoformat()
        else:
            completed_data_iso = None

        result = review.to_dict()
        result.update({
            'violationPoints': review.get_violation_points(),
            'violationCount': review.violation_count,
            'completedDateISO': completed_data_iso
        })

        self.write_json(result)

    def post(self, page_uuid, review_uuid=None):
        page = Page.by_uuid(page_uuid, self.db)

        review_data = loads(self.get_argument('review'))

        review = Review(
            domain=page.domain,
            page=page,
            is_active=True,
            is_complete=False,
            completed_date=datetime.now(),
            uuid=uuid4(),
        )

        self.db.add(review)
        self.db.flush()

        for fact in review_data['facts']:
            review.add_fact(fact['key'], fact['value'], fact['title'], fact['unit'])
        self.db.flush()

        for violation in review_data['violations']:
            review.add_violation(violation['key'], violation['title'], violation['description'], violation['points'])
        self.db.flush()

        review.is_complete = True
        self.db.flush()

        page.last_review = review
        page.last_review_date = review.completed_date

        self.db.flush()

        self._remove_older_reviews_with_same_day(review)

        self.db.query(Review).filter(
            Review.page_id == review.page_id
        ).filter(
            Review.id != review.id
        ).update({
            'is_active': False
        })

        self.db.flush()

        self.application.event_bus.publish(dumps({
            'type': 'new-review',
            'reviewId': str(review.uuid)
        }))

    def _remove_older_reviews_with_same_day(self, review):
        dt = datetime.now()
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

        for review in self.db.query(Review) \
                .filter(Review.page == review.page) \
                .filter(Review.uuid != review.uuid) \
                .filter(Review.created_date >= dt) \
                .all():

            for fact in review.facts:
                self.db.delete(fact)

            for violation in review.violations:
                self.db.delete(violation)

            self.db.delete(review)

            self.db.flush()


class LastReviewsHandler(BaseReviewHandler):
    def get(self):
        reviews = Review.get_last_reviews(self.db)

        reviews_json = []
        for review in reviews:
            review_dict = review.to_dict()
            data = {
                'violationCount': review.violation_count,
                'completedDateISO': review.completed_date.isoformat()
            }
            review_dict.update(data)
            reviews_json.append(review_dict)

        self.write_json(reviews_json)
