import datetime
import time

from errbot import BotPlugin, re_botcmd


class Stats(BotPlugin):
    """
    Various github/gitlab issue, PR related stats
    """

    def __init__(self, bot, name=None):
        super().__init__(bot, name)

    def activate(self):
        super().activate()
        self.LabHub = self.get_plugin('LabHub')

    @staticmethod
    def community_state(pr_count: dict):
        if (sum(pr_count.values())):
            if any([pr_count.get('coala-bears', 0) >= 2,
                    pr_count.get('coala', 0) >= 5,
                    pr_count.get('coala-utils', 0) >= 1]):
                return 'on fire'
            else:
                return 'alive'
        else:
            return 'dead'

    @re_botcmd(pattern=r'pr\s+stats\s+(\d+)(?:hours|hrs)')
    def pr_stats(self, msg, match):
        hours = match.group(1)
        pr_count = dict()
        start = time.time()
        for count, (name, repo) in enumerate(self.LabHub.gh_repos.items(), 1):
            pr_count[name] = len(list(repo.search_mrs(
                                         created_after=datetime.datetime.now() -
                                                       datetime.timedelta(hours=int(hours))
                             )))
            if (count % 30 == 0):
                seconds_to_sleep = 60 - (time.time() - start)
                self.log.info('Sleeping for {} seconds'.format(seconds_to_sleep))
                time.sleep(seconds_to_sleep)
                self.log.info('Waking up from sleep')
                start = time.time()

        for name, repo in self.LabHub.gl_repos.items():
            pr_count[name] = len(list(repo.search_mrs(
                                        created_after=datetime.datetime.fromtimestamp(time.time()) -
                                                      datetime.timedelta(hours=int(hours)))))
        reply = ''
        reply += '{} PRs opened in last {} hours'.format(sum(pr_count.values()),
                                                         hours)

        reply += '\nThe community is {state}'.format(
                    state=type(self).community_state(pr_count)
                 )
        yield reply
