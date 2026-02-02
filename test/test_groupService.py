from unittest import TestCase

from database.model.groupModel import GroupModel, create_group


class TestGroupService(TestCase):
    def test_create_group(self):
        group = GroupModel(
            owner=1,
            name="BESCHTE GRUPPEE",
        )
        new_group = create_group(group)
        print(new_group.id)

    def test_edit_account(self):
        self.fail()

    def test_delete_account(self):
        self.fail()
