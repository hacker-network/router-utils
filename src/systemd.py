import dbus

bus = dbus.SystemBus()
systemd = bus.get_object(
  "org.freedesktop.systemd1",
  "/org/freedesktop/systemd1"
)

manager = dbus.Interface(
  systemd,
  "org.freedesktop.systemd1.Manager"
)

def systemctl_restart(unit):
  return manager.RestartUnit(unit, "fail")
