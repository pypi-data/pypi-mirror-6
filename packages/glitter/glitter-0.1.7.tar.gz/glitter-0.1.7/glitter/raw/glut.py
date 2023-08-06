from ctypes import *

_libraries = {}
_libraries['libglut.so.3'] = CDLL('libglut.so.3')
STRING = c_char_p


GLUT_CURSOR_BOTTOM_RIGHT_CORNER = 18 # Variable c_int '18'
GLUT_WINDOW_BUFFER_SIZE = 104 # Variable c_int '104'
GLUT_FULLY_COVERED = 3 # Variable c_int '3'
GLUT_GAME_MODE_HEIGHT = 3 # Variable c_int '3'
GLUT_SCREEN_HEIGHT = 201 # Variable c_int '201'
GLUT_NUM_MOUSE_BUTTONS = 605 # Variable c_int '605'
GLUT_LEFT = 0 # Variable c_int '0'
GLUT_INIT_STATE = 124 # Variable c_int '124'
GLUT_NORMAL_DAMAGED = 804 # Variable c_int '804'
GLUT_KEY_LEFT = 100 # Variable c_int '100'
GLUT_WINDOW_ALPHA_SIZE = 110 # Variable c_int '110'
GLUT_INIT_DISPLAY_MODE = 504 # Variable c_int '504'
GLUT_CURSOR_TOP_SIDE = 12 # Variable c_int '12'
GLUT_WINDOW_HEIGHT = 103 # Variable c_int '103'
GLUT_BLUE = 2 # Variable c_int '2'
GLUT_VERSION = 508 # Variable c_int '508'
GLUT_INIT_MINOR_VERSION = 513 # Variable c_int '513'
GLUT_LEFT_BUTTON = 0 # Variable c_int '0'
GLUT_WINDOW_DEPTH_SIZE = 106 # Variable c_int '106'
GLUT_FULLY_RETAINED = 1 # Variable c_int '1'
GLUT_VIDEO_RESIZE_WIDTH_DELTA = 904 # Variable c_int '904'
GLUT_CURSOR_WAIT = 7 # Variable c_int '7'
GLUT_CURSOR_HELP = 4 # Variable c_int '4'
GLUT_CURSOR_UP_DOWN = 10 # Variable c_int '10'
GLUT_CURSOR_DESTROY = 3 # Variable c_int '3'
GLUT_JOYSTICK_BUTTONS = 614 # Variable c_int '614'
GLUT_GAME_MODE_PIXEL_DEPTH = 4 # Variable c_int '4'
GLUT_VIDEO_RESIZE_X = 906 # Variable c_int '906'
GLUT_CURSOR_RIGHT_ARROW = 0 # Variable c_int '0'
GLUT_WINDOW_FORMAT_ID = 123 # Variable c_int '123'
GLUT_SCREEN_HEIGHT_MM = 203 # Variable c_int '203'
GLUT_DOUBLE = 2 # Variable c_int '2'
GLUT_WINDOW_STEREO = 121 # Variable c_int '121'
GLUT_WINDOW_BLUE_SIZE = 109 # Variable c_int '109'
GLUT_KEY_REPEAT_ON = 1 # Variable c_int '1'
GLUT_CURSOR_LEFT_SIDE = 14 # Variable c_int '14'
GLUT_INIT_WINDOW_HEIGHT = 503 # Variable c_int '503'
GLUT_WINDOW_RED_SIZE = 107 # Variable c_int '107'
GLUT_FORCE_INDIRECT_CONTEXT = 0 # Variable c_int '0'
GLUT_VISIBLE = 1 # Variable c_int '1'
GLUT_CURSOR_CROSSHAIR = 9 # Variable c_int '9'
GLUT_CURSOR_INHERIT = 100 # Variable c_int '100'
GLUT_WINDOW_RGBA = 116 # Variable c_int '116'
GLUT_KEY_RIGHT = 102 # Variable c_int '102'
GLUT_XLIB_IMPLEMENTATION = 13 # Variable c_int '13'
GLUT_API_VERSION = 4 # Variable c_int '4'
GLUT_LAYER_IN_USE = 801 # Variable c_int '801'
GLUT_INDEX = 1 # Variable c_int '1'
GLUT_JOYSTICK_BUTTON_B = 2 # Variable c_int '2'
GLUT_ALPHA = 8 # Variable c_int '8'
GLUT_WINDOW_NUM_SAMPLES = 120 # Variable c_int '120'
GLUT_MULTISAMPLE = 128 # Variable c_int '128'
GLUT_AUX2 = 8192 # Variable c_int '8192'
GLUT_AUX3 = 16384 # Variable c_int '16384'
GLUT_AUX1 = 4096 # Variable c_int '4096'
GLUT_CURSOR_FULL_CROSSHAIR = 102 # Variable c_int '102'
GLUT_NOT_VISIBLE = 0 # Variable c_int '0'
GLUT_ENTERED = 1 # Variable c_int '1'
GLUT_SRGB = 4096 # Variable c_int '4096'
GLUT_CURSOR_TOP_RIGHT_CORNER = 17 # Variable c_int '17'
GLUT_TRY_DIRECT_CONTEXT = 2 # Variable c_int '2'
GLUT_HAS_DIAL_AND_BUTTON_BOX = 603 # Variable c_int '603'
GLUT_ACTION_EXIT = 0 # Variable c_int '0'
GLUT_KEY_HOME = 106 # Variable c_int '106'
GLUT_VIDEO_RESIZE_POSSIBLE = 900 # Variable c_int '900'
GLUT_CURSOR_RIGHT_SIDE = 15 # Variable c_int '15'
GLUT_KEY_F4 = 4 # Variable c_int '4'
GLUT_KEY_F5 = 5 # Variable c_int '5'
GLUT_KEY_F6 = 6 # Variable c_int '6'
GLUT_KEY_F7 = 7 # Variable c_int '7'
GLUT_KEY_F2 = 2 # Variable c_int '2'
GLUT_FORCE_DIRECT_CONTEXT = 3 # Variable c_int '3'
GLUT_JOYSTICK_BUTTON_D = 8 # Variable c_int '8'
GLUT_JOYSTICK_BUTTON_A = 1 # Variable c_int '1'
GLUT_JOYSTICK_BUTTON_C = 4 # Variable c_int '4'
GLUT_OVERLAY_POSSIBLE = 800 # Variable c_int '800'
GLUT_VIDEO_RESIZE_HEIGHT = 909 # Variable c_int '909'
GLUT_STEREO = 256 # Variable c_int '256'
GLUT_FULL_SCREEN = 511 # Variable c_int '511'
GLUT_RIGHT_BUTTON = 2 # Variable c_int '2'
GLUT_ACTION_GLUTMAINLOOP_RETURNS = 1 # Variable c_int '1'
GLUT_RGB = 0 # Variable c_int '0'
GLUT_KEY_NUM_LOCK = 109 # Variable c_int '109'
GLUT_WINDOW_COLORMAP_SIZE = 119 # Variable c_int '119'
GLUT_WINDOW_DOUBLEBUFFER = 115 # Variable c_int '115'
GLUT_HAS_KEYBOARD = 600 # Variable c_int '600'
GLUT_KEY_REPEAT_DEFAULT = 2 # Variable c_int '2'
GLUT_INIT_WINDOW_WIDTH = 502 # Variable c_int '502'
GLUT_KEY_PAGE_DOWN = 105 # Variable c_int '105'
GLUT_NUM_TABLET_BUTTONS = 609 # Variable c_int '609'
GLUT_TRANSPARENT_INDEX = 803 # Variable c_int '803'
GLUT_PARTIALLY_RETAINED = 2 # Variable c_int '2'
GLUT_RED = 0 # Variable c_int '0'
GLUT_CURSOR_LEFT_RIGHT = 11 # Variable c_int '11'
GLUT_HAS_TABLET = 604 # Variable c_int '604'
GLUT_INIT_MAJOR_VERSION = 512 # Variable c_int '512'
GLUT_HIDDEN = 0 # Variable c_int '0'
GLUT_USE_CURRENT_CONTEXT = 1 # Variable c_int '1'
GLUT_CURSOR_INFO = 2 # Variable c_int '2'
GLUT_VIDEO_RESIZE_IN_USE = 901 # Variable c_int '901'
GLUT_CURSOR_LEFT_ARROW = 1 # Variable c_int '1'
GLUT_DEVICE_KEY_REPEAT = 611 # Variable c_int '611'
GLUT_KEY_UP = 101 # Variable c_int '101'
GLUT_KEY_INSERT = 108 # Variable c_int '108'
GLUT_GAME_MODE_POSSIBLE = 1 # Variable c_int '1'
GLUT_WINDOW_WIDTH = 102 # Variable c_int '102'
GLUT_KEY_PAGE_UP = 104 # Variable c_int '104'
GLUT_WINDOW_ACCUM_BLUE_SIZE = 113 # Variable c_int '113'
GLUT_CREATE_NEW_CONTEXT = 0 # Variable c_int '0'
GLUT_ACTIVE_CTRL = 2 # Variable c_int '2'
GLUT_WINDOW_ACCUM_ALPHA_SIZE = 114 # Variable c_int '114'
GLUT_WINDOW_GREEN_SIZE = 108 # Variable c_int '108'
GLUT_VIDEO_RESIZE_Y = 907 # Variable c_int '907'
GLUT_MIDDLE_BUTTON = 1 # Variable c_int '1'
GLUT_DOWN = 0 # Variable c_int '0'
GLUT_VIDEO_RESIZE_WIDTH = 908 # Variable c_int '908'
GLUT_INIT_WINDOW_Y = 501 # Variable c_int '501'
GLUT_INIT_FLAGS = 514 # Variable c_int '514'
GLUT_KEY_F8 = 8 # Variable c_int '8'
GLUT_KEY_F9 = 9 # Variable c_int '9'
GLUT_KEY_F1 = 1 # Variable c_int '1'
GLUT_KEY_F3 = 3 # Variable c_int '3'
GLUT_VIDEO_RESIZE_HEIGHT_DELTA = 905 # Variable c_int '905'
GLUT_GAME_MODE_REFRESH_RATE = 5 # Variable c_int '5'
GLUT_DEBUG = 1 # Variable c_int '1'
GLUT_HAS_MOUSE = 601 # Variable c_int '601'
GLUT_SCREEN_WIDTH_MM = 202 # Variable c_int '202'
GLUT_WINDOW_ACCUM_RED_SIZE = 111 # Variable c_int '111'
GLUT_ACTION_ON_WINDOW_CLOSE = 505 # Variable c_int '505'
GLUT_WINDOW_ACCUM_GREEN_SIZE = 112 # Variable c_int '112'
GLUT_DEPTH = 16 # Variable c_int '16'
GLUT_SINGLE = 0 # Variable c_int '0'
GLUT_UP = 1 # Variable c_int '1'
GLUT_VIDEO_RESIZE_Y_DELTA = 903 # Variable c_int '903'
GLUT_MENU_NOT_IN_USE = 0 # Variable c_int '0'
GLUT_CURSOR_SPRAY = 6 # Variable c_int '6'
GLUT_ALLOW_DIRECT_CONTEXT = 1 # Variable c_int '1'
GLUT_CORE_PROFILE = 1 # Variable c_int '1'
GLUT_ACTIVE_SHIFT = 1 # Variable c_int '1'
GLUT_GREEN = 1 # Variable c_int '1'
GLUT_CURSOR_CYCLE = 5 # Variable c_int '5'
GLUT_AUX4 = 32768 # Variable c_int '32768'
GLUT_SCREEN_WIDTH = 200 # Variable c_int '200'
GLUT_OWNS_JOYSTICK = 613 # Variable c_int '613'
GLUT_NUM_BUTTON_BOX_BUTTONS = 607 # Variable c_int '607'
GLUT_JOYSTICK_POLL_RATE = 616 # Variable c_int '616'
GLUT_DISPLAY_MODE_POSSIBLE = 400 # Variable c_int '400'
GLUT_VIDEO_RESIZE_X_DELTA = 902 # Variable c_int '902'
GLUT_AUX = 4096 # Variable c_int '4096'
GLUT_WINDOW_CURSOR = 122 # Variable c_int '122'
GLUT_RENDERING_CONTEXT = 509 # Variable c_int '509'
GLUT_STENCIL = 32 # Variable c_int '32'
GLUT_WINDOW_NUM_CHILDREN = 118 # Variable c_int '118'
GLUT_WINDOW_STENCIL_SIZE = 105 # Variable c_int '105'
GLUT_GAME_MODE_WIDTH = 2 # Variable c_int '2'
GLUT_WINDOW_PARENT = 117 # Variable c_int '117'
GLUT_NORMAL = 0 # Variable c_int '0'
GLUT_WINDOW_HEADER_HEIGHT = 507 # Variable c_int '507'
GLUT_RGBA = 0 # Variable c_int '0'
GLUT_NUM_DIALS = 608 # Variable c_int '608'
GLUT_NUM_SPACEBALL_BUTTONS = 606 # Variable c_int '606'
GLUT_LUMINANCE = 512 # Variable c_int '512'
GLUT_COMPATIBILITY_PROFILE = 2 # Variable c_int '2'
GLUT_HAS_SPACEBALL = 602 # Variable c_int '602'
GLUT_KEY_END = 107 # Variable c_int '107'
GLUT_ACCUM = 4 # Variable c_int '4'
GLUT_MENU_NUM_ITEMS = 300 # Variable c_int '300'
GLUT_OVERLAY = 1 # Variable c_int '1'
GLUT_KEY_DOWN = 103 # Variable c_int '103'
GLUT_INIT_PROFILE = 515 # Variable c_int '515'
GLUT_KEY_DELETE = 111 # Variable c_int '111'
GLUT_KEY_F12 = 12 # Variable c_int '12'
GLUT_KEY_F10 = 10 # Variable c_int '10'
GLUT_KEY_F11 = 11 # Variable c_int '11'
GLUT_FORWARD_COMPATIBLE = 2 # Variable c_int '2'
GLUT_CURSOR_TOP_LEFT_CORNER = 16 # Variable c_int '16'
GLUT_ACTIVE_ALT = 4 # Variable c_int '4'
GLUT_CURSOR_NONE = 101 # Variable c_int '101'
GLUT_HAS_OVERLAY = 802 # Variable c_int '802'
GLUT_ELAPSED_TIME = 700 # Variable c_int '700'
GLUT_KEY_REPEAT_OFF = 0 # Variable c_int '0'
GLUT_CURSOR_BOTTOM_SIDE = 13 # Variable c_int '13'
GLUT_BORDERLESS = 2048 # Variable c_int '2048'
GLUT_OVERLAY_DAMAGED = 805 # Variable c_int '805'
GLUT_INIT_WINDOW_X = 500 # Variable c_int '500'
GLUT_GAME_MODE_DISPLAY_CHANGED = 6 # Variable c_int '6'
GLUT_MENU_IN_USE = 1 # Variable c_int '1'
GLUT_CURSOR_TEXT = 8 # Variable c_int '8'
GLUT_GAME_MODE_ACTIVE = 0 # Variable c_int '0'
GLUT_DIRECT_RENDERING = 510 # Variable c_int '510'
GLUT_JOYSTICK_AXES = 615 # Variable c_int '615'
GLUT_WINDOW_Y = 101 # Variable c_int '101'
GLUT_WINDOW_X = 100 # Variable c_int '100'
GLUT_KEY_BEGIN = 110 # Variable c_int '110'
GLUT_ACTION_CONTINUE_EXECUTION = 2 # Variable c_int '2'
GLUT_DEVICE_IGNORE_KEY_REPEAT = 610 # Variable c_int '610'
GLUT_WINDOW_BORDER_WIDTH = 506 # Variable c_int '506'
GLUT_CAPTIONLESS = 1024 # Variable c_int '1024'
GLUT_HAS_JOYSTICK = 612 # Variable c_int '612'
GLUT_CURSOR_BOTTOM_LEFT_CORNER = 19 # Variable c_int '19'
glutMainLoopEvent = _libraries['libglut.so.3'].glutMainLoopEvent
glutMainLoopEvent.restype = None
glutMainLoopEvent.argtypes = []
glutLeaveMainLoop = _libraries['libglut.so.3'].glutLeaveMainLoop
glutLeaveMainLoop.restype = None
glutLeaveMainLoop.argtypes = []
glutExit = _libraries['libglut.so.3'].glutExit
glutExit.restype = None
glutExit.argtypes = []
glutFullScreenToggle = _libraries['libglut.so.3'].glutFullScreenToggle
glutFullScreenToggle.restype = None
glutFullScreenToggle.argtypes = []
glutMouseWheelFunc = _libraries['libglut.so.3'].glutMouseWheelFunc
glutMouseWheelFunc.restype = None
glutMouseWheelFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int, c_int)]
glutCloseFunc = _libraries['libglut.so.3'].glutCloseFunc
glutCloseFunc.restype = None
glutCloseFunc.argtypes = [CFUNCTYPE(None)]
glutWMCloseFunc = _libraries['libglut.so.3'].glutWMCloseFunc
glutWMCloseFunc.restype = None
glutWMCloseFunc.argtypes = [CFUNCTYPE(None)]
glutMenuDestroyFunc = _libraries['libglut.so.3'].glutMenuDestroyFunc
glutMenuDestroyFunc.restype = None
glutMenuDestroyFunc.argtypes = [CFUNCTYPE(None)]
GLenum = c_uint
glutSetOption = _libraries['libglut.so.3'].glutSetOption
glutSetOption.restype = None
glutSetOption.argtypes = [GLenum, c_int]
glutGetModeValues = _libraries['libglut.so.3'].glutGetModeValues
glutGetModeValues.restype = POINTER(c_int)
glutGetModeValues.argtypes = [GLenum, POINTER(c_int)]
glutGetWindowData = _libraries['libglut.so.3'].glutGetWindowData
glutGetWindowData.restype = c_void_p
glutGetWindowData.argtypes = []
glutSetWindowData = _libraries['libglut.so.3'].glutSetWindowData
glutSetWindowData.restype = None
glutSetWindowData.argtypes = [c_void_p]
glutGetMenuData = _libraries['libglut.so.3'].glutGetMenuData
glutGetMenuData.restype = c_void_p
glutGetMenuData.argtypes = []
glutSetMenuData = _libraries['libglut.so.3'].glutSetMenuData
glutSetMenuData.restype = None
glutSetMenuData.argtypes = [c_void_p]
glutBitmapHeight = _libraries['libglut.so.3'].glutBitmapHeight
glutBitmapHeight.restype = c_int
glutBitmapHeight.argtypes = [c_void_p]
GLfloat = c_float
glutStrokeHeight = _libraries['libglut.so.3'].glutStrokeHeight
glutStrokeHeight.restype = GLfloat
glutStrokeHeight.argtypes = [c_void_p]
glutBitmapString = _libraries['libglut.so.3'].glutBitmapString
glutBitmapString.restype = None
glutBitmapString.argtypes = [c_void_p, POINTER(c_ubyte)]
glutStrokeString = _libraries['libglut.so.3'].glutStrokeString
glutStrokeString.restype = None
glutStrokeString.argtypes = [c_void_p, POINTER(c_ubyte)]
glutWireRhombicDodecahedron = _libraries['libglut.so.3'].glutWireRhombicDodecahedron
glutWireRhombicDodecahedron.restype = None
glutWireRhombicDodecahedron.argtypes = []
glutSolidRhombicDodecahedron = _libraries['libglut.so.3'].glutSolidRhombicDodecahedron
glutSolidRhombicDodecahedron.restype = None
glutSolidRhombicDodecahedron.argtypes = []
GLdouble = c_double
glutWireSierpinskiSponge = _libraries['libglut.so.3'].glutWireSierpinskiSponge
glutWireSierpinskiSponge.restype = None
glutWireSierpinskiSponge.argtypes = [c_int, POINTER(GLdouble), GLdouble]
glutSolidSierpinskiSponge = _libraries['libglut.so.3'].glutSolidSierpinskiSponge
glutSolidSierpinskiSponge.restype = None
glutSolidSierpinskiSponge.argtypes = [c_int, POINTER(GLdouble), GLdouble]
GLint = c_int
glutWireCylinder = _libraries['libglut.so.3'].glutWireCylinder
glutWireCylinder.restype = None
glutWireCylinder.argtypes = [GLdouble, GLdouble, GLint, GLint]
glutSolidCylinder = _libraries['libglut.so.3'].glutSolidCylinder
glutSolidCylinder.restype = None
glutSolidCylinder.argtypes = [GLdouble, GLdouble, GLint, GLint]
GLUTproc = CFUNCTYPE(None)
glutGetProcAddress = _libraries['libglut.so.3'].glutGetProcAddress
glutGetProcAddress.restype = GLUTproc
glutGetProcAddress.argtypes = [STRING]
glutJoystickGetNumAxes = _libraries['libglut.so.3'].glutJoystickGetNumAxes
glutJoystickGetNumAxes.restype = c_int
glutJoystickGetNumAxes.argtypes = [c_int]
glutJoystickGetNumButtons = _libraries['libglut.so.3'].glutJoystickGetNumButtons
glutJoystickGetNumButtons.restype = c_int
glutJoystickGetNumButtons.argtypes = [c_int]
glutJoystickNotWorking = _libraries['libglut.so.3'].glutJoystickNotWorking
glutJoystickNotWorking.restype = c_int
glutJoystickNotWorking.argtypes = [c_int]
glutJoystickGetDeadBand = _libraries['libglut.so.3'].glutJoystickGetDeadBand
glutJoystickGetDeadBand.restype = c_float
glutJoystickGetDeadBand.argtypes = [c_int, c_int]
glutJoystickSetDeadBand = _libraries['libglut.so.3'].glutJoystickSetDeadBand
glutJoystickSetDeadBand.restype = None
glutJoystickSetDeadBand.argtypes = [c_int, c_int, c_float]
glutJoystickGetSaturation = _libraries['libglut.so.3'].glutJoystickGetSaturation
glutJoystickGetSaturation.restype = c_float
glutJoystickGetSaturation.argtypes = [c_int, c_int]
glutJoystickSetSaturation = _libraries['libglut.so.3'].glutJoystickSetSaturation
glutJoystickSetSaturation.restype = None
glutJoystickSetSaturation.argtypes = [c_int, c_int, c_float]
glutJoystickSetMinRange = _libraries['libglut.so.3'].glutJoystickSetMinRange
glutJoystickSetMinRange.restype = None
glutJoystickSetMinRange.argtypes = [c_int, POINTER(c_float)]
glutJoystickSetMaxRange = _libraries['libglut.so.3'].glutJoystickSetMaxRange
glutJoystickSetMaxRange.restype = None
glutJoystickSetMaxRange.argtypes = [c_int, POINTER(c_float)]
glutJoystickSetCenter = _libraries['libglut.so.3'].glutJoystickSetCenter
glutJoystickSetCenter.restype = None
glutJoystickSetCenter.argtypes = [c_int, POINTER(c_float)]
glutJoystickGetMinRange = _libraries['libglut.so.3'].glutJoystickGetMinRange
glutJoystickGetMinRange.restype = None
glutJoystickGetMinRange.argtypes = [c_int, POINTER(c_float)]
glutJoystickGetMaxRange = _libraries['libglut.so.3'].glutJoystickGetMaxRange
glutJoystickGetMaxRange.restype = None
glutJoystickGetMaxRange.argtypes = [c_int, POINTER(c_float)]
glutJoystickGetCenter = _libraries['libglut.so.3'].glutJoystickGetCenter
glutJoystickGetCenter.restype = None
glutJoystickGetCenter.argtypes = [c_int, POINTER(c_float)]
glutInitContextVersion = _libraries['libglut.so.3'].glutInitContextVersion
glutInitContextVersion.restype = None
glutInitContextVersion.argtypes = [c_int, c_int]
glutInitContextFlags = _libraries['libglut.so.3'].glutInitContextFlags
glutInitContextFlags.restype = None
glutInitContextFlags.argtypes = [c_int]
glutInitContextProfile = _libraries['libglut.so.3'].glutInitContextProfile
glutInitContextProfile.restype = None
glutInitContextProfile.argtypes = [c_int]
glutStrokeRoman = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutStrokeRoman')
glutStrokeMonoRoman = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutStrokeMonoRoman')
glutBitmap9By15 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmap9By15')
glutBitmap8By13 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmap8By13')
glutBitmapTimesRoman10 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmapTimesRoman10')
glutBitmapTimesRoman24 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmapTimesRoman24')
glutBitmapHelvetica10 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmapHelvetica10')
glutBitmapHelvetica12 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmapHelvetica12')
glutBitmapHelvetica18 = (c_void_p).in_dll(_libraries['libglut.so.3'], 'glutBitmapHelvetica18')
glutInit = _libraries['libglut.so.3'].glutInit
glutInit.restype = None
glutInit.argtypes = [POINTER(c_int), POINTER(STRING)]
glutInitWindowPosition = _libraries['libglut.so.3'].glutInitWindowPosition
glutInitWindowPosition.restype = None
glutInitWindowPosition.argtypes = [c_int, c_int]
glutInitWindowSize = _libraries['libglut.so.3'].glutInitWindowSize
glutInitWindowSize.restype = None
glutInitWindowSize.argtypes = [c_int, c_int]
glutInitDisplayMode = _libraries['libglut.so.3'].glutInitDisplayMode
glutInitDisplayMode.restype = None
glutInitDisplayMode.argtypes = [c_uint]
glutInitDisplayString = _libraries['libglut.so.3'].glutInitDisplayString
glutInitDisplayString.restype = None
glutInitDisplayString.argtypes = [STRING]
glutMainLoop = _libraries['libglut.so.3'].glutMainLoop
glutMainLoop.restype = None
glutMainLoop.argtypes = []
glutCreateWindow = _libraries['libglut.so.3'].glutCreateWindow
glutCreateWindow.restype = c_int
glutCreateWindow.argtypes = [STRING]
glutCreateSubWindow = _libraries['libglut.so.3'].glutCreateSubWindow
glutCreateSubWindow.restype = c_int
glutCreateSubWindow.argtypes = [c_int, c_int, c_int, c_int, c_int]
glutDestroyWindow = _libraries['libglut.so.3'].glutDestroyWindow
glutDestroyWindow.restype = None
glutDestroyWindow.argtypes = [c_int]
glutSetWindow = _libraries['libglut.so.3'].glutSetWindow
glutSetWindow.restype = None
glutSetWindow.argtypes = [c_int]
glutGetWindow = _libraries['libglut.so.3'].glutGetWindow
glutGetWindow.restype = c_int
glutGetWindow.argtypes = []
glutSetWindowTitle = _libraries['libglut.so.3'].glutSetWindowTitle
glutSetWindowTitle.restype = None
glutSetWindowTitle.argtypes = [STRING]
glutSetIconTitle = _libraries['libglut.so.3'].glutSetIconTitle
glutSetIconTitle.restype = None
glutSetIconTitle.argtypes = [STRING]
glutReshapeWindow = _libraries['libglut.so.3'].glutReshapeWindow
glutReshapeWindow.restype = None
glutReshapeWindow.argtypes = [c_int, c_int]
glutPositionWindow = _libraries['libglut.so.3'].glutPositionWindow
glutPositionWindow.restype = None
glutPositionWindow.argtypes = [c_int, c_int]
glutShowWindow = _libraries['libglut.so.3'].glutShowWindow
glutShowWindow.restype = None
glutShowWindow.argtypes = []
glutHideWindow = _libraries['libglut.so.3'].glutHideWindow
glutHideWindow.restype = None
glutHideWindow.argtypes = []
glutIconifyWindow = _libraries['libglut.so.3'].glutIconifyWindow
glutIconifyWindow.restype = None
glutIconifyWindow.argtypes = []
glutPushWindow = _libraries['libglut.so.3'].glutPushWindow
glutPushWindow.restype = None
glutPushWindow.argtypes = []
glutPopWindow = _libraries['libglut.so.3'].glutPopWindow
glutPopWindow.restype = None
glutPopWindow.argtypes = []
glutFullScreen = _libraries['libglut.so.3'].glutFullScreen
glutFullScreen.restype = None
glutFullScreen.argtypes = []
glutPostWindowRedisplay = _libraries['libglut.so.3'].glutPostWindowRedisplay
glutPostWindowRedisplay.restype = None
glutPostWindowRedisplay.argtypes = [c_int]
glutPostRedisplay = _libraries['libglut.so.3'].glutPostRedisplay
glutPostRedisplay.restype = None
glutPostRedisplay.argtypes = []
glutSwapBuffers = _libraries['libglut.so.3'].glutSwapBuffers
glutSwapBuffers.restype = None
glutSwapBuffers.argtypes = []
glutWarpPointer = _libraries['libglut.so.3'].glutWarpPointer
glutWarpPointer.restype = None
glutWarpPointer.argtypes = [c_int, c_int]
glutSetCursor = _libraries['libglut.so.3'].glutSetCursor
glutSetCursor.restype = None
glutSetCursor.argtypes = [c_int]
glutEstablishOverlay = _libraries['libglut.so.3'].glutEstablishOverlay
glutEstablishOverlay.restype = None
glutEstablishOverlay.argtypes = []
glutRemoveOverlay = _libraries['libglut.so.3'].glutRemoveOverlay
glutRemoveOverlay.restype = None
glutRemoveOverlay.argtypes = []
glutUseLayer = _libraries['libglut.so.3'].glutUseLayer
glutUseLayer.restype = None
glutUseLayer.argtypes = [GLenum]
glutPostOverlayRedisplay = _libraries['libglut.so.3'].glutPostOverlayRedisplay
glutPostOverlayRedisplay.restype = None
glutPostOverlayRedisplay.argtypes = []
glutPostWindowOverlayRedisplay = _libraries['libglut.so.3'].glutPostWindowOverlayRedisplay
glutPostWindowOverlayRedisplay.restype = None
glutPostWindowOverlayRedisplay.argtypes = [c_int]
glutShowOverlay = _libraries['libglut.so.3'].glutShowOverlay
glutShowOverlay.restype = None
glutShowOverlay.argtypes = []
glutHideOverlay = _libraries['libglut.so.3'].glutHideOverlay
glutHideOverlay.restype = None
glutHideOverlay.argtypes = []
glutCreateMenu = _libraries['libglut.so.3'].glutCreateMenu
glutCreateMenu.restype = c_int
glutCreateMenu.argtypes = [CFUNCTYPE(None, c_int)]
glutDestroyMenu = _libraries['libglut.so.3'].glutDestroyMenu
glutDestroyMenu.restype = None
glutDestroyMenu.argtypes = [c_int]
glutGetMenu = _libraries['libglut.so.3'].glutGetMenu
glutGetMenu.restype = c_int
glutGetMenu.argtypes = []
glutSetMenu = _libraries['libglut.so.3'].glutSetMenu
glutSetMenu.restype = None
glutSetMenu.argtypes = [c_int]
glutAddMenuEntry = _libraries['libglut.so.3'].glutAddMenuEntry
glutAddMenuEntry.restype = None
glutAddMenuEntry.argtypes = [STRING, c_int]
glutAddSubMenu = _libraries['libglut.so.3'].glutAddSubMenu
glutAddSubMenu.restype = None
glutAddSubMenu.argtypes = [STRING, c_int]
glutChangeToMenuEntry = _libraries['libglut.so.3'].glutChangeToMenuEntry
glutChangeToMenuEntry.restype = None
glutChangeToMenuEntry.argtypes = [c_int, STRING, c_int]
glutChangeToSubMenu = _libraries['libglut.so.3'].glutChangeToSubMenu
glutChangeToSubMenu.restype = None
glutChangeToSubMenu.argtypes = [c_int, STRING, c_int]
glutRemoveMenuItem = _libraries['libglut.so.3'].glutRemoveMenuItem
glutRemoveMenuItem.restype = None
glutRemoveMenuItem.argtypes = [c_int]
glutAttachMenu = _libraries['libglut.so.3'].glutAttachMenu
glutAttachMenu.restype = None
glutAttachMenu.argtypes = [c_int]
glutDetachMenu = _libraries['libglut.so.3'].glutDetachMenu
glutDetachMenu.restype = None
glutDetachMenu.argtypes = [c_int]
glutTimerFunc = _libraries['libglut.so.3'].glutTimerFunc
glutTimerFunc.restype = None
glutTimerFunc.argtypes = [c_uint, CFUNCTYPE(None, c_int), c_int]
glutIdleFunc = _libraries['libglut.so.3'].glutIdleFunc
glutIdleFunc.restype = None
glutIdleFunc.argtypes = [CFUNCTYPE(None)]
glutKeyboardFunc = _libraries['libglut.so.3'].glutKeyboardFunc
glutKeyboardFunc.restype = None
glutKeyboardFunc.argtypes = [CFUNCTYPE(None, c_ubyte, c_int, c_int)]
glutSpecialFunc = _libraries['libglut.so.3'].glutSpecialFunc
glutSpecialFunc.restype = None
glutSpecialFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int)]
glutReshapeFunc = _libraries['libglut.so.3'].glutReshapeFunc
glutReshapeFunc.restype = None
glutReshapeFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutVisibilityFunc = _libraries['libglut.so.3'].glutVisibilityFunc
glutVisibilityFunc.restype = None
glutVisibilityFunc.argtypes = [CFUNCTYPE(None, c_int)]
glutDisplayFunc = _libraries['libglut.so.3'].glutDisplayFunc
glutDisplayFunc.restype = None
glutDisplayFunc.argtypes = [CFUNCTYPE(None)]
glutMouseFunc = _libraries['libglut.so.3'].glutMouseFunc
glutMouseFunc.restype = None
glutMouseFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int, c_int)]
glutMotionFunc = _libraries['libglut.so.3'].glutMotionFunc
glutMotionFunc.restype = None
glutMotionFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutPassiveMotionFunc = _libraries['libglut.so.3'].glutPassiveMotionFunc
glutPassiveMotionFunc.restype = None
glutPassiveMotionFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutEntryFunc = _libraries['libglut.so.3'].glutEntryFunc
glutEntryFunc.restype = None
glutEntryFunc.argtypes = [CFUNCTYPE(None, c_int)]
glutKeyboardUpFunc = _libraries['libglut.so.3'].glutKeyboardUpFunc
glutKeyboardUpFunc.restype = None
glutKeyboardUpFunc.argtypes = [CFUNCTYPE(None, c_ubyte, c_int, c_int)]
glutSpecialUpFunc = _libraries['libglut.so.3'].glutSpecialUpFunc
glutSpecialUpFunc.restype = None
glutSpecialUpFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int)]
glutJoystickFunc = _libraries['libglut.so.3'].glutJoystickFunc
glutJoystickFunc.restype = None
glutJoystickFunc.argtypes = [CFUNCTYPE(None, c_uint, c_int, c_int, c_int), c_int]
glutMenuStateFunc = _libraries['libglut.so.3'].glutMenuStateFunc
glutMenuStateFunc.restype = None
glutMenuStateFunc.argtypes = [CFUNCTYPE(None, c_int)]
glutMenuStatusFunc = _libraries['libglut.so.3'].glutMenuStatusFunc
glutMenuStatusFunc.restype = None
glutMenuStatusFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int)]
glutOverlayDisplayFunc = _libraries['libglut.so.3'].glutOverlayDisplayFunc
glutOverlayDisplayFunc.restype = None
glutOverlayDisplayFunc.argtypes = [CFUNCTYPE(None)]
glutWindowStatusFunc = _libraries['libglut.so.3'].glutWindowStatusFunc
glutWindowStatusFunc.restype = None
glutWindowStatusFunc.argtypes = [CFUNCTYPE(None, c_int)]
glutSpaceballMotionFunc = _libraries['libglut.so.3'].glutSpaceballMotionFunc
glutSpaceballMotionFunc.restype = None
glutSpaceballMotionFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int)]
glutSpaceballRotateFunc = _libraries['libglut.so.3'].glutSpaceballRotateFunc
glutSpaceballRotateFunc.restype = None
glutSpaceballRotateFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int)]
glutSpaceballButtonFunc = _libraries['libglut.so.3'].glutSpaceballButtonFunc
glutSpaceballButtonFunc.restype = None
glutSpaceballButtonFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutButtonBoxFunc = _libraries['libglut.so.3'].glutButtonBoxFunc
glutButtonBoxFunc.restype = None
glutButtonBoxFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutDialsFunc = _libraries['libglut.so.3'].glutDialsFunc
glutDialsFunc.restype = None
glutDialsFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutTabletMotionFunc = _libraries['libglut.so.3'].glutTabletMotionFunc
glutTabletMotionFunc.restype = None
glutTabletMotionFunc.argtypes = [CFUNCTYPE(None, c_int, c_int)]
glutTabletButtonFunc = _libraries['libglut.so.3'].glutTabletButtonFunc
glutTabletButtonFunc.restype = None
glutTabletButtonFunc.argtypes = [CFUNCTYPE(None, c_int, c_int, c_int, c_int)]
glutGet = _libraries['libglut.so.3'].glutGet
glutGet.restype = c_int
glutGet.argtypes = [GLenum]
glutDeviceGet = _libraries['libglut.so.3'].glutDeviceGet
glutDeviceGet.restype = c_int
glutDeviceGet.argtypes = [GLenum]
glutGetModifiers = _libraries['libglut.so.3'].glutGetModifiers
glutGetModifiers.restype = c_int
glutGetModifiers.argtypes = []
glutLayerGet = _libraries['libglut.so.3'].glutLayerGet
glutLayerGet.restype = c_int
glutLayerGet.argtypes = [GLenum]
glutBitmapCharacter = _libraries['libglut.so.3'].glutBitmapCharacter
glutBitmapCharacter.restype = None
glutBitmapCharacter.argtypes = [c_void_p, c_int]
glutBitmapWidth = _libraries['libglut.so.3'].glutBitmapWidth
glutBitmapWidth.restype = c_int
glutBitmapWidth.argtypes = [c_void_p, c_int]
glutStrokeCharacter = _libraries['libglut.so.3'].glutStrokeCharacter
glutStrokeCharacter.restype = None
glutStrokeCharacter.argtypes = [c_void_p, c_int]
glutStrokeWidth = _libraries['libglut.so.3'].glutStrokeWidth
glutStrokeWidth.restype = c_int
glutStrokeWidth.argtypes = [c_void_p, c_int]
glutBitmapLength = _libraries['libglut.so.3'].glutBitmapLength
glutBitmapLength.restype = c_int
glutBitmapLength.argtypes = [c_void_p, POINTER(c_ubyte)]
glutStrokeLength = _libraries['libglut.so.3'].glutStrokeLength
glutStrokeLength.restype = c_int
glutStrokeLength.argtypes = [c_void_p, POINTER(c_ubyte)]
glutWireCube = _libraries['libglut.so.3'].glutWireCube
glutWireCube.restype = None
glutWireCube.argtypes = [GLdouble]
glutSolidCube = _libraries['libglut.so.3'].glutSolidCube
glutSolidCube.restype = None
glutSolidCube.argtypes = [GLdouble]
glutWireSphere = _libraries['libglut.so.3'].glutWireSphere
glutWireSphere.restype = None
glutWireSphere.argtypes = [GLdouble, GLint, GLint]
glutSolidSphere = _libraries['libglut.so.3'].glutSolidSphere
glutSolidSphere.restype = None
glutSolidSphere.argtypes = [GLdouble, GLint, GLint]
glutWireCone = _libraries['libglut.so.3'].glutWireCone
glutWireCone.restype = None
glutWireCone.argtypes = [GLdouble, GLdouble, GLint, GLint]
glutSolidCone = _libraries['libglut.so.3'].glutSolidCone
glutSolidCone.restype = None
glutSolidCone.argtypes = [GLdouble, GLdouble, GLint, GLint]
glutWireTorus = _libraries['libglut.so.3'].glutWireTorus
glutWireTorus.restype = None
glutWireTorus.argtypes = [GLdouble, GLdouble, GLint, GLint]
glutSolidTorus = _libraries['libglut.so.3'].glutSolidTorus
glutSolidTorus.restype = None
glutSolidTorus.argtypes = [GLdouble, GLdouble, GLint, GLint]
glutWireDodecahedron = _libraries['libglut.so.3'].glutWireDodecahedron
glutWireDodecahedron.restype = None
glutWireDodecahedron.argtypes = []
glutSolidDodecahedron = _libraries['libglut.so.3'].glutSolidDodecahedron
glutSolidDodecahedron.restype = None
glutSolidDodecahedron.argtypes = []
glutWireOctahedron = _libraries['libglut.so.3'].glutWireOctahedron
glutWireOctahedron.restype = None
glutWireOctahedron.argtypes = []
glutSolidOctahedron = _libraries['libglut.so.3'].glutSolidOctahedron
glutSolidOctahedron.restype = None
glutSolidOctahedron.argtypes = []
glutWireTetrahedron = _libraries['libglut.so.3'].glutWireTetrahedron
glutWireTetrahedron.restype = None
glutWireTetrahedron.argtypes = []
glutSolidTetrahedron = _libraries['libglut.so.3'].glutSolidTetrahedron
glutSolidTetrahedron.restype = None
glutSolidTetrahedron.argtypes = []
glutWireIcosahedron = _libraries['libglut.so.3'].glutWireIcosahedron
glutWireIcosahedron.restype = None
glutWireIcosahedron.argtypes = []
glutSolidIcosahedron = _libraries['libglut.so.3'].glutSolidIcosahedron
glutSolidIcosahedron.restype = None
glutSolidIcosahedron.argtypes = []
glutWireTeapot = _libraries['libglut.so.3'].glutWireTeapot
glutWireTeapot.restype = None
glutWireTeapot.argtypes = [GLdouble]
glutSolidTeapot = _libraries['libglut.so.3'].glutSolidTeapot
glutSolidTeapot.restype = None
glutSolidTeapot.argtypes = [GLdouble]
glutGameModeString = _libraries['libglut.so.3'].glutGameModeString
glutGameModeString.restype = None
glutGameModeString.argtypes = [STRING]
glutEnterGameMode = _libraries['libglut.so.3'].glutEnterGameMode
glutEnterGameMode.restype = c_int
glutEnterGameMode.argtypes = []
glutLeaveGameMode = _libraries['libglut.so.3'].glutLeaveGameMode
glutLeaveGameMode.restype = None
glutLeaveGameMode.argtypes = []
glutGameModeGet = _libraries['libglut.so.3'].glutGameModeGet
glutGameModeGet.restype = c_int
glutGameModeGet.argtypes = [GLenum]
glutVideoResizeGet = _libraries['libglut.so.3'].glutVideoResizeGet
glutVideoResizeGet.restype = c_int
glutVideoResizeGet.argtypes = [GLenum]
glutSetupVideoResizing = _libraries['libglut.so.3'].glutSetupVideoResizing
glutSetupVideoResizing.restype = None
glutSetupVideoResizing.argtypes = []
glutStopVideoResizing = _libraries['libglut.so.3'].glutStopVideoResizing
glutStopVideoResizing.restype = None
glutStopVideoResizing.argtypes = []
glutVideoResize = _libraries['libglut.so.3'].glutVideoResize
glutVideoResize.restype = None
glutVideoResize.argtypes = [c_int, c_int, c_int, c_int]
glutVideoPan = _libraries['libglut.so.3'].glutVideoPan
glutVideoPan.restype = None
glutVideoPan.argtypes = [c_int, c_int, c_int, c_int]
glutSetColor = _libraries['libglut.so.3'].glutSetColor
glutSetColor.restype = None
glutSetColor.argtypes = [c_int, GLfloat, GLfloat, GLfloat]
glutGetColor = _libraries['libglut.so.3'].glutGetColor
glutGetColor.restype = GLfloat
glutGetColor.argtypes = [c_int, c_int]
glutCopyColormap = _libraries['libglut.so.3'].glutCopyColormap
glutCopyColormap.restype = None
glutCopyColormap.argtypes = [c_int]
glutIgnoreKeyRepeat = _libraries['libglut.so.3'].glutIgnoreKeyRepeat
glutIgnoreKeyRepeat.restype = None
glutIgnoreKeyRepeat.argtypes = [c_int]
glutSetKeyRepeat = _libraries['libglut.so.3'].glutSetKeyRepeat
glutSetKeyRepeat.restype = None
glutSetKeyRepeat.argtypes = [c_int]
glutForceJoystickFunc = _libraries['libglut.so.3'].glutForceJoystickFunc
glutForceJoystickFunc.restype = None
glutForceJoystickFunc.argtypes = []
glutExtensionSupported = _libraries['libglut.so.3'].glutExtensionSupported
glutExtensionSupported.restype = c_int
glutExtensionSupported.argtypes = [STRING]
glutReportErrors = _libraries['libglut.so.3'].glutReportErrors
glutReportErrors.restype = None
glutReportErrors.argtypes = []
__all__ = ['GLUT_GAME_MODE_POSSIBLE', 'GLUT_XLIB_IMPLEMENTATION',
           'glutGameModeString', 'GLUT_COMPATIBILITY_PROFILE',
           'GLUT_NOT_VISIBLE', 'GLUT_MIDDLE_BUTTON',
           'GLUT_API_VERSION', 'glutDetachMenu', 'GLUT_FULLY_COVERED',
           'glutWMCloseFunc', 'GLUT_ACCUM', 'GLUT_WINDOW_WIDTH',
           'glutGameModeGet', 'glutGetProcAddress',
           'glutEstablishOverlay', 'glutWireTetrahedron',
           'glutWireOctahedron', 'GLUT_INDEX',
           'glutWireRhombicDodecahedron', 'glutReportErrors',
           'glutSolidTorus', 'GLUT_KEY_PAGE_UP',
           'GLUT_WINDOW_COLORMAP_SIZE', 'glutLayerGet',
           'glutStrokeString', 'glutStrokeLength',
           'glutDestroyWindow', 'GLUT_GAME_MODE_HEIGHT',
           'glutPostWindowOverlayRedisplay', 'GLUT_SCREEN_HEIGHT',
           'glutJoystickNotWorking', 'glutSolidCone',
           'glutJoystickFunc', 'glutEntryFunc', 'GLint', 'GLUT_RGB',
           'glutBitmapTimesRoman10', 'GLUT_ALPHA', 'GLfloat',
           'GLUT_WINDOW_NUM_SAMPLES', 'GLUT_MULTISAMPLE', 'GLUT_AUX4',
           'GLUT_AUX2', 'GLUT_HAS_SPACEBALL', 'GLUT_AUX1',
           'glutGetModifiers', 'GLUT_RIGHT_BUTTON',
           'glutJoystickSetCenter', 'glutSolidTetrahedron',
           'glutBitmapHelvetica18', 'glutBitmapHelvetica12',
           'GLUT_WINDOW_GREEN_SIZE', 'glutBitmapHelvetica10',
           'GLUT_LEFT', 'glutCreateMenu', 'GLUT_CURSOR_WAIT',
           'GLUT_CURSOR_FULL_CROSSHAIR', 'glutMotionFunc',
           'glutAddMenuEntry', 'GLUT_VIDEO_RESIZE_X',
           'glutStrokeMonoRoman', 'glutTabletButtonFunc',
           'glutCloseFunc', 'GLUT_DEVICE_IGNORE_KEY_REPEAT',
           'glutForceJoystickFunc', 'GLUT_DOWN', 'GLUT_INIT_STATE',
           'GLUT_VIDEO_RESIZE_WIDTH', 'glutDestroyMenu',
           'glutWireCone', 'GLUT_KEY_END', 'glutUseLayer',
           'GLUT_OVERLAY', 'GLUT_INIT_WINDOW_Y', 'GLUT_INIT_WINDOW_X',
           'glutSolidRhombicDodecahedron', 'glutInitDisplayString',
           'glutHideOverlay', 'GLUT_KEY_F8', 'GLUT_KEY_F9',
           'GLUT_NORMAL_DAMAGED', 'GLUT_KEY_F4', 'GLUT_KEY_F5',
           'GLUT_KEY_F6', 'GLUT_KEY_F7', 'GLUT_KEY_F1', 'GLUT_KEY_F2',
           'GLUT_KEY_F3', 'GLUT_ENTERED', 'GLUT_KEY_LEFT',
           'glutAttachMenu', 'GLenum', 'GLUT_SRGB',
           'glutBitmapTimesRoman24', 'glutChangeToMenuEntry',
           'GLUT_WINDOW_ALPHA_SIZE', 'glutInit',
           'glutInitContextFlags', 'glutWarpPointer',
           'glutGetWindowData', 'glutGetMenuData',
           'GLUT_USE_CURRENT_CONTEXT', 'glutWireTorus',
           'glutCreateSubWindow', 'GLUT_INIT_DISPLAY_MODE',
           'glutTimerFunc', 'glutJoystickGetSaturation',
           'GLUT_CURSOR_TOP_SIDE', 'glutInitContextVersion',
           'glutChangeToSubMenu', 'GLUT_KEY_DOWN', 'glutIdleFunc',
           'glutGetWindow', 'glutOverlayDisplayFunc',
           'GLUT_CURSOR_BOTTOM_RIGHT_CORNER', 'glutDisplayFunc',
           'glutPopWindow', 'glutLeaveMainLoop',
           'glutInitDisplayMode', 'glutSolidTeapot',
           'glutGetModeValues', 'glutJoystickGetNumAxes',
           'glutJoystickSetSaturation', 'GLUT_WINDOW_ACCUM_BLUE_SIZE',
           'GLUT_CREATE_NEW_CONTEXT', 'GLUT_INIT_WINDOW_HEIGHT',
           'glutDialsFunc', 'GLUT_WINDOW_ACCUM_ALPHA_SIZE',
           'GLUT_ACTION_EXIT', 'GLUT_INIT_PROFILE',
           'GLUT_WINDOW_BUFFER_SIZE', 'GLUT_KEY_DELETE',
           'GLUT_INIT_MAJOR_VERSION', 'GLUT_BLUE', 'GLUT_KEY_F12',
           'GLUT_KEY_F10', 'GLUT_KEY_F11', 'glutHideWindow',
           'GLUT_HAS_MOUSE', 'GLUT_VERSION', 'glutSolidIcosahedron',
           'GLUT_WINDOW_ACCUM_RED_SIZE', 'glutInitWindowSize',
           'GLUT_VIDEO_RESIZE_POSSIBLE', 'GLUT_CURSOR_RIGHT_SIDE',
           'GLUT_INIT_FLAGS', 'glutWireCube', 'GLUT_KEY_RIGHT',
           'GLUT_FORWARD_COMPATIBLE', 'GLUT_INIT_MINOR_VERSION',
           'glutMainLoopEvent', 'GLUT_ACTIVE_ALT',
           'GLUT_WINDOW_ACCUM_GREEN_SIZE', 'GLUT_DEPTH',
           'GLUT_SINGLE', 'GLUT_CURSOR_TEXT', 'GLUT_UP',
           'GLUT_LAYER_IN_USE', 'GLUT_ACTIVE_SHIFT',
           'glutWireCylinder', 'GLUT_FORCE_DIRECT_CONTEXT',
           'glutSetupVideoResizing', 'GLUT_FULLY_RETAINED',
           'glutPostRedisplay', 'glutSpaceballRotateFunc',
           'glutBitmapHeight', 'glutMenuStatusFunc',
           'GLUT_JOYSTICK_BUTTON_D', 'GLUT_JOYSTICK_BUTTON_A',
           'glutSolidCube', 'GLUT_JOYSTICK_BUTTON_C',
           'GLUT_JOYSTICK_BUTTON_B', 'glutShowOverlay',
           'GLUT_OVERLAY_POSSIBLE', 'GLUT_CURSOR_TOP_LEFT_CORNER',
           'glutEnterGameMode', 'GLUT_ACTIVE_CTRL',
           'glutBitmapCharacter', 'GLUT_CURSOR_NONE', 'glutMainLoop',
           'glutPostOverlayRedisplay', 'GLUT_STEREO',
           'GLUT_MENU_NOT_IN_USE', 'glutSetKeyRepeat',
           'GLUT_CURSOR_SPRAY', 'glutStrokeHeight',
           'GLUT_ALLOW_DIRECT_CONTEXT', 'GLUT_ELAPSED_TIME',
           'GLUT_NUM_MOUSE_BUTTONS', 'glutBitmapWidth',
           'GLUT_CORE_PROFILE', 'GLUT_CURSOR_UP_DOWN',
           'GLUT_KEY_REPEAT_DEFAULT', 'GLUT_KEY_REPEAT_OFF',
           'GLUT_CURSOR_DESTROY', 'GLUT_ACTION_GLUTMAINLOOP_RETURNS',
           'GLUT_CURSOR_BOTTOM_SIDE', 'GLUT_MENU_NUM_ITEMS',
           'glutMenuDestroyFunc', 'GLUT_JOYSTICK_BUTTONS',
           'GLUT_KEY_NUM_LOCK', 'GLUT_HAS_DIAL_AND_BUTTON_BOX',
           'glutJoystickGetMinRange', 'GLUT_BORDERLESS',
           'glutWindowStatusFunc', 'glutCopyColormap',
           'GLUT_KEY_HOME', 'GLUT_WINDOW_DOUBLEBUFFER',
           'GLUT_HAS_KEYBOARD', 'GLUT_OVERLAY_DAMAGED',
           'glutAddSubMenu', 'GLUT_VISIBLE', 'glutSetWindowData',
           'GLUT_VIDEO_RESIZE_Y_DELTA', 'GLUT_KEY_BEGIN',
           'glutFullScreen', 'GLUT_VIDEO_RESIZE_HEIGHT',
           'glutSetColor', 'glutStrokeWidth', 'glutVideoPan',
           'GLUT_INIT_WINDOW_WIDTH', 'glutSolidCylinder',
           'GLUT_GREEN', 'glutGetColor', 'glutSetMenuData',
           'GLUT_GAME_MODE_PIXEL_DEPTH', 'GLUT_WINDOW_DEPTH_SIZE',
           'GLUT_CURSOR_CYCLE', 'GLUT_VIDEO_RESIZE_Y',
           'GLUT_ACTION_CONTINUE_EXECUTION',
           'GLUT_NUM_TABLET_BUTTONS', 'glutSwapBuffers',
           'GLUT_CURSOR_RIGHT_ARROW', 'glutSpaceballButtonFunc',
           'glutSpaceballMotionFunc', 'glutButtonBoxFunc',
           'glutSolidSphere', 'glutReshapeWindow', 'glutSpecialFunc',
           'GLUT_SCREEN_WIDTH', 'GLUT_GAME_MODE_DISPLAY_CHANGED',
           'glutJoystickSetMinRange', 'GLUT_MENU_IN_USE',
           'GLUT_NUM_BUTTON_BOX_BUTTONS', 'glutJoystickGetMaxRange',
           'GLUT_PARTIALLY_RETAINED', 'GLUT_RED', 'glutLeaveGameMode',
           'GLUT_CURSOR_LEFT_SIDE', 'glutSetIconTitle',
           'glutStopVideoResizing', 'GLUT_JOYSTICK_POLL_RATE',
           'glutWireIcosahedron', 'glutFullScreenToggle',
           'GLUT_WINDOW_FORMAT_ID', 'GLUT_VIDEO_RESIZE_HEIGHT_DELTA',
           'GLUT_GAME_MODE_ACTIVE', 'GLUT_GAME_MODE_REFRESH_RATE',
           'glutSpecialUpFunc', 'GLUT_DISPLAY_MODE_POSSIBLE',
           'GLUT_VIDEO_RESIZE_X_DELTA', 'GLUT_DIRECT_RENDERING',
           'GLUT_SCREEN_WIDTH_MM', 'GLUT_ACTION_ON_WINDOW_CLOSE',
           'glutSetWindowTitle', 'GLUT_SCREEN_HEIGHT_MM',
           'glutExtensionSupported', 'glutReshapeFunc',
           'GLUT_KEY_PAGE_DOWN', 'GLUTproc', 'GLUT_AUX',
           'glutVisibilityFunc', 'glutKeyboardFunc',
           'GLUT_WINDOW_CURSOR', 'glutPassiveMotionFunc',
           'GLUT_CURSOR_LEFT_RIGHT', 'glutRemoveMenuItem',
           'GLUT_DOUBLE', 'GLUT_TRY_DIRECT_CONTEXT',
           'GLUT_HAS_TABLET', 'glutDeviceGet', 'GLUT_WINDOW_STEREO',
           'GLUT_OWNS_JOYSTICK', 'GLUT_JOYSTICK_AXES',
           'glutInitContextProfile', 'GLUT_RENDERING_CONTEXT',
           'GLUT_KEY_UP', 'GLUT_CURSOR_TOP_RIGHT_CORNER',
           'GLUT_STENCIL', 'glutWireTeapot', 'GLUT_WINDOW_Y',
           'GLUT_WINDOW_X', 'glutTabletMotionFunc', 'GLUT_HIDDEN',
           'glutShowWindow', 'glutWireDodecahedron',
           'glutInitWindowPosition', 'glutBitmap8By13',
           'GLUT_WINDOW_NUM_CHILDREN', 'glutIgnoreKeyRepeat',
           'GLUT_WINDOW_BLUE_SIZE', 'glutSetOption',
           'GLUT_WINDOW_STENCIL_SIZE', 'glutMouseWheelFunc',
           'glutPositionWindow', 'GLUT_CURSOR_INFO',
           'glutKeyboardUpFunc', 'GLUT_VIDEO_RESIZE_IN_USE',
           'GLUT_CURSOR_CROSSHAIR', 'glutPushWindow',
           'GLUT_KEY_REPEAT_ON', 'glutStrokeRoman',
           'glutSolidDodecahedron', 'GLUT_CURSOR_LEFT_ARROW',
           'glutBitmapLength', 'GLUT_GAME_MODE_WIDTH',
           'glutJoystickSetDeadBand', 'GLUT_WINDOW_BORDER_WIDTH',
           'glutGet', 'GLUT_CAPTIONLESS', 'GLdouble',
           'glutJoystickGetCenter', 'GLUT_AUX3', 'GLUT_WINDOW_PARENT',
           'GLUT_NORMAL', 'GLUT_DEBUG', 'glutVideoResizeGet',
           'GLUT_LEFT_BUTTON', 'glutBitmap9By15',
           'GLUT_DEVICE_KEY_REPEAT', 'glutGetMenu', 'glutSetCursor',
           'glutSolidSierpinskiSponge', 'glutMouseFunc',
           'glutCreateWindow', 'GLUT_WINDOW_HEADER_HEIGHT',
           'glutJoystickSetMaxRange', 'GLUT_WINDOW_RED_SIZE',
           'GLUT_HAS_OVERLAY', 'GLUT_FULL_SCREEN',
           'GLUT_VIDEO_RESIZE_WIDTH_DELTA', 'glutBitmapString',
           'glutWireSierpinskiSponge', 'glutMenuStateFunc',
           'GLUT_RGBA', 'glutVideoResize', 'GLUT_WINDOW_HEIGHT',
           'GLUT_FORCE_INDIRECT_CONTEXT', 'GLUT_CURSOR_HELP',
           'glutPostWindowRedisplay', 'glutSetMenu', 'glutExit',
           'GLUT_NUM_DIALS', 'GLUT_HAS_JOYSTICK', 'glutIconifyWindow',
           'GLUT_CURSOR_BOTTOM_LEFT_CORNER',
           'glutJoystickGetDeadBand', 'GLUT_NUM_SPACEBALL_BUTTONS',
           'glutStrokeCharacter', 'GLUT_CURSOR_INHERIT',
           'GLUT_WINDOW_RGBA', 'glutRemoveOverlay',
           'glutJoystickGetNumButtons', 'glutWireSphere',
           'GLUT_TRANSPARENT_INDEX', 'glutSolidOctahedron',
           'GLUT_LUMINANCE', 'GLUT_KEY_INSERT', 'glutSetWindow']
