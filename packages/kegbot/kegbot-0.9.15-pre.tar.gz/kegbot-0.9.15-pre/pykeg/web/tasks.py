# Copyright 2013 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Tasks for the Kegbot core."""

from kegbot.util import util
from pykeg.plugin import util as plugin_util

from celery.decorators import task

def schedule_tasks(event_list):
    """Synchronously schedules tasks related to the given events."""
    for event in event_list:
        for plugin in plugin_util.get_plugins():
            plugin.handle_new_event(event)

@task
def handle_new_picture(picture_id):
    pass  # TODO(mikey): plugin support

@task
def ping():
    return True
