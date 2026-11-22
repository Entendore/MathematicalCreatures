import sys
import math
import random
import cmath
from collections import deque
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QSlider, QLabel, QFrame, 
                               QFileDialog)
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import (QPainter, QColor, QPolygonF, QPen, QBrush, 
                           QPainterPath, QRadialGradient, QTransform)

# ==========================================
# MATHEMATICAL CREATURES BASE & SUBCLASSES
# ==========================================

class CreatureBase:
    def __init__(self):
        self.hue = random.randint(0, 360)
        self.speed = random.uniform(0.5, 2.0)
        self.phase = 0.0
        self.name = "Base Creature"
        self.math_desc = "Base Math"
        self.dna_stats = {}
        self.has_eyes = True
        
        self.cx_offset = 0.0
        self.cy_offset = 0.0
        self.vx = 0.0
        self.vy = 0.0

    def regenerate(self):
        self.hue = random.randint(0, 360)
        self.speed = random.uniform(0.5, 2.0)
        self.update_dna()

    def update(self, dt, mouse_pos, canvas_center):
        self.phase += self.speed * dt
        
        if mouse_pos:
            mx, my = mouse_pos
            cx, cy = canvas_center
            dx = (cx + self.cx_offset) - mx
            dy = (cy + self.cy_offset) - my
            dist_sq = dx*dx + dy*dy
            
            if dist_sq < 15000:
                dist = math.sqrt(dist_sq)
                force = (150 - dist) * 0.05
                self.vx += (dx / dist) * force
                self.vy += (dy / dist) * force
        
        self.vx -= self.cx_offset * 0.05
        self.vy -= self.cy_offset * 0.05
        self.vx *= 0.85
        self.vy *= 0.85
        self.cx_offset += self.vx
        self.cy_offset += self.vy

    def update_dna(self):
        pass

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        pass

    def draw_eyes(self, painter, cx, cy, base_radius, mouse_pos):
        if not self.has_eyes: return
        
        num_eyes = 2
        for i in range(num_eyes):
            angle = (i - 0.5) * 0.4 + math.pi / 2
            eye_r = base_radius * 0.3
            ex = cx + eye_r * math.cos(angle)
            ey = cy + eye_r * math.sin(angle)
            
            painter.setBrush(QColor(255, 255, 255, 230))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(ex, ey), 12, 12)
            
            tx, ty = mouse_pos if mouse_pos else (cx, cy)
            dx, dy = tx - ex, ty - ey
            dist = math.sqrt(dx*dx + dy*dy)
            px_off = (dx / dist) * 4 if dist > 0 else 0
            py_off = (dy / dist) * 4 if dist > 0 else 0
            
            painter.setBrush(QColor(0, 0, 0))
            painter.drawEllipse(QPointF(ex + px_off, ey + py_off), 6, 6)

# 1. Fourier Series Blob
class FourierBlob(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Fourier Wobble Beast"
        self.math_desc = "r = a + A*sin(nθ) + B*cos(mθ)"
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.limbs = random.randint(3, 12)
        self.base_radius = random.uniform(50, 90)
        self.limb_length = random.uniform(20, 80)
        self.harmonic_2 = random.uniform(0.5, 2.0)

    def update_dna(self):
        self.dna_stats = {"Limbs (n)": self.limbs, "Harmonic 2": f"{self.harmonic_2:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        points = []
        steps = 180
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        
        for i in range(steps + 1):
            theta = (i / steps) * 2 * math.pi
            r = (self.base_radius + \
                 self.limb_length * math.sin(self.limbs * theta + self.phase) + \
                 (self.limb_length / 2) * math.cos(self.limbs * self.harmonic_2 * theta + self.phase * 0.7)) * scale
            r = max(10, r)
            points.append(QPointF(cx + r * math.cos(theta), cy + r * math.sin(theta)))
            
        self._paint_body(painter, points)
        self.draw_eyes(painter, cx, cy, self.base_radius * scale, mouse_pos)

    def _paint_body(self, painter, points):
        poly = QPolygonF(points)
        center = poly.boundingRect().center()
        for i in range(3, 0, -1):
            painter.setBrush(QBrush(QColor.fromHsl(self.hue, 200, 150, 20 * i)))
            painter.setPen(Qt.NoPen)
            glow_poly = QPolygonF([QPointF(center.x() + (p.x()-center.x())*(1 + i*0.05), 
                                           center.y() + (p.y()-center.y())*(1 + i*0.05)) for p in points])
            painter.drawPolygon(glow_poly)
        gradient = QRadialGradient(center, poly.boundingRect().width() / 2)
        c1 = QColor.fromHsl(self.hue, 255, 180); c2 = QColor.fromHsl(self.hue, 255, 100)
        c1.setAlpha(230); c2.setAlpha(230)
        gradient.setColorAt(0.0, c1); gradient.setColorAt(1.0, c2)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 220), 2))
        painter.drawPolygon(poly)

# 2. Gielis Superformula
class SuperformulaCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Superformula Starfish"
        self.math_desc = "r = (|cos(mφ/4)/a|^n2 + |sin(mφ/4)/b|^n3)^(-1/n1)"
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.m = random.randint(2, 12)
        self.n1 = random.uniform(0.5, 2.5); self.n2 = random.uniform(0.5, 2.5)
        self.n3 = random.uniform(0.5, 2.5); self.a = random.uniform(0.8, 1.2)
        self.b = random.uniform(0.8, 1.2); self.base_radius = random.uniform(60, 100)

    def update_dna(self):
        self.dna_stats = {"Symmetry (m)": self.m, "Exp n1": f"{self.n1:.2f}", "Exp n2": f"{self.n2:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        points = []
        steps = 360
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        n1_anim = self.n1 + math.sin(self.phase) * 0.2

        for i in range(steps + 1):
            phi = (i / steps) * 2 * math.pi
            term1 = abs(math.cos(self.m * phi / 4) / self.a) ** n1_anim
            term2 = abs(math.sin(self.m * phi / 4) / self.b) ** self.n3
            r = (term1 + term2) ** (-1 / self.n2)
            if math.isinf(r) or math.isnan(r): r = 0
            r *= self.base_radius * scale
            x = cx + r * math.cos(phi + self.phase * 0.2)
            y = cy + r * math.sin(phi + self.phase * 0.2)
            points.append(QPointF(x, y))
            
        self._paint_body(painter, points)
        self.draw_eyes(painter, cx, cy, self.base_radius * scale * 0.5, mouse_pos)

    def _paint_body(self, painter, points):
        poly = QPolygonF(points)
        center = poly.boundingRect().center()
        for i in range(3, 0, -1):
            painter.setBrush(QBrush(QColor.fromHsl(self.hue, 200, 150, 20 * i)))
            painter.setPen(Qt.NoPen)
            glow_poly = QPolygonF([QPointF(center.x() + (p.x()-center.x())*(1 + i*0.05), 
                                           center.y() + (p.y()-center.y())*(1 + i*0.05)) for p in points])
            painter.drawPolygon(glow_poly)
        gradient = QRadialGradient(center, poly.boundingRect().width() / 2)
        c1 = QColor.fromHsl(self.hue, 255, 180); c2 = QColor.fromHsl(self.hue, 255, 100)
        c1.setAlpha(230); c2.setAlpha(230)
        gradient.setColorAt(0.0, c1); gradient.setColorAt(1.0, c2)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 220), 2))
        painter.drawPolygon(poly)

# 3. De Jong Attractor
class DeJongAttractor(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "De Jong Chaos Cloud"
        self.math_desc = "x'=sin(ay)-cos(bx), y'=sin(cx)-cos(dy)"
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.a = random.uniform(-3, 3); self.b = random.uniform(-3, 3)
        self.c = random.uniform(-3, 3); self.d = random.uniform(-3, 3)

    def update_dna(self):
        self.dna_stats = {"Param a": f"{self.a:.2f}", "Param b": f"{self.b:.2f}", "Param c": f"{self.c:.2f}", "Param d": f"{self.d:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 5.0
        cx += self.cx_offset; cy += self.cy_offset
        a = self.a + math.sin(self.phase * 0.3) * 0.5
        b = self.b + math.cos(self.phase * 0.2) * 0.5
        c = self.c + math.cos(self.phase * 0.4) * 0.5
        d = self.d + math.sin(self.phase * 0.1) * 0.5

        path = QPainterPath()
        x, y = 0.0, 0.0
        for i in range(2000):
            x_new = math.sin(a * y) - math.cos(b * x)
            y_new = math.sin(c * x) - math.cos(d * y)
            x, y = x_new, y_new
            if i == 0: path.moveTo(cx + x * scale, cy + y * scale)
            else: path.lineTo(cx + x * scale, cy + y * scale)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 15), 4)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 30), 2)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 200, 180), 1)); painter.drawPath(path)

# 4. Lissajous Web Creature
class LissajousCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Lissajous Weaver"
        self.math_desc = "x = A sin(at+δ), y = B sin(bt)"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.freq_x = random.randint(1, 7); self.freq_y = random.randint(1, 7)
        self.delta = random.uniform(0, math.pi); self.radius = random.uniform(100, 150)

    def update_dna(self):
        self.dna_stats = {"Freq X": self.freq_x, "Freq Y": self.freq_y, "Delta (δ)": f"{self.delta:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250
        r = self.radius * scale
        cx += self.cx_offset; cy += self.cy_offset
        
        for offset in range(6):
            t_offset = self.phase + (offset * 0.1)
            path = QPainterPath()
            steps = 300
            for i in range(steps + 1):
                t = (i / steps) * 2 * math.pi
                x = cx + r * math.sin(self.freq_x * t + t_offset)
                y = cy + r * math.sin(self.freq_y * t)
                if i == 0: path.moveTo(x, y)
                else: path.lineTo(x, y)
            alpha = 120 - (offset * 15)
            painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 180, alpha), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

# 5. Hypotrochoid (Spirograph)
class HypotrochoidCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Spirograph Crawler"
        self.math_desc = "x=(R-r)cos(t)+d*cos((R-r)/r*t)"
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.R = random.uniform(80, 120); self.r = random.uniform(10, 40)
        self.d = random.uniform(20, 60); self.scale_factor = 1.5

    def update_dna(self):
        self.dna_stats = {"Outer R": f"{self.R:.1f}", "Inner r": f"{self.r:.1f}", "Pen Dist (d)": f"{self.d:.1f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250 * self.scale_factor
        cx += self.cx_offset; cy += self.cy_offset
        d_anim = self.d + math.sin(self.phase * 0.5) * 10
        path = QPainterPath()
        steps = 1000; t_max = 2 * math.pi * 20 
        
        for i in range(steps + 1):
            t = (i / steps) * t_max
            x = (self.R - self.r) * math.cos(t) + d_anim * math.cos(((self.R - self.r) / self.r) * t)
            y = (self.R - self.r) * math.sin(t) - d_anim * math.sin(((self.R - self.r) / self.r) * t)
            px = cx + x * scale * 0.8; py = cy + y * scale * 0.8
            if i == 0: path.moveTo(px, py)
            else: path.lineTo(px, py)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 20), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 40), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 200), 1.5)); painter.drawPath(path)

# 6. Rose Curve (Rhodonea)
class RoseCurveCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Rose Kraken"
        self.math_desc = "r = a * cos(kθ)"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.k = random.uniform(2, 8) 
        self.base_radius = random.uniform(80, 120)

    def update_dna(self):
        self.dna_stats = {"Petals (k)": f"{self.k:.2f}", "Radius (a)": f"{self.base_radius:.1f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        points = []
        steps = 720
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        k_anim = self.k + math.sin(self.phase * 0.3) * 1.5

        for i in range(steps + 1):
            theta = (i / steps) * 2 * math.pi * 4 
            r = self.base_radius * scale * math.cos(k_anim * theta)
            x = cx + r * math.cos(theta + self.phase * 0.1)
            y = cy + r * math.sin(theta + self.phase * 0.1)
            points.append(QPointF(x, y))
            
        self._paint_body(painter, points)
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

    def _paint_body(self, painter, points):
        poly = QPolygonF(points)
        center = poly.boundingRect().center()
        for i in range(3, 0, -1):
            painter.setBrush(QBrush(QColor.fromHsl(self.hue, 200, 150, 15 * i)))
            painter.setPen(Qt.NoPen)
            glow_poly = QPolygonF([QPointF(center.x() + (p.x()-center.x())*(1 + i*0.03), 
                                           center.y() + (p.y()-center.y())*(1 + i*0.03)) for p in points])
            painter.drawPolygon(glow_poly)
        gradient = QRadialGradient(center, poly.boundingRect().width() / 2)
        c1 = QColor.fromHsl(self.hue, 255, 180); c2 = QColor.fromHsl(self.hue, 255, 100)
        c1.setAlpha(200); c2.setAlpha(200)
        gradient.setColorAt(0.0, c1); gradient.setColorAt(1.0, c2)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 220), 2))
        painter.drawPolygon(poly)

# 7. Harmonograph
class HarmonographCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Harmonograph Specter"
        self.math_desc = "x = A sin(f1 t + p) e^(-d t) + ..."
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.f1 = random.uniform(1, 4); self.f2 = random.uniform(1, 4)
        self.f3 = random.uniform(1, 4); self.f4 = random.uniform(1, 4)
        self.d1 = random.uniform(0.001, 0.01); self.d2 = random.uniform(0.001, 0.01)
        self.A = random.uniform(80, 120)

    def update_dna(self):
        self.dna_stats = {"Freq 1": f"{self.f1:.2f}", "Freq 2": f"{self.f2:.2f}", "Decay": f"{self.d1:.4f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        t_start = self.phase * 10
        t_end = t_start + 50.0
        steps = 1500
        path = QPainterPath()
        
        for i in range(steps + 1):
            t = t_start + (i / steps) * (t_end - t_start)
            x = self.A * math.sin(self.f1 * t + self.phase) * math.exp(-self.d1 * t) + \
                self.A * math.sin(self.f2 * t + self.phase * 1.2) * math.exp(-self.d2 * t)
            y = self.A * math.sin(self.f3 * t + self.phase * 0.8) * math.exp(-self.d1 * t) + \
                self.A * math.sin(self.f4 * t + self.phase * 1.5) * math.exp(-self.d2 * t)
            px = cx + x * scale; py = cy + y * scale
            if i == 0: path.moveTo(px, py)
            else: path.lineTo(px, py)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 15), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 30), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 180), 1)); painter.drawPath(path)

# 8. Lorenz Attractor
class LorenzAttractorCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Lorenz Butterfly"
        self.math_desc = "dx/dt=σ(y-x), dy/dt=x(ρ-z)-y, dz/dt=xy-βz"
        self.has_eyes = False
        self.regenerate()
        self.x = 0.1; self.y = 0.0; self.z = 0.0
        self.trail = deque(maxlen=1500) 

    def regenerate(self):
        super().regenerate()
        self.sigma = random.uniform(8, 12); self.rho = random.uniform(24, 30)
        self.beta = random.uniform(2, 3.5); self.trail = deque(maxlen=1500)

    def update(self, dt, mouse_pos, canvas_center):
        super().update(dt, mouse_pos, canvas_center)
        ode_dt = 0.005
        for _ in range(5):
            dx = self.sigma * (self.y - self.x)
            dy = self.x * (self.rho - self.z) - self.y
            dz = self.x * self.y - self.beta * self.z
            self.x += dx * ode_dt; self.y += dy * ode_dt; self.z += dz * ode_dt
            self.trail.append((self.x, self.z)) 

    def update_dna(self):
        self.dna_stats = {"Sigma (σ)": f"{self.sigma:.2f}", "Rho (ρ)": f"{self.rho:.2f}", "Beta (β)": f"{self.beta:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 60.0
        cx += self.cx_offset; cy += self.cy_offset
        if len(self.trail) < 2: return
        
        path = QPainterPath()
        start_x, start_y = self.trail[0]
        path.moveTo(cx + start_x * scale, cy + (start_y - 25) * scale) 
        
        for i in range(1, len(self.trail)):
            tx, ty = self.trail[i]
            path.lineTo(cx + tx * scale, cy + (ty - 25) * scale)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 20), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 40), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 220), 1.5)); painter.drawPath(path)

# 9. Butterfly Curve (Fay's Curve)
class ButterflyCurveCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Fay's Butterfly"
        self.math_desc = "x = sin(t) [e^cos(t) - 2cos(4t) - sin^5(t/12)]"
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.scale_factor = random.uniform(40, 60)
        self.wings = 4 

    def update_dna(self):
        self.dna_stats = {"Scale": f"{self.scale_factor:.1f}", "Wings": f"{self.wings:.1f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250 * self.scale_factor
        cx += self.cx_offset; cy += self.cy_offset
        wings_anim = self.wings + math.sin(self.phase * 0.5) * 0.5
        
        path = QPainterPath()
        steps = 2000
        t_max = 12 * math.pi 
        
        for i in range(steps + 1):
            t = (i / steps) * t_max + self.phase * 0.2
            base_calc = math.exp(math.cos(t)) - 2*math.cos(wings_anim*t) - (math.sin(t/12)**5)
            x = math.sin(t) * base_calc
            y = math.cos(t) * base_calc
            
            px = cx + x * scale
            py = cy - y * scale 
            if i == 0: path.moveTo(px, py)
            else: path.lineTo(px, py)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 15), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 30), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 220), 1.5)); painter.drawPath(path)

# 10. Phyllotaxis (Sunflower)
class PhyllotaxisCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Golden Ratio Sunflower"
        self.math_desc = "r = c*sqrt(i), θ = i * 137.5° (Golden Angle)"
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.c = random.uniform(2.0, 4.0) 
        self.n = 1500 
        
    def update_dna(self):
        self.dna_stats = {"Seeds (N)": self.n, "Scale (c)": f"{self.c:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        golden_angle = 137.5 + math.sin(self.phase * 0.2) * 2.0
        golden_rad = math.radians(golden_angle)
        
        painter.setPen(Qt.NoPen)
        for i in range(self.n):
            theta = i * golden_rad
            r = self.c * math.sqrt(i) * scale
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            hue_offset = (i / self.n) * 60 
            color = QColor.fromHsl((self.hue + int(hue_offset)) % 360, 255, 180, 200)
            painter.setBrush(QBrush(color))
            size = 2.0 + (i / self.n) * 3.0
            painter.drawEllipse(QPointF(x, y), size, size)

# 11. Torus Knot
class TorusKnotCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Torus Knot Weaver"
        self.math_desc = "x=(R+r*cos(qt))cos(pt), y=(R+r*cos(qt))sin(pt)"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.p = random.randint(2, 5)
        self.q = random.randint(2, 5)
        self.R = 60 
        self.r = 20 

    def update_dna(self):
        self.dna_stats = {"Loops p": self.p, "Loops q": self.q}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        rot_phase = self.phase * 0.3
        
        for offset in range(4):
            t_offset = self.phase + (offset * 0.2)
            path = QPainterPath()
            steps = 500
            t_max = 2 * math.pi
            
            for i in range(steps + 1):
                t = (i / steps) * t_max
                x3d = (self.R + self.r * math.cos(self.q * t)) * math.cos(self.p * t)
                y3d = (self.R + self.r * math.cos(self.q * t)) * math.sin(self.p * t)
                z3d = self.r * math.sin(self.q * t)
                x_rot = x3d * math.cos(rot_phase) - z3d * math.sin(rot_phase)
                px = cx + x_rot * scale
                py = cy + y3d * scale
                if i == 0: path.moveTo(px, py)
                else: path.lineTo(px, py)
                
            alpha = 120 - (offset * 20)
            painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 180, alpha), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

# 12. Pythagoras Tree (Fractal)
class PythagorasTreeCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Pythagoras Tree"
        self.math_desc = "Recursive branching: L'=L*cos(θ), L''=L*sin(θ)"
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.depth = 9
        self.angle = 25.0
        self.base_len = 100.0

    def update_dna(self):
        self.dna_stats = {"Depth": self.depth, "Base Angle": f"{self.angle:.1f}°"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250
        angle_anim = math.radians(self.angle + math.sin(self.phase * 0.5) * 10)
        len_anim = self.base_len * scale
        
        start_x = cx + self.cx_offset
        start_y = cy + self.cy_offset + 150 * scale
        self._draw_branch(painter, start_x, start_y, len_anim, -math.pi/2, self.depth, angle_anim)
        
    def _draw_branch(self, painter, x, y, length, angle, depth, branch_angle):
        if depth == 0 or length < 1: return
        x2 = x + length * math.cos(angle)
        y2 = y + length * math.sin(angle)
        
        hue = (self.hue + (self.depth - depth) * 15) % 360
        pen_width = max(1, depth * 0.8)
        painter.setPen(QPen(QColor.fromHsl(hue, 255, 180, 200), pen_width))
        painter.drawLine(QPointF(x, y), QPointF(x2, y2))
        
        self._draw_branch(painter, x2, y2, length * 0.8, angle - branch_angle, depth - 1, branch_angle)
        self._draw_branch(painter, x2, y2, length * 0.8, angle + branch_angle, depth - 1, branch_angle)

# 13. Epitrochoid (Outer Spirograph)
class EpitrochoidCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Epitrochoid Star"
        self.math_desc = "x=(R+r)cos(t)-d*cos((R+r)/r*t)"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.R = random.uniform(30, 50)
        self.r = random.uniform(10, 40)
        self.d = random.uniform(20, 60)
        self.scale_factor = 2.0

    def update_dna(self):
        self.dna_stats = {"Outer R": f"{self.R:.1f}", "Roller r": f"{self.r:.1f}", "Pen d": f"{self.d:.1f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250 * self.scale_factor
        cx += self.cx_offset; cy += self.cy_offset
        d_anim = self.d + math.sin(self.phase * 0.5) * 10
        path = QPainterPath()
        steps = 1000
        t_max = 2 * math.pi * 20 
        
        for i in range(steps + 1):
            t = (i / steps) * t_max
            x = (self.R + self.r) * math.cos(t) - d_anim * math.cos(((self.R + self.r) / self.r) * t)
            y = (self.R + self.r) * math.sin(t) - d_anim * math.sin(((self.R + self.r) / self.r) * t)
            px = cx + x * scale; py = cy + y * scale
            if i == 0: path.moveTo(px, py)
            else: path.lineTo(px, py)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 20), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 40), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 200), 1.5)); painter.drawPath(path)
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

# 14. Sierpinski Ghost (Chaos Game)
class SierpinskiCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Sierpinski Ghost"
        self.math_desc = "Chaos Game: P = (P + V_random) / 2"
        self.has_eyes = True
        self.points_norm = [] 
        self.v_rad = 150.0
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.points_norm = []
        x, y = 0.5, 0.5
        vertices = [(0, 0), (1, 0), (0.5, 1)]
        for _ in range(3000):
            vx, vy = random.choice(vertices)
            x = (x + vx) / 2.0
            y = (y + vy) / 2.0
            self.points_norm.append((x, y))

    def update_dna(self):
        self.dna_stats = {"Points": len(self.points_norm), "Vertex Radius": f"{self.v_rad:.1f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 500
        cx += self.cx_offset; cy += self.cy_offset
        
        v1 = (cx + math.cos(self.phase) * self.v_rad * scale, cy + math.sin(self.phase) * self.v_rad * scale)
        v2 = (cx + math.cos(self.phase + 2.094) * self.v_rad * scale, cy + math.sin(self.phase + 2.094) * self.v_rad * scale)
        v3 = (cx + math.cos(self.phase + 4.188) * self.v_rad * scale, cy + math.sin(self.phase + 4.188) * self.v_rad * scale)
        
        m11 = v2[0] - v1[0]
        m12 = v2[1] - v1[1]
        m21 = v3[0] - v1[0] - 0.5 * m11
        m22 = v3[1] - v1[1] - 0.5 * m12
        dx = v1[0]
        dy = v1[1]
        
        transform = QTransform(m11, m12, m21, m22, dx, dy)
        painter.save()
        painter.setTransform(transform, combine=True)
        
        painter.setPen(Qt.NoPen)
        for i, (nx, ny) in enumerate(self.points_norm):
            hue_offset = (i / len(self.points_norm)) * 60
            color = QColor.fromHsl((self.hue + int(hue_offset)) % 360, 255, 180, 180)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(nx, ny), 1.5, 1.5)
            
        painter.restore()
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

# 15. Barnsley Fern (IFS)
class BarnsleyFernCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Barnsley Fern"
        self.math_desc = "Iterated Function System (Affine Transforms)"
        self.has_eyes = False
        self.points_norm = []
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.points_norm = []
        x, y = 0.0, 0.0
        for _ in range(8000):
            r = random.random()
            if r < 0.01:
                x, y = 0.0, 0.16 * y
            elif r < 0.86:
                x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
            elif r < 0.93:
                x, y = 0.20 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
            else:
                x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
            self.points_norm.append((x / 3.0 - 0.5, 1.0 - y / 10.0 - 0.5))

    def update_dna(self):
        self.dna_stats = {"Points": len(self.points_norm), "Wind Shear": f"{math.sin(self.phase*0.5)*0.3:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250 * 200
        cx += self.cx_offset; cy += self.cy_offset
        
        wind = math.sin(self.phase * 0.5) * 0.3
        rot = math.sin(self.phase * 0.2) * 10
        
        transform = QTransform()
        transform.translate(cx, cy)
        transform.rotate(rot)
        transform.shear(wind, 0)
        transform.scale(scale, scale)
        
        painter.save()
        painter.setTransform(transform, combine=True)
        painter.setPen(Qt.NoPen)
        
        for i, (nx, ny) in enumerate(self.points_norm):
            alpha = 180
            color = QColor.fromHsl((self.hue + int(ny * 60)) % 360, 255, 150 + int(ny * 50), alpha)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(nx, ny), 0.005, 0.005)
            
        painter.restore()

# 16. Mobius Strip (3D Parametric Surface)
class MobiusStripCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Möbius Strip"
        self.math_desc = "x=(R+v*cos(u/2))cos(u), y=(R+v*cos(u/2))sin(u)"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.R = 100.0 
        self.W = 30.0  
        self.scale_factor = 1.5

    def update_dna(self):
        self.dna_stats = {"Radius (R)": f"{self.R:.1f}", "Width (W)": f"{self.W:.1f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250 * self.scale_factor
        cx += self.cx_offset; cy += self.cy_offset
        
        u_steps = 60
        v_steps = 5
        
        painter.setPen(Qt.NoPen)
        
        for i in range(u_steps):
            for j in range(v_steps):
                u1 = (i / u_steps) * 2 * math.pi
                u2 = ((i + 1) / u_steps) * 2 * math.pi
                v1 = (j / v_steps - 0.5) * 2 * self.W
                v2 = ((j + 1) / v_steps - 0.5) * 2 * self.W
                
                p1 = self._calc_3d_point(u1, v1, scale)
                p2 = self._calc_3d_point(u2, v1, scale)
                p3 = self._calc_3d_point(u2, v2, scale)
                p4 = self._calc_3d_point(u1, v2, scale)
                
                avg_z = (p1[2] + p2[2] + p3[2] + p4[2]) / 4.0
                alpha = int(150 + (avg_z / scale) * 3)
                alpha = max(20, min(255, alpha))
                
                color = QColor.fromHsl(self.hue, 255, 180, alpha)
                painter.setBrush(QBrush(color))
                
                poly = QPolygonF([QPointF(cx + p1[0], cy + p1[1]), 
                                  QPointF(cx + p2[0], cy + p2[1]), 
                                  QPointF(cx + p3[0], cy + p3[1]), 
                                  QPointF(cx + p4[0], cy + p4[1])])
                painter.drawPolygon(poly)
                
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

    def _calc_3d_point(self, u, v, scale):
        u_anim = u + self.phase * 0.5
        x3d = (self.R + v * math.cos(u_anim / 2)) * math.cos(u_anim)
        y3d = (self.R + v * math.cos(u_anim / 2)) * math.sin(u_anim)
        z3d = v * math.sin(u_anim / 2)
        
        rot = self.phase * 0.5
        x_rot = x3d * math.cos(rot) + z3d * math.sin(rot)
        z_rot = -x3d * math.sin(rot) + z3d * math.cos(rot)
        
        return (x_rot * scale, y3d * scale, z_rot)

# 17. Aizawa Attractor (3D Strange Attractor)
class AizawaAttractorCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Aizawa Attractor"
        self.math_desc = "dx/dt=(z-b)x-dy, dy/dt=dx+(z-b)y, dz/dt=c+az-z³/3-..."
        self.has_eyes = False
        self.regenerate()
        self.x = 0.1; self.y = 0.0; self.z = 0.0
        self.trail = deque(maxlen=2000)

    def regenerate(self):
        super().regenerate()
        self.a = random.uniform(0.8, 1.1); self.b = random.uniform(0.6, 0.9)
        self.c = random.uniform(0.5, 0.7); self.d = random.uniform(3.0, 3.8)
        self.e = random.uniform(0.2, 0.3); self.f = random.uniform(0.05, 0.15)
        self.trail = deque(maxlen=2000)

    def update(self, dt, mouse_pos, canvas_center):
        super().update(dt, mouse_pos, canvas_center)
        ode_dt = 0.01
        for _ in range(5):
            dx = (self.z - self.b) * self.x - self.d * self.y
            dy = self.d * self.x + (self.z - self.b) * self.y
            dz = self.c + self.a * self.z - (self.z**3)/3 - (self.x**2 + self.y**2) * (1 + self.e * self.z) + self.f * self.z * self.x**3
            self.x += dx * ode_dt; self.y += dy * ode_dt; self.z += dz * ode_dt
            self.trail.append((self.x, self.y, self.z))

    def update_dna(self):
        self.dna_stats = {"Param a": f"{self.a:.2f}", "Param b": f"{self.b:.2f}", "Param d": f"{self.d:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 15.0
        cx += self.cx_offset; cy += self.cy_offset
        if len(self.trail) < 2: return
        
        path = QPainterPath()
        start_x, start_y, start_z = self.trail[0]
        px = cx + start_x * scale
        py = cy + (start_y - start_z * 0.5) * scale
        path.moveTo(px, py)
        
        for i in range(1, len(self.trail)):
            tx, ty, tz = self.trail[i]
            px = cx + tx * scale
            py = cy + (ty - tz * 0.5) * scale
            path.lineTo(px, py)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 15), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 30), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 220), 1.5)); painter.drawPath(path)

# 18. Flower of Life (Sacred Geometry)
class FlowerOfLifeCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Flower of Life"
        self.math_desc = "Overlapping circles in hexagonal lattice"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.layers = 3

    def update_dna(self):
        self.dna_stats = {"Layers": self.layers}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250
        cx += self.cx_offset; cy += self.cy_offset
        
        R = 40 * scale
        R_anim = R + math.sin(self.phase * 0.5) * 5
        rot = self.phase * 0.2
        
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 220, 200), 2))
        painter.setBrush(Qt.NoBrush)
        
        painter.drawEllipse(QPointF(cx, cy), R_anim, R_anim)
        
        for i in range(-self.layers, self.layers + 1):
            for j in range(-self.layers, self.layers + 1):
                if i == 0 and j == 0: continue
                x_off = i * R_anim * 1.5
                y_off = j * R_anim * math.sqrt(3) - (i % 2) * (R_anim * math.sqrt(3) / 2)
                
                rot_x = x_off * math.cos(rot) - y_off * math.sin(rot)
                rot_y = x_off * math.sin(rot) + y_off * math.cos(rot)
                
                dist = math.sqrt(rot_x**2 + rot_y**2)
                if dist <= self.layers * R_anim * 1.5:
                    alpha = int(200 - (dist / (R_anim * 2)) * 100)
                    color = QColor.fromHsl((self.hue + int(dist / 10)) % 360, 255, 180, alpha)
                    painter.setPen(QPen(color, 2))
                    painter.drawEllipse(QPointF(cx + rot_x, cy + rot_y), R_anim, R_anim)
                    
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)

# 19. Heart Curve (Cardioid variation)
class HeartCurveCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Pulsating Heart"
        self.math_desc = "x=16sin^3(t), y=13cos(t)-5cos(2t)-2cos(3t)-cos(4t)"
        self.has_eyes = True
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.scale_factor = 5.0

    def update_dna(self):
        self.dna_stats = {"Scale": self.scale_factor}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 250 * self.scale_factor
        cx += self.cx_offset; cy += self.cy_offset
        
        # Heartbeat pulse
        pulse = 1.0 + math.sin(self.phase * 4.0) * 0.1 + math.sin(self.phase * 8.0) * 0.05
        
        points = []
        steps = 180
        for i in range(steps + 1):
            t = (i / steps) * 2 * math.pi
            x = 16 * (math.sin(t) ** 3)
            y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            points.append(QPointF(cx + x * scale * pulse, cy - y * scale * pulse))
            
        self._paint_body(painter, points)
        self.draw_eyes(painter, cx, cy + 20 * scale, 20, mouse_pos)

    def _paint_body(self, painter, points):
        poly = QPolygonF(points)
        center = poly.boundingRect().center()
        for i in range(3, 0, -1):
            painter.setBrush(QBrush(QColor.fromHsl(self.hue, 200, 150, 20 * i)))
            painter.setPen(Qt.NoPen)
            glow_poly = QPolygonF([QPointF(center.x() + (p.x()-center.x())*(1 + i*0.05), 
                                           center.y() + (p.y()-center.y())*(1 + i*0.05)) for p in points])
            painter.drawPolygon(glow_poly)
        gradient = QRadialGradient(center, poly.boundingRect().width() / 2)
        c1 = QColor.fromHsl(self.hue, 255, 180); c2 = QColor.fromHsl(self.hue, 255, 100)
        c1.setAlpha(230); c2.setAlpha(230)
        gradient.setColorAt(0.0, c1); gradient.setColorAt(1.0, c2)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 220), 2))
        painter.drawPolygon(poly)

# 20. Julia Set (Complex Dynamics)
class JuliaSetCreature(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Julia Set"
        self.math_desc = "z_{n+1} = z_n^2 + c"
        self.has_eyes = False
        self.points_grid = []
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        # Generate a grid of complex points to test
        self.points_grid = []
        res = 70
        for i in range(res):
            for j in range(res):
                x = (i / res - 0.5) * 3.0
                y = (j / res - 0.5) * 3.0
                self.points_grid.append(complex(x, y))

    def update_dna(self):
        # Animate C moving in a circle
        c_real = 0.7885 * math.cos(self.phase)
        c_imag = 0.7885 * math.sin(self.phase)
        self.dna_stats = {"c (real)": f"{c_real:.3f}", "c (imag)": f"{c_imag:.3f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 3.0
        cx += self.cx_offset; cy += self.cy_offset
        
        c = complex(0.7885 * math.cos(self.phase), 0.7885 * math.sin(self.phase))
        
        painter.setPen(Qt.NoPen)
        for z_init in self.points_grid:
            z = z_init
            escaped = False
            for _ in range(10): # Max iterations
                if z.real**2 + z.imag**2 > 4.0:
                    escaped = True
                    break
                z = z*z + c
            
            if not escaped:
                # Point is in the set
                px = cx + z_init.real * scale
                py = cy + z_init.imag * scale
                painter.setBrush(QBrush(QColor.fromHsl(self.hue, 255, 180, 200)))
                painter.drawEllipse(QPointF(px, py), 3, 3)

# 21. Clifford Attractor
class CliffordAttractor(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Clifford Lace"
        self.math_desc = "x'=sin(ay)+c*cos(ax), y'=sin(bx)+d*cos(by)"
        self.has_eyes = False
        self.regenerate()

    def regenerate(self):
        super().regenerate()
        self.a = random.uniform(-2, 2); self.b = random.uniform(-2, 2)
        self.c = random.uniform(-2, 2); self.d = random.uniform(-2, 2)

    def update_dna(self):
        self.dna_stats = {"Param a": f"{self.a:.2f}", "Param b": f"{self.b:.2f}", "Param c": f"{self.c:.2f}", "Param d": f"{self.d:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 6.0
        cx += self.cx_offset; cy += self.cy_offset
        
        # Animate parameters slightly
        a = self.a + math.sin(self.phase * 0.2) * 0.5
        b = self.b + math.cos(self.phase * 0.3) * 0.5
        c = self.c + math.cos(self.phase * 0.1) * 0.5
        d = self.d + math.sin(self.phase * 0.4) * 0.5

        path = QPainterPath()
        x, y = 0.1, 0.1
        for i in range(3000):
            x_new = math.sin(a * y) + c * math.cos(a * x)
            y_new = math.sin(b * x) + d * math.cos(b * y)
            x, y = x_new, y_new
            if i == 0: path.moveTo(cx + x * scale, cy + y * scale)
            else: path.lineTo(cx + x * scale, cy + y * scale)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 15), 4)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 30), 2)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 200, 180), 1)); painter.drawPath(path)

# 22. Henon Attractor
class HenonAttractor(CreatureBase):
    def __init__(self):
        super().__init__()
        self.name = "Hénon Attractor"
        self.math_desc = "x'=1-ax^2+y, y'=bx"
        self.has_eyes = True
        self.regenerate()
        self.x = 0.1; self.y = 0.0
        self.trail = deque(maxlen=2000)

    def regenerate(self):
        super().regenerate()
        self.a = 1.4
        self.b = 0.3
        self.trail = deque(maxlen=2000)

    def update(self, dt, mouse_pos, canvas_center):
        super().update(dt, mouse_pos, canvas_center)
        for _ in range(50):
            x_new = 1 - self.a * self.x**2 + self.y
            y_new = self.b * self.x
            self.x, self.y = x_new, y_new
            self.trail.append((self.x, self.y))

    def update_dna(self):
        self.dna_stats = {"Param a": f"{self.a:.2f}", "Param b": f"{self.b:.2f}"}

    def draw(self, painter, cx, cy, width, height, mouse_pos):
        scale = min(width, height) / 6.0
        cx += self.cx_offset; cy += self.cy_offset
        if len(self.trail) < 2: return
        
        path = QPainterPath()
        start_x, start_y = self.trail[0]
        path.moveTo(cx + start_x * scale, cy - start_y * scale)
        
        for i in range(1, len(self.trail)):
            tx, ty = self.trail[i]
            path.lineTo(cx + tx * scale, cy - ty * scale)

        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 15), 5)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 150, 30), 3)); painter.drawPath(path)
        painter.setPen(QPen(QColor.fromHsl(self.hue, 255, 210, 220), 1.5)); painter.drawPath(path)
        self.draw_eyes(painter, cx, cy, 20, mouse_pos)


# ==========================================
# UI AND CANVAS
# ==========================================

class CreatureCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(700, 600)
        self.setMouseTracking(True)
        
        self.species = [
            FourierBlob,
            SuperformulaCreature,
            DeJongAttractor,
            LissajousCreature,
            HypotrochoidCreature,
            RoseCurveCreature,
            HarmonographCreature,
            LorenzAttractorCreature,
            ButterflyCurveCreature,
            PhyllotaxisCreature,
            TorusKnotCreature,
            PythagorasTreeCreature,
            EpitrochoidCreature,
            SierpinskiCreature,
            BarnsleyFernCreature,
            MobiusStripCreature,
            AizawaAttractorCreature,
            FlowerOfLifeCreature,
            HeartCurveCreature,
            JuliaSetCreature,
            CliffordAttractor,
            HenonAttractor
        ]
        self.current_species_idx = 0
        
        self.creature = self.species[self.current_species_idx]()
        self.time = 0.0
        self.mouse_pos = None
        self.is_paused = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~60 FPS

    def update_animation(self):
        if not self.is_paused:
            dt = 0.016
            self.time += dt
            center = (self.width() / 2, self.height() / 2)
            self.creature.update(dt, self.mouse_pos, center)
            self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = (event.position().x(), event.position().y())
        self.update()

    def mouseLeaveEvent(self, event):
        self.mouse_pos = None
        self.update()

    def next_species(self):
        self.current_species_idx = (self.current_species_idx + 1) % len(self.species)
        self.creature = self.species[self.current_species_idx]()

    def evolve(self):
        self.creature.regenerate()

    def set_complexity(self, value):
        c = self.creature
        if isinstance(c, FourierBlob): c.limbs = max(2, int(value / 10))
        elif isinstance(c, SuperformulaCreature): c.m = max(2, int(value / 10))
        elif isinstance(c, DeJongAttractor): c.a = (value / 10.0) - 5.0 
        elif isinstance(c, LissajousCreature): c.freq_x = max(1, int(value / 15))
        elif isinstance(c, HypotrochoidCreature): c.r = max(5, value / 2.0)
        elif isinstance(c, RoseCurveCreature): c.k = max(2, value / 12.0)
        elif isinstance(c, HarmonographCreature): c.f1 = max(1, value / 20.0)
        elif isinstance(c, LorenzAttractorCreature): c.rho = max(15, value / 3.0)
        elif isinstance(c, ButterflyCurveCreature): c.wings = max(2, value / 15.0)
        elif isinstance(c, PhyllotaxisCreature): c.n = int(value * 30)
        elif isinstance(c, TorusKnotCreature): c.q = max(2, int(value / 20))
        elif isinstance(c, PythagorasTreeCreature): c.depth = max(2, int(value / 12.5))
        elif isinstance(c, EpitrochoidCreature): c.r = max(5, value / 2.5)
        elif isinstance(c, SierpinskiCreature): c.v_rad = max(50, value * 2.5)
        elif isinstance(c, BarnsleyFernCreature): pass
        elif isinstance(c, MobiusStripCreature): c.W = max(10, value / 2.0)
        elif isinstance(c, AizawaAttractorCreature): c.a = max(0.5, value / 100.0)
        elif isinstance(c, FlowerOfLifeCreature): c.layers = max(1, int(value / 20))
        elif isinstance(c, HeartCurveCreature): c.scale_factor = max(1.0, value / 10.0)
        elif isinstance(c, JuliaSetCreature): pass # C animates automatically
        elif isinstance(c, CliffordAttractor): c.a = max(-3.0, value / 25.0 - 2.0)
        elif isinstance(c, HenonAttractor): c.a = max(0.1, value / 50.0)
        c.update_dna()

    def set_hue(self, value):
        self.creature.hue = value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_grad = QRadialGradient(self.width()/2, self.height()/2, self.width())
        bg_grad.setColorAt(0.0, QColor(25, 25, 40))
        bg_grad.setColorAt(1.0, QColor(8, 8, 12))
        painter.fillRect(self.rect(), QBrush(bg_grad))

        cx = self.width() / 2
        cy = self.height() / 2
        self.creature.draw(painter, cx, cy, self.width(), self.height(), self.mouse_pos)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathematical Creatures Lab - 22 Species")
        self.setStyleSheet("background-color: #08080c; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        canvas_frame = QFrame()
        canvas_frame.setStyleSheet("background-color: #12121a; border-radius: 10px;")
        canvas_layout = QVBoxLayout(canvas_frame)
        self.canvas = CreatureCanvas()
        canvas_layout.addWidget(self.canvas)
        main_layout.addWidget(canvas_frame, stretch=1)

        controls = QFrame()
        controls.setFixedWidth(320)
        controls.setStyleSheet("background-color: #12121a; border-radius: 10px;")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(controls)

        title = QLabel("🧬 Creature Lab 🧬")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        controls_layout.addWidget(title)

        subtitle = QLabel("Move mouse over creature to interact.\nWatch the eyes follow you!")
        subtitle.setStyleSheet("font-size: 11px; color: #888888;")
        controls_layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #333333; max-height: 1px;")
        controls_layout.addWidget(line)

        self.lbl_name = QLabel(f"Species: {self.canvas.creature.name}")
        self.lbl_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        controls_layout.addWidget(self.lbl_name)

        self.lbl_math = QLabel(f"Math: {self.canvas.creature.math_desc}")
        self.lbl_math.setWordWrap(True)
        self.lbl_math.setStyleSheet("font-size: 12px; color: #aaaaaa; font-style: italic; font-family: 'Consolas', monospace;")
        controls_layout.addWidget(self.lbl_math)

        controls_layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        self.btn_next = QPushButton("🔁 Species")
        self.btn_next.setStyleSheet(self._btn_style("#2196F3"))
        self.btn_next.clicked.connect(self.change_species)
        btn_layout.addWidget(self.btn_next)

        self.btn_evolve = QPushButton("✨ Evolve")
        self.btn_evolve.setStyleSheet(self._btn_style("#4CAF50"))
        self.btn_evolve.clicked.connect(self.evolve_creature)
        btn_layout.addWidget(self.btn_evolve)
        controls_layout.addLayout(btn_layout)

        btn_layout_2 = QHBoxLayout()
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setStyleSheet(self._btn_style("#FF9800"))
        self.btn_pause.clicked.connect(self.toggle_pause)
        btn_layout_2.addWidget(self.btn_pause)

        self.btn_save = QPushButton("📷 Save PNG")
        self.btn_save.setStyleSheet(self._btn_style("#9C27B0"))
        self.btn_save.clicked.connect(self.save_image)
        btn_layout_2.addWidget(self.btn_save)
        controls_layout.addLayout(btn_layout_2)

        controls_layout.addSpacing(15)

        self.slider_complexity = QSlider(Qt.Horizontal)
        self.slider_complexity.setMinimum(1)
        self.slider_complexity.setMaximum(100)
        self.slider_complexity.setValue(50)
        self.slider_complexity.valueChanged.connect(self.update_complexity)
        self.lbl_complexity = QLabel("Complexity / Frequency: 50%")
        controls_layout.addWidget(self.lbl_complexity)
        controls_layout.addWidget(self.slider_complexity)

        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setMinimum(0)
        self.slider_speed.setMaximum(50)
        self.slider_speed.setValue(int(self.canvas.creature.speed * 10))
        self.slider_speed.valueChanged.connect(self.update_speed)
        self.lbl_speed = QLabel(f"Animation Speed: {self.canvas.creature.speed:.1f}x")
        controls_layout.addWidget(self.lbl_speed)
        controls_layout.addWidget(self.slider_speed)

        self.slider_hue = QSlider(Qt.Horizontal)
        self.slider_hue.setMinimum(0)
        self.slider_hue.setMaximum(359)
        self.slider_hue.setValue(self.canvas.creature.hue)
        self.slider_hue.valueChanged.connect(self.update_hue)
        self.lbl_hue = QLabel(f"Color Hue: {self.canvas.creature.hue}°")
        controls_layout.addWidget(self.lbl_hue)
        controls_layout.addWidget(self.slider_hue)

        controls_layout.addStretch()

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("background-color: #333333; max-height: 1px;")
        controls_layout.addWidget(line2)
        
        lbl_dna_title = QLabel("🧬 Live DNA Sequence")
        lbl_dna_title.setStyleSheet("font-weight: bold; color: #ffffff;")
        controls_layout.addWidget(lbl_dna_title)
        
        self.lbl_dna = QLabel("")
        self.lbl_dna.setStyleSheet("font-size: 12px; color: #00ffff; font-family: 'Consolas', monospace;")
        controls_layout.addWidget(self.lbl_dna)

        self.update_ui()

    def _btn_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color}; border: none; color: white;
                padding: 10px; border-radius: 5px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {color}CC; }}
            QPushButton:pressed {{ background-color: {color}99; }}
        """

    def change_species(self):
        self.canvas.next_species()
        self.update_ui()

    def evolve_creature(self):
        self.canvas.evolve()
        self.update_ui()

    def toggle_pause(self):
        self.canvas.is_paused = not self.canvas.is_paused
        self.btn_pause.setText("▶ Play" if self.canvas.is_paused else "⏸ Pause")

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Creature as Image", "creature.png", "PNG Files (*.png)")
        if file_path:
            pixmap = self.canvas.grab()
            pixmap.save(file_path, "PNG")

    def update_complexity(self, value):
        self.canvas.set_complexity(value)
        self.lbl_complexity.setText(f"Complexity / Frequency: {value}%")
        self.update_dna()

    def update_speed(self, value):
        self.canvas.creature.speed = value / 10.0
        self.lbl_speed.setText(f"Animation Speed: {self.canvas.creature.speed:.1f}x")

    def update_hue(self, value):
        self.canvas.set_hue(value)
        self.lbl_hue.setText(f"Color Hue: {value}°")

    def update_dna(self):
        self.canvas.creature.update_dna()
        dna_text = "\n".join([f"{k}: {v}" for k, v in self.canvas.creature.dna_stats.items()])
        self.lbl_dna.setText(dna_text)

    def update_ui(self):
        c = self.canvas.creature
        self.lbl_name.setText(f"Species: {c.name}")
        self.lbl_math.setText(f"Math: {c.math_desc}")
        self.slider_speed.setValue(int(c.speed * 10))
        self.slider_hue.setValue(c.hue)
        self.update_dna()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())