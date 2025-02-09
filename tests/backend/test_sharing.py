from .relations import *
from .utils import ShouldRaise, MwdbTest


def test_share_with_foreign(admin_session):
    testCase = RelationTestCase(admin_session)

    Alice = testCase.new_user("Alice")
    Bob = testCase.new_user("Bob")
    Joe = testCase.new_user("Joe")

    Workgroup = testCase.new_group("Workgroup")
    Homegroup = testCase.new_group("Homegroup", ["sharing_with_all"])

    Workgroup.add_member(Alice)
    Workgroup.add_member(Bob)
    Homegroup.add_member(Joe)

    File = testCase.new_sample("File")

    File.create(Alice, upload_as=Alice.identity)
    File(should_access=[Alice]).test()

    with ShouldRaise(status_code=404):
        Alice.session.share_with(File.dhash, Homegroup.identity)

    Alice.session.share_with(File.dhash, Workgroup.identity)
    File(should_access=[Alice, Bob]).test()

    FileB = testCase.new_sample("FileB")
    FileB.create(Joe)
    FileB(should_access=[Joe]).test()

    Joe.session.share_with(FileB.dhash, Workgroup.identity)

    FileB(should_access=[Alice, Bob, Joe]).test()


def test_share_with_public(admin_session):
    testCase = RelationTestCase(admin_session)

    Alice = testCase.new_user("Alice")
    Bob = testCase.new_user("Bob")
    Joe = testCase.new_user("Joe")

    Workgroup = testCase.new_group("Workgroup")
    Homegroup = testCase.new_group("Homegroup", ["sharing_with_all"])

    Workgroup.add_member(Alice)
    Workgroup.add_member(Bob)
    Homegroup.add_member(Joe)

    File = testCase.new_sample("File")

    File.create(Alice, upload_as=Alice.identity)
    File(should_access=[Alice]).test()

    Alice.session.share_with(File.dhash, "public")

    File(should_access=[Alice, Bob, Joe]).test()


def test_share_and_leave(admin_session):
    testCase = RelationTestCase(admin_session)

    session = MwdbTest()
    session.login()

    Alice = testCase.new_user("Alice")
    Bob = testCase.new_user("Bob")
    Joe = testCase.new_user("Joe")

    Workgroup = testCase.new_group("Workgroup")
    Homegroup = testCase.new_group("Homegroup", ["sharing_with_all"])

    Workgroup.add_member(Alice)
    Workgroup.add_member(Bob)
    Homegroup.add_member(Joe)

    File = testCase.new_sample("File")

    File.create(Alice)
    File(should_access=[Alice, Bob]).test()

    session.remove_member(Workgroup.identity, Alice.identity)
    File(should_access=[Alice, Bob]).test()

    session.add_member(Workgroup.identity, Joe.identity)
    File(should_access=[Alice, Bob, Joe]).test()

    session.remove_member(Workgroup.identity, Joe.identity)
    File(should_access=[Alice, Bob]).test()


def test_list_groups_for_share(admin_session):
    testCase = RelationTestCase(admin_session)

    Alice = testCase.new_user("Alice")
    Bob = testCase.new_user("Bob")
    Joe = testCase.new_user("Joe")

    Workgroup = testCase.new_group("Workgroup")
    Homegroup = testCase.new_group("Homegroup", ["sharing_with_all"])

    Workgroup.add_member(Alice)
    Workgroup.add_member(Bob)
    Homegroup.add_member(Joe)

    assert sorted(Alice.session.get_sharing_groups()) == sorted([
        Alice.identity,
        Workgroup.identity,
        "registered",
        "public"
    ])

    assert sorted(Bob.session.get_sharing_groups()) == sorted([
        Bob.identity,
        Workgroup.identity,
        "registered",
        "public"
    ])

    assert set(Joe.session.get_sharing_groups()).issuperset([
        Alice.identity,
        Bob.identity,
        Joe.identity,
        Homegroup.identity,
        Workgroup.identity,
        "registered",
        "public"
    ])
