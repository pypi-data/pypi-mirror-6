# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase

from ralph_assets.models_assets import (
    AssetType,
    AssetSource,
    AssetStatus,
    LicenseType,
    OfficeInfo,
)
from ralph_assets.tests.util import (
    create_asset,
    create_category,
    create_model,
    create_warehouse,
)
from ralph.ui.tests.global_utils import login_as_su


class TestAdding(TestCase):
    """Test adding single asset"""

    def setUp(self):
        self.client = login_as_su()
        self.model = create_model()
        self.model2 = create_model('Model2')
        self.warehouse = create_warehouse()
        self.warehouse2 = create_warehouse('Warehouse2')
        self.category = create_category()
        self.asset = create_asset(
            sn='1111-1111-1111-1111',
            category=self.category
        )

    def test_send_data_via_add_form(self):
        url = '/assets/dc/add/device/'
        data_in_add_form = dict(
            type=AssetType.data_center.id,  # 1
            model=self.model.id,  # u'Model1'
            source=AssetSource.shipment.id,  # 1
            invoice_no='Invoice No1',
            order_no='Order no1',
            invoice_date='2001-01-01',
            support_period=48,
            support_type='standard',
            support_void_reporting=True,
            provider='Provider2',
            status=AssetStatus.new.id,  # 1
            price=11,
            request_date='2001-01-02',
            delivery_date='2001-01-03',
            production_use_date='2001-01-04',
            sn='2222-2222-2222-2222',
            barcode='bc-1111-1111-1111',
            warehouse=self.warehouse.id,  # 1
            category=self.category.id,
            ralph_device_id='',
            slots=1.0,
        )
        send_post = self.client.post(url, data_in_add_form)
        # If everything is ok, redirect us to /assets/dc/search
        self.assertRedirects(
            send_post,
            '/assets/dc/edit/device/2/',
            status_code=302,
            target_status_code=200,
        )

        view = self.client.get('/assets/dc/search')
        row_from_table = view.context_data['bob_page'].object_list[1]

        # Overwriting variables to use the object to test the output.
        data_in_add_form.update(
            model='Manufacturer1 Model1',
            warehouse='Warehouse',
            category=self.category.name,
        )
        # Test comparison input data and output data
        for field in data_in_add_form:
            input = data_in_add_form[field]
            if field == 'ralph_device_id':
                output = ''  # test Hook
            else:
                output = getattr(row_from_table, field)
            msg = 'Field: %s Input: %s Output: %s' % (field, input, output)
            self.assertEqual(unicode(input), unicode(output), msg)

    def test_send_data_via_edit_form(self):
        # Fetch data
        url = '/assets/dc/edit/device/1/'
        view = self.client.get(url)
        self.assertEqual(view.status_code, 200)
        old_fields = view.context['asset_form'].initial
        data_in_edit_form = dict(
            type=AssetType.data_center.id,  # 1
            model=self.model2.id,  # u'Model1'
            source=AssetSource.shipment.id,  # 1
            invoice_no='Invoice No2',
            order_no='Order No2',
            support_period=12,
            support_type='d2d',
            support_void_reporting=True,
            provider='Provider2',
            status=AssetStatus.in_progress.id,  # 1
            invoice_date='2001-02-02',
            request_date='2001-01-02',
            delivery_date='2001-01-03',
            production_use_date='2001-01-04',
            provider_order_date='2001-01-05',
            sn='3333-3333-3333-333',
            barcode='bc-3333-3333-333',
            warehouse=self.warehouse.id,  # 1
            license_key='0000-0000-0000-0000',
            version='1.0',
            price=2.00,
            license_type=LicenseType.oem,
            date_of_last_inventory='2003-02-02',
            last_logged_user='James Bond',
            remarks='any remarks',
            category=self.category.id,
            slots=5.0,
            ralph_device_id='',
            asset=True,  # Button name
        )
        self.client.post(url, data_in_edit_form)
        new_view = self.client.get(url)
        new_fields = new_view.context['asset_form'].initial
        if new_view.context['office_info_form']:
            new_office_info = new_view.context['office_info_form'].initial
        correct_data = [
            dict(
                model=self.model2.id,
                invoice_no='Invoice No2',
                order_no='Order No2',
                invoice_date='2001-02-02',
                request_date='2001-01-02',
                delivery_date='2001-01-03',
                production_use_date='2001-01-04',
                provider_order_date='2001-01-05',
                support_period=12,
                support_type='d2d',
                provider='Provider2',
                status=AssetStatus.in_progress.id,
                remarks='any remarks',
            )
        ]
        for data in correct_data:
            for key in data.keys():
                self.assertNotEqual(
                    unicode(old_fields[key]), unicode(new_fields[key])
                )
                self.assertEqual(
                    unicode(new_fields[key]), unicode(data[key])
                )

        office = OfficeInfo.objects.filter(
            license_key='0000-0000-0000-0000'
        ).count()
        if new_view.context['office_info_form']:
            self.assertEqual(office, 1)
            self.assertEqual(
                new_office_info['license_key'], '0000-0000-0000-0000'
            )

        correct_data_office = [
            dict(
                version='1.0',
                license_type=LicenseType.oem.id,
                date_of_last_inventory='2003-02-02',
                last_logged_user='James Bond',
            )
        ]
        if new_view.context['office_info_form']:
            for office in correct_data_office:
                for key in office.keys():
                    self.assertEqual(
                        unicode(new_office_info[key]), unicode(office[key])
                    )

    def test_delete_asset(self):
        """todo"""
        pass
