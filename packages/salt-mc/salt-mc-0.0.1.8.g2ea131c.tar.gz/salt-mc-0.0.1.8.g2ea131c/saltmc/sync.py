import filecmp
import glob
import logging
import os

from saltmc import fetchers
from saltmc import link


LOG = logging.getLogger(__name__)

GLOB_FOLDERS = ['_modules', '_states', '_grains', '_renderers', '_returners']


def fetch_all(formulas, cache_dir):
    """
    Sync all the formulas and their wanted versions.
    """
    for name, data in formulas.items():
        # TODO(ekarlso): Limk creation should maybe happen in get_settings() ?
        l = link.Link(data['url'])

        fetcher = fetchers.get_by_scheme(l.scheme)(l.url)

        source_top = os.path.join(cache_dir, name)
        # This should download / clone or whatever and unpack if a file
        # to the source_top directory within the cache directory
        fetcher.fetch(source_top)


def _dirs_identical(cmp_):
    if not cmp_.left or not cmp_.right:
        return False
    if cmp_.left_only or cmp_.right_only or cmp_.diff_files:
        return False
    else:
        return True


def _base(left=None, right=None, dircmp=None):
    if left is not None and right is not None:
        report = {
            'left': left,
            'right': right,
            'left_present': os.path.exists(left),
            'right_present': os.path.exists(right),
        }

        if (not report['left_present'] or not report['right_present']):
            report['status'] = False
            return report, dircmp

        if os.path.isdir(left) and os.path.isdir(right):
            dircmp = filecmp.dircmp(left, right)
    else:
        report = {
            'left': dircmp.left,
            'right': dircmp.right,
            'left_present': True,
            'right_present': True,
        }

    if dircmp is not None:
        report['status'] = _dirs_identical(dircmp)
        for attr in ['left_only', 'right_only', 'diff_files']:
            report[attr] = getattr(dircmp, attr)
    else:
        report['status'] = filecmp.cmp(left, right)

    report['is_dir'] = True if dircmp is not None else False

    return report, dircmp


def path_report(left_path, right_path):
    top_report, top_cmp = _base(left_path, right_path)

    reports = [top_report]
    if top_cmp is None:
        return reports

    if top_report['is_dir']:

        # Walk through all subdirs from top and add reports.
        def _do_sub_comp(cmp_):
            for subdir, sub_cmp in cmp_.subdirs.items():
                sub_report, _ = _base(dircmp=sub_cmp)
                reports.append(sub_report)
                _do_sub_comp(sub_cmp)
        _do_sub_comp(top_cmp)

    # Ensure that the root is always item 0
    return reports


def report(cache_dir, settings):
    values = {}
    for name, data in settings.get('formulas', {}).items():
        formula_report = {}

        # NOTE: Left root equals the root of the source of the formula.
        left_root = os.path.join(cache_dir, name)

        # NOTE: Compare first the formula directories.
        formula_report['dirs'] = path_report(
            os.path.join(left_root, name),
            os.path.join(settings['directory'], name))

        # Here we store stuff that are inside the _modules etc.
        formula_report['items'] = {}

        # NOTE: Compare files that are in _modules etc in each module to the
        # destinations _modules
        if not data.get('items_skip'):
            items = get_existing_items(left_root,
                                       data.get('items_skip_folders', []))
            for i, globbed in items.items():
                for left_item in globbed:
                    right_item = os.path.join(settings['directory'], i,
                                              os.path.basename(left_item))
                    item_report = path_report(left_item, right_item)
                    formula_report['items'].setdefault(i, [])
                    formula_report['items'][i].extend(item_report)
        else:
            LOG.info('Skipping items for %s' % name)

        values[name] = formula_report
    return values


def diff_items(formula_report):
    """
    Given
    """
    dirs = []
    items = {}

    for i in formula_report.get('dirs', []):
        if not i['status']:
            dirs.append(i)

    for name, values in formula_report.get('items', {}).items():
        for i in values:
            if not i['status']:
                items.setdefault(name, [])
                items[name].append(i)
    return dirs, items


def get_existing_items(path, skip=[]):
    """
    Given a path it will go through each directory like _modules in the path
    and glob it making a dict with the _modules etc as key and the glob
    contents as as the list.
    """
    existing = {}

    for name in GLOB_FOLDERS:
        if name in skip:
            LOG.debug("Skipping items of %s, in skip %s" % (name, skip))
        glob_path = os.path.join(path, name)

        if os.path.exists(glob_path):
            existing[name] = glob.glob(glob_path + '/*')

    return existing
