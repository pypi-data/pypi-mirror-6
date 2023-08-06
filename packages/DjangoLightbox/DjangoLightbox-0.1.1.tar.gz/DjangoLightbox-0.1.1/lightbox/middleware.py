# -*- coding: utf-8 -*-
import re

class MobileDetectMiddleware(object):
    "Detects if request comes from iphone/ipad/android"
    mobile_regex = re.compile('iPhone|iPad|iPod|Android|bot', re.IGNORECASE)
    
    def process_request(self, request):
        agent = request.META.get('HTTP_USER_AGENT')
        if not agent:
            request.is_mobile = False
            return
        if self.mobile_regex.search(agent):
            request.is_mobile = True
        else:
            request.is_mobile = False