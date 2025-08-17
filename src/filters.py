from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QPushButton


class ButtonDisableFilter(QObject):
    """
    This filter prevents the hover effect
    freeze after a QPushButton is set to disable.
    """
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.EnabledChange:
            if isinstance(obj, QPushButton) and not obj.isEnabled():
                obj.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)
                obj.style().unpolish(obj)
                obj.style().polish(obj)
        return super().eventFilter(obj, event)