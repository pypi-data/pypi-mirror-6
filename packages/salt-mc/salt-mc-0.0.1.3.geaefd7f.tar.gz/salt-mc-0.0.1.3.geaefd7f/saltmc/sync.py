import glob
import filecmp
import os

from saltmc import fetchers
from saltmc import link
from saltmc import utils


ITEMS = ['_modules', '_states', '_grains', '_renderers', '_returners']


def fetch_all(formulas, cache_dir):
    """
    Sync all the formulas and their wanted versions.
    """
    for name, data in formulas.items():
        # TODO(ekarlso): Limk creation should maybe happen in get_settings() ?
        l = link.Link(data)

        fetcher = fetchers.get_by_scheme(l.scheme)(l.url)

        source_top = os.path.join(cache_dir, name)
        # This should download / clone or whatever and unpack if a file
        # to the source_top directory within the cache directory
        fetcher.fetch(source_top)


def item_report(left, right):
    i = {
        'left': left,
        'right': right
    }

    i['left_present'] = os.path.exists(i['left'])
    i['right_present'] = os.path.exists(i['right'])

    if not i['left_present'] or not i['right_present']:
        i['status'] = False
        return i

    if os.path.isdir(i['left']):
        cmp_ = filecmp.dircmp(i['left'], i['right'])
        i['status'] = utils.sides_identical(cmp_)
    else:
        i['status'] = filecmp.cmp(left, right)
    return i


def report(cache_dir, settings):
    values = {}
    for name, data in settings.get('formulas', {}).items():
        left_root = os.path.join(cache_dir, name)

        reports = []

        root_report = item_report(os.path.join(left_root, name),
                                  os.path.join(settings['directory'], name))

        reports.append(root_report)

        if root_report['left_present']:
            for i in ITEMS:
                items_left_dir = os.path.join(left_root, i)

                if os.path.exists(items_left_dir):
                    for item_left in glob.glob(items_left_dir + '/*'):
                        n = os.path.basename(item_left)

                        item_right = os.path.join(settings['directory'], i, n)
                        report = item_report(item_left, item_right)

                        reports.append(report)

        status = True
        for r in reports:
            if not r['status']:
                status = False
                break

        values[name] = {'status': status, 'items': reports}
    return values
