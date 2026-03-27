from __future__ import annotations

import json
import sys
import uuid

from pathlib import Path
from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QFileDialog
)

from .ui.main_window import Ui_MainWindow


ROOT_PATH = Path(__file__).parent


class CtrlTcpTransport(QObject):
    connectedChanged = pyqtSignal(bool)
    responseReceived = pyqtSignal(dict)
    eventReceived = pyqtSignal(dict)
    messageReceived = pyqtSignal(dict)
    protocolError = pyqtSignal(str)
    socketError = pyqtSignal(str)

    def __init__(self, host: str = "127.0.0.1", port: int = 4444, parent: QObject | None = None):
        super().__init__(parent)
        self._host = host
        self._port = port
        self._socket = QTcpSocket(self)
        self._buffer = bytearray()

        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)
        self._socket.readyRead.connect(self._on_ready_read)
        self._socket.errorOccurred.connect(self._on_error)

    def set_endpoint(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    def connect_to_server(self) -> None:
        if self._socket.state() != QAbstractSocket.SocketState.UnconnectedState:
            self._socket.abort()
        self._buffer.clear()
        self._socket.connectToHost(self._host, self._port)

    def disconnect_from_server(self) -> None:
        self._socket.disconnectFromHost()

    def is_connected(self) -> bool:
        return self._socket.state() == QAbstractSocket.SocketState.ConnectedState

    def send_command(self, command: str, params: Optional[str] = None, token: Optional[str] = None) -> str:
        if not self.is_connected():
            raise RuntimeError("ctrl_tcp socket is not connected")

        if token is None:
            token = str(uuid.uuid4())

        payload: dict[str, Any] = {
            "command": command,
            "token": token,
        }
        if params:
            payload["params"] = params

        frame = self._encode_netstring(payload)
        self._socket.write(frame)
        return token

    def _encode_netstring(self, payload: dict[str, Any]) -> bytes:
        blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return f"{len(blob)}:".encode("ascii") + blob + b","

    def _on_connected(self) -> None:
        self.connectedChanged.emit(True)

    def _on_disconnected(self) -> None:
        self.connectedChanged.emit(False)

    def _on_error(self, _error) -> None:
        self.socketError.emit(self._socket.errorString())

    def _on_ready_read(self) -> None:
        self._buffer.extend(bytes(self._socket.readAll()))

        while True:
            payload = self._try_take_netstring()
            if payload is None:
                break

            try:
                obj = json.loads(payload.decode("utf-8"))
            except Exception as exc:
                self.protocolError.emit(f"invalid JSON payload: {exc}")
                continue

            if obj.get("response") is True:
                self.responseReceived.emit(obj)
            elif obj.get("event") is True:
                self.eventReceived.emit(obj)
            elif obj.get("message") is True:
                self.messageReceived.emit(obj)
            else:
                self.protocolError.emit(f"unknown ctrl_tcp message kind: {obj!r}")

    def _try_take_netstring(self) -> Optional[bytes]:
        colon = self._buffer.find(b":")
        if colon < 0:
            return None

        len_bytes = self._buffer[:colon]
        if not len_bytes:
            self.protocolError.emit("empty netstring length")
            self._buffer.clear()
            return None

        if any(ch < 48 or ch > 57 for ch in len_bytes):
            self.protocolError.emit("invalid netstring length")
            self._buffer.clear()
            return None

        size = int(len_bytes.decode("ascii"))
        total_size = colon + 1 + size + 1
        if len(self._buffer) < total_size:
            return None

        if self._buffer[total_size - 1] != ord(","):
            self.protocolError.emit("invalid netstring terminator")
            self._buffer.clear()
            return None

        payload = bytes(self._buffer[colon + 1 : colon + 1 + size])
        del self._buffer[:total_size]
        return payload


class BaresipDemoWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.setWindowTitle("baresip ctrl_tcp demo")
        self.resize(1000, 700)

        self.transport = CtrlTcpTransport()
        self._build_ui()
        self._connect_signals()
        self._update_connection_ui(False)

        self._history_start_time = datetime.now()

    def _build_ui(self) -> None:
        self.hostEdit.setText("127.0.0.1")
        self.portEdit.setText("4444")

        self.commandEdit.setEditable(True)
        self.commandEdit.addItems(
            [
                "uanew",
                "reginfo",
                "uadel",
                "dial",
                "mute",
                "resume",
                "accept",
                "hangup",
                "hangupall",
                "callstat",
                "callfind",
                "listcalls",
            ]
        )

    def _connect_signals(self) -> None:
        self.connectButton.clicked.connect(self._connect_to_server)
        self.disconnectButton.clicked.connect(self.transport.disconnect_from_server)
        self.sendButton.clicked.connect(self._send_command)
        self.clearHistoryButton.clicked.connect(self._clear_history)
        self.saveHistoryButton.clicked.connect(self._save_history)

        self.transport.connectedChanged.connect(self._on_connected_changed)
        self.transport.responseReceived.connect(self._on_response)
        self.transport.eventReceived.connect(self._on_event)
        self.transport.messageReceived.connect(self._on_message)
        self.transport.protocolError.connect(self._on_protocol_error)
        self.transport.socketError.connect(self._on_socket_error)

    def _connect_to_server(self) -> None:
        host = self.hostEdit.text().strip() or "127.0.0.1"
        port_text = self.portEdit.text().strip() or "4444"

        try:
            port = int(port_text)
        except ValueError:
            QMessageBox.critical(self, "Invalid port", f"Port must be an integer, got: {port_text!r}")
            return

        self.transport.set_endpoint(host, port)
        self.transport.connect_to_server()

    def _send_command(self) -> None:
        command = self.commandEdit.currentText().strip()
        params = self.paramsEdit.text()
        token = self.tokenEdit.text().strip() or None

        if not command:
            QMessageBox.warning(self, "Missing command", "Please enter a command.")
            return

        payload: dict[str, Any] = {"command": command}
        if params:
            payload["params"] = params
        if token:
            payload["token"] = token

        try:
            actual_token = self.transport.send_command(command=command, params=params or None, token=token)
        except Exception as exc:
            QMessageBox.critical(self, "Send failed", str(exc))
            return

        payload["token"] = actual_token
        self._append_history("user", payload)

        self.paramsEdit.clear()

    def _on_connected_changed(self, connected: bool) -> None:
        self._update_connection_ui(connected)
        self._append_history("status", {
            "connected": connected,
            "host": self.hostEdit.text().strip(),
            "port": self.portEdit.text().strip(),
        })

    def _on_response(self, obj: dict) -> None:
        self._append_history("response", obj)

    def _on_event(self, obj: dict) -> None:
        self._append_history("event", obj)

    def _on_message(self, obj: dict) -> None:
        self._append_history("message", obj)

    def _on_protocol_error(self, message: str) -> None:
        self._append_history("protocol_error", {"error": message})

    def _on_socket_error(self, message: str) -> None:
        self._append_history("socket_error", {"error": message})

    def _append_history(self, kind: str, payload: Any, ) -> None:
        obj = {
            "kind": kind,
            "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": payload
        }

        text = json.dumps(obj, ensure_ascii=False, indent=2)

        cursor = self.historyText.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        existing = self.historyText.toPlainText()
        if existing:
            cursor.insertText("\n\n")
        cursor.insertText(text)

        self.historyText.setTextCursor(cursor)
        self.historyText.ensureCursorVisible()

    def _update_connection_ui(self, connected: bool) -> None:
        self.connectButton.setEnabled(not connected)
        self.disconnectButton.setEnabled(connected)
        self.sendButton.setEnabled(connected)
        self.hostEdit.setEnabled(not connected)
        self.portEdit.setEnabled(not connected)

    def _clear_history(self) -> None:
        self.historyText.clear()
        self._history_start_time = datetime.now()

    def _save_history(self) -> None:
        ftime = self._history_start_time.strftime("%Y-%m-%d_%H-%M")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save File",
            directory=f"history_{ftime}.txt",
            filter="Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return

        try:
            content = self.historyText.toPlainText()
            with open(file_path, "w", encoding="UTF-8") as fout:
                fout.write(content)
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")


def main() -> int:
    app = QApplication(sys.argv)
    window = BaresipDemoWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
