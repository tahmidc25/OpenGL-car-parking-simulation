from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys

camera_pos = (0, 500, 500)
camera_rotation = 0
fovY = 120
GRID_LENGTH = 500
rand_var = 423
weather_type = 0
rain_particles = []
snow_particles = []

car_x = 0
car_z = 0
car_angle = 0
car_speed = 0
max_speed = 8
acceleration = 0.5
friction = 0.9
turn_speed = 3
reverse_camera_active = False
random_obstacles = []
spawn_timer = 0
spawn_interval = 180
max_random_obstacles = 20

collision_detected = False
reset_timer = 0
camera_mode = 1
game_over = False
cheat_mode = False
cheat_vision = False
current_level = 1
parked_successfully = False
parking_timer = 0
required_parking_time = 180
level_completed = False
assigned_spot = None
show_assignment = False
show_hint = False
wrong_spot_timer = 0
parking_failed_timer = 0

level_names = {1: "EASY", 2: "MEDIUM", 3: "HARD"}
camera_names = ["", "Behind Car", "Top-Down", "Side View"]


level_obstacles = {
    1: [
        [250, 0, 40, 60, 25],
        [-250, 0, 40, 60, 25],
        [0, 250, 60, 40, 25],
        [0, -250, 60, 40, 25],
    ],
    2: [
        [200, 200, 40, 80, 30],
        [-200, 200, 40, 80, 30],
        [200, -200, 40, 80, 30],
        [-200, -200, 40, 80, 30],
        [0, 300, 100, 40, 25],
        [300, 0, 40, 100, 25],
        [-300, 0, 40, 100, 25],
        [0, -300, 100, 40, 25],
    ],
    3: [
        [180, 180, 35, 70, 35],
        [-180, 180, 35, 70, 35],
        [180, -180, 35, 70, 35],
        [-180, -180, 35, 70, 35],
        [0, 320, 120, 35, 30],
        [320, 0, 35, 120, 30],
        [-320, 0, 35, 120, 30],
        [0, -320, 120, 35, 30],
        [100, 100, 25, 25, 25],
        [-100, 100, 25, 25, 25],
        [100, -100, 25, 25, 25],
        [-100, -100, 25, 25, 25],
        [150, 0, 20, 20, 15],
        [-150, 0, 20, 20, 15],
        [0, 150, 20, 20, 15],
        [0, -150, 20, 20, 15],
        [250, 120, 30, 30, 20],
        [-250, 120, 30, 30, 20],
        [250, -120, 30, 30, 20],
        [-250, -120, 30, 30, 20],
    ]
}
def generate_random_obstacle(level):
    if level == 2 and len(random_obstacles) < max_random_obstacles:
        x = random.randint(-400, 400)
        z = random.randint(-400, 400)
        
        parking_spots = get_current_parking_spots()
        spot_width, spot_depth = get_parking_spot_size()
        
        valid_position = False
        attempts = 0
        max_attempts = 20
        
        while not valid_position and attempts < max_attempts:
            valid_position = True
            
            if -150 < x < 150 and -150 < z < 150:
                valid_position = False
            
            for spot_x, spot_z in parking_spots:
                if (abs(x - spot_x) < spot_width + 30 and 
                    abs(z - spot_z) < spot_depth + 30):
                    valid_position = False
                    break
            
            if not valid_position:
                x = random.randint(-400, 400)
                z = random.randint(-400, 400)
                attempts += 1
        
        if valid_position:
            width = random.randint(25, 40)
            depth = random.randint(25, 40)
            height = random.randint(20, 35)
            
            return [x, z, width, depth, height]
    
    return None
                           
level_parking_spots = {
    1: [
        [200, 150], [-200, 150],
        [200, -150], [-200, -150],
    ],
    2: [
        [150, 150], [250, 150], [350, 150],
        [-150, 150], [-250, 150], [-350, 150],
        [150, -150], [250, -150], [350, -150],
        [-150, -150], [-250, -150], [-350, -150],
    ],
    3: [
        [130, 130], [200, 130], [270, 130], [340, 130],
        [-130, 130], [-200, 130], [-270, 130], [-340, 130],
        [130, -130], [200, -130], [270, -130], [340, -130],
        [-130, -130], [-200, -130], [-270, -130], [-340, -130],
        [130, 0], [-130, 0], [0, 130], [0, -130],
    ]
}

def init_game():
    global car_x, car_z, car_angle, car_speed, collision_detected, reset_timer, game_over, camera_rotation, cheat_mode, cheat_vision, parked_successfully, parking_timer, random_obstacles, spawn_timer, reverse_camera_active, level_completed, assigned_spot, show_assignment, show_hint, wrong_spot_timer, parking_failed_timer
    
    car_x = 0
    car_z = 0
    car_angle = 0
    car_speed = 0
    collision_detected = False
    reset_timer = 0
    game_over = False
    camera_rotation = 0
    cheat_mode = False
    cheat_vision = False
    parked_successfully = False
    parking_timer = 0
    level_completed = False
    random_obstacles = []
    spawn_timer = 0
    reverse_camera_active = False
    show_assignment = False
    show_hint = False
    wrong_spot_timer = 0
    parking_failed_timer = 0
    
    init_weather_particles()
    spots = get_current_parking_spots()
    assigned_spot = random.choice(spots) if spots else None
    
    random.seed(rand_var)                                              

def get_current_obstacles():
    base_obstacles = level_obstacles.get(current_level, level_obstacles[1])
    
    if current_level == 2:
        return base_obstacles + random_obstacles
    
    return base_obstacles

def get_current_parking_spots():
    return level_parking_spots.get(current_level, level_parking_spots[1])

def get_parking_spot_size():
    if current_level == 1:
        return 50, 35
    elif current_level == 2:
        return 40, 25
    else:
        return 35, 22               

def init_weather_particles():
    global rain_particles, snow_particles
    
    rain_particles = []
    snow_particles = []
    
    for i in range(100):
        rain_particles.append({
            'x': random.uniform(-GRID_LENGTH, GRID_LENGTH),
            'y': random.uniform(-GRID_LENGTH, GRID_LENGTH),
            'z': random.uniform(50, 300),
            'speed': random.uniform(200, 400)
        })
    
    for i in range(150):
        snow_particles.append({
            'x': random.uniform(-GRID_LENGTH, GRID_LENGTH),
            'y': random.uniform(-GRID_LENGTH, GRID_LENGTH),
            'z': random.uniform(50, 200),
            'speed': random.uniform(50, 100),
            'drift': random.uniform(-20, 20)
        })

def update_weather():
    global rain_particles, snow_particles
    
    if weather_type == 1:
        for particle in rain_particles:
            particle['z'] -= particle['speed'] * 0.016
            if particle['z'] < 0:
                particle['z'] = random.uniform(150, 300)
                particle['x'] = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                particle['y'] = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    elif weather_type == 3:
        for particle in snow_particles:
            particle['z'] -= particle['speed'] * 0.016
            particle['x'] += particle['drift'] * 0.016
            if particle['z'] < 0:
                particle['z'] = random.uniform(150, 200)
                particle['x'] = random.uniform(-GRID_LENGTH, GRID_LENGTH)
                particle['y'] = random.uniform(-GRID_LENGTH, GRID_LENGTH)

def draw_weather_effects():
    if weather_type == 1:
        glColor3f(0.7, 0.7, 1.0)
        glBegin(GL_LINES)
        for particle in rain_particles:
            glVertex3f(particle['x'], particle['y'], particle['z'])
            glVertex3f(particle['x'], particle['y'], particle['z'] - 20)
        glEnd()
    
    elif weather_type == 3:
        glColor3f(1.0, 1.0, 1.0)
        for particle in snow_particles:
            glPushMatrix()
            glTranslatef(particle['x'], particle['y'], particle['z'])
            glutSolidSphere(2, 4, 4)
            glPopMatrix()
    
    elif weather_type == 2:
        return

def draw_reverse_parking_lines():
    if not ((car_speed < -0.5) or camera_mode == 4):
        return

    glDisable(GL_DEPTH_TEST)

    angle_rad = math.radians(car_angle)

    def local_to_world(dx, dy):
        wx = car_x + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        wy = car_z + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        return wx, wy

    rear_offset = 32
    z_height = 2

    bands = [
        (40, 20, (1.0, 0.0, 0.0)),
        (80, 25, (1.0, 1.0, 0.0)),
        (120, 30, (0.0, 1.0, 0.0)),
    ]

    for dist, half_width, color in bands:
        glColor3f(*color)
        glBegin(GL_LINES)
        
        base_dx = -(rear_offset + dist)
        
        left_x, left_y = local_to_world(base_dx, -half_width)
        right_x, right_y = local_to_world(base_dx, half_width)
        glVertex3f(left_x, left_y, z_height)
        glVertex3f(right_x, right_y, z_height)
        glEnd()

    glColor3f(0.0, 0.8, 1.0)
    glBegin(GL_LINES)
    for i in range(5):
        dist = 20 + i * 25
        base_dx = -(rear_offset + dist)
        
        seg_start = local_to_world(base_dx - 8, -15)
        seg_end = local_to_world(base_dx + 8, -15)
        glVertex3f(seg_start[0], seg_start[1], z_height)
        glVertex3f(seg_end[0], seg_end[1], z_height)
        
        seg_start = local_to_world(base_dx - 8, 15)
        seg_end = local_to_world(base_dx + 8, 15)
        glVertex3f(seg_start[0], seg_start[1], z_height)
        glVertex3f(seg_end[0], seg_end[1], z_height)
    glEnd()

    glEnable(GL_DEPTH_TEST)

def draw_text(x, y, text, font=None):
    from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
    if font is None:
        font = GLUT_BITMAP_HELVETICA_18
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_ui_panel():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(0, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 200)
    glVertex2f(0, 200)
    glEnd()
    
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(0, 200)
    glVertex2f(1000, 200)
    glVertex2f(1000, 0)
    glVertex2f(0, 0)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_player():
    glPushMatrix()
    
    glTranslatef(car_x, car_z, 0)
    glRotatef(car_angle, 0, 0, 1)
    
    if cheat_mode:
        glColor3f(0.0, 1.0, 0.8)
    else:
        glColor3f(0.8, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glScalef(60, 25, 15)
    glutSolidCube(1)
    glPopMatrix()
    
    if cheat_mode:
        glColor3f(0.0, 0.9, 0.9)
    else:
        glColor3f(0.9, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glScalef(40, 20, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(32, 0, 10)
    glScalef(4, 30, 8)
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-32, 0, 10)
    glScalef(4, 30, 8)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.1, 0.1, 0.1)
    
    glPushMatrix()
    glTranslatef(20, 18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(20, -18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-20, 18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-20, -18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    glColor3f(1, 1, 0.8)
    glPushMatrix()
    glTranslatef(30, 10, 15)
    glutSolidSphere(3, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(30, -10, 15)
    glutSolidSphere(3, 8, 8)
    glPopMatrix()
    
    if car_speed < -0.5:
        glColor3f(1, 1, 1)
        glPushMatrix()
        glTranslatef(-30, 8, 15)
        glutSolidSphere(2, 8, 8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-30, -8, 15)
        glutSolidSphere(2, 8, 8)
        glPopMatrix()
    
    glPopMatrix()

def draw_obstacles():
    obstacles = get_current_obstacles()
    
    for obstacle in obstacles:
        x, z, width, depth, height = obstacle
        
        glPushMatrix()
        glTranslatef(x, z, height/2)
        
        if current_level == 1:
            glColor3f(0.8, 0.8, 0.2)
        elif current_level == 2:
            if cheat_mode:
                glColor3f(1, 0.5, 1)
            else:
                glColor3f(0.8, 0.4, 0.2)
        else:           
            if cheat_mode:
                glColor3f(1, 0.2, 0.2)
            else:
                glColor3f(0.6, 0.1, 0.1)
            
        glScalef(width, depth, height)
        glutSolidCube(1)
        glPopMatrix()
    
    if cheat_mode:
        glColor3f(1, 1, 1)
        for obstacle in obstacles:
            x, z, width, depth, height = obstacle
            glPushMatrix()
            glTranslatef(x, z, height/2)
            glPushMatrix(); glScalef(width + 10, 2, height + 10); glutSolidCube(1); glPopMatrix()
            glPushMatrix(); glScalef(2, depth + 10, height + 10); glutSolidCube(1); glPopMatrix()
            glPopMatrix()

def draw_parking_spots():
    parking_spots = get_current_parking_spots()
    spot_width, spot_depth = get_parking_spot_size()
    
    if cheat_mode:
        glColor3f(0, 1, 0)
    else:
        if current_level == 1:
            glColor3f(0, 1, 0)
        elif current_level == 2:
            glColor3f(1, 1, 0)
        else:
            glColor3f(1, 0.5, 0)
    
    for spot_x, spot_z in parking_spots:
        is_target = (assigned_spot is not None and (spot_x, spot_z) == tuple(assigned_spot))
        if is_target:
            glColor3f(0.0, 1.0, 0.0)
        else:
            glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_LINE_LOOP)
        glVertex3f(spot_x - spot_width, spot_z - spot_depth, 1)
        glVertex3f(spot_x + spot_width, spot_z - spot_depth, 1)
        glVertex3f(spot_x + spot_width, spot_z + spot_depth, 1)
        glVertex3f(spot_x - spot_width, spot_z + spot_depth, 1)
        glEnd()
        if is_target:
            glBegin(GL_LINE_LOOP)
            inset = 3
            glVertex3f(spot_x - spot_width + inset, spot_z - spot_depth + inset, 1)
            glVertex3f(spot_x + spot_width - inset, spot_z - spot_depth + inset, 1)
            glVertex3f(spot_x + spot_width - inset, spot_z + spot_depth - inset, 1)
            glVertex3f(spot_x - spot_width + inset, spot_z + spot_depth - inset, 1)
            glEnd()
        
        glPushMatrix()
        glTranslatef(spot_x, spot_z, 2)
        if current_level == 1:
            glColor3f(0, 0.8, 0)
        elif current_level == 2:
            glColor3f(0.8, 0.8, 0)
        else:
            glColor3f(0.8, 0.4, 0)
        glutSolidCube(8)
        glPopMatrix()

def draw_grid():
    square_size = 100
    
    glBegin(GL_QUADS)
    
    for i in range(-GRID_LENGTH, GRID_LENGTH, square_size):
        for j in range(-GRID_LENGTH, GRID_LENGTH, square_size):
            
            square_x = (i + GRID_LENGTH) // square_size
            square_z = (j + GRID_LENGTH) // square_size
            
            if (square_x + square_z) % 2 == 0:
                glColor3f(0.3, 0.3, 0.3)
            else:
                glColor3f(0.5, 0.5, 0.5)
            
            glVertex3f(i, j, 0)
            glVertex3f(i + square_size, j, 0)
            glVertex3f(i + square_size, j + square_size, 0)
            glVertex3f(i, j + square_size, 0)
    
    glEnd()
    
    wall_height = 50
    
    glColor3f(0.2, 0.2, 0.8)
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH * 2, 10, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.2, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH * 2, 10, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.8, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(GRID_LENGTH, 0, wall_height/2)
    glScalef(10, GRID_LENGTH * 2, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.8, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH, 0, wall_height/2)
    glScalef(10, GRID_LENGTH * 2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def check_collision(new_x, new_z):
    if cheat_mode:
        return False
    
    car_width = 60
    car_depth = 25
    
    if (abs(new_x) > GRID_LENGTH - car_width/2 or 
        abs(new_z) > GRID_LENGTH - car_depth/2):
        return True
    
    obstacles = get_current_obstacles()
    for obstacle in obstacles:
        obs_x, obs_z, obs_width, obs_depth, obs_height = obstacle
        
        if (abs(new_x - obs_x) < (car_width + obs_width)/2 and
            abs(new_z - obs_z) < (car_depth + obs_depth)/2):
            return True
    
    return False

def check_parking():
    global parked_successfully, parking_timer, current_level, level_completed, game_over, wrong_spot_timer, parking_failed_timer
    
    parking_spots = get_current_parking_spots()
    spot_width, spot_depth = get_parking_spot_size()
    car_width = 60
    car_depth = 25

    if abs(car_speed) < 0.5:
        for spot_x, spot_z in parking_spots:
            if (abs(car_x - spot_x) < spot_width - 10 and
                abs(car_z - spot_z) < spot_depth - 5):
                if assigned_spot is not None and (spot_x, spot_z) == tuple(assigned_spot):
                    parking_timer += 1
                    if parking_timer >= required_parking_time:
                        parked_successfully = True
                        level_completed = True
                        return
                    return
                else:
                    wrong_spot_timer = 60
                    parking_failed_timer = 180
                    parking_timer = 0
                    parked_successfully = False
                    return
    parking_timer = 0
    parked_successfully = False


def update_car_physics():
    global car_x, car_z, car_speed, collision_detected, reset_timer, reverse_camera_active
    if reset_timer > 0:
        reset_timer -= 1
        collision_detected = reset_timer > 0
        return
    
    weather_friction_modifier = 1.0
    if weather_type == 1:
        weather_friction_modifier = 0.85
    elif weather_type == 3:
        weather_friction_modifier = 0.7
    
    if cheat_mode:
        car_speed *= 0.95
    else:
        car_speed *= friction * weather_friction_modifier
    
    reverse_camera_active = car_speed < -1.0
    
    if abs(car_speed) > 0.1:
        angle_rad = math.radians(car_angle)
        new_x = car_x + math.cos(angle_rad) * car_speed
        new_z = car_z + math.sin(angle_rad) * car_speed
        
        if not check_collision(new_x, new_z):
            car_x = new_x
            car_z = new_z
            collision_detected = False
        else:
            car_speed = 0
            collision_detected = True
            reset_timer = 60

def draw_collision_effects():
    if collision_detected:
        glPushMatrix()
        glTranslatef(car_x, car_z, 40)
        
        if (reset_timer // 5) % 2 == 0:
            glColor3f(1, 0, 0)
        else:
            glColor3f(1, 0.5, 0.5)
            
        glutSolidSphere(80, 8, 8)
        glPopMatrix()

def start_parking_assist():
    pass

def cheat_mode_update():
    global car_speed, max_speed, car_angle, car_x, car_z
    
    if cheat_mode:
        if max_speed < 15:
            max_speed = 15
        
        parking_spots = get_current_parking_spots()
        
        closest_distance = float('inf')
        closest_spot = None
        
        for spot_x, spot_z in parking_spots:
            distance = math.sqrt((car_x - spot_x)**2 + (car_z - spot_z)**2)
            if distance < closest_distance:
                closest_distance = distance
                closest_spot = (spot_x, spot_z)
        
        if closest_spot and closest_distance < 100 and abs(car_speed) < 2:
            target_x, target_z = closest_spot
            
            dx = target_x - car_x
            dz = target_z - car_z
            
            if abs(dx) > 5 or abs(dz) > 5:
                target_angle = math.degrees(math.atan2(dz, dx))
                
                angle_diff = target_angle - car_angle
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360
                
                if abs(angle_diff) > 2:
                    car_angle += angle_diff * 0.1
                    if car_angle >= 360:
                        car_angle -= 360
                    elif car_angle < 0:
                        car_angle += 360
    else:
        if max_speed > 8:
            max_speed = 8

def keyboardListener(key, x, y):
    global car_speed, car_angle, camera_mode, collision_detected, cheat_mode, cheat_vision, current_level,level_completed, weather_type, assigned_spot, show_assignment, show_hint, parking_timer, parked_successfully
    
    if key == b'q' or key == b'Q' or key == ord('q') or key == ord('Q') or key == 27:
        try:
            glutLeaveMainLoop()
        except:
            pass
        sys.exit()
    
    if collision_detected and reset_timer > 0:
        return

    if key == b'w':
        if cheat_mode:
            car_speed = min(car_speed + acceleration * 1.5, max_speed)
        else:
            weather_accel_modifier = 1.0
            if weather_type == 1:
                weather_accel_modifier = 0.9
            elif weather_type == 3:
                weather_accel_modifier = 0.8
            car_speed = min(car_speed + acceleration * weather_accel_modifier, max_speed)
    elif key == b's':
        if cheat_mode:
            car_speed = max(car_speed - acceleration * 1.5, -max_speed/2)
        else:
            weather_accel_modifier = 1.0
            if weather_type == 1:
                weather_accel_modifier = 0.9
            elif weather_type == 3:
                weather_accel_modifier = 0.8
            car_speed = max(car_speed - acceleration * weather_accel_modifier, -max_speed/2)
    elif key == b'a':
        turn_modifier = 1.0
        if weather_type == 1: 
            turn_modifier = 1.2
        elif weather_type == 3: 
            turn_modifier = 0.8
            
        if cheat_mode:
            car_angle += turn_speed * 1.5 * turn_modifier
        else:
            car_angle += turn_speed * turn_modifier
        if car_angle >= 360:
            car_angle -= 360

    elif key == b'd':
        turn_modifier = 1.0
        if weather_type == 1: 
            turn_modifier = 1.2
        elif weather_type == 3: 
            turn_modifier = 0.8
            
        if cheat_mode:
            car_angle -= turn_speed * 1.5 * turn_modifier
        else:
            car_angle -= turn_speed * turn_modifier
        if car_angle < 0:
            car_angle += 360
    elif key == b'n' and level_completed: 
        if current_level < max(level_names.keys()):
            current_level += 1
            reset_level()
            level_completed = False
        else:
            print("All levels completed!")
            sys.exit()
    
    elif key == b'r':
        init_game()
    
    elif key == b'1':
        camera_mode = 1
    elif key == b'2':
        camera_mode = 2
    elif key == b'3':
        camera_mode = 4
    
    elif key == b'c':
        cheat_mode = not cheat_mode
    elif key == b'v':
        cheat_vision = not cheat_vision
    
    elif key == b'e':
        next_type = (weather_type + 1) % 4
        weather_type = 3 if next_type == 2 else next_type
    elif key == b'n':
        if current_level < 3:
            current_level += 1
            init_game()
    elif key == b'p':
        if current_level > 1:
            current_level -= 1
            init_game()
    elif key == b'j':
        spots = get_current_parking_spots()
        assigned_spot = random.choice(spots) if spots else None
        parking_timer = 0
        parked_successfully = False
        level_completed = False
    elif key == b'k':
        show_assignment = not show_assignment
    elif key == b'l':
        show_hint = not show_hint


def reset_level():
    global car_x, car_z, car_angle, car_speed, collision_detected
    car_x, car_z = 0, 0
    car_angle = 0
    car_speed = 0
    collision_detected = False


def specialKeyListener(key, x, y):
    global camera_pos
    if camera_mode != 1:
        return
        
    x, y, z = camera_pos
    
    if key == GLUT_KEY_UP:
        z += 20

    if key == GLUT_KEY_DOWN:
        z -= 20

    if key == GLUT_KEY_LEFT:
        distance = math.sqrt(x**2 + y**2)
        if distance > 0:
            current_angle = math.atan2(y, x)
            new_angle = current_angle + math.radians(5)
            
            x = distance * math.cos(new_angle)
            y = distance * math.sin(new_angle)
  
    if key == GLUT_KEY_RIGHT:
        distance = math.sqrt(x**2 + y**2)
        if distance > 0:
            current_angle = math.atan2(y, x)
            new_angle = current_angle - math.radians(5)
            
            x = distance * math.cos(new_angle)
            y = distance * math.sin(new_angle)

    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    global camera_rotation
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        camera_rotation += 5
        if camera_rotation >= 360:
            camera_rotation -= 360
    
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_rotation -= 5
        if camera_rotation < 0:
            camera_rotation += 360

def setupCamera():
    global camera_mode, camera_rotation, cheat_vision
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if cheat_vision and cheat_mode:
        gluPerspective(90, 1.25, 0.1, 1500)
    else:
        gluPerspective(fovY, 1.25, 0.1, 1500)
        
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    effective_camera_mode = camera_mode
    if reverse_camera_active and camera_mode == 1:
        effective_camera_mode = 4
    
    if effective_camera_mode == 1:
        angle_rad = math.radians(car_angle)
        
        if cheat_vision and cheat_mode:
            cam_x = car_x - math.cos(angle_rad) * 200
            cam_z = car_z - math.sin(angle_rad) * 200
            cam_y = 120
        else:
            cam_x = car_x - math.cos(angle_rad) * 150
            cam_z = car_z - math.sin(angle_rad) * 150
            cam_y = 80
        target_x = car_x + math.cos(angle_rad) * 50
        target_z = car_z + math.sin(angle_rad) * 50
        
        gluLookAt(cam_x, cam_z, cam_y,
                  target_x, target_z, 15,
                  0, 0, 1)
        
        glRotatef(camera_rotation, 0, 0, 1)
                  
    elif effective_camera_mode == 2:
        if cheat_vision and cheat_mode:
            gluLookAt(car_x, car_z, 600,
                      car_x, car_z, 0,
                      0, 1, 0)
        else:
            gluLookAt(car_x, car_z, 400,
                      car_x, car_z, 0,
                      0, 1, 0)
    
    elif effective_camera_mode == 4:
        angle_rad = math.radians(car_angle)
        
        cam_x = car_x + math.cos(angle_rad) * 120
        cam_z = car_z + math.sin(angle_rad) * 120
        cam_y = 60
        
        target_x = car_x - math.cos(angle_rad) * 50
        target_z = car_z - math.sin(angle_rad) * 50
        
        gluLookAt(cam_x, cam_z, cam_y,
                  target_x, target_z, 15,
                  0, 0, 1)

def idle():
    global spawn_timer, random_obstacles
    
    if not game_over:
        update_car_physics()
        draw_collision_effects() 
        cheat_mode_update()
        check_parking()
        update_weather()
    
        if current_level == 2:
            spawn_timer += 1
            if spawn_timer >= spawn_interval and len(random_obstacles) < max_random_obstacles:
                new_obstacle = generate_random_obstacle(current_level)
                if new_obstacle:
                    random_obstacles.append(new_obstacle)
                    spawn_timer = 0
        
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    draw_grid()
    draw_parking_spots()
    draw_obstacles()
    if show_hint and assigned_spot is not None:
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(car_x, car_z, 2)
        glVertex3f(assigned_spot[0], assigned_spot[1], 2)
        glEnd()
        glEnable(GL_DEPTH_TEST)
    if not game_over:
        draw_player()
        draw_collision_effects()
    
    draw_weather_effects()
    
    draw_reverse_parking_lines()
    
    draw_ui_panel()

                                                    
    weather_names = ["Clear", "Rain", "Clear", "Snow"]
    camera_names = ["", "Behind Car", "Top-Down", "Reverse Camera"]
    
    draw_text(20, 170, f"Level: {current_level} ({level_names.get(current_level, 'Unknown')})")
    draw_text(20, 150, f"Camera: {camera_names[camera_mode] if camera_mode <= 3 else 'Reverse'} (1-3)")
    if reverse_camera_active:
        draw_text(20, 130, "REVERSE CAMERA ACTIVE")
    else:
        draw_text(20, 130, f"Speed: {abs(car_speed):.1f}")
    draw_text(20, 110, f"Position: ({car_x:.0f}, {car_z:.0f})")
    draw_text(20, 90, f"Angle: {car_angle:.0f}°")
    
    draw_text(300, 170, f"Weather: {weather_names[weather_type]} (E to change)")
    if show_assignment and assigned_spot is not None:
        draw_text(300, 70, f"Assigned Spot: ({assigned_spot[0]}, {assigned_spot[1]}) [J new, K show, L hint]")
    draw_text(300, 150, f"Ground Rotation: {camera_rotation:.0f}°")
    draw_text(300, 130, f"Cheat Mode: {'ON' if cheat_mode else 'OFF'} (C)")
    draw_text(300, 110, f"Cheat Vision: {'ON' if cheat_vision else 'OFF'} (V)")
    draw_text(300, 90, f"Random Obstacles: {len(random_obstacles)}")
    
    if collision_detected:
        draw_text(600, 170, "COLLISION! Press R to reset")
    elif cheat_mode:
        draw_text(600, 170, "CHEAT ACTIVE: No collision!")
    else:
        draw_text(600, 170, "Status: Normal")
    
    draw_text(600, 150, f"Parking Timer: {parking_timer}")
    draw_text(600, 130, f"Level Completed: {'YES' if level_completed else 'NO'}")
    draw_text(600, 110, f"Car in Reverse: {'YES' if car_speed < -0.5 else 'NO'}")
    draw_text(600, 90, f"Parked: {'YES' if parked_successfully else 'NO'}")
    
    if level_completed:
        glColor3f(1, 1, 0)
        draw_text(300, 400, "SUCCESS! Level Completed")
        draw_text(300, 360, "Press N for Next Level")
        draw_text(300, 330, "Press Q to Quit")

    glColor3f(0.8, 0.8, 0.8)
    draw_text(20, 50, "WASD: Move/Turn | 1-3: Cameras (3=Reverse) | E: Weather | R: Reset")
    draw_text(20, 30, "J: New Assignment | K: Show/Hide Assignment | L: Hint Line to Spot")
    draw_text(20, 10, "Camera 1: Behind Car | Camera 2: Top-Down | Camera 3: Reverse + Parking Lines")

    
    global wrong_spot_timer
    if wrong_spot_timer > 0:
        draw_text(600, 70, "Wrong spot! Park in the assigned one (press K)")
        wrong_spot_timer -= 1

    global parking_failed_timer
    if parking_failed_timer > 0 and not level_completed:
        draw_text(300, 440, "Parking FAILED — Wrong spot")
        parking_failed_timer -= 1

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Car Parking Frenzy!")
  
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.1, 0.1, 0.2, 1.0)
    
    init_game()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    
    def windowCloseCallback():
        sys.exit()
    
    try:
        glutCloseFunc(windowCloseCallback)
    except:
        pass
    
    glutMainLoop()

if __name__ == "__main__":
    main()

