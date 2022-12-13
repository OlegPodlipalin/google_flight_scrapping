import argparse
from libraries.work_with_libraries import get_data


class GetInput:
    def __init__(self):
        self.data = None
        self._dest_k = []
        self._dest_ch = []
        self.input_parser = \
            argparse.ArgumentParser(prog='Google Flights Scraper',
                                    description='This script scrape the data about flight options to chosen '
                                    'destination(s) on chosen date from Google Flights service',
                                    epilog='Input your initial data and enjoy the result.')
        self._get_keys_choices()
        self._set_args()
        self.args = self.input_parser.parse_args()

    def _get_keys_choices(self):
        self.data = get_data('destinations')
        self._dest_k = [k for k in self.data]
        self._dest_ch = [k + ':' + v for k, v in self.data.items()]

    def _set_args(self):
        self.input_parser.add_argument(
            '-d', '--dest', nargs="+", choices=self._dest_k, required=True,  metavar='',
            help=f"takes a list of desirable destinations by their number. choices: {self._dest_ch}")
        self.input_parser.add_argument(
            '-t', '--term', nargs="+", required=True, metavar='',
            help="takes the list of all the desirable dates of flight in <DD-MM-YYYY> format")
        # self.input_parser.add_argument('-a', '--adult', default=1, type=int, metavar='', help='number of adults')
        # self.input_parser.add_argument('-k', '--kids', default=1, type=int, metavar='', help='number of children')
        self.input_parser.add_argument(
            '-f', '--flight_class', choices=['business', 'economy'], default='economy', metavar='',
            help='option to chose a flight class. choices: {%(choices)s}, default: {%(default)s}')
        self.input_parser.add_argument(
            '-w', '--wait', action='store', default=5, type=int, metavar='',
            help='maximum delay time for webpage to be loaded. default: {%(default)s}')
        self.input_parser.add_argument(
            '-s', '--silent', action='store_true', help='option to run the script without opening a browser window')
        # self.input_parser.add_argument(
        #     '-j', '--json', action='store_true', help='save data collected in "flights.json" file')
        # self.input_parser.add_argument('-p', '--print', action='store_true', help='print data collected in stdout')
