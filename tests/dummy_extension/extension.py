# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Unay Santisteban
# All rights reserved.
#
from connect.processors_toolkit.application import Application
from connect.processors_toolkit.application.dispatcher import WithDispatcher


class AbstractExtension(Application, WithDispatcher):
    def process_asset_purchase_request(self, request):
        return self.dispatch_process(request)

    def validate_asset_purchase_request(self, request):
        return self.dispatch_validation(request)

    def execute_product_action(self, request):
        return self.dispatch_action(request)

    def process_product_custom_event(self, request):
        return self.dispatch_custom_event(request)
