import requests
import logging
import decimal

from django.utils.dateparse import parse_date


class ExampleScraper(object):

    def __init(self):
        api_source = "https://www.example.com"
        # .....
        
    def scrape_full_address(self, house_no, postcode):
        address_path = '/api/addresses'
        address_url = self.api_source + address_path
        params = {
            'houseNo': house_no,
            'postcode': postcode,
        }
        return self.http_recorder(url=address_url, method='get', headers=self.headers, params=params)

    def scrape_region_from_full_address(self, full_address):
        region_path = '/api/regions'
        region_url = self.api_source + region_path
        params = {
            'addressAsStr': full_address
        }
        return self.http_recorder(url=region_url, headers=self.headers, method='get', params=params)

    def scrape_payment_methods(self):
        """Scrapes list of user's possible current payment methods"""
        path = '/api/paymentMethods'
        address_url = self.api_source + path
        return self.http_recorder(url=address_url, headers=self.headers, method='get')
        
    def scrape_supplier_payment_methods(self, supplier, service_type, e7):
        """Scrapes supplier's available payment methods"
        payment_methods_path = '/api/paymentMethods/suppliers/'
        payment_methods_url = self.api_source + payment_methods_path + str(supplier)
        params = {
            'service': service_type,
            'e7': e7,
        }
        return self.http_recorder(url=payment_methods_url, headers=self.headers, method='get', params=params)
       
    def write_address(self, address_list):
        for address in address_list:
            region = self.write_region(address)
            defaults = {
                'region': region,
                'building_name': address['bldName'],
                'building_number': address['bldNumber'],
                'sub_building': address['subBld'],
                'throughfare': address['throughfare'],
                'line_2': address['line2'],
                'line_3': address['line3'],
                'town': address['town'],
                'county': address['county'],
                'address_as_string': address['addressAsLongString'],
                'address_with_delimiter': address['addressAsLongStringWithDelimiter'],
            }
            instance, created = Address.objects.update_or_create(
                postcode=address['postcode'], line_1=address['line1'], defaults=defaults)
            if created:
                self.log_database_create(instance)
                
     def write_region(self, region):
        default_supplier, created = Supplier.objects.get_or_create(unique_id=region['region']['defaultSupplier'])
        if created:
            self.log_database_create(default_supplier)

        region_defaults = {
            'core_elec_region': region['region']['coreElecRegion'],
            'default_supplier': default_supplier,
            'mpan_distributor_id': region['region']['mpanDistributorId'],
            'name': region['region']['name'],
        }
        region = self.create_or_update_if_diff(model=PowerRegion, unique_id=region['region']['id'],
                                               defaults=region_defaults)

    def create_or_update_if_diff(self, model, defaults=None, **lookup):
        """Helper function which is similar to update_or_create(), but will compare defaults to database entry
         and only update when there is any difference"""
        defaults = defaults or {}
        instance, created = model.objects.get_or_create(**lookup, defaults=defaults)
        if created:
            self.log_database_create(instance)
            return instance
        else:
            for key, value in defaults.items():
                attr = getattr(instance, key)
                if key == 'end_date_fixed' and value:  # Quick fix for Tariff type dif
                    value = parse_date(value)  # TODO Ideally should compare serialised vs serialised
                if isinstance(attr, decimal.Decimal):
                    attr = float(attr)
                if attr != value:
                    # If any change detected update all for efficiency
                    model.objects.filter(**lookup).update(**defaults)
                    self.log_database_update(instance)
                    instance.refresh_from_db()
                    return instance
            return instance
            
            
    def http_recorder(self, url, headers, method, params=None, data=None):
        if self.recording_type == 7 and url == 'https://example_endpoint_to_exclude.com':
            data = get_data(url, headers, method, params, data, 6)
        else:
            data = get_data(url, headers, method, params, data, 4)
        return data

   
  
