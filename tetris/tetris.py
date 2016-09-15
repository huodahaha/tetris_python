# -*- coding: utf-8 -*- 

from Tkinter import *
import time
import pdb
import random

#error
TETRIS_RET_OK = 0
TETRIS_ERR_CROSS_BORDER = 100
TETRIS_ERR_COLLISION = 101


# 碰撞表
blueprint = list()
blueprint.append([[0,0,0,0], [0,1,0,0], [0,1,1,1], [0,0,0,0]])
blueprint.append([[0,0,0,0], [0,1,0,0], [1,1,1,0], [0,0,0,0]])
blueprint.append([[0,0,0,0], [0,0,1,0], [0,1,1,1], [0,0,0,0]])
blueprint.append([[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]])
blueprint.append([[0,0,0,0], [0,1,1,0], [0,0,1,1], [0,0,0,0]])
blueprint.append([[0,0,0,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]])
blueprint.append([[0,0,0,0], [0,0,0,0], [1,1,1,1], [0,0,0,0]])

# rotate修饰


# cfg
window_width = 500
window_height = 800

square_pixels = 32

column_bricks = 10
row_bricks = 20

start_point_x = 5
start_point_y = 3

style_names = ["blue", "cyan", "green", "orange", "purple", "red", "yellow"]


# util
def get_brick_path(color_name):
    return "./pic/" + color_name + ".gif"

def my_dice():
    return int((random.random()*10000))%len(style_names)



# 表示frame中的一个点
class XY(object):
    def __init__(self, cell_unit = square_pixels):
        self._x_grid = 0
        self._y_grid = 0
        self._cell_unit = cell_unit

    def on_adjusted_location(self):
        pass 

    @property
    def x_grid(self):
        print "getter"
        return self._x_grid
     
    @x_grid.setter
    def x_grid(self, value):
        pdb.set_trace()
        self._x_grid = value        
        self.on_adjusted_location()

    @property
    def y_grid(self):
        print "getter"
        return self._y_grid
     
    @y_grid.setter
    def y_grid(self, value):
        self._y_grid = value        
        self.on_adjusted_location()

    @property
    def x(self):
        return self._x_grid * self._cell_unit

    @property
    def y(self):
        return self._y_grid * self._cell_unit
        


class Cell(XY):
    def __init__(self, frame, img_type):
        super(Cell, self).__init__()
        img_object = gs_img_loader.load_img_by_key(img_type)
        self._item_widget = Label(frame.raw_frame, image = img_object)
        # frame.suspending_shape = self     
        
    def redraw(self):
        self._item_widget.place(x = self.x,y = self.y, anchor = NW)

    # 当Item的位置改变时被调用
    def on_adjusted_location(self):        
        self.redraw()

# 一个item Group有自己的位置，和自己的长宽
# group的位置用来计算每一个Item的绝对位置
# 计算位置的算法和长宽是否为偶数有关，为了方便，
# 这里的group一定是偶数*偶数
class TetrisShape(Cell):    
    # 只由load_from_blueprint工厂方法调用    
    def __init__(self, frame, size, x_pos, y_pos):        
        if (size%2) != 0:
            raise "size should be 2.."
        self._size = size
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._frame = frame

        # 初始化二维container空间
        self._cell_container = [None]*size
        for i in range(len(self._cell_container)):  
            self._cell_container[i] = [None]*size
        

    @property
    def cell_container(self):
        return self._cell_container

    @staticmethod
    def load_from_blueplant(blueprint, img_type, x_pos, y_pos):
        if (len(blueprint) == 0):
            raise Exception("invalid blueprint")
        size = len(blueprint)            
        item_group = TetrisShape(gs_frame, size, x_pos, y_pos)
        for row in range(len(blueprint)):
            for column in range(len(blueprint[row])):
                element = blueprint[row][column]
                if (element == 1):
                    item_group.cell_container[row][column] = Cell(frame = gs_frame, img_type = img_type)
        if (item_group.can_update()):
            item_group.update()
            frame.suspending_shape = item_group
            return item_group
        else:
            return False
                    
    # 遍历item group，算出每个item的相对位置
    # 改变位置会触发item的重绘回掉
    def update(self):
        ret = self.can_update()
        if ret != TETRIS_RET_OK:
            return ret
                    
        for row in range(len(self._cell_container)):
            for column in range(len(self._cell_container[row])):
                cell = self._cell_container[row][column]
                if (cell != None):                    
                    cell.x_grid = self._x_pos + column
                    cell.y_grid = self._y_pos + row
        return TETRIS_RET_OK

    def can_update(self):
        # 遍历所有cell
        for row in range(len(self._cell_container)):
            for column in range(len(self._cell_container[row])):
                cell = self._cell_container[row][column]
                if (cell != None):                    
                    new_x_grid = self._x_pos + column
                    new_y_grid = self._y_pos + row
                    # 边缘检测
                    if (new_x_grid < 0) or (new_x_grid >= column_bricks):
                        return TETRIS_ERR_CROSS_BORDER
                    if new_y_grid >= row_bricks:
                        return TETRIS_ERR_CROSS_BORDER
                    # 碰撞检测
                    if self._frame.is_collision(new_x_grid, new_y_grid):
                        return TETRIS_ERR_COLLISION
        return TETRIS_RET_OK



    def move(self, dir_x, dir_y):
        self._x_pos += dir_x
        self._y_pos += dir_y
        return self.update()


    def rotate(self):
        for layer in range(int(self._size/2)):
            last = self._size-1-layer            
            for i in range(layer, last):
                offset = i-layer
                top = self.cell_container[layer][i]
                self.cell_container[layer][i] = self.cell_container[last-offset][layer]
                self.cell_container[last-offset][layer] = self.cell_container[last][last-offset]
                self.cell_container[last][last-offset] = self.cell_container[i][last]
                self.cell_container[i][last] = top
        return self.update()




# 对于俄罗斯方块而言，有两种
class MyFrame(object):
    def __init__(self, window):
        width_ = square_pixels * column_bricks + 10
        height_ = square_pixels * row_bricks + 10
        self.__frame = Frame(window, width=width_, height=height_, bd=2, relief=SUNKEN)
        self.__frame.pack(padx=10, pady=10)
                
        # 初始化二维container空间
        self._anchored_cells = [None]*column_bricks
        for i in range(len(self._anchored_cells)):  
            self._anchored_cells[i] = [None]*row_bricks


        # anchored item
        self.anchored_item_list = list()

    @property
    def raw_frame(self):
        return self.__frame

    @property 
    def suspending_shape(self):
        return self.__suspending_shape

    def is_collision(self, row, column):
        return self._anchored_cells[column][row] != None

    @suspending_shape.setter
    def suspending_shape(self, shape):
        if hasattr(self, '__suspending_shape'):
            self.anchor(self.__suspending_shape)
        self.__suspending_shape = shape

    def anchor(self, item_group):
        cell_container = self.__suspending_shape.cell_container
        for row in range(len(cell_container)):
            for column in range(len(cell_container[row])):
                element = cell_container[row][column]
                if (element != None):    
                    self._anchored_cells[element.y_grid][element.x_grid] = element




# Timer 
class Timer(object):
    def __init__(self, window, tick, tick_time):
        self.update_clock()
        self._tick = tick
        self._tick_time = tick_time

    def update_clock(self):
        tick()        
        self.root.after(self._tick_time, self.update_clock)



class ImgLoader(object):
    def __init__(self):
        self._dict = dict()

    def insert_img_with_key(self, file_name, picture_type):    
        img = PhotoImage(file = file_name)
        self._dict[picture_type] = img

    def load_img_by_key(self, picture_type):
        return self._dict[picture_type]


# 组件初始化函数
def init_img_loader():
    img_loader = ImgLoader()
    for element in style_names:
        img_loader.insert_img_with_key(get_brick_path(element), element)
    return img_loader


def init_window():
    window = Tk()    
    # window.geometry('500x1000+0+0')
    return window


# 键盘响应回调函数
def up(event):
    cur_item_group = gs_frame.suspending_shape
    cur_item_group.rotate()

def down(event):
    cur_item_group = gs_frame.suspending_shape    
    cur_item_group.move(0, 1)

def left(event):
    cur_item_group = gs_frame.suspending_shape
    cur_item_group.move(-1, 0)

def right(event):
    cur_item_group = gs_frame.suspending_shape
    cur_item_group.move(1, 0)

def tab(event):
    cur_item_group = gs_frame.suspending_shape
    gs_frame.anchor(cur_item_group)
    dice = my_dice()    
    new_item_group = TetrisShape.load_from_blueplant(
        blueprint[dice], 
        style_names[dice], 
        start_point_x, start_point_y)
    



def init_frame_callback(frame):
    frame.raw_frame.bind_all("<Up>", up)
    frame.raw_frame.bind_all("<Down>", down)
    frame.raw_frame.bind_all("<Right>", right)
    frame.raw_frame.bind_all("<Left>", left)
    frame.raw_frame.bind_all("<Tab>", tab)

def init_frame(window):
    frame = MyFrame(window)
    init_frame_callback(frame)
    return frame

def init_timer(window, tick_cb, tick_time = 1000):
    timer = Timer(window, tick_cb, tick_time)

def ticker():
    print "this is a tick"

# 全局组件
gs_img_loader = None
gs_root_window = None
gs_frame = None
gs_tiemr = None


if __name__ == '__main__':
    
    # 初始化组件    
    gs_root_window = init_window()
    gs_frame = init_frame(gs_root_window)
    # gs_tiemr = init_timer(window, ticker)
    gs_img_loader = init_img_loader()

    
    
    # # add item
    # item = Cell(frame = gs_frame, img_type = 'blue')
    # item.x_grid = 0
    # item.y_grid = 0

    dice = my_dice()
    test_item_group = TetrisShape.load_from_blueplant(blueprint[dice], style_names[dice], 5,5)

    mainloop()
