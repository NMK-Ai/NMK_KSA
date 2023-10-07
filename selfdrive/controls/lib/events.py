#!/usr/bin/env python3
import math
import os
from enum import IntEnum
from typing import Dict, Union, Callable, List, Optional

from cereal import log, car
import cereal.messaging as messaging
from openpilot.common.conversions import Conversions as CV
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.locationd.calibrationd import MIN_SPEED_FILTER
from openpilot.system.version import get_short_branch

AlertSize = log.ControlsState.AlertSize
AlertStatus = log.ControlsState.AlertStatus
VisualAlert = car.CarControl.HUDControl.VisualAlert
AudibleAlert = car.CarControl.HUDControl.AudibleAlert
EventName = car.CarEvent.EventName


# Alert priorities
class Priority(IntEnum):
  LOWEST = 0
  LOWER = 1
  LOW = 2
  MID = 3
  HIGH = 4
  HIGHEST = 5


# Event types
class ET:
  ENABLE = 'enable'
  PRE_ENABLE = 'preEnable'
  OVERRIDE_LATERAL = 'overrideLateral'
  OVERRIDE_LONGITUDINAL = 'overrideLongitudinal'
  NO_ENTRY = 'noEntry'
  WARNING = 'warning'
  USER_DISABLE = 'userDisable'
  SOFT_DISABLE = 'softDisable'
  IMMEDIATE_DISABLE = 'immediateDisable'
  PERMANENT = 'permanent'


# get event name from enum
EVENT_NAME = {v: k for k, v in EventName.schema.enumerants.items()}


class Events:
  def __init__(self):
    self.events: List[int] = []
    self.static_events: List[int] = []
    self.events_prev = dict.fromkeys(EVENTS.keys(), 0)

  @property
  def names(self) -> List[int]:
    return self.events

  def __len__(self) -> int:
    return len(self.events)

  def add(self, event_name: int, static: bool=False) -> None:
    if static:
      self.static_events.append(event_name)
    self.events.append(event_name)

  def clear(self) -> None:
    self.events_prev = {k: (v + 1 if k in self.events else 0) for k, v in self.events_prev.items()}
    self.events = self.static_events.copy()

  def contains(self, event_type: str) -> bool:
    return any(event_type in EVENTS.get(e, {}) for e in self.events)

  def create_alerts(self, event_types: List[str], callback_args=None):
    if callback_args is None:
      callback_args = []

    ret = []
    for e in self.events:
      types = EVENTS[e].keys()
      for et in event_types:
        if et in types:
          alert = EVENTS[e][et]
          if not isinstance(alert, Alert):
            alert = alert(*callback_args)

          if DT_CTRL * (self.events_prev[e] + 1) >= alert.creation_delay:
            alert.alert_type = f"{EVENT_NAME[e]}/{et}"
            alert.event_type = et
            ret.append(alert)
    return ret

  def add_from_msg(self, events):
    for e in events:
      self.events.append(e.name.raw)

  def to_msg(self):
    ret = []
    for event_name in self.events:
      event = car.CarEvent.new_message()
      event.name = event_name
      for event_type in EVENTS.get(event_name, {}):
        setattr(event, event_type, True)
      ret.append(event)
    return ret


class Alert:
  def __init__(self,
               alert_text_1: str,
               alert_text_2: str,
               alert_status: log.ControlsState.AlertStatus,
               alert_size: log.ControlsState.AlertSize,
               priority: Priority,
               visual_alert: car.CarControl.HUDControl.VisualAlert,
               audible_alert: car.CarControl.HUDControl.AudibleAlert,
               duration: float,
               alert_rate: float = 0.,
               creation_delay: float = 0.):

    self.alert_text_1 = alert_text_1
    self.alert_text_2 = alert_text_2
    self.alert_status = alert_status
    self.alert_size = alert_size
    self.priority = priority
    self.visual_alert = visual_alert
    self.audible_alert = audible_alert

    self.duration = int(duration / DT_CTRL)

    self.alert_rate = alert_rate
    self.creation_delay = creation_delay

    self.alert_type = ""
    self.event_type: Optional[str] = None

  def __str__(self) -> str:
    return f"{self.alert_text_1}/{self.alert_text_2} {self.priority} {self.visual_alert} {self.audible_alert}"

  def __gt__(self, alert2) -> bool:
    if not isinstance(alert2, Alert):
      return False
    return self.priority > alert2.priority


class NoEntryAlert(Alert):
  def __init__(self, alert_text_2: str,
               alert_text_1: str = "القائد الآلي غير متوفر",
               visual_alert: car.CarControl.HUDControl.VisualAlert=VisualAlert.none):
    super().__init__(alert_text_1, alert_text_2, AlertStatus.normal,
                     AlertSize.mid, Priority.LOW, visual_alert,
                     AudibleAlert.refuse, 3.)


class SoftDisableAlert(Alert):
  def __init__(self, alert_text_2: str):
    super().__init__("القائد الآلي غير متوفر", alert_text_2,
                     AlertStatus.userPrompt, AlertSize.full,
                     Priority.MID, VisualAlert.steerRequired,
                     AudibleAlert.warningSoft, 2.),


# less harsh version of SoftDisable, where the condition is user-triggered
class UserSoftDisableAlert(SoftDisableAlert):
  def __init__(self, alert_text_2: str):
    super().__init__(alert_text_2),
    self.alert_text_1 = "سيتم إلغاء تشغيل القائد الآلي"


class ImmediateDisableAlert(Alert):
  def __init__(self, alert_text_2: str):
    super().__init__("قم بالتحكم بالسيارة فوراً", alert_text_2,
                     AlertStatus.critical, AlertSize.full,
                     Priority.HIGHEST, VisualAlert.steerRequired,
                     AudibleAlert.warningImmediate, 4.),


class EngagementAlert(Alert):
  def __init__(self, audible_alert: car.CarControl.HUDControl.AudibleAlert):
    super().__init__("", "",
                     AlertStatus.normal, AlertSize.none,
                     Priority.MID, VisualAlert.none,
                     audible_alert, .2),


class NormalPermanentAlert(Alert):
  def __init__(self, alert_text_1: str, alert_text_2: str = "", duration: float = 0.2, priority: Priority = Priority.LOWER, creation_delay: float = 0.):
    super().__init__(alert_text_1, alert_text_2,
                     AlertStatus.normal, AlertSize.mid if len(alert_text_2) else AlertSize.small,
                     priority, VisualAlert.none, AudibleAlert.none, duration, creation_delay=creation_delay),


class StartupAlert(Alert):
  def __init__(self, alert_text_1: str, alert_text_2: str = "أبقِ يديك على المقود وعينيك على الطريق دائمًا", alert_status=AlertStatus.normal):
    super().__init__(alert_text_1, alert_text_2,
                     alert_status, AlertSize.mid,
                     Priority.LOWER, VisualAlert.none, AudibleAlert.none, 5.),


# ********** helper functions **********
def get_display_speed(speed_ms: float, metric: bool) -> str:
  speed = int(round(speed_ms * (CV.MS_TO_KPH if metric else CV.MS_TO_MPH)))
  unit = 'km/h' if metric else 'mph'
  return f"{speed} {unit}"


# ********** alert callback functions **********

AlertCallbackType = Callable[[car.CarParams, car.CarState, messaging.SubMaster, bool, int], Alert]


def soft_disable_alert(alert_text_2: str) -> AlertCallbackType:
  def func(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
    if soft_disable_time < int(0.5 / DT_CTRL):
      return ImmediateDisableAlert(alert_text_2)
    return SoftDisableAlert(alert_text_2)
  return func

def user_soft_disable_alert(alert_text_2: str) -> AlertCallbackType:
  def func(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
    if soft_disable_time < int(0.5 / DT_CTRL):
      return ImmediateDisableAlert(alert_text_2)
    return UserSoftDisableAlert(alert_text_2)
  return func

def startup_master_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  branch = get_short_branch("")  # تأكد من تخزين get_short_branch مسبقًا لتجنب التأخير عند بدء التشغيل
  if "REPLAY" in os.environ:
    branch = "replay"

  return StartupAlert("تحذير: هذا الفرع غير مُختبر", branch, alert_status=AlertStatus.userPrompt)

def below_engage_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  return NoEntryAlert(f"قد فوق {get_display_speed(CP.minEnableSpeed, metric)} للتفعيل")


def below_steer_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  return Alert(
    f"التوجيه غير متاح أدناه {get_display_speed(CP.minSteerSpeed, metric)}",
    "",
    AlertStatus.userPrompt, AlertSize.small,
    Priority.LOW, VisualAlert.steerRequired, AudibleAlert.prompt, 0.4)


def calibration_incomplete_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  first_word = 'إعادة المعايرة' if sm['liveCalibration'].calStatus == log.LiveCalibrationData.Status.recalibrating else 'المعايرة'
  return Alert(
    f"{first_word} قيد التقدم: {sm['liveCalibration'].calPerc:.0f}%",
    f"قد بسرعة أعلى من {get_display_speed(MIN_SPEED_FILTER, metric)}",
    AlertStatus.normal, AlertSize.mid,
    Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2)


def no_gps_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  return Alert(
    "استقبال ضعيف للـ GPS",
    "خلل في الأجهزة إذا كان السماء مرئية",
    AlertStatus.normal, AlertSize.mid,
    Priority.LOWER, VisualAlert.none, AudibleAlert.none, .2, creation_delay=300.)

# *** debug alerts ***

def out_of_space_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  full_perc = round(100. - sm['deviceState'].freeSpacePercent)
  return NormalPermanentAlert("نفاد مساحة التخزين", f"{full_perc}% ممتلئ")


def posenet_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  mdl = sm['modelV2'].velocity.x[0] if len(sm['modelV2'].velocity.x) else math.nan
  err = CS.vEgo - mdl
  msg = f"خطأ في السرعة: {err:.1f} م/ث"
  return NoEntryAlert(msg, alert_text_1="سرعة Posenet غير صالحة")


def process_not_running_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  not_running = [p.name for p in sm['managerState'].processes if not p.running and p.shouldBeRunning]
  msg = ', '.join(not_running)
  return NoEntryAlert(msg, alert_text_1="العملية ليست قيد التشغيل")


def comm_issue_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  bs = [s for s in sm.data.keys() if not sm.all_checks([s, ])]
  msg = ', '.join(bs[:4])  # لا يمكن استيعاب الكثير على سطر واحد
  return NoEntryAlert(msg, alert_text_1="مشكلة في الاتصال بين العمليات")


def camera_malfunction_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  all_cams = ('roadCameraState', 'driverCameraState', 'wideRoadCameraState')
  bad_cams = [s.replace('State', '') for s in all_cams if s in sm.data.keys() and not sm.all_checks([s, ])]
  return NormalPermanentAlert("عطل الكاميرا", ', '.join(bad_cams))


def calibration_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  rpy = sm['liveCalibration'].rpyCalib
  yaw = math.degrees(rpy[2] if len(rpy) == 3 else math.nan)
  pitch = math.degrees(rpy[1] if len(rpy) == 3 else math.nan)
  angles = f"إعادة تركيب الجهاز (ميل: {pitch:.1f}°، يو: {yaw:.1f}°)"
  return NormalPermanentAlert("عدم صحة الوزن", angles)



def overheat_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  cpu = max(sm['deviceState'].cpuTempC, default=0.)
  gpu = max(sm['deviceState'].gpuTempC, default=0.)
  temp = max((cpu, gpu, sm['deviceState'].memoryTempC))
  return NormalPermanentAlert("النظام ساخن", f"{temp:.0f} °م")


def low_memory_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  return NormalPermanentAlert("الذاكرة منخفضة", f"{sm['deviceState'].memoryUsagePercent}% مستخدمة")


def high_cpu_usage_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  x = max(sm['deviceState'].cpuUsagePercent, default=0.)
  return NormalPermanentAlert("استخدام معالج المعلومات مرتفع", f"{x}% مستخدمة")


def modeld_lagging_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  return NormalPermanentAlert("تأخر نموذج القيادة", f"{sm['modelV2'].frameDropPerc:.1f}% من الإطارات تم التخلي عنها")


def wrong_car_mode_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  text = "قم بتمكين مثبت السرعة للتفعيل"
  if CP.carName == "هوندا":
    text = "قم بتمكين المفتاح الرئيسي للتفعيل"
  return NoEntryAlert(text)


def joystick_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  axes = sm['testJoystick'].axes
  gb, steer = list(axes)[:2] if len(axes) else (0., 0.)
  vals = f"المحرك: {round(gb * 100.)}%, القيادة: {round(steer * 100.)}%"
  return NormalPermanentAlert("وضع الجويستيك", vals)

def speed_limit_adjust_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int) -> Alert:
  speedLimit = sm['longitudinalPlanSP'].speedLimit
  speed = round(speedLimit * (CV.MS_TO_KPH if metric else CV.MS_TO_MPH))
  message = f'ضبط السرعة إلى {speed} {"كم/ساعة" if metric else "ميل/ساعة"} الحد الأقصى للسرعة'
  return Alert(
    message,
    "",
    AlertStatus.normal, AlertSize.small,
    Priority.LOW, VisualAlert.none, AudibleAlert.none, 4.)



EVENTS: Dict[int, Dict[str, Union[Alert, AlertCallbackType]]] = {
  # ********** events with no alerts **********

  EventName.stockFcw: {},

  # ********** events only containing alerts displayed in all states **********

  EventName.joystickDebug: {
    ET.WARNING: joystick_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع التحكم باليد"),
  },

  EventName.controlsInitializing: {
    ET.NO_ENTRY: NoEntryAlert("جاري تهيئة النظام"),
  },

  EventName.startup: {
    ET.PERMANENT: StartupAlert("كن مستعدًا للتدخل في أي وقت")
  },

  EventName.startupMaster: {
    ET.PERMANENT: startup_master_alert,
  },

  # Car is recognized, but marked as dashcam only
  EventName.startupNoControl: {
    ET.PERMANENT: StartupAlert("وضع الداش كام"),
    ET.NO_ENTRY: NoEntryAlert("وضع الداش كام"),
  },

  # Car is not recognized
  EventName.startupNoCar: {
    ET.PERMANENT: StartupAlert("وضع الداش كام للسيارة غير المدعومة"),
  },

  EventName.startupNoFw: {
    ET.PERMANENT: StartupAlert("لم يتم التعرف على السيارة",
                               "تحقق من اتصالات الطاقة للOBD",
                               alert_status=AlertStatus.userPrompt),
  },

  EventName.dashcamMode: {
    ET.PERMANENT: NormalPermanentAlert("وضع الداش كام",
                                       priority=Priority.LOWEST),
  },

  EventName.invalidLkasSetting: {
    ET.PERMANENT: NormalPermanentAlert("تم تفعيل نظام LKAS الأصلي",
                                       "قم بإيقاف نظام LKAS الأصلي للتفعيل"),
  },

  EventName.cruiseMismatch: {
    #ET.PERMANENT: ImmediateDisableAlert("openpilot failed to cancel cruise"),
  },

  # openpilot doesn't recognize the car. This switches openpilot into a
  # read-only mode. This can be solved by adding your fingerprint.
  # See https://github.com/commaai/openpilot/wiki/Fingerprinting for more information
  EventName.carUnrecognized: {
    ET.PERMANENT: NormalPermanentAlert("وضع الداش كام",
                                       "السيارة غير معروفة",
                                       priority=Priority.LOWEST),
  },

  EventName.stockAeb: {
    ET.PERMANENT: Alert(
      "فرملة الطوارئ!",
      "نظام AEB الأصلي: خطر الاصطدام",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 2.),
    ET.NO_ENTRY: NoEntryAlert("نظام AEB الأصلي: خطر الاصطدام"),
  },

  EventName.fcw: {
    ET.PERMANENT: Alert(
      "فرملة الظوارئ!",
      "خطر الاصطدام",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.warningSoft, 2.),
  },

  EventName.ldw: {
    ET.PERMANENT: Alert(
      "تم اكتشاف انحراف عن المسار",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.ldw, AudibleAlert.prompt, 3.),
  },

  # ********** events only containing alerts that display while engaged **********

  EventName.steerTempUnavailableSilent: {
    ET.WARNING: Alert(
      "التوجيه غير متاح مؤقتًا",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.prompt, 1.8),
  },

  EventName.preDriverDistracted: {
    ET.WARNING: Alert(
      "كن حذرًا",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.promptDriverDistracted: {
    ET.WARNING: Alert(
      "كن حذرًا",
      "السائق مشتت الانتباه",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverDistracted: {
    ET.WARNING: Alert(
      "قم بالغاء التفعيل فورًا",
      "السائق مشتت الانتباه",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.preDriverUnresponsive: {
    ET.WARNING: Alert(
      "المس العجلة: لا تم الكشف عن وجه",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .1, alert_rate=0.75),
  },

  EventName.promptDriverUnresponsive: {
    ET.WARNING: Alert(
      "المس العجلة",
      "السائق غير مستجيب",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverUnresponsive: {
    ET.WARNING: Alert(
      "قم بالغاء التفعيل فورًا",
      "السائق غير متجاوب",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.preKeepHandsOnWheel: {
    ET.WARNING: Alert(
      "لم يتم الكشف عن يد السائق على عجلة القيادة",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.none, .1, alert_rate=0.75),
  },

  EventName.promptKeepHandsOnWheel: {
    ET.WARNING: Alert(
      "يد السائق بعيدة عن عجلة القيادة",
      "ضع يدك على عجلة القيادة",
      AlertStatus.critical, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.keepHandsOnWheel: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("السائق لا يضع يديه على عجلة القيادة"),
  },

  EventName.manualRestart: {
    ET.WARNING: Alert(
      "قم بالتحكم",
      "استأنف القيادة يدويًا",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.resumeRequired: {
    ET.WARNING: Alert(
      "اضغط على استئناف للخروج من وضع الوقوف",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.MID, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.belowSteerSpeed: {
    ET.WARNING: below_steer_speed_alert,
  },

  EventName.preLaneChangeLeft: {
    ET.WARNING: Alert(
      "انعطف يسارًا لبدء تغيير المسار بأمان",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1, alert_rate=0.75),
  },

  EventName.preLaneChangeRight: {
    ET.WARNING: Alert(
      "انعطف يمينًا لبدء تغيير المسار بأمان",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1, alert_rate=0.75),
  },

  EventName.laneChangeBlocked: {
    ET.WARNING: Alert(
      "تم اكتشاف سيارة في المنطقة العمياء",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.prompt, .1),
  },

  EventName.laneChangeRoadEdge: {
    ET.WARNING: Alert(
      "تغيير المسار غير متاح: حافة الطريق",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.prompt, .1),
  },

  EventName.laneChange: {
    ET.WARNING: Alert(
      "جاري تغيير المسار",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.manualSteeringRequired: {
    ET.WARNING: Alert(
      "تم إيقاف التوسط التلقائي في الحارة",
      "التوجيه اليدوي مطلوب",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.disengage, 1.),
  },

  EventName.manualLongitudinalRequired: {
    ET.WARNING: Alert(
      "تم إيقاف التحكم الذكي/التحكم التكيفي بالسرعة",
      "التحكم اليدوي في الوقود/الفرامل مطلوب",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },

  EventName.cruiseEngageBlocked: {
    ET.WARNING: Alert(
      "القائد الآلي غير متوفر",
      "تم الضغط على الدواسة أثناء تفعيل التحكم بالسرعة",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.brakePressed, AudibleAlert.refuse, 3.),
  },

  EventName.steerSaturated: {
    ET.WARNING: Alert(
      "ساعد في التوجيه",
      "المنعطف يتجاوز حد التوجيه",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 2.),
  },

  # Thrown when the fan is driven at >50% but is not rotating
  EventName.fanMalfunction: {
    ET.PERMANENT: NormalPermanentAlert("عطل في المروحة", "ربما هنالك مشكلة في الجهاز"),
  },

  # Camera is not outputting frames
  EventName.cameraMalfunction: {
    ET.PERMANENT: camera_malfunction_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عطل في الكاميرا"),
    ET.NO_ENTRY: NoEntryAlert("عطل في الكاميرا: أعد تشغيل الجهاز الخاص بك"),
  },
  # Camera framerate too low
  EventName.cameraFrameRate: {
    ET.PERMANENT: NormalPermanentAlert("معدل الإطارات للكاميرا منخفض", "أعد تشغيل جهازك"),
    ET.SOFT_DISABLE: soft_disable_alert("معدل الإطارات للكاميرا منخفض"),
    ET.NO_ENTRY: NoEntryAlert("معدل الإطارات للكاميرا منخفض: أعد تشغيل جهازك"),
  },

  # Unused
  EventName.gpsMalfunction: {
    ET.PERMANENT: NormalPermanentAlert("عطل في نظام تحديد المواقع (GPS)", "ربما هناك مشكلة في الأجهزة"),
  },

  EventName.locationdTemporaryError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ مؤقت في خدمة تحديد المواقع"),
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في خدمة تحديد المواقع"),
  },

  EventName.locationdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في خدمة تحديد المواقع"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في خدمة تحديد المواقع"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في خدمة تحديد المواقع"),
  },

  # openpilot tries to learn certain parameters about your car by observing
  # how the car behaves to steering inputs from both human and openpilot driving.
  # This includes:
  # - steer ratio: gear ratio of the steering rack. Steering angle divided by tire angle
  # - tire stiffness: how much grip your tires have
  # - angle offset: most steering angle sensors are offset and measure a non zero angle when driving straight
  # This alert is thrown when any of these values exceed a sanity check. This can be caused by
  # bad alignment or bad sensor data. If this happens consistently consider creating an issue on GitHub
  EventName.paramsdTemporaryError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ مؤقت في خدمة الحساسات"),
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في خدمة الحساسات"),
  },

  EventName.paramsdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في خدمة الحساسات"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في خدمة الحساسات"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في خدمة الحساسات"),
  },

  EventName.speedLimitActive: {
    ET.WARNING: Alert(
      "تم تعيين التحكم بالسرعة إلى الحد الأقصى للسرعة",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 2.),
  },

  EventName.speedLimitValueChange: {
    ET.WARNING: speed_limit_adjust_alert,
  },

  EventName.e2eLongStart: {
    ET.PERMANENT: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.promptStarting, 1.5),
  },

  # ********** events that affect controls state transitions **********

  EventName.pcmEnable: {
    ET.ENABLE: EngagementAlert(AudibleAlert.engage),
  },

  EventName.buttonEnable: {
    ET.ENABLE: EngagementAlert(AudibleAlert.engage),
  },

  EventName.silentButtonEnable: {
    ET.ENABLE: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.none, .2, 0., 0.),
  },

  EventName.pcmDisable: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
  },

  EventName.buttonCancel: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على الإلغاء"),
  },

  EventName.brakeHold: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("الفرامل ممسوكة"),
  },

  EventName.silentBrakeHold: {
    ET.USER_DISABLE: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.none, .2, 0., 0.),
    ET.NO_ENTRY: NoEntryAlert("الفرامل ممسوكة"),
  },

  EventName.parkBrake: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم تشغيل الفرامل اليدوية"),
  },

  EventName.pedalPressed: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على الدواسة",
                              visual_alert=VisualAlert.brakePressed),
  },

  EventName.silentPedalPressed: {
    ET.USER_DISABLE: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.none, .2),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على الدواسة أثناء المحاولة",
                              visual_alert=VisualAlert.brakePressed),
  },

  EventName.preEnableStandstill: {
    ET.PRE_ENABLE: Alert(
      "اترك الفرامل للتفعيل",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1, creation_delay=1.),
  },

  EventName.gasPressedOverride: {
    ET.OVERRIDE_LONGITUDINAL: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.steerOverride: {
    ET.OVERRIDE_LATERAL: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.wrongCarMode: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: wrong_car_mode_alert,
  },

  EventName.resumeBlocked: {
    ET.NO_ENTRY: NoEntryAlert("اضغط على تعيين للتفعيل"),
  },

  EventName.wrongCruiseMode: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم تعطيل التحكم التكيفي بالسرعة"),
  },

  EventName.steerTempUnavailable: {
    ET.SOFT_DISABLE: soft_disable_alert("التوجيه غير متاح مؤقتًا"),
    ET.NO_ENTRY: NoEntryAlert("التوجيه غير متاح مؤقتًا"),
  },

  EventName.steerTimeLimit: {
    ET.SOFT_DISABLE: soft_disable_alert("الحد الزمني لتوجيه السيارة"),
    ET.NO_ENTRY: NoEntryAlert("الحد الزمني لتوجيه السيارة"),
  },

  EventName.outOfSpace: {
    ET.PERMANENT: out_of_space_alert,
    ET.NO_ENTRY: NoEntryAlert("نفاد المساحة التخزينية"),
  },

  EventName.belowEngageSpeed: {
    ET.NO_ENTRY: below_engage_speed_alert,
  },

  EventName.sensorDataInvalid: {
    ET.PERMANENT: Alert(
      "بيانات الاستشعار غير صالحة",
      "تأكد من تثبيت الجهاز بشكل آمن",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, .2, creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("بيانات الاستشعار غير صالحة"),
    ET.SOFT_DISABLE: soft_disable_alert("بيانات الاستشعار غير صالحة"),
  },

  EventName.noGps: {
    ET.PERMANENT: no_gps_alert,
  },

  EventName.soundsUnavailable: {
    ET.PERMANENT: NormalPermanentAlert("لم يتم اكتشاف السماعات", "أعد تشغيل جهازك"),
    ET.NO_ENTRY: NoEntryAlert("السماعات غير موجودة"),
  },

  EventName.tooDistracted: {
    ET.NO_ENTRY: NoEntryAlert("مستوى التشتت مرتفع جدًا"),
  },

  EventName.overheat: {
    ET.PERMANENT: overheat_alert,
    ET.SOFT_DISABLE: soft_disable_alert("النظام ساخن"),
    ET.NO_ENTRY: NoEntryAlert("النظام ساخن"),
  },

  EventName.wrongGear: {
    ET.SOFT_DISABLE: user_soft_disable_alert("الترس ليس على وضع القيادة D"),
    ET.NO_ENTRY: NoEntryAlert("الترس ليس على وضع القيادة D"),
  },

  EventName.silentWrongGear: {
    ET.SOFT_DISABLE: Alert(
      "الترس ليس على وضع القيادة D",
      "القائد الآلي غير متوفر",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 2., 3.),
    ET.NO_ENTRY: Alert(
      "الترس ليس على وضع القيادة D",
      "القائد الآلي غير متوفر",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 2., 3.),
  },

  # This alert is thrown when the calibration angles are outside of the acceptable range.
  # For example if the device is pointed too much to the left or the right.
  # Usually this can only be solved by removing the mount from the windshield completely,
  # and attaching while making sure the device is pointed straight forward and is level.
  # See https://comma.ai/setup for more information
  EventName.calibrationInvalid: {
    ET.PERMANENT: calibration_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عدم صحة التعديل: أعد تركيب الجهاز وأعد معايرته"),
    ET.NO_ENTRY: NoEntryAlert("عدم صحة التعديل: أعد تركيب الجهاز وأعد معايرته"),
  },

  EventName.calibrationIncomplete: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عملية المعايرة غير مكتملة"),
    ET.NO_ENTRY: NoEntryAlert("جاري إجراء عملية المعايرة"),
  },

  EventName.calibrationRecalibrating: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("تم اكتشاف إعادة تركيب الجهاز: إعادة المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("تم اكتشاف إعادة تركيب: إعادة المعايرة"),
  },

  EventName.doorOpen: {
    ET.SOFT_DISABLE: user_soft_disable_alert("الباب مفتوح"),
    ET.NO_ENTRY: NoEntryAlert("الباب مفتوح"),
  },

  EventName.seatbeltNotLatched: {
    ET.SOFT_DISABLE: user_soft_disable_alert("الحزام غير مربوط"),
    ET.NO_ENTRY: NoEntryAlert("الحزام غير مربوط"),
  },

  EventName.espDisabled: {
    ET.SOFT_DISABLE: soft_disable_alert("تم تعطيل نظام التحكم في الثبات الإلكتروني"),
    ET.NO_ENTRY: NoEntryAlert("تم تعطيل نظام التحكم في الثبات الإلكتروني"),
  },

  EventName.lowBattery: {
    ET.SOFT_DISABLE: soft_disable_alert("البطارية منخفضة"),
    ET.NO_ENTRY: NoEntryAlert("البطارية منخفضة"),
  },

  # Different openpilot services communicate between each other at a certain
  # interval. If communication does not follow the regular schedule this alert
  # is thrown. This can mean a service crashed, did not broadcast a message for
  # ten times the regular interval, or the average interval is more than 10% too high.
  EventName.commIssue: {
    ET.SOFT_DISABLE: soft_disable_alert("مشكلة في التواصل بين العمليات"),
    ET.NO_ENTRY: comm_issue_alert,
  },
  EventName.commIssueAvgFreq: {
    ET.SOFT_DISABLE: soft_disable_alert("معدل اتصال منخفض بين العمليات"),
    ET.NO_ENTRY: NoEntryAlert("معدل اتصال منخفض بين العمليات"),
  },

  EventName.controlsdLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخر في التحكم"),
    ET.NO_ENTRY: NoEntryAlert("تأخر في عملية التحكم: أعد تشغيل جهازك"),
  },

  # Thrown when manager detects a service exited unexpectedly while driving
  EventName.processNotRunning: {
    ET.NO_ENTRY: process_not_running_alert,
    ET.SOFT_DISABLE: soft_disable_alert("العملية غير جارية"),
  },

  EventName.radarFault: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ في الرادار: قم بإعادة تشغيل السيارة"),
    ET.NO_ENTRY: NoEntryAlert("خطأ في الرادار: قم بإعادة تشغيل السيارة"),
  },

  # Every frame from the camera should be processed by the model. If modeld
  # is not processing frames fast enough they have to be dropped. This alert is
  # thrown when over 20% of frames are dropped.
  EventName.modeldLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخر في نموذج القيادة"),
    ET.NO_ENTRY: NoEntryAlert("تأخر في نموذج القيادة"),
    ET.PERMANENT: modeld_lagging_alert,
  },

  # Besides predicting the path, lane lines and lead car data the model also
  # predicts the current velocity and rotation speed of the car. If the model is
  # very uncertain about the current velocity while the car is moving, this
  # usually means the model has trouble understanding the scene. This is used
  # as a heuristic to warn the driver.
  EventName.posenetInvalid: {
    ET.SOFT_DISABLE: soft_disable_alert("سرعة الأجسام غير صالحة"),
    ET.NO_ENTRY: posenet_invalid_alert,
  },

  # When the localizer detects an acceleration of more than 40 m/s^2 (~4G) we
  # alert the driver the device might have fallen from the windshield.
  EventName.deviceFalling: {
    ET.SOFT_DISABLE: soft_disable_alert("الجهاز يسقط من القاعدة"),
    ET.NO_ENTRY: NoEntryAlert("الجهاز يسقط من القاعدة"),
  },

  EventName.lowMemory: {
    ET.SOFT_DISABLE: soft_disable_alert("الذاكرة منخفضة: أعد تشغيل جهازك"),
    ET.PERMANENT: low_memory_alert,
    ET.NO_ENTRY: NoEntryAlert("الذاكرة منخفضة: أعد تشغيل جهازك"),
  },

  EventName.highCpuUsage: {
    #ET.SOFT_DISABLE: soft_disable_alert("System Malfunction: Reboot Your Device"),
    #ET.PERMANENT: NormalPermanentAlert("System Malfunction", "Reboot your Device"),
    ET.NO_ENTRY: high_cpu_usage_alert,
  },

  EventName.accFaulted: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في نظام مثبت بالسرعة: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("عطل في نظام مثبت بالسرعة: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل في نظام مثبت بالسرعة: أعد تشغيل السيارة"),
  },

  EventName.controlsMismatch: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عدم تطابق في نظام التحكم"),
    ET.NO_ENTRY: NoEntryAlert("عدم تطابق في نظام التحكم"),
  },

  EventName.controlsMismatchLong: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عدم تطابق في نظام التحكم\nطوليًا"),
    ET.NO_ENTRY: NoEntryAlert("عدم تطابق في نظام التحكم\nطوليًا"),
  },

  EventName.roadCameraError: {
    ET.PERMANENT: NormalPermanentAlert("خطأ في CRC الكاميرا - الطريق",
                                       duration=1.,
                                       creation_delay=30.),
  },

  EventName.wideRoadCameraError: {
    ET.PERMANENT: NormalPermanentAlert("خطأ في CRC الكاميرا - عدسة الطريق الواسعة",
                                       duration=1.,
                                       creation_delay=30.),
  },

  EventName.driverCameraError: {
    ET.PERMANENT: NormalPermanentAlert("خطأ في CRC الكاميرا - السائق",
                                       duration=1.,
                                       creation_delay=30.),
  },

  # Sometimes the USB stack on the device can get into a bad state
  # causing the connection to the panda to be lost
  EventName.usbError: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ في USB: أعد تشغيل جهازك"),
    ET.PERMANENT: NormalPermanentAlert("خطأ في USB: أعد تشغيل جهازك", ""),
    ET.NO_ENTRY: NoEntryAlert("خطأ في USB: أعد تشغيل جهازك"),
  },

  # This alert can be thrown for the following reasons:
  # - No CAN data received at all
  # - CAN data is received, but some message are not received at the right frequency
  # If you're not writing a new car port, this is usually cause by faulty wiring
  EventName.canError: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطاء في الكان"),
    ET.PERMANENT: Alert(
      "خطاء في الكان - تحقق من الاتصالات",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("حدث خطأ في الكان: تحقق من الاتصالات"),
  },

  EventName.canBusMissing: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("تم فصل الكان: ربما هناك مشكلة في الكابل"),
    ET.PERMANENT: Alert(
      "تم فصل الكان: ربما هناك مشكلة في الكابل",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("تم فصل الكان: تحقق من التوصيلات"),
  },

  EventName.steerUnavailable: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في نظام LKAS: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("عطل في نظام LKAS: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل في نظام LKAS: أعد تشغيل السيارة"),
  },

  EventName.reverseGear: {
    ET.PERMANENT: Alert(
      "الرجوع للخلف",
      "",
      AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.USER_DISABLE: ImmediateDisableAlert("الرجوع للخلف"),
    ET.NO_ENTRY: NoEntryAlert("الرجوع للخلف"),
  },

  EventName.spReverseGear: {
    ET.PERMANENT: Alert(
      "الرجوع للخلف",
      "",
      AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.NO_ENTRY: NoEntryAlert("الرجوع للخلف"),
  },

  # On cars that use stock ACC the car can decide to cancel ACC for various reasons.
  # When this happens we can no long control the car so the user needs to be warned immediately.
  EventName.cruiseDisabled: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مثبت السرعة مطفئ"),
  },

  # For planning the trajectory Model Predictive Control (MPC) is used. This is
  # an optimization algorithm that is not guaranteed to find a feasible solution.
  # If no solution is found or the solution has a very high cost this alert is thrown.
  EventName.plannerError: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ في حلاقة التخطيط"),
    ET.NO_ENTRY: NoEntryAlert("خطأ في حلاقة التخطيط"),
  },

  # When the relay in the harness box opens the CAN bus between the LKAS camera
  # and the rest of the car is separated. When messages from the LKAS camera
  # are received on the car side this usually means the relay hasn't opened correctly
  # and this alert is thrown.
  EventName.relayMalfunction: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في ريلاي الظفيرة"),
    ET.PERMANENT: NormalPermanentAlert("عطل في ريلاي الظفيرة", "افحص علبة الريلاي"),
    ET.NO_ENTRY: NoEntryAlert("عطل في ريلاي الظفيرة"),
  },

  EventName.speedTooLow: {
    ET.IMMEDIATE_DISABLE: Alert(
      "تم الغاء القائد اللآلي",
      "السرعة منخفضة جداً",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.disengage, 3.),
  },

  # When the car is driving faster than most cars in the training data, the model outputs can be unpredictable.
  EventName.speedTooHigh: {
    ET.WARNING: Alert(
      "السرعة مرتفعة جداً",
      "المودل لا يعمل على السرعات العالية",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 4.),
    ET.NO_ENTRY: NoEntryAlert("قم بتخفيض السرعة للتفعيل"),
  },

  EventName.lowSpeedLockout: {
    ET.PERMANENT: NormalPermanentAlert("عطل في نظام مقبت بالسرعة: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل في نظام مثبت بالسرعة: أعد تشغيل السيارة"),
  },

  EventName.lkasDisabled: {
    ET.PERMANENT: NormalPermanentAlert("تم تعطيل نظام LKAS: قم بتمكين LKAS للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("تم تعطيل نظام LKAS"),
  },

  EventName.vehicleSensorsInvalid: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مستشعرات السيارة غير صالحة"),
    ET.PERMANENT: NormalPermanentAlert("تتم معايرة حساسات المركبة", "قد لتتم المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("تتم معايرة حساسات المركبة"),
  },

}


if __name__ == '__main__':
  # print all alerts by type and priority
  from cereal.services import service_list
  from collections import defaultdict, OrderedDict

  event_names = {v: k for k, v in EventName.schema.enumerants.items()}
  alerts_by_type: Dict[str, Dict[int, List[str]]] = defaultdict(lambda: defaultdict(list))

  CP = car.CarParams.new_message()
  CS = car.CarState.new_message()
  sm = messaging.SubMaster(list(service_list.keys()))

  for i, alerts in EVENTS.items():
    for et, alert in alerts.items():
      if callable(alert):
        alert = alert(CP, CS, sm, False, 1)
      priority = alert.priority
      alerts_by_type[et][priority].append(event_names[i])

  all_alerts = {}
  for et, priority_alerts in alerts_by_type.items():
    all_alerts[et] = OrderedDict([
      (str(priority), l)
      for priority, l in sorted(priority_alerts.items(), key=lambda x: -int(x[0]))
    ])

  for status, evs in sorted(all_alerts.items(), key=lambda x: x[0]):
    print(f"**** {status} ****")
    for p, alert_list in evs.items():
      print(f"  {p}:")
      print("   ", ', '.join(alert_list), "\n")
