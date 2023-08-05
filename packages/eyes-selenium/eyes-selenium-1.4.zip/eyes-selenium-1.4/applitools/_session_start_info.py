from .errors import EyesError


class SessionStartInfo(object):
    """
    Encapsulates data required to start session using the Eyes session API.
    """

    def __init__(self, agent_id, app_id_or_name, scenario_id_or_name, batch_info, environment,
                 match_level, ver_id=None, branch_name=None, parent_branch_name=None):
        self.agent_id = agent_id
        self.app_id_or_name = app_id_or_name
        self.scenario_id_or_name = scenario_id_or_name
        self.batch_info = batch_info
        self.environment = environment
        self.match_level = match_level
        self.ver_id = ver_id
        self.branch_name = branch_name
        self.parent_branch_name = parent_branch_name

    def __getstate__(self):
        return dict(agentId=self.agent_id, AppIdOrName=self.app_id_or_name, VerId=self.ver_id,
                    ScenarioIdOrName=self.scenario_id_or_name, BatchInfo=self.batch_info,
                    Environment=self.environment, matchLevel=self.match_level,
                    branchName=self.branch_name, parentBranchName=self.parent_branch_name)

    def __setstate__(self, state):
        raise EyesError("Cannot set session start info from dict!")