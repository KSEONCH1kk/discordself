"""Тесты для permissions calculator"""

import unittest
from discordself.permissions import (
    Permissions,
    PermissionCalculator,
    has_permission,
    has_any_permission,
    has_all_permissions
)


class TestPermissions(unittest.TestCase):
    """Тесты для Permissions"""
    
    def test_from_value(self):
        """Тест создания Permissions из значения"""
        perms = PermissionCalculator.from_value(8)  # ADMINISTRATOR
        self.assertEqual(perms, Permissions.ADMINISTRATOR)
        
        perms = PermissionCalculator.from_value("8")
        self.assertEqual(perms, Permissions.ADMINISTRATOR)
    
    def test_has_permission(self):
        """Тест проверки наличия permission"""
        perms = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL
        self.assertTrue(has_permission(perms, Permissions.SEND_MESSAGES))
        self.assertTrue(has_permission(perms, Permissions.VIEW_CHANNEL))
        self.assertFalse(has_permission(perms, Permissions.KICK_MEMBERS))
        
        # ADMINISTRATOR дает все права
        admin = Permissions.ADMINISTRATOR
        self.assertTrue(has_permission(admin, Permissions.SEND_MESSAGES))
        self.assertTrue(has_permission(admin, Permissions.KICK_MEMBERS))
    
    def test_has_any_permission(self):
        """Тест проверки наличия хотя бы одного permission"""
        perms = Permissions.SEND_MESSAGES
        self.assertTrue(has_any_permission(perms, Permissions.SEND_MESSAGES, Permissions.VIEW_CHANNEL))
        self.assertFalse(has_any_permission(perms, Permissions.KICK_MEMBERS, Permissions.BAN_MEMBERS))
    
    def test_has_all_permissions(self):
        """Тест проверки наличия всех permissions"""
        perms = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL
        self.assertTrue(has_all_permissions(perms, Permissions.SEND_MESSAGES, Permissions.VIEW_CHANNEL))
        self.assertFalse(has_all_permissions(perms, Permissions.SEND_MESSAGES, Permissions.KICK_MEMBERS))
    
    def test_add_remove_permission(self):
        """Тест добавления и удаления permissions"""
        perms = Permissions.SEND_MESSAGES
        perms = PermissionCalculator.add_permission(perms, Permissions.VIEW_CHANNEL)
        self.assertTrue(Permissions.VIEW_CHANNEL in perms)
        
        perms = PermissionCalculator.remove_permission(perms, Permissions.VIEW_CHANNEL)
        self.assertFalse(Permissions.VIEW_CHANNEL in perms)
    
    def test_calculate_overwrite(self):
        """Тест вычисления overwrite"""
        base = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL
        allow = Permissions.KICK_MEMBERS
        deny = Permissions.SEND_MESSAGES
        
        result = PermissionCalculator.calculate_overwrite(base, allow, deny)
        self.assertTrue(Permissions.KICK_MEMBERS in result)
        self.assertTrue(Permissions.VIEW_CHANNEL in result)
        self.assertFalse(Permissions.SEND_MESSAGES in result)
    
    def test_get_permission_list(self):
        """Тест получения списка permissions"""
        perms = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL
        perm_list = PermissionCalculator.get_permission_list(perms)
        self.assertIn("SEND_MESSAGES", perm_list)
        self.assertIn("VIEW_CHANNEL", perm_list)


if __name__ == '__main__':
    unittest.main()

