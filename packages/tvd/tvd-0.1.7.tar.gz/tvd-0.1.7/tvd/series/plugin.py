#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 Hervé BREDIN (http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import yaml
import logging
from pkg_resources import resource_filename

from tvd.common.episode import Episode
from tvd.common.time import TFloating

CONFIG_HUMAN_READABLE_NAME = 'name'
CONFIG_ORIGINAL_LANGUAGE = 'language'
CONFIG_EPISODES = 'episodes'
CONFIG_WEB_RESOURCES = 'www'


SOURCE = 'source'
URL = 'url'
SEASON = 'season'
EPISODE = 'episode'


class SeriesPlugin(object):

    def __init__(self):

        super(SeriesPlugin, self).__init__()

        # obtain path to YAML configuration file and load it
        path = resource_filename(self.__class__.__name__, 'tvd.yml')
        with open(path, mode='r') as f:
            self.config = yaml.load(f)

        # human readable name is obtained from YAML configuration file
        self.name = self.config[CONFIG_HUMAN_READABLE_NAME]

        # original language is obtained from YAML configuration file
        self.language = self.config[CONFIG_ORIGINAL_LANGUAGE]

        # list of episodes according to configuration file
        # e.g. episodes: [17, 23, 23] ==> season 1 (2, 3) with 17 (23, 23) eps
        episodes = self.config.get(CONFIG_EPISODES, [])
        self.episodes = [
            Episode(
                series=self.__class__.__name__,
                season=season_index+1,
                episode=episode_index+1
            )
            for season_index, n_episodes in enumerate(episodes)
            for episode_index in range(n_episodes)
        ]

        # initialize web resources data structure
        # resources[episode] contains all resources for a given episode
        self.resources = {}

        # load 'www' section from YAML configuration file
        www = self.config.get(CONFIG_WEB_RESOURCES, {})

        # loop on web resources described in 'www' section
        for resource_type, resource in www.iteritems():

            # obtain corresponding 'get_resource' method
            resource_method = self._get_resource_method(resource_type)

            # read resource 'source' from YAML configuration when provided
            source = resource.get(SOURCE, None)

            # loop on all provided URLs
            # NB: some episodes might not have some resources
            for url in resource.get(URL, []):

                season_number = url[SEASON]
                episode_number = url[EPISODE]
                episode = Episode(
                    series=self.__class__.__name__,
                    season=season_number,
                    episode=episode_number
                )

                # add episode to resource main structure
                # in case it is the first time it is encountered
                if episode not in self.resources:
                    self.resources[episode] = {}

                # initialize resource placeholder
                #
                self.resources[episode][resource_type] = {
                    # method to call to get the resource
                    'method': resource_method,
                    # parameters to pass to method to get the resource
                    'params': {
                        'url': url[URL],
                        'source': source,
                        'episode': episode
                    },
                    # results of call "method(**params)"
                    # NB: it is set to None until we actually get this resource
                    'result': None
                }

    def _get_resource_method(self, resource_type):
        """Get method for given resource

        resource_type : str
            Resource type, as provided in YAML configuration file

        Returns
        -------
        method : callable
            Method defined in inheriting plugin to be used
            to obtain `resource_type` resource

        """
        resource_method = getattr(self, resource_type, None)

        if resource_method is None:

            error = 'Class %s has no method called %s.' % (
                self.__class__.__name__, resource_type)

            raise ValueError(error)

        return resource_method

    def has_resource(self, resource_type, episode):
        """
        Checks whether resource `resource_type` exists
        for given `episode`

        Parameters
        ----------
        resource_type : str
        episode : `tvd.Episode`
        """

        resources = self.resources.get(episode, None)
        if resources is None:
            return False

        resource = resources.get(resource_type, None)
        if resource is None:
            return False

        return True

    def get_resource(self, resource_type, episode, update=False):
        """

        Parameters
        ----------
        resource_type: str
        episode : `Episode`
        update : bool, optional
            When True, force re-downloading of resources
        """

        if not self.has_resource(resource_type, episode):
            error = 'Episode {episode} has no resource "{resource_type}"'
            raise ValueError(error.format(
                episode=episode,
                resource_type=resource_type)
            )

        resource = self.resources[episode][resource_type]

        result = resource['result']
        if update or result is None:
            method = resource['method']
            params = resource['params']

            msg = 'updating "{ep:s}" "{rsrc:s}"'
            logging.debug(msg.format(ep=episode, rsrc=resource_type))

            TFloating.reset()
            result = method(**params)

            self.resources[episode][resource_type]['result'] = result

        return result

    def iter_resources(self, resource_type=None, episode=None, update=False):
        """Resource iterator

        Resources are yielded in episode chronological order
        and resource name alphabetical order

        Parameters
        ----------
        resource_type : str, optional
            When provided, only iterate over this resource type
        episode : `tvd.Episode`, optional
            When provided, only iterate over resources for this episode
        update : boolean, optional
            Whether to force update resource.
            Defaults to False (i.e. use existing resource)

        Returns
        -------
        (episode, resource_type, data) iterator
        """

        # loop on episodes in airing chronological order
        for _episode in sorted(self.resources):

            # skip this episode if not requested
            if (episode is not None) and \
               (episode != _episode):
                continue

            # loop on resources in name alphabetical order
            for _resource_type in sorted(self.resources[_episode]):

                # skip this resource if not requested
                if (resource_type is not None) and \
                   (resource_type != _resource_type):
                    continue

                # this is where we really get this resource
                _data = self.get_resource(
                    _resource_type,
                    _episode,
                    update=update
                )

                yield _episode, _resource_type, _data

    def get_all_resources(self, update=False):

        resources = {}

        for episode, resource_type, resource in self.iter_resources(
            resource_type=None, episode=None,
            update=update
        ):

            if episode not in resources:
                resources[episode] = {}

            resources[episode][resource_type] = resource

        return resources
