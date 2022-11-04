# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Unay Santisteban
# All rights reserved.
#
from abc import ABC

from connect.eaas.core.responses import (
    ProcessingResponse,
    ValidationResponse,
    ScheduledExecutionResponse,
)

from connect.processors_toolkit.application import Application
from connect.processors_toolkit.router.mixin import WithRouter


class AbstractExtension(Application, WithRouter, ABC):
    def process_asset_purchase_request(self, request):
        return ProcessingResponse.done()

    def validate_asset_purchase_request(self, request):
        return ValidationResponse.done({})

    def execute_product_action(self, request):
        return self.route_and_dispatch_product_action(request)

    def process_product_custom_event(self, request):
        return self.route_and_dispatch_custom_event(request)

    def execute_refresh_token_schedule(self, request):
        return ScheduledExecutionResponse.done()
