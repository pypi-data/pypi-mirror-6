from fabric.api import local, lcd, run, env


def test():
    """All Tests"""
    local("python ../../manage.py test ftp_deploy --settings=ftp_deploy.tests.conf.conf --exe")


def testc():
    """All Tests with coverage"""
    local("python ../../manage.py test ftp_deploy --settings=ftp_deploy.tests.conf.confc --exe")


def testu():
    """Unit Tests"""
    local("python ../../manage.py test ftp_deploy --exclude=integration_tests --exclude==external_tests --settings=ftp_deploy.tests.conf.conf --exe")


def testi():
    """Integration Tests"""
    local("python ../../manage.py test ftp_deploy --exclude=external_tests --exclude=unit_tests  --settings=ftp_deploy.tests.conf.conf --exe")


def teste():
    """External Tests (FTP, repository etc.)"""
    local("python ../../manage.py test ftp_deploy --exclude=unit_tests --exclude=integration_tests --settings=ftp_deploy.tests.conf.conf --exe")
