import json, sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from QPanda3D.Panda3DWorld import Panda3DWorld
from QPanda3D.QPanda3DWidget import QPanda3DWidget
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import LColor, LVecBase3, LineSegs, NodePath
from math import cos, sin, radians

def remapRGB(r, g, b): # на вход значения от 0 до 255, на выходе значения от 0 до 1
    return r / 255, g / 255, b / 255

class WorkspaceSettings: # настройки рабочего протсранства
    def __init__(self, settings):
        self.background = LColor(*remapRGB(settings['background']['r'], settings['background']['g'], settings['background']['b']), 1) # цвет заднего фона
        self.camera_position = LVecBase3(settings['camera']['position']['x'], settings['camera']['position']['y'], settings['camera']['position']['z']) # позиция камеры
        self.camera_angle = LVecBase3(settings['camera']['angle']['yaw'], settings['camera']['angle']['pitch'], settings['camera']['angle']['roll']) # углы наклона камеры
        self.axis = settings['axis'] # нужно ли отображать оси
        self.sensitivity = settings['sensitivity'] # чувствительность при движении камеры
        self.trajectory = settings['trajectory']['need'] # нужно ли отображать траекторию
        self.trajectory_marker = settings['trajectory']['marker'] # имя модели отображения траектории
        self.trajectory_distance = settings['trajectory']['distance']
        self.trajectory_scale = settings['trajectory']['scale']
        self.trajectory_color = LColor(*remapRGB(settings['trajectory']['color']['r'], settings['trajectory']['color']['g'], settings['trajectory']['color']['b']), 1)

class PolygonSettings: # настройки полигона
    def __init__(self, settings):
        self.image_name = settings['image_name'] # путь до изображения полигона
        self.scale = LVecBase3(settings['scale']['x'] * 0.5, settings['scale']['z'], settings['scale']['y'] * 0.5) # размеры полигона

class ObjectsSetings: # настройки объектов
    def __init__(self, settings):
        self.path = settings['path'] # путь до папки с объектами (файлами .egg)
        self.color = LColor(*remapRGB(settings['color']['r'], settings['color']['g'], settings['color']['b']), 1) # цвета объектов
        self.scale = LVecBase3(settings['scale']['x'], settings['scale']['y'], settings['scale']['z']) # размеры объектов

class ServerSettings:
    def __init__(self, settings = None):
        if settings is None:
            self.ip = None
            self.port = None
        else:
            self.ip = settings['ip']
            self.port = settings['port']

class SettingsManager: # менеджер настроек
    def __init__(self):
        self.workspace = None
        self.polygon = None
        self.objects = None
        self.server = None

    def load(self, path): # четние настроек из json файла
        with open(path, 'r') as f:
            settings = json.load(f)
            self.workspace = WorkspaceSettings(settings['workspace'])
            self.polygon = PolygonSettings(settings['polygon'])
            self.objects = ObjectsSetings(settings['objects'])
            self.server = ServerSettings(settings.get('server'))
            return settings

class VisualizationWorld(Panda3DWorld): # Приложение визуализатора
    def __init__(self, settings):
        self.__mouse_pos = None
        self.__mouse1_click = False
        self.__mouse2_click = False
        self.__mouse3_click = False
        Panda3DWorld.__init__(self)

        self.settings = settings
        self.__trajectories_visible = self.settings.workspace.trajectory
        self.models = [] # список объектов
        self.__trajectories = []

        if settings.workspace.axis:
            x_line = LineSegs()
            x_line.setColor(1, 0, 0)
            x_line.moveTo(0, 0, 0)
            x_line.drawTo(settings.polygon.scale.getX() * 2 + 2, 0, 0)
            x_line.setThickness(2)
            NodePath(x_line.create()).reparentTo(self.render)

            y_line = LineSegs()
            y_line.setColor(0, 1, 0)
            y_line.moveTo(0, 0, 0)
            y_line.drawTo(0, settings.polygon.scale.getZ() * 2 + 2, 0)
            y_line.setThickness(2)
            NodePath(y_line.create()).reparentTo(self.render)

            z_line = LineSegs()
            z_line.setColor(0, 0, 1)
            z_line.moveTo(0, 0, 0)
            z_line.drawTo(0, 0, settings.polygon.scale.getY() + 2)
            z_line.setThickness(2)
            NodePath(z_line.create()).reparentTo(self.render)

        self.setBackgroundColor(settings.workspace.background) # устанавливаем фон

        self.imageObject = OnscreenImage(image=settings.polygon.image_name, pos=(settings.polygon.scale.getX(), settings.polygon.scale.getZ(), 0)) # создаем объект полигона
        self.imageObject.setScale(settings.polygon.scale)
        self.imageObject.setP(270)
        self.imageObject.reparentTo(self.render) # добавляем в сцену объект полигона

        self.disableMouse()
        self.accept("mouse-move", self.mouse_move)
        self.accept("mouse1", self.mouse1_button)
        self.accept("mouse1-up", self.mouse1_button)
        self.accept("mouse2", self.mouse2_button)
        self.accept("mouse2-up", self.mouse2_button)
        self.accept("mouse3", self.mouse3_button)
        self.accept("mouse3-up", self.mouse3_button)
        self.reset_camera() # устанавливаем камеру в стартовое положение

    def mouse_move(self, event):
        if self.__mouse_pos is None:
            self.__mouse_pos = event
            
        if self.__mouse_pos['x'] - event['x'] > 3:
            if self.__mouse1_click:
                self.yaw_left_camera()
            elif self.__mouse2_click:
                self.left_camera()
        elif self.__mouse_pos['x'] - event['x'] < -3:
            if self.__mouse1_click:
                self.yaw_right_camera()
            elif self.__mouse2_click:
                self.right_camera()
        if self.__mouse_pos['y'] - event['y'] > 3:
            if self.__mouse1_click:
                self.roll_up_camera()
            elif self.__mouse2_click:
                self.forward_camera()
            elif self.__mouse3_click:
                self.up_camera()
        elif self.__mouse_pos['y'] - event['y'] < -3:
            if self.__mouse1_click:
                self.roll_down_camera()
            elif self.__mouse2_click:
                self.backward_camera()
            elif self.__mouse3_click:
                self.down_camera()
        
        self.__mouse_pos = event

    def mouse1_button(self, event):
        self.__mouse1_click = not self.__mouse1_click

    def mouse2_button(self, event):
        self.__mouse2_click = not self.__mouse2_click

    def mouse3_button(self, event):
        self.__mouse3_click = not self.__mouse3_click

    def yaw_left_camera(self):
        self.camera.setH(self.camera.getH() + 1 * self.settings.workspace.sensitivity)

    def yaw_right_camera(self):
        self.camera.setH(self.camera.getH() - 1 * self.settings.workspace.sensitivity)

    def roll_up_camera(self):
        self.camera.setP(self.camera.getP() + 1 * self.settings.workspace.sensitivity)

    def roll_down_camera(self):
        self.camera.setP(self.camera.getP() - 1 * self.settings.workspace.sensitivity)

    def reset_camera(self):
        self.camera.setPos(self.settings.workspace.camera_position)
        self.camera.setHpr(self.settings.workspace.camera_angle)

    def forward_camera(self):
        self.camera.setY(self.camera.getY() + cos(radians(self.camera.getH())) * self.settings.workspace.sensitivity)
        self.camera.setX(self.camera.getX() - sin(radians(self.camera.getH())) * self.settings.workspace.sensitivity)

    def backward_camera(self):
        self.camera.setY(self.camera.getY() - cos(radians(self.camera.getH())) * self.settings.workspace.sensitivity)
        self.camera.setX(self.camera.getX() + sin(radians(self.camera.getH())) * self.settings.workspace.sensitivity)

    def left_camera(self):
        self.camera.setY(self.camera.getY() - sin(radians(self.camera.getH())) * self.settings.workspace.sensitivity)
        self.camera.setX(self.camera.getX() - cos(radians(self.camera.getH())) * self.settings.workspace.sensitivity)

    def right_camera(self):
        self.camera.setY(self.camera.getY() + sin(radians(self.camera.getH())) * self.settings.workspace.sensitivity)
        self.camera.setX(self.camera.getX() + cos(radians(self.camera.getH())) * self.settings.workspace.sensitivity)

    def up_camera(self):
        self.camera.setZ(self.camera.getZ() + 1)

    def down_camera(self):
        self.camera.setZ(self.camera.getZ() - 1)

    def add_model(self, model_type, position, yaw, trajectory = True, trajectory_color = (0, 0, 0)):
        model = self.loader.loadModel(f"{self.settings.objects.path}/{model_type}.egg") # загружаем модель
        self.models.append(model)

        trajectory_dict = {}
        trajectory_dict["need"] = trajectory
        trajectory_dict["color"] = LColor(*trajectory_color, 1)
        trajectory_dict["objects"] = []

        self.__trajectories.append(trajectory_dict)
        model.setPos(*position)
        model.setH(yaw)
        model.setScale(self.settings.objects.scale)
        model.setP(270)
        model.setColor(self.settings.objects.color)
        model.reparentTo(self.render)

    def remove_model(self, id):
        self.models[id].removeNode()
        self.models.pop(id)

    def change_model_color(self, id, r = 0, g = 0, b = 0):
        if not any((r, g, b)):
            self.models[id].setColor(self.settings.objects.color)
        else:
            self.models[id].setColor(LColor(r, g, b, 1))

    def change_model_scale(self, id, scale = (0, 0, 0)):
        if not any(scale):
            self.models[id].setScale(self.settings.objects.scale)
        else:
            self.models[id].setScale(*scale)

    def __get_between_distance(self, model1, model2):
        x = abs(model1.getX() - model2.getX())
        y = abs(model1.getY() - model2.getY())
        z = abs(model1.getZ() - model2.getZ())
        return x, y, z

    def change_model_position(self, id, position, yaw):
        self.models[id].setPos(*position)
        self.models[id].setH(yaw)
        if self.__trajectories[id]["need"]:
            if len(self.__trajectories[id]["objects"]) == 0:
                self.add_trajectory(id, *position)
            else:
                distance = self.__get_between_distance(self.models[id], self.__trajectories[id]["objects"][-1])
                if distance[0] >= self.settings.workspace.trajectory_distance or distance[1] >= self.settings.workspace.trajectory_distance or distance[2] >= self.settings.workspace.trajectory_distance:
                    self.add_trajectory(id, *position)

    def get_model_position(self, id):
        return self.models[id].getX(), self.models[id].getY(), self.models[id].getZ(), self.models[id].getH()

    def get_model_color(self, id):
        color = self.models[id].getColor()
        return color.getX(), color.getY(), color.getZ()

    def add_trajectory(self, object_id, x, y, z):
        trajectory = self.loader.loadModel(f"{self.settings.objects.path}/{self.settings.workspace.trajectory_marker}.egg")
        self.__trajectories[object_id]["objects"].append(trajectory)
        trajectory.setPos(x, y, z)
        trajectory.setScale(self.settings.workspace.trajectory_scale, self.settings.workspace.trajectory_scale, self.settings.workspace.trajectory_scale)
        trajectory.setColor(*self.__trajectories[object_id]["color"])
        if not self.__trajectories_visible:
            trajectory.hide()
        trajectory.reparentTo(self.render)

    def reset_trajectories(self):
        for index in range(len(self.models)):
            for trajectory in self.__trajectories[index]["objects"]:
                trajectory.removeNode()
            self.__trajectories[index]["objects"] = []

    def get_trajectory_visible(self):
        return self.__trajectories_visible

    def set_trajectory_visible(self, value = True):
        self.__trajectories_visible = value
        if self.__trajectories_visible:
            for index1 in range(len(self.__trajectories)):
                for index2 in range(len(self.__trajectories[index1]["objects"])):
                    self.__trajectories[index1]["objects"][index2].show()
        else:
            for index1 in range(len(self.__trajectories)):
                for index2 in range(len(self.__trajectories[index1]["objects"])):
                    self.__trajectories[index1]["objects"][index2].hide()

    def change_trajectory_color(self, id, r = 0, g = 0, b = 0):
        if not any((r, g, b)):
            color = self.settings.workspace.trajectory_color
        else:
            color = LColor(r, g, b, 1)

        self.__trajectories[id]["color"] = color

        for index in range(len(self.__trajectories[id]["objects"])):
            self.__trajectories[id]["objects"][index].setColor(color)

class VisWidget(QPanda3DWidget):
    def __init__(self, world, main, server):
        self.world = world
        self.server = server
        self.__main = main
        super().__init__(self.world)

    def close(self):
        self.__main.close()
        self.server.close()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Left:
            self.world.yaw_left_camera()
        elif event.key() == Qt.Key_Right:
            self.world.yaw_right_camera()
        elif event.key() == Qt.Key_Up:
            self.world.roll_up_camera()
        elif event.key() == Qt.Key_Down:
            self.world.roll_down_camera()
        elif event.key() == Qt.Key_R:
            self.world.reset_camera()
        elif event.key() == Qt.Key_W:
            self.world.forward_camera()
        elif event.key() == Qt.Key_S:
            self.world.backward_camera()
        elif event.key() == Qt.Key_A:
            self.world.left_camera()
        elif event.key() == Qt.Key_D:
            self.world.right_camera()
        elif event.key() == Qt.Key_Q:
            self.world.up_camera()
        elif event.key() == Qt.Key_E:
            self.world.down_camera()

if __name__ == '__main__':
    from util import ObjectServer
    
    settings = SettingsManager()
    settings.load("./settings/settings.json")
    world = VisualizationWorld(settings)
    server = ObjectServer(world, settings)
    
    app = QApplication(sys.argv)
    appw = QMainWindow()
    appw.setGeometry(50, 50, 800, 600)
    pandaWidget = VisWidget(world, appw, server)
    appw.setCentralWidget(pandaWidget)
    appw.show()

    server.run()
    
    sys.exit(app.exec_())