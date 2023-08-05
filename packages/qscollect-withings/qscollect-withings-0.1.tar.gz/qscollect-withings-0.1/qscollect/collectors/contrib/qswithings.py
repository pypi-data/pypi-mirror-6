import logging
import withings
import pytz
import datetime

log = logging.getLogger("WiThingsCollector")

import qscollect.collector_base as collector_base

class WiThingsWeightCollector(collector_base.CollectorBase):
    """ Gets records of weight entries from WiThings.com via API """

    class Meta:
        name = "withings"
        style = "oauth"

    def __init__(self, db=None):
        super(WiThingsWeightCollector, self).__init__(db)

    @classmethod
    def config_args(cls, parser):
        """ Adds the configuration arguments necessary for configuring the withings collector """
        parser.add_argument("--browser", "-b", action="store_true", help="Open the url in default webbrowser")
        parser.add_argument("key", help="Key from WiThings App")
        parser.add_argument("secret", help="Secret from WiThings App")

    @classmethod
    def config(cls, args):
        """ return a dictionary of values to store as part of the keys for this collector """
        auth = withings.WithingsAuth(args.key, args.secret)
        url = auth.get_authorize_url()

        if args.browser:
            import webbrowser
            webbrowser.open(url)
            print "Allow the app and then copy the oauth_verifier"
        else:
            print "Go to {0}, allow the app, and then copy the oauth_verifier".format(url)

        verifier = raw_input("Enter your oauth_verifier: ")
        credentials = auth.get_credentials(verifier)

        return credentials.__dict__

    def register(self, system):
        self._system = system
        self.register_schedule(self, hour=6)  # 4 times a day

    def to_row(self, entry):
        return {
            'modified': entry.date.replace(tzinfo=pytz.timezone('UTC')),
            'weight': entry.weight,
            'fat_mass_weight': entry.fat_mass_weight,
            'fat_free_mass': entry.fat_free_mass,
            'fat_ratio': entry.fat_ratio,
        }

    def __call__(self, config=None):
        if config is None:
            config = self.keys
        state = self.state
        if state is None:
            state = {
                'last_entry': 0,
            }

        logging.debug(config)
        logging.debug(state)

        credentials = withings.WithingsCredentials(
            access_token=config['access_token'],
            access_token_secret=config['access_token_secret'],
            consumer_key=config['consumer_key'],
            consumer_secret=config['consumer_secret'],
            user_id=config['user_id']
        )

        api = withings.WithingsApi(credentials)
        try:
            entries = api.get_measures(lastupdate=state['last_entry'], category=1)
        except Exception, ex:
            log.warn(ex)
            raise StopIteration

        for entry in entries:
            if entry.attrib > 0:
                # Data wasn't captured by device or is ambiguous
                continue
            row = self.to_row(entry)
            logging.debug(row)

            date = row['modified']
            timestamp = (date - datetime.datetime.fromtimestamp(0, tz=pytz.timezone('UTC'))).total_seconds()

            state['last_entry'] = max(state['last_entry'], timestamp)
            yield row

        self._db.set_state(self.Meta.name, state)