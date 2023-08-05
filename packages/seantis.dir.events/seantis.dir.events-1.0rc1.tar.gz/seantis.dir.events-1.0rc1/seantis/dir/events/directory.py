import logging
log = logging.getLogger('seantis.dir.events')

from five import grok
from pytz import timezone

from datetime import datetime
from datetime import date as datetime_date
from urllib import urlopen
from icalendar import Calendar
from plone.dexterity.utils import createContent, addContentToContainer
from zope.component import queryAdapter
from zope.component.hooks import getSite
from Products.CMFPlone.PloneBatch import Batch

from seantis.dir.base import directory
from seantis.dir.base import session
from seantis.dir.base.utils import cached_property

from seantis.dir.events.unrestricted import execute_under_special_role
from seantis.dir.events.interfaces import (
    IEventsDirectory, IActionGuard
)

from seantis.dir.events.recurrence import grouped_occurrences
from seantis.dir.events import dates
from seantis.dir.events import utils
from seantis.dir.events import maintenance
from seantis.dir.events import _

from AccessControl import getSecurityManager
from Products.CMFCore import permissions

from seantis.dir.events import pages


class EventsDirectory(directory.Directory, pages.CustomPageHook):

    def labels(self):
        return dict(cat1=_(u'What'), cat2=_(u'Where'))

    def used_categories(self):
        return ('cat1', 'cat2')

    def unused_categories(self):
        return ('cat3', 'cat4')

    def allow_action(self, action, item_brain):
        """ Return true if the given action is allowed. This is not a
        wrapper for the transition guards of the event workflow. Instead
        it is called *by* the transition guards.

        This allows a number of people to work together on an event website
        with every person having its own group of events which he or she is
        responsible for.

        There's no actual implementation of that in seantis.dir.events
        but client specific packages like izug.seantis.dir.events may
        use a custom adapter to implement such a thing.
        """
        guard = queryAdapter(self, IActionGuard)

        if guard:
            return guard.allow_action(action, item_brain)
        else:
            return True


class ExtendedDirectoryViewlet(grok.Viewlet, pages.CustomDirectory):
    grok.context(IEventsDirectory)
    grok.name('seantis.dir.events.directory.detail')
    grok.require('zope2.View')
    grok.viewletmanager(directory.DirectoryViewletManager)

    template = grok.PageTemplateFile('templates/directorydetail.pt')

    def __init__(self, *args, **kwargs):
        super(ExtendedDirectoryViewlet, self).__init__(*args, **kwargs)
        self.context = self.custom_directory


class EventsDirectoryIndexView(grok.View, directory.DirectoryCatalogMixin):

    grok.name('eventindex')
    grok.context(IEventsDirectory)
    grok.require('cmf.ManagePortal')

    template = None

    def render(self):

        self.request.response.setHeader("Content-type", "text/plain")

        if 'rebuild' in self.request:
            log.info('rebuilding ZCatalog')
            self.catalog.catalog.clearFindAndRebuild()

        if 'reindex' in self.request:
            log.info('reindexing event indices')
            self.catalog.reindex()

        result = []
        for name, index in self.catalog.indices.items():

            result.append(name)
            result.append('-' * len(name))
            result.append('')

            for ix, identity in enumerate(index.index):
                result.append('%i -> %s' % (ix, identity))

            result.append('')

            dateindex = index.get_metadata('dateindex')

            if dateindex:
                result.append('-> dateindex')

                for date in sorted(dateindex):
                    result.append('%s -> %s' % (
                        date.strftime('%y.%m.%d'), dateindex[date])
                    )

        return '\n'.join(result)


class EventsDirectoryView(directory.View, pages.CustomDirectory):

    grok.name('view')
    grok.context(IEventsDirectory)
    grok.require('zope2.View')

    template = None
    _template = grok.PageTemplateFile('templates/directory.pt')

    @property
    def title(self):
        return self.custom_directory.title

    @property
    def is_ical_export(self):
        """ Returns true if the current request is an ical request. """
        return self.request.get('type') == 'ical'

    def get_last_daterange(self):
        """ Returns the last selected daterange. """
        return session.get_session(self.context, 'daterange') \
            or dates.default_daterange

    def set_last_daterange(self, method):
        """ Store the last selected daterange on the session. """
        session.set_session(self.context, 'daterange', method)

    def get_last_state(self):
        """ Returns the last selected event state. """
        return session.get_session(self.context, 'state') or 'published'

    def set_last_state(self, method):
        """ Store the last selected event state on the session. """
        session.set_session(self.context, 'state', method)

    @property
    def no_events_helptext(self):
        if 'published' == self.catalog.state:
            return _(u'No events for the current daterange')
        else:
            return _(u'No events for the current state')

    @property
    def selected_daterange(self):
        return self.catalog.daterange

    @property
    def dateranges(self):
        return dates.methods

    def daterange_url(self, method):
        return self.directory.absolute_url() + '?range=' + method

    @property
    def has_results(self):
        return len(self.batch) > 0

    def render(self):
        """ Renders the ical if asked, or the usual template. """
        if not self.is_ical_export:
            return self._template.render(self)
        else:
            if 'search' in self.request.keys():
                calendar = self.catalog.calendar(
                    search=self.request.get('searchtext')
                )
            elif 'filter' in self.request.keys():
                calendar = self.catalog.calendar(
                    filter=self.get_filter_terms()
                )
            else:
                calendar = self.catalog.calendar()

            utils.render_ical_response(self.request, self.context, calendar)

    def update(self, **kwargs):
        daterange = self.request.get('range', self.get_last_daterange())

        # do not trust the user's input blindly
        if not dates.is_valid_daterange(daterange):
            daterange = 'this_month'
        else:
            self.set_last_daterange(daterange)

        state = self.request.get('state', self.get_last_state())

        if not self.show_state_filters or state not in (
            'submitted', 'published', 'archived'
        ):
            state = 'published'
        else:
            self.set_last_state(state)

        self.catalog.state = state
        self.catalog.daterange = daterange

        if not self.is_ical_export:
            super(EventsDirectoryView, self).update(**kwargs)

    def groups(self, items):
        """ Returns the given occurrences grouped by human_date. """
        groups = grouped_occurrences(items, self.request)

        for key, items in groups.items():
            for ix, item in enumerate(items):
                items[ix] = item.get_object()

        return groups

    def translate(self, text, domain="seantis.dir.events"):
        return utils.translate(self.request, text, domain)

    @property
    def show_state_filters(self):
        return getSecurityManager().checkPermission(
            permissions.ReviewPortalContent, self.context
        )

    @cached_property
    def batch(self):
        # use a custom batch whose items are lazy evaluated on __getitem__
        start = int(self.request.get('b_start') or 0)
        lazy_list = self.catalog.lazy_list

        # seantis.dir.events lazy list implementation currently cannot
        # deal with orphans.
        return Batch(lazy_list, directory.ITEMSPERPAGE, start, orphan=0)

    @property
    def selected_state(self):
        return self.catalog.state

    def state_filter_list(self):

        submitted = utils.translate(self.request, _(u'Submitted'))
        submitted += u' (%i)' % self.catalog.submitted_count

        return [
            ('submitted', submitted),
            ('published', _(u'Published'))
        ]

    def state_url(self, method):
        return self.directory.absolute_url() + '?state=' + method

    @utils.webcal
    def ical_url(self, for_all):
        """ Returns the ical url of the current view. """
        url = self.daterange_url('this_year') + '&type=ical'

        if for_all:
            return url

        action, param = self.primary_action()

        if action not in (self.search, self.filter):
            return ''

        if action == self.search:
            if param:
                return url + '&search=true&searchtext=%s' % param
            else:
                return ''

        if action == self.filter:
            terms = dict([(k, v) for k, v in param.items() if v != '!empty'])

            if not terms:
                return ''

            url += '&filter=true'

            for item in terms.items():
                url += '&%s=%s' % item

            return url


class TermsView(grok.View):

    grok.name('terms')
    grok.context(IEventsDirectory)
    grok.require('zope2.View')

    label = _(u'Terms and Conditions')
    template = grok.PageTemplateFile('templates/terms.pt')


class CleanupView(grok.View):

    grok.name('cleanup')
    grok.context(IEventsDirectory)
    grok.require('zope2.View')

    def render(self):

        # dryrun must be disabled explicitly using &run=1
        dryrun = not self.request.get('run') == '1'

        # this maintenance feature may be run unrestricted as it does not
        # leak any information and it's behavior cannot be altered by the
        # user. This allows for easy use via cronjobs.
        execute_under_special_role(
            getSite(), 'Manager',
            maintenance.cleanup_directory, self.context, dryrun
        )

        return u''


class ImportIcsView(grok.View):

    grok.name('import-ics')
    grok.context(IEventsDirectory)
    grok.require('cmf.ManagePortal')

    messages = []

    @property
    def url(self):
        return self.request.get('url', '').replace('webcal://', 'https://')

    def say(self, text):
        print text
        self.messages.append(text)
        return '<br>'.join(self.messages)

    def read_ical(self):
        return urlopen(self.url).read()

    def valid_event(self, component):
        if component.name != 'VEVENT':
            return False

        required_fields = ('dtstart', 'dtend')

        for req in required_fields:
            if not req in component:
                return False

        return True

    def events(self, calendar):
        current_timezone = 'utc'
        for component in calendar.subcomponents:
            if component.name == 'VTIMEZONE':
                current_timezone = unicode(component['TZID'])

            if self.valid_event(component):
                component.timezone = current_timezone
                yield component

    def daterange(self, event):
        start = event['dtstart'].dt
        end = event['dtend'].dt

        if isinstance(start, datetime_date):
            start = datetime(
                start.year, start.month, start.day,
                tzinfo=timezone(event.timezone)
            )

        if isinstance(end, datetime_date):
            end = datetime(
                end.year, end.month, end.day, 23, 59, 59,
                tzinfo=timezone(event.timezone)
            )

        return start, end

    def render(self):
        if not self.url:
            return self.say('No url given')

        calendar = Calendar.from_ical(self.read_ical())
        self.say('loaded %s' % self.url)

        events = list(self.events(calendar))
        self.say('found %i events' % len(events))

        for event in events:

            params = dict()
            params['title'] = unicode(event.get('summary', 'No Title'))
            params['short_description'] = unicode(
                event.get('description', 'No Description')
            )

            params['start'], params['end'] = self.daterange(event)

            params['timezone'] = event.timezone
            params['whole_day'] = False
            params['recurrence'] = event.get('rrule', '')

            if params['recurrence']:
                params['recurrence'] = ''.join(
                    'RRULE:', params['recurrence'].to_ical()
                )

            content = addContentToContainer(self.context, createContent(
                'seantis.dir.events.item', **params
            ))

            content.submit()
            content.publish()

        return self.say('events successfully imported')
