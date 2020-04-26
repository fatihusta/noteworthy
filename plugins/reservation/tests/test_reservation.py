import pytest

from noteworthy.reservation import ReservationController

from noteworthy.reservation.api.models import BetaUser


def test_reserve_domain():
    # TODO implement me
    pass

@pytest.mark.django_db
def test_get_user_by_auth_code():
    user = BetaUser.objects.create_user('testuser@gmail.com')
    BetaUser.objects.provision_beta_keys(1)
    user.refresh_from_db()
    rc = ReservationController()
    user_by_auth = rc._get_user_by_auth(str(user.beta_key))
    assert user.id == user_by_auth.id
    # also works without casting auth_code to str
    user_by_auth = rc._get_user_by_auth(user.beta_key)
    assert user.id == user_by_auth.id

@pytest.mark.django_db
def test_validate_registration():
    pass

def test_validate_domain():
    rc = ReservationController()
    base, subdomain, site = rc._validate_domain('matrix.noteworthy.im')
    assert base == 'noteworthy.im'
    assert subdomain == 'matrix'
    assert site == ''
    base, subdomain, site = rc._validate_domain('matrix.subdomain.noteworthy.im')
    assert base == 'noteworthy.im'
    assert subdomain == 'subdomain'
    assert site == 'matrix'

def test_is_valid_hostname():
    rc = ReservationController()
    assert rc._is_valid_hostname('abc.noteworthy') == True
    assert rc._is_valid_hostname('abracadabra.noteworthy.im') == True
    assert rc._is_valid_hostname('noteworthy.') == True
    assert rc._is_valid_hostname('www.google.com') == True
    assert rc._is_valid_hostname('my.name.is.mo.noteworthy.im') == True
    assert rc._is_valid_hostname('a'*63) == True
    assert rc._is_valid_hostname('a'*64) == False
    assert rc._is_valid_hostname('') == False
    assert rc._is_valid_hostname('.') == False
    assert rc._is_valid_hostname('---') == False
    assert rc._is_valid_hostname('.noteworthy.') == False
    assert rc._is_valid_hostname('$$$.noteworthy.im') == False
    assert rc._is_valid_hostname('hello_word.com') == False