from PySide6.QtCore import QThread, Signal, QObject
import time
import datetime
from core.mouse_engine import move_relative, set_mouse_position
from core.idle_detector import get_idle_duration

class AutomationWorker(QThread):
    status_updated = Signal(str) # 发送状态文本
    error_occurred = Signal(str) # 发送错误信息
    request_auto_close = Signal() # 请求自动关闭应用
    finished = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True
        self.is_paused = False
        
    def stop(self):
        self.running = False
        self.wait()

    def run(self):
        # 读取配置
        try:
            start_h = int(self.config.get('start_hour'))
            start_m = int(self.config.get('start_minute'))
            start_s = int(self.config.get('start_second'))
            end_h = int(self.config.get('end_hour'))
            end_m = int(self.config.get('end_minute'))
            end_s = int(self.config.get('end_second'))
            interval = int(self.config.get('interval'))
            direction = self.config.get('direction')
            pixels = int(self.config.get('pixels'))
            threshold = int(self.config.get('activity_threshold'))
        except Exception as e:
            self.error_occurred.emit(f"Config Error: {e}")
            return

        direction_map = {
            "上": (0, -1), "Up": (0, -1),
            "下": (0, 1),  "Down": (0, 1),
            "左": (-1, 0), "Left": (-1, 0),
            "右": (1, 0),  "Right": (1, 0)
        }
        dx, dy = direction_map.get(direction, (-1, 0))
        dx *= pixels
        dy *= pixels

        first_move = True

        # 状态标记：本次会话是否已经开始工作过
        has_active_session = False

        while self.running:
            now_dt = datetime.datetime.now()
            current_time = now_dt.time()
            start_time = datetime.time(start_h, start_m, start_s)
            end_time = datetime.time(end_h, end_m, end_s)

            should_run = False
            
            # --- 核心判定逻辑 (V6 Asymmetric) ---
            if start_time <= end_time:
                # [单日模式 Single Day]
                if current_time > end_time:
                    # 严格判定：超过结束时间 -> 视为会话完成
                    # 发送特殊状态字符串，UI层需识别并翻译
                    self.status_updated.emit("Scheduled end reached.")
                    self.request_auto_close.emit()
                    break # 退出循环，触发自动关闭
                
                elif current_time < start_time:
                    should_run = False # Wait
                else:
                    should_run = True  # Run
            
            else:
                # [跨天模式 Cross Day]
                # 始终保持循环 Loop (除非被外部停止)
                after_start = current_time >= start_time
                before_end = current_time <= end_time
                
                if after_start:
                    should_run = True # 前半段：无条件运行 (20:00~23:59)
                elif before_end:
                    # 后半段 (00:00~05:00): 仅允许延续，禁止新准入 (Strict Entry)
                    should_run = has_active_session
                else:
                    should_run = False # Gap: Waiting
            
            # --- 执行逻辑 ---
            if should_run:
                has_active_session = True 
                
                idle_time = get_idle_duration()
                
                if idle_time < threshold:
                    self.status_updated.emit(f"User active (idle {idle_time:.1f}s), skipping...")
                else:
                    if first_move:
                         # Align to start_second logic
                         # This logic aligns the FIRST active move to the :start_s second mark if possible
                         current_s = now_dt.second
                         target_s = start_s
                         
                         wait_s = 0
                         if current_s < target_s:
                             wait_s = target_s - current_s
                         elif current_s > target_s:
                             wait_s = (60 - current_s) + target_s
                             
                         if wait_s > 0:
                             # Formatted string will be handled by UI via format()
                             # "status_aligning_first_move" expects: "Waiting {}s to align... {:02d}"
                             # We pass a special string that UI can parse? 
                             # No, existing UI logic parses "Moved at" etc.
                             # But `status_aligning_first_move` has placeholders.
                             # Let's send a formatted string that UI logic can either display raw or I need to handle it in UI.
                             # The easiest way is to format it here if we assume the KEY is used for lookup but formatting is done here?
                             # Wait, the `log_message` in MainWindow uses `_translate_log`.
                             # If I send "AligningFirstMove|10|00", I can parse it.
                             # But let's stick to the protocol.
                             # "status_aligning_first_move" in language.ini: "Waiting {}s ... {:02d}"
                             # If `_translate_log` doesn't support format args for this key, I need to update UI.
                             # Let's update UI to handle "Aligning: 10, 00" or similar protocol?
                             # Or just send format params?
                             # Let's emit a special signal? No status_updated is str.
                             
                             # Let's use a protocol prefix: "status_aligning_first_move:10:00"
                             self.status_updated.emit(f"status_aligning_first_move:{wait_s}:{target_s}")
                             
                             for _ in range(wait_s):
                                 if not self.running: break
                                 time.sleep(1)
                             
                             if not self.running: break
                             
                             # Re-check time after wait (in case we drifted into forbidden zone?)
                             # But simplistic is fine.
                             pass

                    # Jiggle
                    move_relative(dx, dy)
                    time.sleep(0.1)
                    move_relative(-dx, -dy)
                    
                    self.status_updated.emit(f"Moved at {now_dt.strftime('%H:%M:%S')}")

                # Interval Wait
                for _ in range(interval * 10): 
                    if not self.running: break
                    time.sleep(0.1) 
                    
                first_move = False

            else:
                # Not Running
                if has_active_session:
                    # 刚才还在跑，现在断了 -> 说明是自然结束 (Cross Day End)
                    # 单日模式已在上方 break，所以这里一定是跨天模式的自然结束 (05:01)
                    self.status_updated.emit("Scheduled end reached.")
                    self.request_auto_close.emit()
                    break # 退出循环，触发自动关闭
                else:
                    # Waiting
                    self.status_updated.emit("Waiting - Outside working hours")
                    time.sleep(1)
        
        self.finished.emit()
