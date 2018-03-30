from requests.compat import urljoin

from goji.models import Model, User, Issue, Transition
from goji.auth import get_credentials

from uplink import (
    Field, loads, returns, json, Consumer, get, post, put, response_handler
)

loads.from_json(Model).using(lambda model, j: model.from_json(j))


@response_handler
def return_success(response):
    return response.status_code in [200, 201, 204]


@json
class JIRAClient(Consumer):
    def __init__(self, base_url):
        self.auth = email, password = get_credentials(base_url)

        if email is not None and password is not None:
            self.base_url = base_url
            rest_base_url = urljoin(base_url, 'rest/api/2/')
            super(JIRAClient, self).__init__(
                base_url=rest_base_url, auth=(email, password)
            )
        else:
            print('== Authentication not configured. Run `goji login`')
            exit()

    @property
    def username(self):
        return self.auth[0]

    @returns.json(User)
    @get("myself")
    def get_user(self): pass

    @returns.json(Issue)
    @get("issue/{issue_key}")
    def get_issue(self, issue_key): pass

    @returns.json(returns.List[Transition], member="transitions")
    @get("issue/{issue_key}/transitions")
    def get_issue_transitions(self, issue_key): pass

    @returns.json(returns.List[Issue], member="issues")
    @post("search", args={"query": Field("jql")})
    def search(self, query): pass

    @return_success
    @post("issue/{issue_key}/transactions",
          args={"transaction_id": Field(("transaction", "id"))})
    def change_status(self, issue_key, transaction_id): pass

    @return_success
    @put("issue/{issue_key}", args={"fields": Field})
    def edit_issue(self, issue_key, fields): pass

    @return_success
    @put("issue/{issue_key}/assignee", args={"name": Field})
    def assign(self, issue_key, name): pass

    @return_success
    @post("issue/{issue_key}/comment", args={"comment": Field("body")})
    def comment(self, issue_key, comment): pass
