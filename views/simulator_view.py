import matplotlib.pyplot as plt
import folium
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QSlider
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import tempfile
import os

class SimulatorView(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("UE Simulator")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.controller.start)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.clicked.connect(self.controller.stop)
        layout.addWidget(self.stop_button)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.controller.set_speed)
        layout.addWidget(QLabel("Speed Control"))
        layout.addWidget(self.speed_slider)
        
        self.canvas = FigureCanvas(plt.figure())
        layout.addWidget(self.canvas)
        
        self.map_view = QWebEngineView()
        layout.addWidget(self.map_view)
        
        central_widget.setLayout(layout)
        
        self.update_map()
    
    def update_map(self):
        ax = self.canvas.figure.add_subplot(111)
        ax.clear()
        
        for gnb in self.model.gnbs:
            ax.scatter(gnb.latitude, gnb.longitude, c='red', marker='^', label='gNB' if gnb == self.model.gnbs[0] else "")
        
        for ue in self.model.ues:
            ax.scatter(ue.latitude, ue.longitude, c='blue', label='UE' if ue == self.model.ues[0] else "")
        
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.legend()
        self.canvas.draw()
        
        self.update_online_map()
    
    def update_online_map(self):
        m = folium.Map(location=[self.model.ues[0].latitude, self.model.ues[0].longitude], zoom_start=12)
        
        for gnb in self.model.gnbs:
            folium.Marker([gnb.latitude, gnb.longitude], popup=f"gNB {gnb.gn_id}", icon=folium.Icon(color='red')).add_to(m)
        
        for ue in self.model.ues:
            folium.Marker([ue.latitude, ue.longitude], popup=f"UE {ue.ue_id}", icon=folium.Icon(color='blue')).add_to(m)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        m.save(temp_file.name)
        # self.map_view.setUrl(f"file://{temp_file.name}")