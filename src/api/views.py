import os

from django.conf import settings
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from eventbrite import Eventbrite

eventbrite = Eventbrite(settings.EVENTBRITE_OAUTH_TOKEN)


class CategoryDataView(GenericAPIView):
    """Return category data from Eventbrite."""

    def get(self, request):
        """Process GET request and return data."""

        raw_categories = eventbrite.get_categories().get('categories', [])
        categories = [self._simplify_category(category) for category in raw_categories]

        data = {
            'categories': sorted(categories, key=lambda k: k['id'])
        }

        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def _simplify_category(category):
        return {
            'id': category['id'],
            'name': category['short_name']
        }


class SubcategoryDataView(GenericAPIView):
    """Return subcategory data from Eventbrite."""

    def get(self, request):
        """Process GET request and return data."""

        raw_subcategories = eventbrite.get_subcategories().get('subcategories', [])
        subcategories = [self._simplify_subcategory(subcategory) for subcategory in raw_subcategories]

        data = {
            'subcategories': sorted(subcategories, key=lambda k: k['id'])
        }

        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def _simplify_subcategory(subcategory):
        return {
            'id': subcategory['id'],
            'parentId': subcategory['parent_category']['id'],
            'name': subcategory['name'],        }


class EventDataView(GenericAPIView):
    """Return event search results."""

    def get(self, request):
        return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Process POST request and return event data."""
        default_location = 'San Francisco, CA'
        events = []
        raw_events = []

        query_params = {
            'expand': 'venue, logo',
            'categories': request.data.get('category'),
            'location.within': '20mi'
        }

        if request.data.get('latitude') and request.data.get('longitude'):
            location = {
                'location.latitude': request.data.get('latitude'),
                'location.longitude': request.data.get('longitude'),
            }
        else:
            location = {
                'location.address': request.data.get('address', default_location)
            }

        query_params.update(location)

        if query_params['categories']:
            raw_events = eventbrite.event_search(**query_params).get('events')

        if raw_events:
            events = [self._simplify_event(event) for event in raw_events]

        data = {
            'events': events
        }

        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def _simplify_event(event):
        return {
            'id': event['id'],
            'categoryId': event['category_id'],
            'subcategoryId': event['subcategory_id'],
            'name': event['name']['text'],
            'start': event['start']['local'],
            'url': event['url'],
            'logo': event['logo'],
            'address': event['venue']['address']['localized_address_display'],
            'latitude': event['venue']['address']['latitude'],
            'longitude': event['venue']['address']['longitude'],
        }
