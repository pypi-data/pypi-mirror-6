from ctypes import *

_libraries = {}
_libraries['libGLU.so.1'] = CDLL('libGLU.so.1')


GLU_OUTLINE_PATCH = 100241 # Variable c_int '100241'
GLU_NURBS_ERROR1 = 100251 # Variable c_int '100251'
GLU_TESS_END = 100102 # Variable c_int '100102'
GLU_EDGE_FLAG = 100104 # Variable c_int '100104'
GLU_TESS_MISSING_END_POLYGON = 100153 # Variable c_int '100153'
GLU_TESS_NEED_COMBINE_CALLBACK = 100156 # Variable c_int '100156'
GLU_U_STEP = 100206 # Variable c_int '100206'
GLU_OUTSIDE = 100020 # Variable c_int '100020'
GLU_UNKNOWN = 100124 # Variable c_int '100124'
GLU_NONE = 100002 # Variable c_int '100002'
GLU_TESS_WINDING_NEGATIVE = 100133 # Variable c_int '100133'
GLU_NURBS_BEGIN_DATA_EXT = 100170 # Variable c_int '100170'
GLU_NURBS_ERROR30 = 100280 # Variable c_int '100280'
GLU_OUT_OF_MEMORY = 100902 # Variable c_int '100902'
GLU_NURBS_ERROR15 = 100265 # Variable c_int '100265'
GLU_NURBS_ERROR10 = 100260 # Variable c_int '100260'
GLU_NURBS_ERROR11 = 100261 # Variable c_int '100261'
GLU_NURBS_ERROR12 = 100262 # Variable c_int '100262'
GLU_NURBS_ERROR18 = 100268 # Variable c_int '100268'
GLU_NURBS_ERROR19 = 100269 # Variable c_int '100269'
GLU_TESS_MISSING_BEGIN_POLYGON = 100151 # Variable c_int '100151'
GLU_VERTEX = 100101 # Variable c_int '100101'
GLU_NURBS_ERROR5 = 100255 # Variable c_int '100255'
GLU_NURBS_VERTEX_EXT = 100165 # Variable c_int '100165'
GLU_NURBS_END = 100169 # Variable c_int '100169'
GLU_TESS_WINDING_NONZERO = 100131 # Variable c_int '100131'
GLU_NURBS_BEGIN_DATA = 100170 # Variable c_int '100170'
GLU_TESS_TOLERANCE = 100142 # Variable c_int '100142'
GLU_FALSE = 0 # Variable c_int '0'
GLU_TESS_MAX_COORD = 1e+150 # Variable c_double '9.99999999999999980835596172437374590573120014030318793091e+149'
GLU_NURBS_BEGIN = 100164 # Variable c_int '100164'
GLU_VERSION_1_1 = 1 # Variable c_int '1'
GLU_VERSION_1_3 = 1 # Variable c_int '1'
GLU_VERSION_1_2 = 1 # Variable c_int '1'
GLU_TESS_ERROR1 = 100151 # Variable c_int '100151'
GLU_TESS_ERROR3 = 100153 # Variable c_int '100153'
GLU_TESS_ERROR4 = 100154 # Variable c_int '100154'
GLU_TESS_ERROR5 = 100155 # Variable c_int '100155'
GLU_TESS_ERROR7 = 100157 # Variable c_int '100157'
GLU_TESS_ERROR8 = 100158 # Variable c_int '100158'
GLU_TESS_WINDING_ABS_GEQ_TWO = 100134 # Variable c_int '100134'
GLU_TESS_EDGE_FLAG_DATA = 100110 # Variable c_int '100110'
GLU_PARAMETRIC_ERROR = 100216 # Variable c_int '100216'
GLU_EXTENSIONS = 100801 # Variable c_int '100801'
GLU_INSIDE = 100021 # Variable c_int '100021'
GLU_NURBS_RENDERER_EXT = 100162 # Variable c_int '100162'
GLU_NURBS_ERROR6 = 100256 # Variable c_int '100256'
GLU_NURBS_ERROR7 = 100257 # Variable c_int '100257'
GLU_NURBS_ERROR4 = 100254 # Variable c_int '100254'
GLU_NURBS_ERROR2 = 100252 # Variable c_int '100252'
GLU_NURBS_ERROR3 = 100253 # Variable c_int '100253'
GLU_NURBS_NORMAL = 100166 # Variable c_int '100166'
GLU_NURBS_ERROR8 = 100258 # Variable c_int '100258'
GLU_NURBS_ERROR9 = 100259 # Variable c_int '100259'
GLU_SMOOTH = 100000 # Variable c_int '100000'
GLU_SILHOUETTE = 100013 # Variable c_int '100013'
GLU_TRUE = 1 # Variable c_int '1'
GLU_OBJECT_PATH_LENGTH = 100209 # Variable c_int '100209'
GLU_TESS_BOUNDARY_ONLY = 100141 # Variable c_int '100141'
GLU_TESS_WINDING_POSITIVE = 100132 # Variable c_int '100132'
GLU_DISPLAY_MODE = 100204 # Variable c_int '100204'
GLU_CW = 100120 # Variable c_int '100120'
GLU_OBJECT_PARAMETRIC_ERROR_EXT = 100208 # Variable c_int '100208'
GLU_NURBS_MODE_EXT = 100160 # Variable c_int '100160'
GLU_OBJECT_PARAMETRIC_ERROR = 100208 # Variable c_int '100208'
GLU_TESS_WINDING_ODD = 100130 # Variable c_int '100130'
GLU_NURBS_VERTEX = 100165 # Variable c_int '100165'
GLU_TESS_COORD_TOO_LARGE = 100155 # Variable c_int '100155'
GLU_NURBS_TESSELLATOR_EXT = 100161 # Variable c_int '100161'
GLU_NURBS_ERROR = 100103 # Variable c_int '100103'
GLU_TESS_BEGIN = 100100 # Variable c_int '100100'
GLU_NURBS_TEXTURE_COORD = 100168 # Variable c_int '100168'
GLU_POINT = 100010 # Variable c_int '100010'
GLU_EXT_object_space_tess = 1 # Variable c_int '1'
GLU_NURBS_TEXTURE_COORD_DATA = 100174 # Variable c_int '100174'
GLU_DOMAIN_DISTANCE = 100217 # Variable c_int '100217'
GLU_NURBS_COLOR_DATA = 100173 # Variable c_int '100173'
GLU_EXT_nurbs_tessellator = 1 # Variable c_int '1'
GLU_NURBS_ERROR25 = 100275 # Variable c_int '100275'
GLU_TESS_ERROR6 = 100156 # Variable c_int '100156'
GLU_FILL = 100012 # Variable c_int '100012'
GLU_TESS_COMBINE_DATA = 100111 # Variable c_int '100111'
GLU_SAMPLING_TOLERANCE = 100203 # Variable c_int '100203'
GLU_PATH_LENGTH = 100215 # Variable c_int '100215'
GLU_NURBS_BEGIN_EXT = 100164 # Variable c_int '100164'
GLU_NURBS_VERTEX_DATA = 100171 # Variable c_int '100171'
GLU_NURBS_COLOR_DATA_EXT = 100173 # Variable c_int '100173'
GLU_NURBS_NORMAL_DATA = 100172 # Variable c_int '100172'
GLU_END = 100102 # Variable c_int '100102'
GLU_CULLING = 100201 # Variable c_int '100201'
GLU_NURBS_RENDERER = 100162 # Variable c_int '100162'
GLU_CCW = 100121 # Variable c_int '100121'
GLU_OBJECT_PATH_LENGTH_EXT = 100209 # Variable c_int '100209'
GLU_INVALID_OPERATION = 100904 # Variable c_int '100904'
GLU_TESS_VERTEX_DATA = 100107 # Variable c_int '100107'
GLU_TESS_BEGIN_DATA = 100106 # Variable c_int '100106'
GLU_NURBS_VERTEX_DATA_EXT = 100171 # Variable c_int '100171'
GLU_INCOMPATIBLE_GL_VERSION = 100903 # Variable c_int '100903'
GLU_NURBS_NORMAL_DATA_EXT = 100172 # Variable c_int '100172'
GLU_INTERIOR = 100122 # Variable c_int '100122'
GLU_TESS_ERROR2 = 100152 # Variable c_int '100152'
GLU_TESS_WINDING_RULE = 100140 # Variable c_int '100140'
GLU_VERSION = 100800 # Variable c_int '100800'
GLU_NURBS_ERROR34 = 100284 # Variable c_int '100284'
GLU_NURBS_ERROR35 = 100285 # Variable c_int '100285'
GLU_TESS_MISSING_END_CONTOUR = 100154 # Variable c_int '100154'
GLU_NURBS_TEX_COORD_DATA_EXT = 100174 # Variable c_int '100174'
GLU_TESS_ERROR = 100103 # Variable c_int '100103'
GLU_NURBS_ERROR14 = 100264 # Variable c_int '100264'
GLU_MAP1_TRIM_3 = 100211 # Variable c_int '100211'
GLU_TESS_COMBINE = 100105 # Variable c_int '100105'
GLU_TESS_MISSING_BEGIN_CONTOUR = 100152 # Variable c_int '100152'
GLU_FLAT = 100001 # Variable c_int '100001'
GLU_TESS_END_DATA = 100108 # Variable c_int '100108'
GLU_NURBS_ERROR23 = 100273 # Variable c_int '100273'
GLU_PARAMETRIC_TOLERANCE = 100202 # Variable c_int '100202'
GLU_OUTLINE_POLYGON = 100240 # Variable c_int '100240'
GLU_LINE = 100011 # Variable c_int '100011'
GLU_MAP1_TRIM_2 = 100210 # Variable c_int '100210'
GLU_NURBS_ERROR16 = 100266 # Variable c_int '100266'
GLU_NURBS_ERROR17 = 100267 # Variable c_int '100267'
GLU_NURBS_END_DATA = 100175 # Variable c_int '100175'
GLU_NURBS_ERROR13 = 100263 # Variable c_int '100263'
GLU_NURBS_END_DATA_EXT = 100175 # Variable c_int '100175'
GLU_V_STEP = 100207 # Variable c_int '100207'
GLU_TESS_ERROR_DATA = 100109 # Variable c_int '100109'
GLU_AUTO_LOAD_MATRIX = 100200 # Variable c_int '100200'
GLU_NURBS_MODE = 100160 # Variable c_int '100160'
GLU_NURBS_ERROR29 = 100279 # Variable c_int '100279'
GLU_NURBS_ERROR28 = 100278 # Variable c_int '100278'
GLU_NURBS_ERROR24 = 100274 # Variable c_int '100274'
GLU_NURBS_ERROR27 = 100277 # Variable c_int '100277'
GLU_NURBS_ERROR26 = 100276 # Variable c_int '100276'
GLU_NURBS_ERROR21 = 100271 # Variable c_int '100271'
GLU_NURBS_ERROR20 = 100270 # Variable c_int '100270'
GLU_NURBS_ERROR22 = 100272 # Variable c_int '100272'
GLU_NURBS_TEX_COORD_EXT = 100168 # Variable c_int '100168'
GLU_BEGIN = 100100 # Variable c_int '100100'
GLU_NURBS_ERROR37 = 100287 # Variable c_int '100287'
GLU_NURBS_ERROR32 = 100282 # Variable c_int '100282'
GLU_ERROR = 100103 # Variable c_int '100103'
GLU_TESS_EDGE_FLAG = 100104 # Variable c_int '100104'
GLU_NURBS_TESSELLATOR = 100161 # Variable c_int '100161'
GLU_NURBS_COLOR = 100167 # Variable c_int '100167'
GLU_INVALID_ENUM = 100900 # Variable c_int '100900'
GLU_TESS_VERTEX = 100101 # Variable c_int '100101'
GLU_NURBS_END_EXT = 100169 # Variable c_int '100169'
GLU_NURBS_NORMAL_EXT = 100166 # Variable c_int '100166'
GLU_NURBS_ERROR36 = 100286 # Variable c_int '100286'
GLU_NURBS_ERROR33 = 100283 # Variable c_int '100283'
GLU_NURBS_ERROR31 = 100281 # Variable c_int '100281'
GLU_INVALID_VALUE = 100901 # Variable c_int '100901'
GLU_EXTERIOR = 100123 # Variable c_int '100123'
GLU_NURBS_COLOR_EXT = 100167 # Variable c_int '100167'
GLU_SAMPLING_METHOD = 100205 # Variable c_int '100205'
class GLUnurbs(Structure):
    pass
GLUnurbs._fields_ = [
]
class GLUquadric(Structure):
    pass
GLUquadric._fields_ = [
]
class GLUtesselator(Structure):
    pass
GLUtesselator._fields_ = [
]
GLUnurbsObj = GLUnurbs
GLUquadricObj = GLUquadric
GLUtesselatorObj = GLUtesselator
GLUtriangulatorObj = GLUtesselator
gluBeginCurve = _libraries['libGLU.so.1'].gluBeginCurve
gluBeginCurve.restype = None
gluBeginCurve.argtypes = [POINTER(GLUnurbs)]
gluBeginPolygon = _libraries['libGLU.so.1'].gluBeginPolygon
gluBeginPolygon.restype = None
gluBeginPolygon.argtypes = [POINTER(GLUtesselator)]
gluBeginSurface = _libraries['libGLU.so.1'].gluBeginSurface
gluBeginSurface.restype = None
gluBeginSurface.argtypes = [POINTER(GLUnurbs)]
gluBeginTrim = _libraries['libGLU.so.1'].gluBeginTrim
gluBeginTrim.restype = None
gluBeginTrim.argtypes = [POINTER(GLUnurbs)]
GLint = c_int
GLenum = c_uint
GLsizei = c_int
gluBuild1DMipmapLevels = _libraries['libGLU.so.1'].gluBuild1DMipmapLevels
gluBuild1DMipmapLevels.restype = GLint
gluBuild1DMipmapLevels.argtypes = [GLenum, GLint, GLsizei, GLenum, GLenum, GLint, GLint, GLint, c_void_p]
gluBuild1DMipmaps = _libraries['libGLU.so.1'].gluBuild1DMipmaps
gluBuild1DMipmaps.restype = GLint
gluBuild1DMipmaps.argtypes = [GLenum, GLint, GLsizei, GLenum, GLenum, c_void_p]
gluBuild2DMipmapLevels = _libraries['libGLU.so.1'].gluBuild2DMipmapLevels
gluBuild2DMipmapLevels.restype = GLint
gluBuild2DMipmapLevels.argtypes = [GLenum, GLint, GLsizei, GLsizei, GLenum, GLenum, GLint, GLint, GLint, c_void_p]
gluBuild2DMipmaps = _libraries['libGLU.so.1'].gluBuild2DMipmaps
gluBuild2DMipmaps.restype = GLint
gluBuild2DMipmaps.argtypes = [GLenum, GLint, GLsizei, GLsizei, GLenum, GLenum, c_void_p]
gluBuild3DMipmapLevels = _libraries['libGLU.so.1'].gluBuild3DMipmapLevels
gluBuild3DMipmapLevels.restype = GLint
gluBuild3DMipmapLevels.argtypes = [GLenum, GLint, GLsizei, GLsizei, GLsizei, GLenum, GLenum, GLint, GLint, GLint, c_void_p]
gluBuild3DMipmaps = _libraries['libGLU.so.1'].gluBuild3DMipmaps
gluBuild3DMipmaps.restype = GLint
gluBuild3DMipmaps.argtypes = [GLenum, GLint, GLsizei, GLsizei, GLsizei, GLenum, GLenum, c_void_p]
GLboolean = c_ubyte
GLubyte = c_ubyte
gluCheckExtension = _libraries['libGLU.so.1'].gluCheckExtension
gluCheckExtension.restype = GLboolean
gluCheckExtension.argtypes = [POINTER(GLubyte), POINTER(GLubyte)]
GLdouble = c_double
gluCylinder = _libraries['libGLU.so.1'].gluCylinder
gluCylinder.restype = None
gluCylinder.argtypes = [POINTER(GLUquadric), GLdouble, GLdouble, GLdouble, GLint, GLint]
gluDeleteNurbsRenderer = _libraries['libGLU.so.1'].gluDeleteNurbsRenderer
gluDeleteNurbsRenderer.restype = None
gluDeleteNurbsRenderer.argtypes = [POINTER(GLUnurbs)]
gluDeleteQuadric = _libraries['libGLU.so.1'].gluDeleteQuadric
gluDeleteQuadric.restype = None
gluDeleteQuadric.argtypes = [POINTER(GLUquadric)]
gluDeleteTess = _libraries['libGLU.so.1'].gluDeleteTess
gluDeleteTess.restype = None
gluDeleteTess.argtypes = [POINTER(GLUtesselator)]
gluDisk = _libraries['libGLU.so.1'].gluDisk
gluDisk.restype = None
gluDisk.argtypes = [POINTER(GLUquadric), GLdouble, GLdouble, GLint, GLint]
gluEndCurve = _libraries['libGLU.so.1'].gluEndCurve
gluEndCurve.restype = None
gluEndCurve.argtypes = [POINTER(GLUnurbs)]
gluEndPolygon = _libraries['libGLU.so.1'].gluEndPolygon
gluEndPolygon.restype = None
gluEndPolygon.argtypes = [POINTER(GLUtesselator)]
gluEndSurface = _libraries['libGLU.so.1'].gluEndSurface
gluEndSurface.restype = None
gluEndSurface.argtypes = [POINTER(GLUnurbs)]
gluEndTrim = _libraries['libGLU.so.1'].gluEndTrim
gluEndTrim.restype = None
gluEndTrim.argtypes = [POINTER(GLUnurbs)]
gluErrorString = _libraries['libGLU.so.1'].gluErrorString
gluErrorString.restype = POINTER(GLubyte)
gluErrorString.argtypes = [GLenum]
GLfloat = c_float
gluGetNurbsProperty = _libraries['libGLU.so.1'].gluGetNurbsProperty
gluGetNurbsProperty.restype = None
gluGetNurbsProperty.argtypes = [POINTER(GLUnurbs), GLenum, POINTER(GLfloat)]
gluGetString = _libraries['libGLU.so.1'].gluGetString
gluGetString.restype = POINTER(GLubyte)
gluGetString.argtypes = [GLenum]
gluGetTessProperty = _libraries['libGLU.so.1'].gluGetTessProperty
gluGetTessProperty.restype = None
gluGetTessProperty.argtypes = [POINTER(GLUtesselator), GLenum, POINTER(GLdouble)]
gluLoadSamplingMatrices = _libraries['libGLU.so.1'].gluLoadSamplingMatrices
gluLoadSamplingMatrices.restype = None
gluLoadSamplingMatrices.argtypes = [POINTER(GLUnurbs), POINTER(GLfloat), POINTER(GLfloat), POINTER(GLint)]
gluLookAt = _libraries['libGLU.so.1'].gluLookAt
gluLookAt.restype = None
gluLookAt.argtypes = [GLdouble, GLdouble, GLdouble, GLdouble, GLdouble, GLdouble, GLdouble, GLdouble, GLdouble]
gluNewNurbsRenderer = _libraries['libGLU.so.1'].gluNewNurbsRenderer
gluNewNurbsRenderer.restype = POINTER(GLUnurbs)
gluNewNurbsRenderer.argtypes = []
gluNewQuadric = _libraries['libGLU.so.1'].gluNewQuadric
gluNewQuadric.restype = POINTER(GLUquadric)
gluNewQuadric.argtypes = []
gluNewTess = _libraries['libGLU.so.1'].gluNewTess
gluNewTess.restype = POINTER(GLUtesselator)
gluNewTess.argtypes = []
gluNextContour = _libraries['libGLU.so.1'].gluNextContour
gluNextContour.restype = None
gluNextContour.argtypes = [POINTER(GLUtesselator), GLenum]
_GLUfuncptr = CFUNCTYPE(None)
gluNurbsCallback = _libraries['libGLU.so.1'].gluNurbsCallback
gluNurbsCallback.restype = None
gluNurbsCallback.argtypes = [POINTER(GLUnurbs), GLenum, _GLUfuncptr]
GLvoid = None
gluNurbsCallbackData = _libraries['libGLU.so.1'].gluNurbsCallbackData
gluNurbsCallbackData.restype = None
gluNurbsCallbackData.argtypes = [POINTER(GLUnurbs), POINTER(GLvoid)]
gluNurbsCallbackDataEXT = _libraries['libGLU.so.1'].gluNurbsCallbackDataEXT
gluNurbsCallbackDataEXT.restype = None
gluNurbsCallbackDataEXT.argtypes = [POINTER(GLUnurbs), POINTER(GLvoid)]
gluNurbsCurve = _libraries['libGLU.so.1'].gluNurbsCurve
gluNurbsCurve.restype = None
gluNurbsCurve.argtypes = [POINTER(GLUnurbs), GLint, POINTER(GLfloat), GLint, POINTER(GLfloat), GLint, GLenum]
gluNurbsProperty = _libraries['libGLU.so.1'].gluNurbsProperty
gluNurbsProperty.restype = None
gluNurbsProperty.argtypes = [POINTER(GLUnurbs), GLenum, GLfloat]
gluNurbsSurface = _libraries['libGLU.so.1'].gluNurbsSurface
gluNurbsSurface.restype = None
gluNurbsSurface.argtypes = [POINTER(GLUnurbs), GLint, POINTER(GLfloat), GLint, POINTER(GLfloat), GLint, GLint, POINTER(GLfloat), GLint, GLint, GLenum]
gluOrtho2D = _libraries['libGLU.so.1'].gluOrtho2D
gluOrtho2D.restype = None
gluOrtho2D.argtypes = [GLdouble, GLdouble, GLdouble, GLdouble]
gluPartialDisk = _libraries['libGLU.so.1'].gluPartialDisk
gluPartialDisk.restype = None
gluPartialDisk.argtypes = [POINTER(GLUquadric), GLdouble, GLdouble, GLint, GLint, GLdouble, GLdouble]
gluPerspective = _libraries['libGLU.so.1'].gluPerspective
gluPerspective.restype = None
gluPerspective.argtypes = [GLdouble, GLdouble, GLdouble, GLdouble]
gluPickMatrix = _libraries['libGLU.so.1'].gluPickMatrix
gluPickMatrix.restype = None
gluPickMatrix.argtypes = [GLdouble, GLdouble, GLdouble, GLdouble, POINTER(GLint)]
gluProject = _libraries['libGLU.so.1'].gluProject
gluProject.restype = GLint
gluProject.argtypes = [GLdouble, GLdouble, GLdouble, POINTER(GLdouble), POINTER(GLdouble), POINTER(GLint), POINTER(GLdouble), POINTER(GLdouble), POINTER(GLdouble)]
gluPwlCurve = _libraries['libGLU.so.1'].gluPwlCurve
gluPwlCurve.restype = None
gluPwlCurve.argtypes = [POINTER(GLUnurbs), GLint, POINTER(GLfloat), GLint, GLenum]
gluQuadricCallback = _libraries['libGLU.so.1'].gluQuadricCallback
gluQuadricCallback.restype = None
gluQuadricCallback.argtypes = [POINTER(GLUquadric), GLenum, _GLUfuncptr]
gluQuadricDrawStyle = _libraries['libGLU.so.1'].gluQuadricDrawStyle
gluQuadricDrawStyle.restype = None
gluQuadricDrawStyle.argtypes = [POINTER(GLUquadric), GLenum]
gluQuadricNormals = _libraries['libGLU.so.1'].gluQuadricNormals
gluQuadricNormals.restype = None
gluQuadricNormals.argtypes = [POINTER(GLUquadric), GLenum]
gluQuadricOrientation = _libraries['libGLU.so.1'].gluQuadricOrientation
gluQuadricOrientation.restype = None
gluQuadricOrientation.argtypes = [POINTER(GLUquadric), GLenum]
gluQuadricTexture = _libraries['libGLU.so.1'].gluQuadricTexture
gluQuadricTexture.restype = None
gluQuadricTexture.argtypes = [POINTER(GLUquadric), GLboolean]
gluScaleImage = _libraries['libGLU.so.1'].gluScaleImage
gluScaleImage.restype = GLint
gluScaleImage.argtypes = [GLenum, GLsizei, GLsizei, GLenum, c_void_p, GLsizei, GLsizei, GLenum, POINTER(GLvoid)]
gluSphere = _libraries['libGLU.so.1'].gluSphere
gluSphere.restype = None
gluSphere.argtypes = [POINTER(GLUquadric), GLdouble, GLint, GLint]
gluTessBeginContour = _libraries['libGLU.so.1'].gluTessBeginContour
gluTessBeginContour.restype = None
gluTessBeginContour.argtypes = [POINTER(GLUtesselator)]
gluTessBeginPolygon = _libraries['libGLU.so.1'].gluTessBeginPolygon
gluTessBeginPolygon.restype = None
gluTessBeginPolygon.argtypes = [POINTER(GLUtesselator), POINTER(GLvoid)]
gluTessCallback = _libraries['libGLU.so.1'].gluTessCallback
gluTessCallback.restype = None
gluTessCallback.argtypes = [POINTER(GLUtesselator), GLenum, _GLUfuncptr]
gluTessEndContour = _libraries['libGLU.so.1'].gluTessEndContour
gluTessEndContour.restype = None
gluTessEndContour.argtypes = [POINTER(GLUtesselator)]
gluTessEndPolygon = _libraries['libGLU.so.1'].gluTessEndPolygon
gluTessEndPolygon.restype = None
gluTessEndPolygon.argtypes = [POINTER(GLUtesselator)]
gluTessNormal = _libraries['libGLU.so.1'].gluTessNormal
gluTessNormal.restype = None
gluTessNormal.argtypes = [POINTER(GLUtesselator), GLdouble, GLdouble, GLdouble]
gluTessProperty = _libraries['libGLU.so.1'].gluTessProperty
gluTessProperty.restype = None
gluTessProperty.argtypes = [POINTER(GLUtesselator), GLenum, GLdouble]
gluTessVertex = _libraries['libGLU.so.1'].gluTessVertex
gluTessVertex.restype = None
gluTessVertex.argtypes = [POINTER(GLUtesselator), POINTER(GLdouble), POINTER(GLvoid)]
gluUnProject = _libraries['libGLU.so.1'].gluUnProject
gluUnProject.restype = GLint
gluUnProject.argtypes = [GLdouble, GLdouble, GLdouble, POINTER(GLdouble), POINTER(GLdouble), POINTER(GLint), POINTER(GLdouble), POINTER(GLdouble), POINTER(GLdouble)]
gluUnProject4 = _libraries['libGLU.so.1'].gluUnProject4
gluUnProject4.restype = GLint
gluUnProject4.argtypes = [GLdouble, GLdouble, GLdouble, GLdouble, POINTER(GLdouble), POINTER(GLdouble), POINTER(GLint), GLdouble, GLdouble, POINTER(GLdouble), POINTER(GLdouble), POINTER(GLdouble), POINTER(GLdouble)]
__all__ = ['gluEndPolygon', 'GLU_TESS_ERROR1', 'GLU_TESS_ERROR2',
           'GLU_TESS_ERROR3', 'GLU_TESS_ERROR4', 'GLU_TESS_ERROR5',
           'GLU_TESS_ERROR6', 'GLU_TESS_ERROR7', 'GLU_TESS_ERROR8',
           'GLU_NURBS_ERROR25', 'GLU_NURBS_ERROR24',
           'GLU_TESS_VERTEX', 'GLU_TESS_WINDING_ABS_GEQ_TWO',
           'GLenum', 'gluNurbsProperty', 'GLU_OUTSIDE', 'GLU_LINE',
           'GLboolean', 'GLU_NURBS_ERROR', 'gluDeleteTess',
           'GLU_V_STEP', 'GLU_END', 'GLU_NURBS_COLOR_DATA',
           'GLU_MAP1_TRIM_2', 'GLU_NURBS_ERROR22', 'GLU_INSIDE',
           'GLU_OBJECT_PATH_LENGTH_EXT', 'GLU_SAMPLING_METHOD',
           'gluTessEndContour', 'GLU_NURBS_VERTEX_DATA_EXT',
           'GLU_TESS_ERROR', 'GLU_ERROR', 'GLU_NURBS_ERROR14',
           'GLU_NURBS_ERROR15', 'GLU_NURBS_ERROR16',
           'GLU_NURBS_ERROR17', 'GLU_NURBS_ERROR10',
           'GLU_NURBS_ERROR11', 'GLU_NURBS_ERROR12',
           'GLU_NURBS_ERROR13', 'GLU_TESS_TOLERANCE', 'gluNurbsCurve',
           'GLU_TESS_ERROR_DATA', 'GLU_NURBS_ERROR18',
           'GLU_NURBS_ERROR19', 'GLU_NONE', 'GLU_AUTO_LOAD_MATRIX',
           'gluLoadSamplingMatrices', 'gluCylinder', 'GLU_POINT',
           'gluDeleteQuadric', 'GLubyte', 'GLU_NURBS_ERROR4',
           'GLU_NURBS_BEGIN_DATA', 'GLU_INVALID_OPERATION',
           'GLUnurbs', 'GLU_NURBS_TEX_COORD_EXT', 'gluNewQuadric',
           'gluErrorString', 'GLU_NURBS_COLOR_DATA_EXT',
           'gluBuild1DMipmaps', 'GLU_EXTERIOR', 'gluNextContour',
           'GLU_TESS_WINDING_RULE', 'GLU_TESS_COMBINE', 'GLU_FILL',
           'GLU_NURBS_ERROR1', 'GLU_TESS_MISSING_BEGIN_CONTOUR',
           'GLU_NURBS_NORMAL_DATA', 'GLU_TESS_COORD_TOO_LARGE',
           'GLU_UNKNOWN', 'GLU_TESS_END', 'GLU_TESS_EDGE_FLAG_DATA',
           'gluTessBeginContour', 'gluNurbsSurface', 'GLsizei',
           'GLU_NURBS_ERROR6', 'GLU_NURBS_ERROR7',
           'GLU_TESS_COMBINE_DATA', 'GLU_NURBS_ERROR5',
           'GLU_NURBS_ERROR2', 'GLU_NURBS_ERROR3', 'GLU_EDGE_FLAG',
           'GLU_NURBS_MODE_EXT', 'gluLookAt',
           'gluBuild1DMipmapLevels', 'GLU_NURBS_ERROR8',
           'GLU_NURBS_ERROR9', 'GLU_EXT_object_space_tess',
           'gluBeginSurface', 'GLU_SMOOTH', 'GLU_TESS_EDGE_FLAG',
           'GLdouble', 'GLU_NURBS_MODE', '_GLUfuncptr', 'GLU_CCW',
           'GLU_OBJECT_PARAMETRIC_ERROR_EXT', 'gluBeginTrim',
           'gluTessBeginPolygon', 'GLU_NURBS_NORMAL_DATA_EXT',
           'GLU_CULLING', 'gluNurbsCallbackData',
           'GLU_NURBS_TESSELLATOR', 'GLU_VERSION',
           'GLU_TESS_MISSING_END_POLYGON', 'GLU_FALSE', 'GLU_CW',
           'GLU_INVALID_ENUM', 'GLU_TESS_VERTEX_DATA',
           'GLU_TESS_BEGIN_DATA', 'gluUnProject', 'GLU_VERTEX',
           'gluScaleImage', 'gluQuadricDrawStyle',
           'GLU_PARAMETRIC_ERROR', 'GLU_OUTLINE_POLYGON',
           'gluTessNormal', 'GLUnurbsObj',
           'GLU_OBJECT_PARAMETRIC_ERROR', 'GLU_FLAT',
           'gluPartialDisk', 'gluPwlCurve', 'GLUtriangulatorObj',
           'GLUtesselatorObj', 'gluQuadricNormals',
           'GLU_NURBS_RENDERER_EXT', 'GLU_NURBS_NORMAL',
           'gluEndSurface', 'gluTessEndPolygon', 'GLUquadric',
           'gluProject', 'GLU_MAP1_TRIM_3', 'gluSphere', 'GLvoid',
           'gluPickMatrix', 'gluEndCurve', 'GLU_NURBS_VERTEX',
           'gluTessProperty', 'gluTessVertex',
           'GLU_NURBS_TEXTURE_COORD_DATA', 'GLU_NURBS_ERROR29',
           'GLU_TESS_NEED_COMBINE_CALLBACK',
           'GLU_NURBS_TEXTURE_COORD', 'GLU_TRUE', 'GLU_NURBS_ERROR27',
           'GLU_NURBS_ERROR26', 'GLU_NURBS_ERROR21',
           'GLU_NURBS_ERROR20', 'GLU_NURBS_ERROR23',
           'GLU_OUTLINE_PATCH', 'GLU_TESS_WINDING_NEGATIVE',
           'gluBuild2DMipmaps', 'GLfloat',
           'GLU_INCOMPATIBLE_GL_VERSION', 'GLU_OBJECT_PATH_LENGTH',
           'gluNewTess', 'GLU_NURBS_VERTEX_EXT', 'GLUquadricObj',
           'gluBuild3DMipmapLevels', 'gluNurbsCallback',
           'GLU_TESS_BOUNDARY_ONLY', 'gluTessCallback',
           'gluNurbsCallbackDataEXT', 'GLint', 'GLU_PATH_LENGTH',
           'GLU_BEGIN', 'GLU_NURBS_END', 'gluBuild2DMipmapLevels',
           'gluQuadricOrientation', 'GLU_TESS_BEGIN',
           'GLU_SILHOUETTE', 'GLU_TESS_WINDING_ODD',
           'gluNewNurbsRenderer', 'gluBuild3DMipmaps',
           'GLU_NURBS_END_DATA_EXT', 'gluQuadricTexture',
           'GLU_U_STEP', 'GLU_NURBS_TESSELLATOR_EXT',
           'gluPerspective', 'GLUtesselator', 'GLU_NURBS_ERROR36',
           'GLU_NURBS_ERROR37', 'GLU_NURBS_ERROR34',
           'GLU_NURBS_ERROR35', 'GLU_NURBS_ERROR32',
           'GLU_NURBS_ERROR33', 'GLU_NURBS_ERROR30',
           'GLU_NURBS_RENDERER', 'GLU_SAMPLING_TOLERANCE',
           'GLU_TESS_MAX_COORD', 'GLU_NURBS_BEGIN_DATA_EXT',
           'GLU_TESS_WINDING_NONZERO',
           'GLU_TESS_MISSING_BEGIN_POLYGON', 'GLU_INVALID_VALUE',
           'GLU_NURBS_BEGIN_EXT', 'GLU_NURBS_COLOR',
           'GLU_TESS_WINDING_POSITIVE', 'GLU_NURBS_NORMAL_EXT',
           'gluDisk', 'GLU_EXTENSIONS', 'GLU_DOMAIN_DISTANCE',
           'GLU_OUT_OF_MEMORY', 'GLU_NURBS_ERROR31',
           'GLU_NURBS_VERTEX_DATA', 'gluBeginCurve',
           'gluCheckExtension', 'GLU_NURBS_COLOR_EXT',
           'gluUnProject4', 'GLU_NURBS_END_EXT',
           'gluDeleteNurbsRenderer', 'GLU_NURBS_BEGIN',
           'GLU_DISPLAY_MODE', 'GLU_TESS_MISSING_END_CONTOUR',
           'gluOrtho2D', 'GLU_INTERIOR', 'GLU_TESS_END_DATA',
           'GLU_NURBS_END_DATA', 'GLU_EXT_nurbs_tessellator',
           'gluBeginPolygon', 'gluEndTrim', 'gluGetTessProperty',
           'gluGetString', 'GLU_VERSION_1_1', 'GLU_VERSION_1_3',
           'GLU_VERSION_1_2', 'GLU_NURBS_TEX_COORD_DATA_EXT',
           'GLU_PARAMETRIC_TOLERANCE', 'gluGetNurbsProperty',
           'gluQuadricCallback', 'GLU_NURBS_ERROR28']
