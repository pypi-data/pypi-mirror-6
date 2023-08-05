import argparse
import logging
import sys
import venusian
try:
    import transaction
    HAVE_TRANSACTION = True
except ImportError:
    HAVE_TRANSACTION = False

try:
    string_type = basestring
except NameError:  # pragma: no cover
    # Python 3
    string_type = str


log = logging.getLogger(__name__)

_context_providers = {}
_upgrade_steps = []


class InvalidRequirement(KeyError):
    pass


class upgrade_context(object):
    def __init__(self, name, parameters=[]):
        self.name = name
        self.parameters = parameters

    def __call__(self, wrapped):
        log.debug('Discovered context provider \"%s\".', self.name)
        _context_providers[self.name] = (wrapped, self.parameters)
        return wrapped


class upgrade_step(object):
    def __init__(self, require=[]):
        if isinstance(require, string_type):
            require = [require]
        self.require = require

    def __call__(self, wrapped):
        log.debug('Discovered upgrade step \"%s\".', wrapped)
        _upgrade_steps.append((wrapped, self.require))
        return wrapped


def scan(packages):
    scanner = venusian.Scanner()
    for pkg in packages:
        log.debug('Scanning package %s', pkg)
        try:
            module = __import__(pkg)
            scanner.scan(module, ())
        except (ImportError, SyntaxError):
            log.exception('Can not import %s, aborting', pkg)
            return False
    return True


def run_context_provider(func, parameters):
    if parameters:
        parser = argparse.ArgumentParser()
        for (name, kw) in parameters:
            parser.add_argument(name, **kw)
            (options, remainder) = parser.parse_known_args()
    else:
        options = argparse.Namespace()

    try:
        log.info('Querying context provider %s', func)
        return func(options)
    except TypeError:
        return func()


def build_environment(requirements):
    environment = {}
    for requirement in requirements:
        if requirement in _context_providers:
            ctx = run_context_provider(*_context_providers[requirement])
            environment.update(ctx)
        else:
            raise InvalidRequirement(requirement)
    return environment


def upgrade():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest='verbosity',
            action='append_const', const=1, default=[1],
            help='Be more verbose. Use multiple times to increase verbosity')
    parser.add_argument('--scan',
            dest='packages',
            type=lambda arg: [a.strip() for a in arg.split(',')],
            required=True,
            help='Packages to scan for upgrade steps')
    (options, remainder) = parser.parse_known_args()

    logging.basicConfig(
            format='%(message)s',
            level=logging.CRITICAL - (10 * len(options.verbosity)))

    if not scan(options.packages):
        sys.exit(1)

    for (step, requirements) in _upgrade_steps:
        try:
            environment = build_environment(requirements)
        except InvalidRequirement as e:
            log.error('Encountered unknown requirement for context '
                      'provider "%s", aborting.', e)
            sys.exit(2)
            continue  # This helps with testing when we mock sys.exit
        log.info('Executing upgrade step %s', step)
        step(environment)
        if HAVE_TRANSACTION:  # pragma: no cover
            transaction.get().commit()
