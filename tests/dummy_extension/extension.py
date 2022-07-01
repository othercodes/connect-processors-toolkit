# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Unay Santisteban
# All rights reserved.
#
from abc import ABC

from connect.processors_toolkit.application import Application
from connect.processors_toolkit.application.dispatcher import WithDispatcher


class AbstractExtension(Application, WithDispatcher, ABC):
    def process_asset_purchase_request(self, request):
        return self.dispatch_process(request, 3600)

    def validate_asset_purchase_request(self, request):
        return self.dispatch_validation(request)

    def execute_product_action(self, request):
        return self.dispatch_action(request)

    def process_product_custom_event(self, request):
        return self.dispatch_custom_event(request)

    def execute_refresh_token_schedule(self, request):
        return self.dispatch_schedule_process(request, 'refresh-token')
