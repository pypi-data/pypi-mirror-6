
class InteractObjectConfig(object):
    def __init__(profile_list=None, campaign=None, event=None):
        self._list = profile_list
        self._campaign = campaign
        self._event = event

    @property
    def list(self):
        return self._list

    @property
    def campaign(self):
        return self._campaign

    @property
    def event(self):
        return self._event

TEST_CAMPAIGN = InteractObjectConfig(
    profile_list='folder/list',
    campaign='folder/campaign',
    event='event',
)

WELCOME_CAMPAIGN = InteractObjectConfig(
    profile_list='welcome/my_list',
    campaign='welcome/welcome_campaign',
    event='welcome_custom_event',
)
        
