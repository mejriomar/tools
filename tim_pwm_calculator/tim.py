import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QGroupBox
)

class TimerTool(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("STM32 Timer Calculator")
        self.setGeometry(200, 200, 500, 500)

        layout = QVBoxLayout()

        # =========================
        # SECTION FREQUENCE
        # =========================
        freq_group = QGroupBox("Fréquence PWM")
        freq_layout = QVBoxLayout()

        self.f_timer = QLineEdit("72000000")
        self.psc = QLineEdit("71")
        self.arr = QLineEdit("20000")

        freq_layout.addWidget(QLabel("Fréquence Timer (Hz)"))
        freq_layout.addWidget(self.f_timer)
        freq_layout.addWidget(QLabel("PSC"))
        freq_layout.addWidget(self.psc)
        freq_layout.addWidget(QLabel("ARR"))
        freq_layout.addWidget(self.arr)

        self.freq_result = QLabel("Fréquence = ?")

        btn_calc_freq = QPushButton("Calculer fréquence")
        btn_calc_freq.clicked.connect(self.calculate_frequency)

        freq_layout.addWidget(btn_calc_freq)
        freq_layout.addWidget(self.freq_result)

        freq_group.setLayout(freq_layout)

        # =========================
        # SECTION SERVO
        # =========================
        servo_group = QGroupBox("Servo (angle → pulse)")
        servo_layout = QVBoxLayout()

        self.angle = QLineEdit("90")
        self.servo_result = QLabel("Pulse = ?")

        btn_servo = QPushButton("Calculer Pulse")
        btn_servo.clicked.connect(self.calculate_servo)

        servo_layout.addWidget(QLabel("Angle (0-180)"))
        servo_layout.addWidget(self.angle)
        servo_layout.addWidget(btn_servo)
        servo_layout.addWidget(self.servo_result)

        servo_group.setLayout(servo_layout)

        # =========================
        # SECTION DUTY
        # =========================
        duty_group = QGroupBox("PWM Duty Cycle")
        duty_layout = QVBoxLayout()

        self.ccr = QLineEdit("1500")
        self.arr_duty = QLineEdit("20000")

        self.duty_result = QLabel("Duty = ?")

        btn_duty = QPushButton("Calculer Duty")
        btn_duty.clicked.connect(self.calculate_duty)

        duty_layout.addWidget(QLabel("CCR"))
        duty_layout.addWidget(self.ccr)
        duty_layout.addWidget(QLabel("ARR"))
        duty_layout.addWidget(self.arr_duty)
        duty_layout.addWidget(btn_duty)
        duty_layout.addWidget(self.duty_result)

        duty_group.setLayout(duty_layout)

        # =========================
        # SECTION CALCUL INVERSE
        # =========================
        inv_group = QGroupBox("Calcul inverse (fixer fréquence)")
        inv_layout = QVBoxLayout()

        self.target_freq = QLineEdit("50")
        self.psc_fixed = QLineEdit("")
        self.arr_fixed = QLineEdit("")

        self.inv_result = QLabel("Résultat = ?")

        btn_calc_inv = QPushButton("Calculer")
        btn_calc_inv.clicked.connect(self.calculate_inverse)

        inv_layout.addWidget(QLabel("Fréquence cible (Hz)"))
        inv_layout.addWidget(self.target_freq)

        inv_layout.addWidget(QLabel("PSC (laisser vide si inconnu)"))
        inv_layout.addWidget(self.psc_fixed)

        inv_layout.addWidget(QLabel("ARR (laisser vide si inconnu)"))
        inv_layout.addWidget(self.arr_fixed)

        inv_layout.addWidget(btn_calc_inv)
        inv_layout.addWidget(self.inv_result)

        inv_group.setLayout(inv_layout)

        # =========================
        # AJOUT GLOBAL
        # =========================
        layout.addWidget(freq_group)
        layout.addWidget(inv_group)
        layout.addWidget(servo_group)
        layout.addWidget(duty_group)

        self.setLayout(layout)

    # =========================
    # FONCTIONS
    # =========================

    def calculate_frequency(self):
        try:
            f_timer = float(self.f_timer.text())
            psc = float(self.psc.text())
            arr = float(self.arr.text())

            freq = f_timer / ((psc + 1) * (arr + 1))
            self.freq_result.setText(f"Fréquence = {freq:.2f} Hz")

        except:
            self.freq_result.setText("Erreur")

    def calculate_inverse(self):
        try:
            f_timer = float(self.f_timer.text())
            target_freq = float(self.target_freq.text())

            psc_text = self.psc_fixed.text()
            arr_text = self.arr_fixed.text()

            # PSC donné → calcul ARR
            if psc_text != "" and arr_text == "":
                psc = float(psc_text)
                arr = (f_timer / ((psc + 1) * target_freq)) - 1
                self.inv_result.setText(f"ARR = {arr:.2f}")

            # ARR donné → calcul PSC
            elif arr_text != "" and psc_text == "":
                arr = float(arr_text)
                psc = (f_timer / ((arr + 1) * target_freq)) - 1
                self.inv_result.setText(f"PSC = {psc:.2f}")

            else:
                self.inv_result.setText("Remplir soit PSC soit ARR")

        except:
            self.inv_result.setText("Erreur")

    def calculate_servo(self):
        try:
            angle = float(self.angle.text())

            if angle < 0: angle = 0
            if angle > 180: angle = 180

            pulse = 1000 + (angle / 180.0) * 1000
            self.servo_result.setText(f"Pulse = {pulse:.0f}")

        except:
            self.servo_result.setText("Erreur")

    def calculate_duty(self):
        try:
            ccr = float(self.ccr.text())
            arr = float(self.arr_duty.text())

            duty = (ccr / arr) * 100
            self.duty_result.setText(f"Duty = {duty:.2f} %")

        except:
            self.duty_result.setText("Erreur")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerTool()
    window.show()
    sys.exit(app.exec_())