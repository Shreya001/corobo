import logging
import unittest
from unittest.mock import create_autospec, PropertyMock

from errbot.backends.test import TestBot
from IGitt.GitHub.GitHubRepository import GitHubRepository

import plugins
from plugins.stats import Stats
from plugins.labhub import LabHub, GitHub, GitLab
from tests.helper import plugin_testbot


class TestStats(unittest.TestCase):

    def setUp(self):
        GitHub.write_repositories = PropertyMock()
        GitLab.write_repositories = PropertyMock()

        labhub, self.testbot = plugin_testbot(LabHub, loglevel=logging.ERROR)
        labhub.activate()
        self.stats = self.testbot.bot.plugin_manager.instanciateElement(Stats)
        self.stats.activate()
        self.stats.LabHub.gh_repos = {
            'coala': create_autospec(GitHubRepository),
            'coala-bears': create_autospec(GitHubRepository),
            'coala-utils': create_autospec(GitHubRepository)
        }

    def test_alive(self):
        self.stats.LabHub.gh_repos['coala'].search_mrs.return_value = [1, 2]
        self.stats.LabHub.gh_repos['coala-bears'].search_mrs.return_value = []
        self.stats.LabHub.gh_repos['coala-utils'].search_mrs.return_value = []
        self.testbot.assertCommand('!pr stats 10hours',
                                   '2 PRs opened in last 10 hours\n'
                                   'The community is alive')

        self.stats.LabHub.gh_repos['coala'].search_mrs.return_value = []
        self.testbot.assertCommand('!pr stats 5hours',
                                   '0 PRs opened in last 5 hours\n'
                                   'The community is dead')

        self.stats.LabHub.gh_repos['coala'].search_mrs.return_value = [
            1, 2, 3, 4, 5,
            6, 7, 8, 9, 10
        ]
        self.testbot.assertCommand('!pr stats 3hours',
                                   '8 PRs opened in last 3 hours\n'
                                   'The community is on fire')
