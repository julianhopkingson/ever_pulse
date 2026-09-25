import sys
import os
import unittest
from PySide6.QtWidgets import QApplication

# 确保导入路径正确
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.config_mgr import ConfigManager
from core.i18n import I18n
from ui.widgets import AutostartScheduleButton
from ui.components.autostart_schedule_dialog import AutoStartScheduleDialog, WeekDayToggleButton


class TestAutostartSchedule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.config_mgr = ConfigManager(project_root)
        cls.i18n = I18n(os.path.join(project_root, "assets"))

    def test_01_config_mgr_schedule(self):
        # 测试默认值读取
        schedule = self.config_mgr.get_autostart_days()
        self.assertEqual(len(schedule), 7)
        
        # 测试设置为工作日
        workdays = [True, True, True, True, True, False, False]
        self.config_mgr.set_autostart_days(workdays)
        saved = self.config_mgr.get("autostart_days")
        self.assertEqual(saved, "1,2,3,4,5")
        self.assertEqual(self.config_mgr.get_autostart_days(), workdays)
        
        # 测试设置为全周
        everyday = [True] * 7
        self.config_mgr.set_autostart_days(everyday)
        self.assertEqual(self.config_mgr.get("autostart_days"), "1,2,3,4,5,6,7")
        self.assertEqual(self.config_mgr.get_autostart_days(), everyday)

        # 恢复默认工作日
        self.config_mgr.set_autostart_days(workdays)
        self.config_mgr.save()

    def test_02_schedule_dialog_and_quick_presets(self):
        initial = [True, True, True, True, True, False, False]
        dlg = AutoStartScheduleDialog(initial, self.i18n, theme_name="Light")
        
        # 初始状态校验
        self.assertEqual(len(dlg.day_buttons), 7)
        self.assertTrue(dlg.day_buttons[0].isChecked()) # Mon
        self.assertTrue(dlg.day_buttons[4].isChecked()) # Fri
        self.assertFalse(dlg.day_buttons[5].isChecked()) # Sat
        self.assertFalse(dlg.day_buttons[6].isChecked()) # Sun
        
        # 触发全周开启
        dlg.set_quick_everyday()
        self.assertTrue(all(btn.isChecked() for btn in dlg.day_buttons))
        
        # 触发工作日开启
        dlg.set_quick_workdays()
        self.assertEqual([btn.isChecked() for btn in dlg.day_buttons], initial)

        # 单个切换
        dlg.day_buttons[5].setChecked(True) # Sat 开启
        self.assertTrue(dlg.day_buttons[5].isChecked())
        
        # 保存并获取
        dlg.save_and_close()
        res = dlg.get_schedule()
        self.assertEqual(res, [True, True, True, True, True, True, False])

    def test_03_schedule_button_and_theme(self):
        btn = AutostartScheduleButton(theme_name="Light")
        self.assertEqual(btn.width(), 36)
        self.assertEqual(btn.height(), 36)
        
        # 切换暗色主题
        btn.set_theme("Dark")
        self.assertEqual(btn.theme_name, "Dark")


if __name__ == "__main__":
    unittest.main()
