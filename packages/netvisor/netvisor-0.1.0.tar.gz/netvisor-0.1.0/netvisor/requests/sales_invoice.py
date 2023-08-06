# -*- coding: utf-8 -*-
"""
    netvisor.requests.sales_invoice
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013-2014 by Fast Monkeys Oy.
    :license: MIT, see LICENSE for more details.
"""
from .base import Request
from ..exc import InvalidData
from ..responses.sales_invoices import (
    GetSalesInvoiceResponse,
    SalesInvoiceListResponse,
)


class GetSalesInvoiceRequest(Request):
    method = 'GET'
    uri = 'GetSalesInvoice.nv'
    response_cls = GetSalesInvoiceResponse
    resource_key = 'sales_invoice'

    def parse_response(self, response):
        data = super(GetSalesInvoiceRequest, self).parse_response(response)
        self.ensure_not_empty(data)
        return data

    def ensure_not_empty(self, data):
        if data is None:
            raise InvalidData(
                'Data form incorrect:. '
                'Sales invoice not found with Netvisor identifier: {0}'.format(
                    self.params['NetvisorKey']
                )
            )


class SalesInvoiceListRequest(Request):
    method = 'GET'
    uri = 'SalesInvoiceList.nv'
    response_cls = SalesInvoiceListResponse
    resource_key = 'sales_invoice_list'
