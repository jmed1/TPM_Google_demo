#Demo test for TPM position at Google.
#Author: Jose F. Medrano
#date: March, 2023
import importlib, pytest, json, requests


@pytest.fixture(scope='session')
def let_me_out():
    loader = importlib.machinery.SourceFileLoader('demos', 'demo.py')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    demos = importlib.util.module_from_spec(spec)
    loader.exec_module(demos)
    return demos


def test_assignIssue(let_me_out):
    assert (let_me_out.assignIssue("AD-3", "1")).status_code == 204