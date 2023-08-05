# coding: utf-8

import random
import time

from django.conf import settings


class BarricadeMiddleware(object):
    def process_request(self, request):
        bounds = getattr(settings, 'BARRICADE_BOUND', (0, 5))

        lower_bound = min(bounds)
        upper_bound = max(bounds)

        r = random.random()
        time_to_sleep = r * (upper_bound - lower_bound) + lower_bound

        time.sleep(time_to_sleep)
