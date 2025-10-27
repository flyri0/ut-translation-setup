import json
import sys

from PySide6.QtCore import QObject, QEvent, Qt, QResource, QTranslator, \
    QLocale, QLibraryInfo
from PySide6.QtWidgets import QApplication, QPushButton

from src.utils import resource_path
from src.window import AppWindow


class _ButtonDisableFilter(QObject):
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


try:
    with open(resource_path("config.json"), "r", encoding="utf-8") as config_file:
        config_data = json.load(config_file)
except Exception as error:
    print("Configuration file not found.")
    print("Error details:", error)
    sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.installEventFilter(_ButtonDisableFilter(app))
    QResource.registerResource(str(resource_path("assets.rcc")))

    translator = QTranslator()
    locale = QLocale.system().name()

    translation_path = QLibraryInfo.path(
        QLibraryInfo.LibraryPath.TranslationsPath)
    if translator.load(f"qtbase_{locale}", translation_path):
        app.installTranslator(translator)

    window = AppWindow(config=config_data)
    window.show()
    sys.exit(app.exec())
