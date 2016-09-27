from django.core.management.base import BaseCommand
from django.conf import settings

from ...scrapers. import ExampleScraper


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--recording', '-r', default=4, type=int, choices=[1, 3, 4, 5, 6, 7],
                            help='Specify a http recording type value from 1-7. Default is 4')

        parser.add_argument('type', default=1, type=int,
                            help='Specify a type of tariff scrape: 1 for scrape all by id, 2 scrape all by name,'
                                 '3 scrape tariff lists')

    def handle(self, *args, **options):
        scraper = ExampleScraper()
        recording_type = options['recording']
        scraper.recording_type = recording_type
        input = { "example": "example"}
        current_service_type = 'example'
        address_file = 'httprecorder/scrapers/Addresses 131015.csv'
        if options['type'] == 1:
            scraper.full_scrape_and_save(address_file, input, current_service_type)
        elif options['type'] == 2:
            scraper.scrape_tariffs_by_name(address_file, input, current_service_type)
        elif options['type'] == 3:
            scraper.scrape_tariff_lists(address_file, input, current_service_type)
        else:
            print("Please specify a correct scrape type")
