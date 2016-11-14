import mock

from openerp.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @mock.patch('openerp.addons.base_geolocalize.models.res_partner.json.load')
    def test_zip_search(self, mock_api_call):
        mock_api_call.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {
                            "lat": -20.4324245,
                            "lng": -49.9810484
                        }
                    },
                }
            ],
            "status": "OK"
        }

        record = self.browse_ref('base.res_partner_1')
        record.zip = '04576-060'
        assert record.zip_search(), 'Zip search does not return true'
        assert -21 < record.partner_latitude < -20, \
            "Latitude is wrong: 23 < %s < 24" % record.partner_latitude
        assert -50 < record.partner_longitude < -49, \
            "Longitude is wrong: 46 < %s < 47" % record.partner_longitude