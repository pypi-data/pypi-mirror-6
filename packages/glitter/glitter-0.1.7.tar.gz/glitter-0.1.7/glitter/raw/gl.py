from ctypes import *

_libraries = {}
_libraries['libGL.so.1'] = CDLL('libGL.so.1')
STRING = c_char_p


GL_FRAMEBUFFER_BINDING = 36006 # Variable c_int '36006'
GL_DRAW_FRAMEBUFFER_BINDING = GL_FRAMEBUFFER_BINDING # alias
GLenum = c_uint
GLboolean = c_ubyte
GLbitfield = c_uint
GLbyte = c_byte
GLshort = c_short
GLint = c_int
GLsizei = c_int
GLubyte = c_ubyte
GLushort = c_ushort
GLuint = c_uint
GLhalf = c_ushort
GLfloat = c_float
GLclampf = c_float
GLdouble = c_double
GLclampd = c_double
GLvoid = None
GLchar = c_char
ptrdiff_t = c_long
GLintptr = ptrdiff_t
GLsizeiptr = ptrdiff_t
GLintptrARB = ptrdiff_t
GLsizeiptrARB = ptrdiff_t
GLcharARB = c_char
GLhandleARB = c_uint
GLhalfARB = c_ushort
GLhalfNV = c_ushort
int64_t = c_int64
GLint64EXT = int64_t
uint64_t = c_uint64
GLuint64EXT = uint64_t
GLint64 = int64_t
GLuint64 = uint64_t
class __GLsync(Structure):
    pass
GLsync = POINTER(__GLsync)
GLvdpauSurfaceNV = GLintptr
glCullFace = _libraries['libGL.so.1'].glCullFace
glCullFace.restype = None
glCullFace.argtypes = [GLenum]
glFrontFace = _libraries['libGL.so.1'].glFrontFace
glFrontFace.restype = None
glFrontFace.argtypes = [GLenum]
glHint = _libraries['libGL.so.1'].glHint
glHint.restype = None
glHint.argtypes = [GLenum, GLenum]
glLineWidth = _libraries['libGL.so.1'].glLineWidth
glLineWidth.restype = None
glLineWidth.argtypes = [GLfloat]
glPointSize = _libraries['libGL.so.1'].glPointSize
glPointSize.restype = None
glPointSize.argtypes = [GLfloat]
glPolygonMode = _libraries['libGL.so.1'].glPolygonMode
glPolygonMode.restype = None
glPolygonMode.argtypes = [GLenum, GLenum]
glScissor = _libraries['libGL.so.1'].glScissor
glScissor.restype = None
glScissor.argtypes = [GLint, GLint, GLsizei, GLsizei]
glTexParameterf = _libraries['libGL.so.1'].glTexParameterf
glTexParameterf.restype = None
glTexParameterf.argtypes = [GLenum, GLenum, GLfloat]
glTexParameterfv = _libraries['libGL.so.1'].glTexParameterfv
glTexParameterfv.restype = None
glTexParameterfv.argtypes = [GLenum, GLenum, POINTER(GLfloat)]
glTexParameteri = _libraries['libGL.so.1'].glTexParameteri
glTexParameteri.restype = None
glTexParameteri.argtypes = [GLenum, GLenum, GLint]
glTexParameteriv = _libraries['libGL.so.1'].glTexParameteriv
glTexParameteriv.restype = None
glTexParameteriv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glTexImage1D = _libraries['libGL.so.1'].glTexImage1D
glTexImage1D.restype = None
glTexImage1D.argtypes = [GLenum, GLint, GLint, GLsizei, GLint, GLenum, GLenum, POINTER(GLvoid)]
glTexImage2D = _libraries['libGL.so.1'].glTexImage2D
glTexImage2D.restype = None
glTexImage2D.argtypes = [GLenum, GLint, GLint, GLsizei, GLsizei, GLint, GLenum, GLenum, POINTER(GLvoid)]
glDrawBuffer = _libraries['libGL.so.1'].glDrawBuffer
glDrawBuffer.restype = None
glDrawBuffer.argtypes = [GLenum]
glClear = _libraries['libGL.so.1'].glClear
glClear.restype = None
glClear.argtypes = [GLbitfield]
glClearColor = _libraries['libGL.so.1'].glClearColor
glClearColor.restype = None
glClearColor.argtypes = [GLclampf, GLclampf, GLclampf, GLclampf]
glClearStencil = _libraries['libGL.so.1'].glClearStencil
glClearStencil.restype = None
glClearStencil.argtypes = [GLint]
glClearDepth = _libraries['libGL.so.1'].glClearDepth
glClearDepth.restype = None
glClearDepth.argtypes = [GLclampd]
glStencilMask = _libraries['libGL.so.1'].glStencilMask
glStencilMask.restype = None
glStencilMask.argtypes = [GLuint]
glColorMask = _libraries['libGL.so.1'].glColorMask
glColorMask.restype = None
glColorMask.argtypes = [GLboolean, GLboolean, GLboolean, GLboolean]
glDepthMask = _libraries['libGL.so.1'].glDepthMask
glDepthMask.restype = None
glDepthMask.argtypes = [GLboolean]
glDisable = _libraries['libGL.so.1'].glDisable
glDisable.restype = None
glDisable.argtypes = [GLenum]
glEnable = _libraries['libGL.so.1'].glEnable
glEnable.restype = None
glEnable.argtypes = [GLenum]
glFinish = _libraries['libGL.so.1'].glFinish
glFinish.restype = None
glFinish.argtypes = []
glFlush = _libraries['libGL.so.1'].glFlush
glFlush.restype = None
glFlush.argtypes = []
glBlendFunc = _libraries['libGL.so.1'].glBlendFunc
glBlendFunc.restype = None
glBlendFunc.argtypes = [GLenum, GLenum]
glLogicOp = _libraries['libGL.so.1'].glLogicOp
glLogicOp.restype = None
glLogicOp.argtypes = [GLenum]
glStencilFunc = _libraries['libGL.so.1'].glStencilFunc
glStencilFunc.restype = None
glStencilFunc.argtypes = [GLenum, GLint, GLuint]
glStencilOp = _libraries['libGL.so.1'].glStencilOp
glStencilOp.restype = None
glStencilOp.argtypes = [GLenum, GLenum, GLenum]
glDepthFunc = _libraries['libGL.so.1'].glDepthFunc
glDepthFunc.restype = None
glDepthFunc.argtypes = [GLenum]
glPixelStoref = _libraries['libGL.so.1'].glPixelStoref
glPixelStoref.restype = None
glPixelStoref.argtypes = [GLenum, GLfloat]
glPixelStorei = _libraries['libGL.so.1'].glPixelStorei
glPixelStorei.restype = None
glPixelStorei.argtypes = [GLenum, GLint]
glReadBuffer = _libraries['libGL.so.1'].glReadBuffer
glReadBuffer.restype = None
glReadBuffer.argtypes = [GLenum]
glReadPixels = _libraries['libGL.so.1'].glReadPixels
glReadPixels.restype = None
glReadPixels.argtypes = [GLint, GLint, GLsizei, GLsizei, GLenum, GLenum, POINTER(GLvoid)]
glGetBooleanv = _libraries['libGL.so.1'].glGetBooleanv
glGetBooleanv.restype = None
glGetBooleanv.argtypes = [GLenum, POINTER(GLboolean)]
glGetDoublev = _libraries['libGL.so.1'].glGetDoublev
glGetDoublev.restype = None
glGetDoublev.argtypes = [GLenum, POINTER(GLdouble)]
glGetError = _libraries['libGL.so.1'].glGetError
glGetError.restype = GLenum
glGetError.argtypes = []
glGetFloatv = _libraries['libGL.so.1'].glGetFloatv
glGetFloatv.restype = None
glGetFloatv.argtypes = [GLenum, POINTER(GLfloat)]
glGetIntegerv = _libraries['libGL.so.1'].glGetIntegerv
glGetIntegerv.restype = None
glGetIntegerv.argtypes = [GLenum, POINTER(GLint)]
glGetString = _libraries['libGL.so.1'].glGetString
glGetString.restype = POINTER(GLubyte)
glGetString.argtypes = [GLenum]
glGetTexImage = _libraries['libGL.so.1'].glGetTexImage
glGetTexImage.restype = None
glGetTexImage.argtypes = [GLenum, GLint, GLenum, GLenum, POINTER(GLvoid)]
glGetTexParameterfv = _libraries['libGL.so.1'].glGetTexParameterfv
glGetTexParameterfv.restype = None
glGetTexParameterfv.argtypes = [GLenum, GLenum, POINTER(GLfloat)]
glGetTexParameteriv = _libraries['libGL.so.1'].glGetTexParameteriv
glGetTexParameteriv.restype = None
glGetTexParameteriv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glGetTexLevelParameterfv = _libraries['libGL.so.1'].glGetTexLevelParameterfv
glGetTexLevelParameterfv.restype = None
glGetTexLevelParameterfv.argtypes = [GLenum, GLint, GLenum, POINTER(GLfloat)]
glGetTexLevelParameteriv = _libraries['libGL.so.1'].glGetTexLevelParameteriv
glGetTexLevelParameteriv.restype = None
glGetTexLevelParameteriv.argtypes = [GLenum, GLint, GLenum, POINTER(GLint)]
glIsEnabled = _libraries['libGL.so.1'].glIsEnabled
glIsEnabled.restype = GLboolean
glIsEnabled.argtypes = [GLenum]
glDepthRange = _libraries['libGL.so.1'].glDepthRange
glDepthRange.restype = None
glDepthRange.argtypes = [GLclampd, GLclampd]
glViewport = _libraries['libGL.so.1'].glViewport
glViewport.restype = None
glViewport.argtypes = [GLint, GLint, GLsizei, GLsizei]
glDrawArrays = _libraries['libGL.so.1'].glDrawArrays
glDrawArrays.restype = None
glDrawArrays.argtypes = [GLenum, GLint, GLsizei]
glDrawElements = _libraries['libGL.so.1'].glDrawElements
glDrawElements.restype = None
glDrawElements.argtypes = [GLenum, GLsizei, GLenum, POINTER(GLvoid)]
glGetPointerv = _libraries['libGL.so.1'].glGetPointerv
glGetPointerv.restype = None
glGetPointerv.argtypes = [GLenum, POINTER(POINTER(GLvoid))]
glPolygonOffset = _libraries['libGL.so.1'].glPolygonOffset
glPolygonOffset.restype = None
glPolygonOffset.argtypes = [GLfloat, GLfloat]
glCopyTexImage1D = _libraries['libGL.so.1'].glCopyTexImage1D
glCopyTexImage1D.restype = None
glCopyTexImage1D.argtypes = [GLenum, GLint, GLenum, GLint, GLint, GLsizei, GLint]
glCopyTexImage2D = _libraries['libGL.so.1'].glCopyTexImage2D
glCopyTexImage2D.restype = None
glCopyTexImage2D.argtypes = [GLenum, GLint, GLenum, GLint, GLint, GLsizei, GLsizei, GLint]
glCopyTexSubImage1D = _libraries['libGL.so.1'].glCopyTexSubImage1D
glCopyTexSubImage1D.restype = None
glCopyTexSubImage1D.argtypes = [GLenum, GLint, GLint, GLint, GLint, GLsizei]
glCopyTexSubImage2D = _libraries['libGL.so.1'].glCopyTexSubImage2D
glCopyTexSubImage2D.restype = None
glCopyTexSubImage2D.argtypes = [GLenum, GLint, GLint, GLint, GLint, GLint, GLsizei, GLsizei]
glTexSubImage1D = _libraries['libGL.so.1'].glTexSubImage1D
glTexSubImage1D.restype = None
glTexSubImage1D.argtypes = [GLenum, GLint, GLint, GLsizei, GLenum, GLenum, POINTER(GLvoid)]
glTexSubImage2D = _libraries['libGL.so.1'].glTexSubImage2D
glTexSubImage2D.restype = None
glTexSubImage2D.argtypes = [GLenum, GLint, GLint, GLint, GLsizei, GLsizei, GLenum, GLenum, POINTER(GLvoid)]
glBindTexture = _libraries['libGL.so.1'].glBindTexture
glBindTexture.restype = None
glBindTexture.argtypes = [GLenum, GLuint]
glDeleteTextures = _libraries['libGL.so.1'].glDeleteTextures
glDeleteTextures.restype = None
glDeleteTextures.argtypes = [GLsizei, POINTER(GLuint)]
glGenTextures = _libraries['libGL.so.1'].glGenTextures
glGenTextures.restype = None
glGenTextures.argtypes = [GLsizei, POINTER(GLuint)]
glIsTexture = _libraries['libGL.so.1'].glIsTexture
glIsTexture.restype = GLboolean
glIsTexture.argtypes = [GLuint]
glBlendColor = _libraries['libGL.so.1'].glBlendColor
glBlendColor.restype = None
glBlendColor.argtypes = [GLclampf, GLclampf, GLclampf, GLclampf]
glBlendEquation = _libraries['libGL.so.1'].glBlendEquation
glBlendEquation.restype = None
glBlendEquation.argtypes = [GLenum]
glDrawRangeElements = _libraries['libGL.so.1'].glDrawRangeElements
glDrawRangeElements.restype = None
glDrawRangeElements.argtypes = [GLenum, GLuint, GLuint, GLsizei, GLenum, POINTER(GLvoid)]
glTexImage3D = _libraries['libGL.so.1'].glTexImage3D
glTexImage3D.restype = None
glTexImage3D.argtypes = [GLenum, GLint, GLint, GLsizei, GLsizei, GLsizei, GLint, GLenum, GLenum, POINTER(GLvoid)]
glTexSubImage3D = _libraries['libGL.so.1'].glTexSubImage3D
glTexSubImage3D.restype = None
glTexSubImage3D.argtypes = [GLenum, GLint, GLint, GLint, GLint, GLsizei, GLsizei, GLsizei, GLenum, GLenum, POINTER(GLvoid)]
glCopyTexSubImage3D = _libraries['libGL.so.1'].glCopyTexSubImage3D
glCopyTexSubImage3D.restype = None
glCopyTexSubImage3D.argtypes = [GLenum, GLint, GLint, GLint, GLint, GLint, GLint, GLsizei, GLsizei]
glActiveTexture = _libraries['libGL.so.1'].glActiveTexture
glActiveTexture.restype = None
glActiveTexture.argtypes = [GLenum]
glSampleCoverage = _libraries['libGL.so.1'].glSampleCoverage
glSampleCoverage.restype = None
glSampleCoverage.argtypes = [GLclampf, GLboolean]
glCompressedTexImage3D = _libraries['libGL.so.1'].glCompressedTexImage3D
glCompressedTexImage3D.restype = None
glCompressedTexImage3D.argtypes = [GLenum, GLint, GLenum, GLsizei, GLsizei, GLsizei, GLint, GLsizei, POINTER(GLvoid)]
glCompressedTexImage2D = _libraries['libGL.so.1'].glCompressedTexImage2D
glCompressedTexImage2D.restype = None
glCompressedTexImage2D.argtypes = [GLenum, GLint, GLenum, GLsizei, GLsizei, GLint, GLsizei, POINTER(GLvoid)]
glCompressedTexImage1D = _libraries['libGL.so.1'].glCompressedTexImage1D
glCompressedTexImage1D.restype = None
glCompressedTexImage1D.argtypes = [GLenum, GLint, GLenum, GLsizei, GLint, GLsizei, POINTER(GLvoid)]
glCompressedTexSubImage3D = _libraries['libGL.so.1'].glCompressedTexSubImage3D
glCompressedTexSubImage3D.restype = None
glCompressedTexSubImage3D.argtypes = [GLenum, GLint, GLint, GLint, GLint, GLsizei, GLsizei, GLsizei, GLenum, GLsizei, POINTER(GLvoid)]
glCompressedTexSubImage2D = _libraries['libGL.so.1'].glCompressedTexSubImage2D
glCompressedTexSubImage2D.restype = None
glCompressedTexSubImage2D.argtypes = [GLenum, GLint, GLint, GLint, GLsizei, GLsizei, GLenum, GLsizei, POINTER(GLvoid)]
glCompressedTexSubImage1D = _libraries['libGL.so.1'].glCompressedTexSubImage1D
glCompressedTexSubImage1D.restype = None
glCompressedTexSubImage1D.argtypes = [GLenum, GLint, GLint, GLsizei, GLenum, GLsizei, POINTER(GLvoid)]
glGetCompressedTexImage = _libraries['libGL.so.1'].glGetCompressedTexImage
glGetCompressedTexImage.restype = None
glGetCompressedTexImage.argtypes = [GLenum, GLint, POINTER(GLvoid)]
glBlendFuncSeparate = _libraries['libGL.so.1'].glBlendFuncSeparate
glBlendFuncSeparate.restype = None
glBlendFuncSeparate.argtypes = [GLenum, GLenum, GLenum, GLenum]
glMultiDrawArrays = _libraries['libGL.so.1'].glMultiDrawArrays
glMultiDrawArrays.restype = None
glMultiDrawArrays.argtypes = [GLenum, POINTER(GLint), POINTER(GLsizei), GLsizei]
glMultiDrawElements = _libraries['libGL.so.1'].glMultiDrawElements
glMultiDrawElements.restype = None
glMultiDrawElements.argtypes = [GLenum, POINTER(GLsizei), GLenum, POINTER(POINTER(GLvoid)), GLsizei]
glPointParameterf = _libraries['libGL.so.1'].glPointParameterf
glPointParameterf.restype = None
glPointParameterf.argtypes = [GLenum, GLfloat]
glPointParameterfv = _libraries['libGL.so.1'].glPointParameterfv
glPointParameterfv.restype = None
glPointParameterfv.argtypes = [GLenum, POINTER(GLfloat)]
glPointParameteri = _libraries['libGL.so.1'].glPointParameteri
glPointParameteri.restype = None
glPointParameteri.argtypes = [GLenum, GLint]
glPointParameteriv = _libraries['libGL.so.1'].glPointParameteriv
glPointParameteriv.restype = None
glPointParameteriv.argtypes = [GLenum, POINTER(GLint)]
glGenQueries = _libraries['libGL.so.1'].glGenQueries
glGenQueries.restype = None
glGenQueries.argtypes = [GLsizei, POINTER(GLuint)]
glDeleteQueries = _libraries['libGL.so.1'].glDeleteQueries
glDeleteQueries.restype = None
glDeleteQueries.argtypes = [GLsizei, POINTER(GLuint)]
glIsQuery = _libraries['libGL.so.1'].glIsQuery
glIsQuery.restype = GLboolean
glIsQuery.argtypes = [GLuint]
glBeginQuery = _libraries['libGL.so.1'].glBeginQuery
glBeginQuery.restype = None
glBeginQuery.argtypes = [GLenum, GLuint]
glEndQuery = _libraries['libGL.so.1'].glEndQuery
glEndQuery.restype = None
glEndQuery.argtypes = [GLenum]
glGetQueryiv = _libraries['libGL.so.1'].glGetQueryiv
glGetQueryiv.restype = None
glGetQueryiv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glGetQueryObjectiv = _libraries['libGL.so.1'].glGetQueryObjectiv
glGetQueryObjectiv.restype = None
glGetQueryObjectiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetQueryObjectuiv = _libraries['libGL.so.1'].glGetQueryObjectuiv
glGetQueryObjectuiv.restype = None
glGetQueryObjectuiv.argtypes = [GLuint, GLenum, POINTER(GLuint)]
glBindBuffer = _libraries['libGL.so.1'].glBindBuffer
glBindBuffer.restype = None
glBindBuffer.argtypes = [GLenum, GLuint]
glDeleteBuffers = _libraries['libGL.so.1'].glDeleteBuffers
glDeleteBuffers.restype = None
glDeleteBuffers.argtypes = [GLsizei, POINTER(GLuint)]
glGenBuffers = _libraries['libGL.so.1'].glGenBuffers
glGenBuffers.restype = None
glGenBuffers.argtypes = [GLsizei, POINTER(GLuint)]
glIsBuffer = _libraries['libGL.so.1'].glIsBuffer
glIsBuffer.restype = GLboolean
glIsBuffer.argtypes = [GLuint]
glBufferData = _libraries['libGL.so.1'].glBufferData
glBufferData.restype = None
glBufferData.argtypes = [GLenum, GLsizeiptr, POINTER(GLvoid), GLenum]
glBufferSubData = _libraries['libGL.so.1'].glBufferSubData
glBufferSubData.restype = None
glBufferSubData.argtypes = [GLenum, GLintptr, GLsizeiptr, POINTER(GLvoid)]
glGetBufferSubData = _libraries['libGL.so.1'].glGetBufferSubData
glGetBufferSubData.restype = None
glGetBufferSubData.argtypes = [GLenum, GLintptr, GLsizeiptr, POINTER(GLvoid)]
glMapBuffer = _libraries['libGL.so.1'].glMapBuffer
glMapBuffer.restype = POINTER(GLvoid)
glMapBuffer.argtypes = [GLenum, GLenum]
glUnmapBuffer = _libraries['libGL.so.1'].glUnmapBuffer
glUnmapBuffer.restype = GLboolean
glUnmapBuffer.argtypes = [GLenum]
glGetBufferParameteriv = _libraries['libGL.so.1'].glGetBufferParameteriv
glGetBufferParameteriv.restype = None
glGetBufferParameteriv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glGetBufferPointerv = _libraries['libGL.so.1'].glGetBufferPointerv
glGetBufferPointerv.restype = None
glGetBufferPointerv.argtypes = [GLenum, GLenum, POINTER(POINTER(GLvoid))]
glBlendEquationSeparate = _libraries['libGL.so.1'].glBlendEquationSeparate
glBlendEquationSeparate.restype = None
glBlendEquationSeparate.argtypes = [GLenum, GLenum]
glDrawBuffers = _libraries['libGL.so.1'].glDrawBuffers
glDrawBuffers.restype = None
glDrawBuffers.argtypes = [GLsizei, POINTER(GLenum)]
glStencilOpSeparate = _libraries['libGL.so.1'].glStencilOpSeparate
glStencilOpSeparate.restype = None
glStencilOpSeparate.argtypes = [GLenum, GLenum, GLenum, GLenum]
glStencilFuncSeparate = _libraries['libGL.so.1'].glStencilFuncSeparate
glStencilFuncSeparate.restype = None
glStencilFuncSeparate.argtypes = [GLenum, GLenum, GLint, GLuint]
glStencilMaskSeparate = _libraries['libGL.so.1'].glStencilMaskSeparate
glStencilMaskSeparate.restype = None
glStencilMaskSeparate.argtypes = [GLenum, GLuint]
glAttachShader = _libraries['libGL.so.1'].glAttachShader
glAttachShader.restype = None
glAttachShader.argtypes = [GLuint, GLuint]
glBindAttribLocation = _libraries['libGL.so.1'].glBindAttribLocation
glBindAttribLocation.restype = None
glBindAttribLocation.argtypes = [GLuint, GLuint, STRING]
glCompileShader = _libraries['libGL.so.1'].glCompileShader
glCompileShader.restype = None
glCompileShader.argtypes = [GLuint]
glCreateProgram = _libraries['libGL.so.1'].glCreateProgram
glCreateProgram.restype = GLuint
glCreateProgram.argtypes = []
glCreateShader = _libraries['libGL.so.1'].glCreateShader
glCreateShader.restype = GLuint
glCreateShader.argtypes = [GLenum]
glDeleteProgram = _libraries['libGL.so.1'].glDeleteProgram
glDeleteProgram.restype = None
glDeleteProgram.argtypes = [GLuint]
glDeleteShader = _libraries['libGL.so.1'].glDeleteShader
glDeleteShader.restype = None
glDeleteShader.argtypes = [GLuint]
glDetachShader = _libraries['libGL.so.1'].glDetachShader
glDetachShader.restype = None
glDetachShader.argtypes = [GLuint, GLuint]
glDisableVertexAttribArray = _libraries['libGL.so.1'].glDisableVertexAttribArray
glDisableVertexAttribArray.restype = None
glDisableVertexAttribArray.argtypes = [GLuint]
glEnableVertexAttribArray = _libraries['libGL.so.1'].glEnableVertexAttribArray
glEnableVertexAttribArray.restype = None
glEnableVertexAttribArray.argtypes = [GLuint]
glGetActiveAttrib = _libraries['libGL.so.1'].glGetActiveAttrib
glGetActiveAttrib.restype = None
glGetActiveAttrib.argtypes = [GLuint, GLuint, GLsizei, POINTER(GLsizei), POINTER(GLint), POINTER(GLenum), STRING]
glGetActiveUniform = _libraries['libGL.so.1'].glGetActiveUniform
glGetActiveUniform.restype = None
glGetActiveUniform.argtypes = [GLuint, GLuint, GLsizei, POINTER(GLsizei), POINTER(GLint), POINTER(GLenum), STRING]
glGetAttachedShaders = _libraries['libGL.so.1'].glGetAttachedShaders
glGetAttachedShaders.restype = None
glGetAttachedShaders.argtypes = [GLuint, GLsizei, POINTER(GLsizei), POINTER(GLuint)]
glGetAttribLocation = _libraries['libGL.so.1'].glGetAttribLocation
glGetAttribLocation.restype = GLint
glGetAttribLocation.argtypes = [GLuint, STRING]
glGetProgramiv = _libraries['libGL.so.1'].glGetProgramiv
glGetProgramiv.restype = None
glGetProgramiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetProgramInfoLog = _libraries['libGL.so.1'].glGetProgramInfoLog
glGetProgramInfoLog.restype = None
glGetProgramInfoLog.argtypes = [GLuint, GLsizei, POINTER(GLsizei), STRING]
glGetShaderiv = _libraries['libGL.so.1'].glGetShaderiv
glGetShaderiv.restype = None
glGetShaderiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetShaderInfoLog = _libraries['libGL.so.1'].glGetShaderInfoLog
glGetShaderInfoLog.restype = None
glGetShaderInfoLog.argtypes = [GLuint, GLsizei, POINTER(GLsizei), STRING]
glGetShaderSource = _libraries['libGL.so.1'].glGetShaderSource
glGetShaderSource.restype = None
glGetShaderSource.argtypes = [GLuint, GLsizei, POINTER(GLsizei), STRING]
glGetUniformLocation = _libraries['libGL.so.1'].glGetUniformLocation
glGetUniformLocation.restype = GLint
glGetUniformLocation.argtypes = [GLuint, STRING]
glGetUniformfv = _libraries['libGL.so.1'].glGetUniformfv
glGetUniformfv.restype = None
glGetUniformfv.argtypes = [GLuint, GLint, POINTER(GLfloat)]
glGetUniformiv = _libraries['libGL.so.1'].glGetUniformiv
glGetUniformiv.restype = None
glGetUniformiv.argtypes = [GLuint, GLint, POINTER(GLint)]
glGetVertexAttribdv = _libraries['libGL.so.1'].glGetVertexAttribdv
glGetVertexAttribdv.restype = None
glGetVertexAttribdv.argtypes = [GLuint, GLenum, POINTER(GLdouble)]
glGetVertexAttribfv = _libraries['libGL.so.1'].glGetVertexAttribfv
glGetVertexAttribfv.restype = None
glGetVertexAttribfv.argtypes = [GLuint, GLenum, POINTER(GLfloat)]
glGetVertexAttribiv = _libraries['libGL.so.1'].glGetVertexAttribiv
glGetVertexAttribiv.restype = None
glGetVertexAttribiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetVertexAttribPointerv = _libraries['libGL.so.1'].glGetVertexAttribPointerv
glGetVertexAttribPointerv.restype = None
glGetVertexAttribPointerv.argtypes = [GLuint, GLenum, POINTER(POINTER(GLvoid))]
glIsProgram = _libraries['libGL.so.1'].glIsProgram
glIsProgram.restype = GLboolean
glIsProgram.argtypes = [GLuint]
glIsShader = _libraries['libGL.so.1'].glIsShader
glIsShader.restype = GLboolean
glIsShader.argtypes = [GLuint]
glLinkProgram = _libraries['libGL.so.1'].glLinkProgram
glLinkProgram.restype = None
glLinkProgram.argtypes = [GLuint]
glShaderSource = _libraries['libGL.so.1'].glShaderSource
glShaderSource.restype = None
glShaderSource.argtypes = [GLuint, GLsizei, POINTER(STRING), POINTER(GLint)]
glUseProgram = _libraries['libGL.so.1'].glUseProgram
glUseProgram.restype = None
glUseProgram.argtypes = [GLuint]
glUniform1f = _libraries['libGL.so.1'].glUniform1f
glUniform1f.restype = None
glUniform1f.argtypes = [GLint, GLfloat]
glUniform2f = _libraries['libGL.so.1'].glUniform2f
glUniform2f.restype = None
glUniform2f.argtypes = [GLint, GLfloat, GLfloat]
glUniform3f = _libraries['libGL.so.1'].glUniform3f
glUniform3f.restype = None
glUniform3f.argtypes = [GLint, GLfloat, GLfloat, GLfloat]
glUniform4f = _libraries['libGL.so.1'].glUniform4f
glUniform4f.restype = None
glUniform4f.argtypes = [GLint, GLfloat, GLfloat, GLfloat, GLfloat]
glUniform1i = _libraries['libGL.so.1'].glUniform1i
glUniform1i.restype = None
glUniform1i.argtypes = [GLint, GLint]
glUniform2i = _libraries['libGL.so.1'].glUniform2i
glUniform2i.restype = None
glUniform2i.argtypes = [GLint, GLint, GLint]
glUniform3i = _libraries['libGL.so.1'].glUniform3i
glUniform3i.restype = None
glUniform3i.argtypes = [GLint, GLint, GLint, GLint]
glUniform4i = _libraries['libGL.so.1'].glUniform4i
glUniform4i.restype = None
glUniform4i.argtypes = [GLint, GLint, GLint, GLint, GLint]
glUniform1fv = _libraries['libGL.so.1'].glUniform1fv
glUniform1fv.restype = None
glUniform1fv.argtypes = [GLint, GLsizei, POINTER(GLfloat)]
glUniform2fv = _libraries['libGL.so.1'].glUniform2fv
glUniform2fv.restype = None
glUniform2fv.argtypes = [GLint, GLsizei, POINTER(GLfloat)]
glUniform3fv = _libraries['libGL.so.1'].glUniform3fv
glUniform3fv.restype = None
glUniform3fv.argtypes = [GLint, GLsizei, POINTER(GLfloat)]
glUniform4fv = _libraries['libGL.so.1'].glUniform4fv
glUniform4fv.restype = None
glUniform4fv.argtypes = [GLint, GLsizei, POINTER(GLfloat)]
glUniform1iv = _libraries['libGL.so.1'].glUniform1iv
glUniform1iv.restype = None
glUniform1iv.argtypes = [GLint, GLsizei, POINTER(GLint)]
glUniform2iv = _libraries['libGL.so.1'].glUniform2iv
glUniform2iv.restype = None
glUniform2iv.argtypes = [GLint, GLsizei, POINTER(GLint)]
glUniform3iv = _libraries['libGL.so.1'].glUniform3iv
glUniform3iv.restype = None
glUniform3iv.argtypes = [GLint, GLsizei, POINTER(GLint)]
glUniform4iv = _libraries['libGL.so.1'].glUniform4iv
glUniform4iv.restype = None
glUniform4iv.argtypes = [GLint, GLsizei, POINTER(GLint)]
glUniformMatrix2fv = _libraries['libGL.so.1'].glUniformMatrix2fv
glUniformMatrix2fv.restype = None
glUniformMatrix2fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix3fv = _libraries['libGL.so.1'].glUniformMatrix3fv
glUniformMatrix3fv.restype = None
glUniformMatrix3fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix4fv = _libraries['libGL.so.1'].glUniformMatrix4fv
glUniformMatrix4fv.restype = None
glUniformMatrix4fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glValidateProgram = _libraries['libGL.so.1'].glValidateProgram
glValidateProgram.restype = None
glValidateProgram.argtypes = [GLuint]
glVertexAttrib1d = _libraries['libGL.so.1'].glVertexAttrib1d
glVertexAttrib1d.restype = None
glVertexAttrib1d.argtypes = [GLuint, GLdouble]
glVertexAttrib1dv = _libraries['libGL.so.1'].glVertexAttrib1dv
glVertexAttrib1dv.restype = None
glVertexAttrib1dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttrib1f = _libraries['libGL.so.1'].glVertexAttrib1f
glVertexAttrib1f.restype = None
glVertexAttrib1f.argtypes = [GLuint, GLfloat]
glVertexAttrib1fv = _libraries['libGL.so.1'].glVertexAttrib1fv
glVertexAttrib1fv.restype = None
glVertexAttrib1fv.argtypes = [GLuint, POINTER(GLfloat)]
glVertexAttrib1s = _libraries['libGL.so.1'].glVertexAttrib1s
glVertexAttrib1s.restype = None
glVertexAttrib1s.argtypes = [GLuint, GLshort]
glVertexAttrib1sv = _libraries['libGL.so.1'].glVertexAttrib1sv
glVertexAttrib1sv.restype = None
glVertexAttrib1sv.argtypes = [GLuint, POINTER(GLshort)]
glVertexAttrib2d = _libraries['libGL.so.1'].glVertexAttrib2d
glVertexAttrib2d.restype = None
glVertexAttrib2d.argtypes = [GLuint, GLdouble, GLdouble]
glVertexAttrib2dv = _libraries['libGL.so.1'].glVertexAttrib2dv
glVertexAttrib2dv.restype = None
glVertexAttrib2dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttrib2f = _libraries['libGL.so.1'].glVertexAttrib2f
glVertexAttrib2f.restype = None
glVertexAttrib2f.argtypes = [GLuint, GLfloat, GLfloat]
glVertexAttrib2fv = _libraries['libGL.so.1'].glVertexAttrib2fv
glVertexAttrib2fv.restype = None
glVertexAttrib2fv.argtypes = [GLuint, POINTER(GLfloat)]
glVertexAttrib2s = _libraries['libGL.so.1'].glVertexAttrib2s
glVertexAttrib2s.restype = None
glVertexAttrib2s.argtypes = [GLuint, GLshort, GLshort]
glVertexAttrib2sv = _libraries['libGL.so.1'].glVertexAttrib2sv
glVertexAttrib2sv.restype = None
glVertexAttrib2sv.argtypes = [GLuint, POINTER(GLshort)]
glVertexAttrib3d = _libraries['libGL.so.1'].glVertexAttrib3d
glVertexAttrib3d.restype = None
glVertexAttrib3d.argtypes = [GLuint, GLdouble, GLdouble, GLdouble]
glVertexAttrib3dv = _libraries['libGL.so.1'].glVertexAttrib3dv
glVertexAttrib3dv.restype = None
glVertexAttrib3dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttrib3f = _libraries['libGL.so.1'].glVertexAttrib3f
glVertexAttrib3f.restype = None
glVertexAttrib3f.argtypes = [GLuint, GLfloat, GLfloat, GLfloat]
glVertexAttrib3fv = _libraries['libGL.so.1'].glVertexAttrib3fv
glVertexAttrib3fv.restype = None
glVertexAttrib3fv.argtypes = [GLuint, POINTER(GLfloat)]
glVertexAttrib3s = _libraries['libGL.so.1'].glVertexAttrib3s
glVertexAttrib3s.restype = None
glVertexAttrib3s.argtypes = [GLuint, GLshort, GLshort, GLshort]
glVertexAttrib3sv = _libraries['libGL.so.1'].glVertexAttrib3sv
glVertexAttrib3sv.restype = None
glVertexAttrib3sv.argtypes = [GLuint, POINTER(GLshort)]
glVertexAttrib4Nbv = _libraries['libGL.so.1'].glVertexAttrib4Nbv
glVertexAttrib4Nbv.restype = None
glVertexAttrib4Nbv.argtypes = [GLuint, POINTER(GLbyte)]
glVertexAttrib4Niv = _libraries['libGL.so.1'].glVertexAttrib4Niv
glVertexAttrib4Niv.restype = None
glVertexAttrib4Niv.argtypes = [GLuint, POINTER(GLint)]
glVertexAttrib4Nsv = _libraries['libGL.so.1'].glVertexAttrib4Nsv
glVertexAttrib4Nsv.restype = None
glVertexAttrib4Nsv.argtypes = [GLuint, POINTER(GLshort)]
glVertexAttrib4Nub = _libraries['libGL.so.1'].glVertexAttrib4Nub
glVertexAttrib4Nub.restype = None
glVertexAttrib4Nub.argtypes = [GLuint, GLubyte, GLubyte, GLubyte, GLubyte]
glVertexAttrib4Nubv = _libraries['libGL.so.1'].glVertexAttrib4Nubv
glVertexAttrib4Nubv.restype = None
glVertexAttrib4Nubv.argtypes = [GLuint, POINTER(GLubyte)]
glVertexAttrib4Nuiv = _libraries['libGL.so.1'].glVertexAttrib4Nuiv
glVertexAttrib4Nuiv.restype = None
glVertexAttrib4Nuiv.argtypes = [GLuint, POINTER(GLuint)]
glVertexAttrib4Nusv = _libraries['libGL.so.1'].glVertexAttrib4Nusv
glVertexAttrib4Nusv.restype = None
glVertexAttrib4Nusv.argtypes = [GLuint, POINTER(GLushort)]
glVertexAttrib4bv = _libraries['libGL.so.1'].glVertexAttrib4bv
glVertexAttrib4bv.restype = None
glVertexAttrib4bv.argtypes = [GLuint, POINTER(GLbyte)]
glVertexAttrib4d = _libraries['libGL.so.1'].glVertexAttrib4d
glVertexAttrib4d.restype = None
glVertexAttrib4d.argtypes = [GLuint, GLdouble, GLdouble, GLdouble, GLdouble]
glVertexAttrib4dv = _libraries['libGL.so.1'].glVertexAttrib4dv
glVertexAttrib4dv.restype = None
glVertexAttrib4dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttrib4f = _libraries['libGL.so.1'].glVertexAttrib4f
glVertexAttrib4f.restype = None
glVertexAttrib4f.argtypes = [GLuint, GLfloat, GLfloat, GLfloat, GLfloat]
glVertexAttrib4fv = _libraries['libGL.so.1'].glVertexAttrib4fv
glVertexAttrib4fv.restype = None
glVertexAttrib4fv.argtypes = [GLuint, POINTER(GLfloat)]
glVertexAttrib4iv = _libraries['libGL.so.1'].glVertexAttrib4iv
glVertexAttrib4iv.restype = None
glVertexAttrib4iv.argtypes = [GLuint, POINTER(GLint)]
glVertexAttrib4s = _libraries['libGL.so.1'].glVertexAttrib4s
glVertexAttrib4s.restype = None
glVertexAttrib4s.argtypes = [GLuint, GLshort, GLshort, GLshort, GLshort]
glVertexAttrib4sv = _libraries['libGL.so.1'].glVertexAttrib4sv
glVertexAttrib4sv.restype = None
glVertexAttrib4sv.argtypes = [GLuint, POINTER(GLshort)]
glVertexAttrib4ubv = _libraries['libGL.so.1'].glVertexAttrib4ubv
glVertexAttrib4ubv.restype = None
glVertexAttrib4ubv.argtypes = [GLuint, POINTER(GLubyte)]
glVertexAttrib4uiv = _libraries['libGL.so.1'].glVertexAttrib4uiv
glVertexAttrib4uiv.restype = None
glVertexAttrib4uiv.argtypes = [GLuint, POINTER(GLuint)]
glVertexAttrib4usv = _libraries['libGL.so.1'].glVertexAttrib4usv
glVertexAttrib4usv.restype = None
glVertexAttrib4usv.argtypes = [GLuint, POINTER(GLushort)]
glVertexAttribPointer = _libraries['libGL.so.1'].glVertexAttribPointer
glVertexAttribPointer.restype = None
glVertexAttribPointer.argtypes = [GLuint, GLint, GLenum, GLboolean, GLsizei, POINTER(GLvoid)]
glUniformMatrix2x3fv = _libraries['libGL.so.1'].glUniformMatrix2x3fv
glUniformMatrix2x3fv.restype = None
glUniformMatrix2x3fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix3x2fv = _libraries['libGL.so.1'].glUniformMatrix3x2fv
glUniformMatrix3x2fv.restype = None
glUniformMatrix3x2fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix2x4fv = _libraries['libGL.so.1'].glUniformMatrix2x4fv
glUniformMatrix2x4fv.restype = None
glUniformMatrix2x4fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix4x2fv = _libraries['libGL.so.1'].glUniformMatrix4x2fv
glUniformMatrix4x2fv.restype = None
glUniformMatrix4x2fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix3x4fv = _libraries['libGL.so.1'].glUniformMatrix3x4fv
glUniformMatrix3x4fv.restype = None
glUniformMatrix3x4fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glUniformMatrix4x3fv = _libraries['libGL.so.1'].glUniformMatrix4x3fv
glUniformMatrix4x3fv.restype = None
glUniformMatrix4x3fv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glColorMaski = _libraries['libGL.so.1'].glColorMaski
glColorMaski.restype = None
glColorMaski.argtypes = [GLuint, GLboolean, GLboolean, GLboolean, GLboolean]
glGetBooleani_v = _libraries['libGL.so.1'].glGetBooleani_v
glGetBooleani_v.restype = None
glGetBooleani_v.argtypes = [GLenum, GLuint, POINTER(GLboolean)]
glGetIntegeri_v = _libraries['libGL.so.1'].glGetIntegeri_v
glGetIntegeri_v.restype = None
glGetIntegeri_v.argtypes = [GLenum, GLuint, POINTER(GLint)]
glEnablei = _libraries['libGL.so.1'].glEnablei
glEnablei.restype = None
glEnablei.argtypes = [GLenum, GLuint]
glDisablei = _libraries['libGL.so.1'].glDisablei
glDisablei.restype = None
glDisablei.argtypes = [GLenum, GLuint]
glIsEnabledi = _libraries['libGL.so.1'].glIsEnabledi
glIsEnabledi.restype = GLboolean
glIsEnabledi.argtypes = [GLenum, GLuint]
glBeginTransformFeedback = _libraries['libGL.so.1'].glBeginTransformFeedback
glBeginTransformFeedback.restype = None
glBeginTransformFeedback.argtypes = [GLenum]
glEndTransformFeedback = _libraries['libGL.so.1'].glEndTransformFeedback
glEndTransformFeedback.restype = None
glEndTransformFeedback.argtypes = []
glBindBufferRange = _libraries['libGL.so.1'].glBindBufferRange
glBindBufferRange.restype = None
glBindBufferRange.argtypes = [GLenum, GLuint, GLuint, GLintptr, GLsizeiptr]
glBindBufferBase = _libraries['libGL.so.1'].glBindBufferBase
glBindBufferBase.restype = None
glBindBufferBase.argtypes = [GLenum, GLuint, GLuint]
glTransformFeedbackVaryings = _libraries['libGL.so.1'].glTransformFeedbackVaryings
glTransformFeedbackVaryings.restype = None
glTransformFeedbackVaryings.argtypes = [GLuint, GLsizei, POINTER(STRING), GLenum]
glGetTransformFeedbackVarying = _libraries['libGL.so.1'].glGetTransformFeedbackVarying
glGetTransformFeedbackVarying.restype = None
glGetTransformFeedbackVarying.argtypes = [GLuint, GLuint, GLsizei, POINTER(GLsizei), POINTER(GLsizei), POINTER(GLenum), STRING]
glClampColor = _libraries['libGL.so.1'].glClampColor
glClampColor.restype = None
glClampColor.argtypes = [GLenum, GLenum]
glBeginConditionalRender = _libraries['libGL.so.1'].glBeginConditionalRender
glBeginConditionalRender.restype = None
glBeginConditionalRender.argtypes = [GLuint, GLenum]
glEndConditionalRender = _libraries['libGL.so.1'].glEndConditionalRender
glEndConditionalRender.restype = None
glEndConditionalRender.argtypes = []
glVertexAttribIPointer = _libraries['libGL.so.1'].glVertexAttribIPointer
glVertexAttribIPointer.restype = None
glVertexAttribIPointer.argtypes = [GLuint, GLint, GLenum, GLsizei, POINTER(GLvoid)]
glGetVertexAttribIiv = _libraries['libGL.so.1'].glGetVertexAttribIiv
glGetVertexAttribIiv.restype = None
glGetVertexAttribIiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetVertexAttribIuiv = _libraries['libGL.so.1'].glGetVertexAttribIuiv
glGetVertexAttribIuiv.restype = None
glGetVertexAttribIuiv.argtypes = [GLuint, GLenum, POINTER(GLuint)]
glVertexAttribI1i = _libraries['libGL.so.1'].glVertexAttribI1i
glVertexAttribI1i.restype = None
glVertexAttribI1i.argtypes = [GLuint, GLint]
glVertexAttribI2i = _libraries['libGL.so.1'].glVertexAttribI2i
glVertexAttribI2i.restype = None
glVertexAttribI2i.argtypes = [GLuint, GLint, GLint]
glVertexAttribI3i = _libraries['libGL.so.1'].glVertexAttribI3i
glVertexAttribI3i.restype = None
glVertexAttribI3i.argtypes = [GLuint, GLint, GLint, GLint]
glVertexAttribI4i = _libraries['libGL.so.1'].glVertexAttribI4i
glVertexAttribI4i.restype = None
glVertexAttribI4i.argtypes = [GLuint, GLint, GLint, GLint, GLint]
glVertexAttribI1ui = _libraries['libGL.so.1'].glVertexAttribI1ui
glVertexAttribI1ui.restype = None
glVertexAttribI1ui.argtypes = [GLuint, GLuint]
glVertexAttribI2ui = _libraries['libGL.so.1'].glVertexAttribI2ui
glVertexAttribI2ui.restype = None
glVertexAttribI2ui.argtypes = [GLuint, GLuint, GLuint]
glVertexAttribI3ui = _libraries['libGL.so.1'].glVertexAttribI3ui
glVertexAttribI3ui.restype = None
glVertexAttribI3ui.argtypes = [GLuint, GLuint, GLuint, GLuint]
glVertexAttribI4ui = _libraries['libGL.so.1'].glVertexAttribI4ui
glVertexAttribI4ui.restype = None
glVertexAttribI4ui.argtypes = [GLuint, GLuint, GLuint, GLuint, GLuint]
glVertexAttribI1iv = _libraries['libGL.so.1'].glVertexAttribI1iv
glVertexAttribI1iv.restype = None
glVertexAttribI1iv.argtypes = [GLuint, POINTER(GLint)]
glVertexAttribI2iv = _libraries['libGL.so.1'].glVertexAttribI2iv
glVertexAttribI2iv.restype = None
glVertexAttribI2iv.argtypes = [GLuint, POINTER(GLint)]
glVertexAttribI3iv = _libraries['libGL.so.1'].glVertexAttribI3iv
glVertexAttribI3iv.restype = None
glVertexAttribI3iv.argtypes = [GLuint, POINTER(GLint)]
glVertexAttribI4iv = _libraries['libGL.so.1'].glVertexAttribI4iv
glVertexAttribI4iv.restype = None
glVertexAttribI4iv.argtypes = [GLuint, POINTER(GLint)]
glVertexAttribI1uiv = _libraries['libGL.so.1'].glVertexAttribI1uiv
glVertexAttribI1uiv.restype = None
glVertexAttribI1uiv.argtypes = [GLuint, POINTER(GLuint)]
glVertexAttribI2uiv = _libraries['libGL.so.1'].glVertexAttribI2uiv
glVertexAttribI2uiv.restype = None
glVertexAttribI2uiv.argtypes = [GLuint, POINTER(GLuint)]
glVertexAttribI3uiv = _libraries['libGL.so.1'].glVertexAttribI3uiv
glVertexAttribI3uiv.restype = None
glVertexAttribI3uiv.argtypes = [GLuint, POINTER(GLuint)]
glVertexAttribI4uiv = _libraries['libGL.so.1'].glVertexAttribI4uiv
glVertexAttribI4uiv.restype = None
glVertexAttribI4uiv.argtypes = [GLuint, POINTER(GLuint)]
glVertexAttribI4bv = _libraries['libGL.so.1'].glVertexAttribI4bv
glVertexAttribI4bv.restype = None
glVertexAttribI4bv.argtypes = [GLuint, POINTER(GLbyte)]
glVertexAttribI4sv = _libraries['libGL.so.1'].glVertexAttribI4sv
glVertexAttribI4sv.restype = None
glVertexAttribI4sv.argtypes = [GLuint, POINTER(GLshort)]
glVertexAttribI4ubv = _libraries['libGL.so.1'].glVertexAttribI4ubv
glVertexAttribI4ubv.restype = None
glVertexAttribI4ubv.argtypes = [GLuint, POINTER(GLubyte)]
glVertexAttribI4usv = _libraries['libGL.so.1'].glVertexAttribI4usv
glVertexAttribI4usv.restype = None
glVertexAttribI4usv.argtypes = [GLuint, POINTER(GLushort)]
glGetUniformuiv = _libraries['libGL.so.1'].glGetUniformuiv
glGetUniformuiv.restype = None
glGetUniformuiv.argtypes = [GLuint, GLint, POINTER(GLuint)]
glBindFragDataLocation = _libraries['libGL.so.1'].glBindFragDataLocation
glBindFragDataLocation.restype = None
glBindFragDataLocation.argtypes = [GLuint, GLuint, STRING]
glGetFragDataLocation = _libraries['libGL.so.1'].glGetFragDataLocation
glGetFragDataLocation.restype = GLint
glGetFragDataLocation.argtypes = [GLuint, STRING]
glUniform1ui = _libraries['libGL.so.1'].glUniform1ui
glUniform1ui.restype = None
glUniform1ui.argtypes = [GLint, GLuint]
glUniform2ui = _libraries['libGL.so.1'].glUniform2ui
glUniform2ui.restype = None
glUniform2ui.argtypes = [GLint, GLuint, GLuint]
glUniform3ui = _libraries['libGL.so.1'].glUniform3ui
glUniform3ui.restype = None
glUniform3ui.argtypes = [GLint, GLuint, GLuint, GLuint]
glUniform4ui = _libraries['libGL.so.1'].glUniform4ui
glUniform4ui.restype = None
glUniform4ui.argtypes = [GLint, GLuint, GLuint, GLuint, GLuint]
glUniform1uiv = _libraries['libGL.so.1'].glUniform1uiv
glUniform1uiv.restype = None
glUniform1uiv.argtypes = [GLint, GLsizei, POINTER(GLuint)]
glUniform2uiv = _libraries['libGL.so.1'].glUniform2uiv
glUniform2uiv.restype = None
glUniform2uiv.argtypes = [GLint, GLsizei, POINTER(GLuint)]
glUniform3uiv = _libraries['libGL.so.1'].glUniform3uiv
glUniform3uiv.restype = None
glUniform3uiv.argtypes = [GLint, GLsizei, POINTER(GLuint)]
glUniform4uiv = _libraries['libGL.so.1'].glUniform4uiv
glUniform4uiv.restype = None
glUniform4uiv.argtypes = [GLint, GLsizei, POINTER(GLuint)]
glTexParameterIiv = _libraries['libGL.so.1'].glTexParameterIiv
glTexParameterIiv.restype = None
glTexParameterIiv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glTexParameterIuiv = _libraries['libGL.so.1'].glTexParameterIuiv
glTexParameterIuiv.restype = None
glTexParameterIuiv.argtypes = [GLenum, GLenum, POINTER(GLuint)]
glGetTexParameterIiv = _libraries['libGL.so.1'].glGetTexParameterIiv
glGetTexParameterIiv.restype = None
glGetTexParameterIiv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glGetTexParameterIuiv = _libraries['libGL.so.1'].glGetTexParameterIuiv
glGetTexParameterIuiv.restype = None
glGetTexParameterIuiv.argtypes = [GLenum, GLenum, POINTER(GLuint)]
glClearBufferiv = _libraries['libGL.so.1'].glClearBufferiv
glClearBufferiv.restype = None
glClearBufferiv.argtypes = [GLenum, GLint, POINTER(GLint)]
glClearBufferuiv = _libraries['libGL.so.1'].glClearBufferuiv
glClearBufferuiv.restype = None
glClearBufferuiv.argtypes = [GLenum, GLint, POINTER(GLuint)]
glClearBufferfv = _libraries['libGL.so.1'].glClearBufferfv
glClearBufferfv.restype = None
glClearBufferfv.argtypes = [GLenum, GLint, POINTER(GLfloat)]
glClearBufferfi = _libraries['libGL.so.1'].glClearBufferfi
glClearBufferfi.restype = None
glClearBufferfi.argtypes = [GLenum, GLint, GLfloat, GLint]
glGetStringi = _libraries['libGL.so.1'].glGetStringi
glGetStringi.restype = POINTER(GLubyte)
glGetStringi.argtypes = [GLenum, GLuint]
glDrawArraysInstanced = _libraries['libGL.so.1'].glDrawArraysInstanced
glDrawArraysInstanced.restype = None
glDrawArraysInstanced.argtypes = [GLenum, GLint, GLsizei, GLsizei]
glDrawElementsInstanced = _libraries['libGL.so.1'].glDrawElementsInstanced
glDrawElementsInstanced.restype = None
glDrawElementsInstanced.argtypes = [GLenum, GLsizei, GLenum, POINTER(GLvoid), GLsizei]
glTexBuffer = _libraries['libGL.so.1'].glTexBuffer
glTexBuffer.restype = None
glTexBuffer.argtypes = [GLenum, GLenum, GLuint]
glPrimitiveRestartIndex = _libraries['libGL.so.1'].glPrimitiveRestartIndex
glPrimitiveRestartIndex.restype = None
glPrimitiveRestartIndex.argtypes = [GLuint]
glGetInteger64i_v = _libraries['libGL.so.1'].glGetInteger64i_v
glGetInteger64i_v.restype = None
glGetInteger64i_v.argtypes = [GLenum, GLuint, POINTER(GLint64)]
glGetBufferParameteri64v = _libraries['libGL.so.1'].glGetBufferParameteri64v
glGetBufferParameteri64v.restype = None
glGetBufferParameteri64v.argtypes = [GLenum, GLenum, POINTER(GLint64)]
glFramebufferTexture = _libraries['libGL.so.1'].glFramebufferTexture
glFramebufferTexture.restype = None
glFramebufferTexture.argtypes = [GLenum, GLenum, GLuint, GLint]
glVertexAttribDivisor = _libraries['libGL.so.1'].glVertexAttribDivisor
glVertexAttribDivisor.restype = None
glVertexAttribDivisor.argtypes = [GLuint, GLuint]
glMinSampleShading = _libraries['libGL.so.1'].glMinSampleShading
glMinSampleShading.restype = None
glMinSampleShading.argtypes = [GLclampf]
glBlendEquationi = _libraries['libGL.so.1'].glBlendEquationi
glBlendEquationi.restype = None
glBlendEquationi.argtypes = [GLuint, GLenum]
glBlendEquationSeparatei = _libraries['libGL.so.1'].glBlendEquationSeparatei
glBlendEquationSeparatei.restype = None
glBlendEquationSeparatei.argtypes = [GLuint, GLenum, GLenum]
glBlendFunci = _libraries['libGL.so.1'].glBlendFunci
glBlendFunci.restype = None
glBlendFunci.argtypes = [GLuint, GLenum, GLenum]
glBlendFuncSeparatei = _libraries['libGL.so.1'].glBlendFuncSeparatei
glBlendFuncSeparatei.restype = None
glBlendFuncSeparatei.argtypes = [GLuint, GLenum, GLenum, GLenum, GLenum]
glIsRenderbuffer = _libraries['libGL.so.1'].glIsRenderbuffer
glIsRenderbuffer.restype = GLboolean
glIsRenderbuffer.argtypes = [GLuint]
glBindRenderbuffer = _libraries['libGL.so.1'].glBindRenderbuffer
glBindRenderbuffer.restype = None
glBindRenderbuffer.argtypes = [GLenum, GLuint]
glDeleteRenderbuffers = _libraries['libGL.so.1'].glDeleteRenderbuffers
glDeleteRenderbuffers.restype = None
glDeleteRenderbuffers.argtypes = [GLsizei, POINTER(GLuint)]
glGenRenderbuffers = _libraries['libGL.so.1'].glGenRenderbuffers
glGenRenderbuffers.restype = None
glGenRenderbuffers.argtypes = [GLsizei, POINTER(GLuint)]
glRenderbufferStorage = _libraries['libGL.so.1'].glRenderbufferStorage
glRenderbufferStorage.restype = None
glRenderbufferStorage.argtypes = [GLenum, GLenum, GLsizei, GLsizei]
glGetRenderbufferParameteriv = _libraries['libGL.so.1'].glGetRenderbufferParameteriv
glGetRenderbufferParameteriv.restype = None
glGetRenderbufferParameteriv.argtypes = [GLenum, GLenum, POINTER(GLint)]
glIsFramebuffer = _libraries['libGL.so.1'].glIsFramebuffer
glIsFramebuffer.restype = GLboolean
glIsFramebuffer.argtypes = [GLuint]
glBindFramebuffer = _libraries['libGL.so.1'].glBindFramebuffer
glBindFramebuffer.restype = None
glBindFramebuffer.argtypes = [GLenum, GLuint]
glDeleteFramebuffers = _libraries['libGL.so.1'].glDeleteFramebuffers
glDeleteFramebuffers.restype = None
glDeleteFramebuffers.argtypes = [GLsizei, POINTER(GLuint)]
glGenFramebuffers = _libraries['libGL.so.1'].glGenFramebuffers
glGenFramebuffers.restype = None
glGenFramebuffers.argtypes = [GLsizei, POINTER(GLuint)]
glCheckFramebufferStatus = _libraries['libGL.so.1'].glCheckFramebufferStatus
glCheckFramebufferStatus.restype = GLenum
glCheckFramebufferStatus.argtypes = [GLenum]
glFramebufferTexture1D = _libraries['libGL.so.1'].glFramebufferTexture1D
glFramebufferTexture1D.restype = None
glFramebufferTexture1D.argtypes = [GLenum, GLenum, GLenum, GLuint, GLint]
glFramebufferTexture2D = _libraries['libGL.so.1'].glFramebufferTexture2D
glFramebufferTexture2D.restype = None
glFramebufferTexture2D.argtypes = [GLenum, GLenum, GLenum, GLuint, GLint]
glFramebufferTexture3D = _libraries['libGL.so.1'].glFramebufferTexture3D
glFramebufferTexture3D.restype = None
glFramebufferTexture3D.argtypes = [GLenum, GLenum, GLenum, GLuint, GLint, GLint]
glFramebufferRenderbuffer = _libraries['libGL.so.1'].glFramebufferRenderbuffer
glFramebufferRenderbuffer.restype = None
glFramebufferRenderbuffer.argtypes = [GLenum, GLenum, GLenum, GLuint]
glGetFramebufferAttachmentParameteriv = _libraries['libGL.so.1'].glGetFramebufferAttachmentParameteriv
glGetFramebufferAttachmentParameteriv.restype = None
glGetFramebufferAttachmentParameteriv.argtypes = [GLenum, GLenum, GLenum, POINTER(GLint)]
glGenerateMipmap = _libraries['libGL.so.1'].glGenerateMipmap
glGenerateMipmap.restype = None
glGenerateMipmap.argtypes = [GLenum]
glBlitFramebuffer = _libraries['libGL.so.1'].glBlitFramebuffer
glBlitFramebuffer.restype = None
glBlitFramebuffer.argtypes = [GLint, GLint, GLint, GLint, GLint, GLint, GLint, GLint, GLbitfield, GLenum]
glRenderbufferStorageMultisample = _libraries['libGL.so.1'].glRenderbufferStorageMultisample
glRenderbufferStorageMultisample.restype = None
glRenderbufferStorageMultisample.argtypes = [GLenum, GLsizei, GLenum, GLsizei, GLsizei]
glFramebufferTextureLayer = _libraries['libGL.so.1'].glFramebufferTextureLayer
glFramebufferTextureLayer.restype = None
glFramebufferTextureLayer.argtypes = [GLenum, GLenum, GLuint, GLint, GLint]
glMapBufferRange = _libraries['libGL.so.1'].glMapBufferRange
glMapBufferRange.restype = POINTER(GLvoid)
glMapBufferRange.argtypes = [GLenum, GLintptr, GLsizeiptr, GLbitfield]
glFlushMappedBufferRange = _libraries['libGL.so.1'].glFlushMappedBufferRange
glFlushMappedBufferRange.restype = None
glFlushMappedBufferRange.argtypes = [GLenum, GLintptr, GLsizeiptr]
glBindVertexArray = _libraries['libGL.so.1'].glBindVertexArray
glBindVertexArray.restype = None
glBindVertexArray.argtypes = [GLuint]
glDeleteVertexArrays = _libraries['libGL.so.1'].glDeleteVertexArrays
glDeleteVertexArrays.restype = None
glDeleteVertexArrays.argtypes = [GLsizei, POINTER(GLuint)]
glGenVertexArrays = _libraries['libGL.so.1'].glGenVertexArrays
glGenVertexArrays.restype = None
glGenVertexArrays.argtypes = [GLsizei, POINTER(GLuint)]
glIsVertexArray = _libraries['libGL.so.1'].glIsVertexArray
glIsVertexArray.restype = GLboolean
glIsVertexArray.argtypes = [GLuint]
glGetUniformIndices = _libraries['libGL.so.1'].glGetUniformIndices
glGetUniformIndices.restype = None
glGetUniformIndices.argtypes = [GLuint, GLsizei, POINTER(STRING), POINTER(GLuint)]
glGetActiveUniformsiv = _libraries['libGL.so.1'].glGetActiveUniformsiv
glGetActiveUniformsiv.restype = None
glGetActiveUniformsiv.argtypes = [GLuint, GLsizei, POINTER(GLuint), GLenum, POINTER(GLint)]
glGetActiveUniformName = _libraries['libGL.so.1'].glGetActiveUniformName
glGetActiveUniformName.restype = None
glGetActiveUniformName.argtypes = [GLuint, GLuint, GLsizei, POINTER(GLsizei), STRING]
glGetUniformBlockIndex = _libraries['libGL.so.1'].glGetUniformBlockIndex
glGetUniformBlockIndex.restype = GLuint
glGetUniformBlockIndex.argtypes = [GLuint, STRING]
glGetActiveUniformBlockiv = _libraries['libGL.so.1'].glGetActiveUniformBlockiv
glGetActiveUniformBlockiv.restype = None
glGetActiveUniformBlockiv.argtypes = [GLuint, GLuint, GLenum, POINTER(GLint)]
glGetActiveUniformBlockName = _libraries['libGL.so.1'].glGetActiveUniformBlockName
glGetActiveUniformBlockName.restype = None
glGetActiveUniformBlockName.argtypes = [GLuint, GLuint, GLsizei, POINTER(GLsizei), STRING]
glUniformBlockBinding = _libraries['libGL.so.1'].glUniformBlockBinding
glUniformBlockBinding.restype = None
glUniformBlockBinding.argtypes = [GLuint, GLuint, GLuint]
glCopyBufferSubData = _libraries['libGL.so.1'].glCopyBufferSubData
glCopyBufferSubData.restype = None
glCopyBufferSubData.argtypes = [GLenum, GLenum, GLintptr, GLintptr, GLsizeiptr]
glDrawElementsBaseVertex = _libraries['libGL.so.1'].glDrawElementsBaseVertex
glDrawElementsBaseVertex.restype = None
glDrawElementsBaseVertex.argtypes = [GLenum, GLsizei, GLenum, POINTER(GLvoid), GLint]
glDrawRangeElementsBaseVertex = _libraries['libGL.so.1'].glDrawRangeElementsBaseVertex
glDrawRangeElementsBaseVertex.restype = None
glDrawRangeElementsBaseVertex.argtypes = [GLenum, GLuint, GLuint, GLsizei, GLenum, POINTER(GLvoid), GLint]
glDrawElementsInstancedBaseVertex = _libraries['libGL.so.1'].glDrawElementsInstancedBaseVertex
glDrawElementsInstancedBaseVertex.restype = None
glDrawElementsInstancedBaseVertex.argtypes = [GLenum, GLsizei, GLenum, POINTER(GLvoid), GLsizei, GLint]
glMultiDrawElementsBaseVertex = _libraries['libGL.so.1'].glMultiDrawElementsBaseVertex
glMultiDrawElementsBaseVertex.restype = None
glMultiDrawElementsBaseVertex.argtypes = [GLenum, POINTER(GLsizei), GLenum, POINTER(POINTER(GLvoid)), GLsizei, POINTER(GLint)]
glProvokingVertex = _libraries['libGL.so.1'].glProvokingVertex
glProvokingVertex.restype = None
glProvokingVertex.argtypes = [GLenum]
glFenceSync = _libraries['libGL.so.1'].glFenceSync
glFenceSync.restype = GLsync
glFenceSync.argtypes = [GLenum, GLbitfield]
glIsSync = _libraries['libGL.so.1'].glIsSync
glIsSync.restype = GLboolean
glIsSync.argtypes = [GLsync]
glDeleteSync = _libraries['libGL.so.1'].glDeleteSync
glDeleteSync.restype = None
glDeleteSync.argtypes = [GLsync]
glClientWaitSync = _libraries['libGL.so.1'].glClientWaitSync
glClientWaitSync.restype = GLenum
glClientWaitSync.argtypes = [GLsync, GLbitfield, GLuint64]
glWaitSync = _libraries['libGL.so.1'].glWaitSync
glWaitSync.restype = None
glWaitSync.argtypes = [GLsync, GLbitfield, GLuint64]
glGetInteger64v = _libraries['libGL.so.1'].glGetInteger64v
glGetInteger64v.restype = None
glGetInteger64v.argtypes = [GLenum, POINTER(GLint64)]
glGetSynciv = _libraries['libGL.so.1'].glGetSynciv
glGetSynciv.restype = None
glGetSynciv.argtypes = [GLsync, GLenum, GLsizei, POINTER(GLsizei), POINTER(GLint)]
glTexImage2DMultisample = _libraries['libGL.so.1'].glTexImage2DMultisample
glTexImage2DMultisample.restype = None
glTexImage2DMultisample.argtypes = [GLenum, GLsizei, GLint, GLsizei, GLsizei, GLboolean]
glTexImage3DMultisample = _libraries['libGL.so.1'].glTexImage3DMultisample
glTexImage3DMultisample.restype = None
glTexImage3DMultisample.argtypes = [GLenum, GLsizei, GLint, GLsizei, GLsizei, GLsizei, GLboolean]
glGetMultisamplefv = _libraries['libGL.so.1'].glGetMultisamplefv
glGetMultisamplefv.restype = None
glGetMultisamplefv.argtypes = [GLenum, GLuint, POINTER(GLfloat)]
glSampleMaski = _libraries['libGL.so.1'].glSampleMaski
glSampleMaski.restype = None
glSampleMaski.argtypes = [GLuint, GLbitfield]
glBlendEquationiARB = _libraries['libGL.so.1'].glBlendEquationiARB
glBlendEquationiARB.restype = None
glBlendEquationiARB.argtypes = [GLuint, GLenum]
glBlendEquationSeparateiARB = _libraries['libGL.so.1'].glBlendEquationSeparateiARB
glBlendEquationSeparateiARB.restype = None
glBlendEquationSeparateiARB.argtypes = [GLuint, GLenum, GLenum]
glBlendFunciARB = _libraries['libGL.so.1'].glBlendFunciARB
glBlendFunciARB.restype = None
glBlendFunciARB.argtypes = [GLuint, GLenum, GLenum]
glBlendFuncSeparateiARB = _libraries['libGL.so.1'].glBlendFuncSeparateiARB
glBlendFuncSeparateiARB.restype = None
glBlendFuncSeparateiARB.argtypes = [GLuint, GLenum, GLenum, GLenum, GLenum]
glMinSampleShadingARB = _libraries['libGL.so.1'].glMinSampleShadingARB
glMinSampleShadingARB.restype = None
glMinSampleShadingARB.argtypes = [GLclampf]
glNamedStringARB = _libraries['libGL.so.1'].glNamedStringARB
glNamedStringARB.restype = None
glNamedStringARB.argtypes = [GLenum, GLint, STRING, GLint, STRING]
glDeleteNamedStringARB = _libraries['libGL.so.1'].glDeleteNamedStringARB
glDeleteNamedStringARB.restype = None
glDeleteNamedStringARB.argtypes = [GLint, STRING]
glCompileShaderIncludeARB = _libraries['libGL.so.1'].glCompileShaderIncludeARB
glCompileShaderIncludeARB.restype = None
glCompileShaderIncludeARB.argtypes = [GLuint, GLsizei, POINTER(STRING), POINTER(GLint)]
glIsNamedStringARB = _libraries['libGL.so.1'].glIsNamedStringARB
glIsNamedStringARB.restype = GLboolean
glIsNamedStringARB.argtypes = [GLint, STRING]
glGetNamedStringARB = _libraries['libGL.so.1'].glGetNamedStringARB
glGetNamedStringARB.restype = None
glGetNamedStringARB.argtypes = [GLint, STRING, GLsizei, POINTER(GLint), STRING]
glGetNamedStringivARB = _libraries['libGL.so.1'].glGetNamedStringivARB
glGetNamedStringivARB.restype = None
glGetNamedStringivARB.argtypes = [GLint, STRING, GLenum, POINTER(GLint)]
glBindFragDataLocationIndexed = _libraries['libGL.so.1'].glBindFragDataLocationIndexed
glBindFragDataLocationIndexed.restype = None
glBindFragDataLocationIndexed.argtypes = [GLuint, GLuint, GLuint, STRING]
glGetFragDataIndex = _libraries['libGL.so.1'].glGetFragDataIndex
glGetFragDataIndex.restype = GLint
glGetFragDataIndex.argtypes = [GLuint, STRING]
glGenSamplers = _libraries['libGL.so.1'].glGenSamplers
glGenSamplers.restype = None
glGenSamplers.argtypes = [GLsizei, POINTER(GLuint)]
glDeleteSamplers = _libraries['libGL.so.1'].glDeleteSamplers
glDeleteSamplers.restype = None
glDeleteSamplers.argtypes = [GLsizei, POINTER(GLuint)]
glIsSampler = _libraries['libGL.so.1'].glIsSampler
glIsSampler.restype = GLboolean
glIsSampler.argtypes = [GLuint]
glBindSampler = _libraries['libGL.so.1'].glBindSampler
glBindSampler.restype = None
glBindSampler.argtypes = [GLuint, GLuint]
glSamplerParameteri = _libraries['libGL.so.1'].glSamplerParameteri
glSamplerParameteri.restype = None
glSamplerParameteri.argtypes = [GLuint, GLenum, GLint]
glSamplerParameteriv = _libraries['libGL.so.1'].glSamplerParameteriv
glSamplerParameteriv.restype = None
glSamplerParameteriv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glSamplerParameterf = _libraries['libGL.so.1'].glSamplerParameterf
glSamplerParameterf.restype = None
glSamplerParameterf.argtypes = [GLuint, GLenum, GLfloat]
glSamplerParameterfv = _libraries['libGL.so.1'].glSamplerParameterfv
glSamplerParameterfv.restype = None
glSamplerParameterfv.argtypes = [GLuint, GLenum, POINTER(GLfloat)]
glSamplerParameterIiv = _libraries['libGL.so.1'].glSamplerParameterIiv
glSamplerParameterIiv.restype = None
glSamplerParameterIiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glSamplerParameterIuiv = _libraries['libGL.so.1'].glSamplerParameterIuiv
glSamplerParameterIuiv.restype = None
glSamplerParameterIuiv.argtypes = [GLuint, GLenum, POINTER(GLuint)]
glGetSamplerParameteriv = _libraries['libGL.so.1'].glGetSamplerParameteriv
glGetSamplerParameteriv.restype = None
glGetSamplerParameteriv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetSamplerParameterIiv = _libraries['libGL.so.1'].glGetSamplerParameterIiv
glGetSamplerParameterIiv.restype = None
glGetSamplerParameterIiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glGetSamplerParameterfv = _libraries['libGL.so.1'].glGetSamplerParameterfv
glGetSamplerParameterfv.restype = None
glGetSamplerParameterfv.argtypes = [GLuint, GLenum, POINTER(GLfloat)]
glGetSamplerParameterIuiv = _libraries['libGL.so.1'].glGetSamplerParameterIuiv
glGetSamplerParameterIuiv.restype = None
glGetSamplerParameterIuiv.argtypes = [GLuint, GLenum, POINTER(GLuint)]
glQueryCounter = _libraries['libGL.so.1'].glQueryCounter
glQueryCounter.restype = None
glQueryCounter.argtypes = [GLuint, GLenum]
glGetQueryObjecti64v = _libraries['libGL.so.1'].glGetQueryObjecti64v
glGetQueryObjecti64v.restype = None
glGetQueryObjecti64v.argtypes = [GLuint, GLenum, POINTER(GLint64)]
glGetQueryObjectui64v = _libraries['libGL.so.1'].glGetQueryObjectui64v
glGetQueryObjectui64v.restype = None
glGetQueryObjectui64v.argtypes = [GLuint, GLenum, POINTER(GLuint64)]
glVertexAttribP1ui = _libraries['libGL.so.1'].glVertexAttribP1ui
glVertexAttribP1ui.restype = None
glVertexAttribP1ui.argtypes = [GLuint, GLenum, GLboolean, GLuint]
glVertexAttribP1uiv = _libraries['libGL.so.1'].glVertexAttribP1uiv
glVertexAttribP1uiv.restype = None
glVertexAttribP1uiv.argtypes = [GLuint, GLenum, GLboolean, POINTER(GLuint)]
glVertexAttribP2ui = _libraries['libGL.so.1'].glVertexAttribP2ui
glVertexAttribP2ui.restype = None
glVertexAttribP2ui.argtypes = [GLuint, GLenum, GLboolean, GLuint]
glVertexAttribP2uiv = _libraries['libGL.so.1'].glVertexAttribP2uiv
glVertexAttribP2uiv.restype = None
glVertexAttribP2uiv.argtypes = [GLuint, GLenum, GLboolean, POINTER(GLuint)]
glVertexAttribP3ui = _libraries['libGL.so.1'].glVertexAttribP3ui
glVertexAttribP3ui.restype = None
glVertexAttribP3ui.argtypes = [GLuint, GLenum, GLboolean, GLuint]
glVertexAttribP3uiv = _libraries['libGL.so.1'].glVertexAttribP3uiv
glVertexAttribP3uiv.restype = None
glVertexAttribP3uiv.argtypes = [GLuint, GLenum, GLboolean, POINTER(GLuint)]
glVertexAttribP4ui = _libraries['libGL.so.1'].glVertexAttribP4ui
glVertexAttribP4ui.restype = None
glVertexAttribP4ui.argtypes = [GLuint, GLenum, GLboolean, GLuint]
glVertexAttribP4uiv = _libraries['libGL.so.1'].glVertexAttribP4uiv
glVertexAttribP4uiv.restype = None
glVertexAttribP4uiv.argtypes = [GLuint, GLenum, GLboolean, POINTER(GLuint)]
glDrawArraysIndirect = _libraries['libGL.so.1'].glDrawArraysIndirect
glDrawArraysIndirect.restype = None
glDrawArraysIndirect.argtypes = [GLenum, POINTER(GLvoid)]
glDrawElementsIndirect = _libraries['libGL.so.1'].glDrawElementsIndirect
glDrawElementsIndirect.restype = None
glDrawElementsIndirect.argtypes = [GLenum, GLenum, POINTER(GLvoid)]
glUniform1d = _libraries['libGL.so.1'].glUniform1d
glUniform1d.restype = None
glUniform1d.argtypes = [GLint, GLdouble]
glUniform2d = _libraries['libGL.so.1'].glUniform2d
glUniform2d.restype = None
glUniform2d.argtypes = [GLint, GLdouble, GLdouble]
glUniform3d = _libraries['libGL.so.1'].glUniform3d
glUniform3d.restype = None
glUniform3d.argtypes = [GLint, GLdouble, GLdouble, GLdouble]
glUniform4d = _libraries['libGL.so.1'].glUniform4d
glUniform4d.restype = None
glUniform4d.argtypes = [GLint, GLdouble, GLdouble, GLdouble, GLdouble]
glUniform1dv = _libraries['libGL.so.1'].glUniform1dv
glUniform1dv.restype = None
glUniform1dv.argtypes = [GLint, GLsizei, POINTER(GLdouble)]
glUniform2dv = _libraries['libGL.so.1'].glUniform2dv
glUniform2dv.restype = None
glUniform2dv.argtypes = [GLint, GLsizei, POINTER(GLdouble)]
glUniform3dv = _libraries['libGL.so.1'].glUniform3dv
glUniform3dv.restype = None
glUniform3dv.argtypes = [GLint, GLsizei, POINTER(GLdouble)]
glUniform4dv = _libraries['libGL.so.1'].glUniform4dv
glUniform4dv.restype = None
glUniform4dv.argtypes = [GLint, GLsizei, POINTER(GLdouble)]
glUniformMatrix2dv = _libraries['libGL.so.1'].glUniformMatrix2dv
glUniformMatrix2dv.restype = None
glUniformMatrix2dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix3dv = _libraries['libGL.so.1'].glUniformMatrix3dv
glUniformMatrix3dv.restype = None
glUniformMatrix3dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix4dv = _libraries['libGL.so.1'].glUniformMatrix4dv
glUniformMatrix4dv.restype = None
glUniformMatrix4dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix2x3dv = _libraries['libGL.so.1'].glUniformMatrix2x3dv
glUniformMatrix2x3dv.restype = None
glUniformMatrix2x3dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix2x4dv = _libraries['libGL.so.1'].glUniformMatrix2x4dv
glUniformMatrix2x4dv.restype = None
glUniformMatrix2x4dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix3x2dv = _libraries['libGL.so.1'].glUniformMatrix3x2dv
glUniformMatrix3x2dv.restype = None
glUniformMatrix3x2dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix3x4dv = _libraries['libGL.so.1'].glUniformMatrix3x4dv
glUniformMatrix3x4dv.restype = None
glUniformMatrix3x4dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix4x2dv = _libraries['libGL.so.1'].glUniformMatrix4x2dv
glUniformMatrix4x2dv.restype = None
glUniformMatrix4x2dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glUniformMatrix4x3dv = _libraries['libGL.so.1'].glUniformMatrix4x3dv
glUniformMatrix4x3dv.restype = None
glUniformMatrix4x3dv.argtypes = [GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glGetUniformdv = _libraries['libGL.so.1'].glGetUniformdv
glGetUniformdv.restype = None
glGetUniformdv.argtypes = [GLuint, GLint, POINTER(GLdouble)]
glGetSubroutineUniformLocation = _libraries['libGL.so.1'].glGetSubroutineUniformLocation
glGetSubroutineUniformLocation.restype = GLint
glGetSubroutineUniformLocation.argtypes = [GLuint, GLenum, STRING]
glGetSubroutineIndex = _libraries['libGL.so.1'].glGetSubroutineIndex
glGetSubroutineIndex.restype = GLuint
glGetSubroutineIndex.argtypes = [GLuint, GLenum, STRING]
glGetActiveSubroutineUniformiv = _libraries['libGL.so.1'].glGetActiveSubroutineUniformiv
glGetActiveSubroutineUniformiv.restype = None
glGetActiveSubroutineUniformiv.argtypes = [GLuint, GLenum, GLuint, GLenum, POINTER(GLint)]
glGetActiveSubroutineUniformName = _libraries['libGL.so.1'].glGetActiveSubroutineUniformName
glGetActiveSubroutineUniformName.restype = None
glGetActiveSubroutineUniformName.argtypes = [GLuint, GLenum, GLuint, GLsizei, POINTER(GLsizei), STRING]
glGetActiveSubroutineName = _libraries['libGL.so.1'].glGetActiveSubroutineName
glGetActiveSubroutineName.restype = None
glGetActiveSubroutineName.argtypes = [GLuint, GLenum, GLuint, GLsizei, POINTER(GLsizei), STRING]
glUniformSubroutinesuiv = _libraries['libGL.so.1'].glUniformSubroutinesuiv
glUniformSubroutinesuiv.restype = None
glUniformSubroutinesuiv.argtypes = [GLenum, GLsizei, POINTER(GLuint)]
glGetUniformSubroutineuiv = _libraries['libGL.so.1'].glGetUniformSubroutineuiv
glGetUniformSubroutineuiv.restype = None
glGetUniformSubroutineuiv.argtypes = [GLenum, GLint, POINTER(GLuint)]
glGetProgramStageiv = _libraries['libGL.so.1'].glGetProgramStageiv
glGetProgramStageiv.restype = None
glGetProgramStageiv.argtypes = [GLuint, GLenum, GLenum, POINTER(GLint)]
glPatchParameteri = _libraries['libGL.so.1'].glPatchParameteri
glPatchParameteri.restype = None
glPatchParameteri.argtypes = [GLenum, GLint]
glPatchParameterfv = _libraries['libGL.so.1'].glPatchParameterfv
glPatchParameterfv.restype = None
glPatchParameterfv.argtypes = [GLenum, POINTER(GLfloat)]
glBindTransformFeedback = _libraries['libGL.so.1'].glBindTransformFeedback
glBindTransformFeedback.restype = None
glBindTransformFeedback.argtypes = [GLenum, GLuint]
glDeleteTransformFeedbacks = _libraries['libGL.so.1'].glDeleteTransformFeedbacks
glDeleteTransformFeedbacks.restype = None
glDeleteTransformFeedbacks.argtypes = [GLsizei, POINTER(GLuint)]
glGenTransformFeedbacks = _libraries['libGL.so.1'].glGenTransformFeedbacks
glGenTransformFeedbacks.restype = None
glGenTransformFeedbacks.argtypes = [GLsizei, POINTER(GLuint)]
glIsTransformFeedback = _libraries['libGL.so.1'].glIsTransformFeedback
glIsTransformFeedback.restype = GLboolean
glIsTransformFeedback.argtypes = [GLuint]
glPauseTransformFeedback = _libraries['libGL.so.1'].glPauseTransformFeedback
glPauseTransformFeedback.restype = None
glPauseTransformFeedback.argtypes = []
glResumeTransformFeedback = _libraries['libGL.so.1'].glResumeTransformFeedback
glResumeTransformFeedback.restype = None
glResumeTransformFeedback.argtypes = []
glDrawTransformFeedback = _libraries['libGL.so.1'].glDrawTransformFeedback
glDrawTransformFeedback.restype = None
glDrawTransformFeedback.argtypes = [GLenum, GLuint]
glDrawTransformFeedbackStream = _libraries['libGL.so.1'].glDrawTransformFeedbackStream
glDrawTransformFeedbackStream.restype = None
glDrawTransformFeedbackStream.argtypes = [GLenum, GLuint, GLuint]
glBeginQueryIndexed = _libraries['libGL.so.1'].glBeginQueryIndexed
glBeginQueryIndexed.restype = None
glBeginQueryIndexed.argtypes = [GLenum, GLuint, GLuint]
glEndQueryIndexed = _libraries['libGL.so.1'].glEndQueryIndexed
glEndQueryIndexed.restype = None
glEndQueryIndexed.argtypes = [GLenum, GLuint]
glGetQueryIndexediv = _libraries['libGL.so.1'].glGetQueryIndexediv
glGetQueryIndexediv.restype = None
glGetQueryIndexediv.argtypes = [GLenum, GLuint, GLenum, POINTER(GLint)]
glReleaseShaderCompiler = _libraries['libGL.so.1'].glReleaseShaderCompiler
glReleaseShaderCompiler.restype = None
glReleaseShaderCompiler.argtypes = []
glShaderBinary = _libraries['libGL.so.1'].glShaderBinary
glShaderBinary.restype = None
glShaderBinary.argtypes = [GLsizei, POINTER(GLuint), GLenum, POINTER(GLvoid), GLsizei]
glGetShaderPrecisionFormat = _libraries['libGL.so.1'].glGetShaderPrecisionFormat
glGetShaderPrecisionFormat.restype = None
glGetShaderPrecisionFormat.argtypes = [GLenum, GLenum, POINTER(GLint), POINTER(GLint)]
glDepthRangef = _libraries['libGL.so.1'].glDepthRangef
glDepthRangef.restype = None
glDepthRangef.argtypes = [GLclampf, GLclampf]
glClearDepthf = _libraries['libGL.so.1'].glClearDepthf
glClearDepthf.restype = None
glClearDepthf.argtypes = [GLclampf]
glGetProgramBinary = _libraries['libGL.so.1'].glGetProgramBinary
glGetProgramBinary.restype = None
glGetProgramBinary.argtypes = [GLuint, GLsizei, POINTER(GLsizei), POINTER(GLenum), POINTER(GLvoid)]
glProgramBinary = _libraries['libGL.so.1'].glProgramBinary
glProgramBinary.restype = None
glProgramBinary.argtypes = [GLuint, GLenum, POINTER(GLvoid), GLsizei]
glProgramParameteri = _libraries['libGL.so.1'].glProgramParameteri
glProgramParameteri.restype = None
glProgramParameteri.argtypes = [GLuint, GLenum, GLint]
glUseProgramStages = _libraries['libGL.so.1'].glUseProgramStages
glUseProgramStages.restype = None
glUseProgramStages.argtypes = [GLuint, GLbitfield, GLuint]
glActiveShaderProgram = _libraries['libGL.so.1'].glActiveShaderProgram
glActiveShaderProgram.restype = None
glActiveShaderProgram.argtypes = [GLuint, GLuint]
glCreateShaderProgramv = _libraries['libGL.so.1'].glCreateShaderProgramv
glCreateShaderProgramv.restype = GLuint
glCreateShaderProgramv.argtypes = [GLenum, GLsizei, POINTER(STRING)]
glBindProgramPipeline = _libraries['libGL.so.1'].glBindProgramPipeline
glBindProgramPipeline.restype = None
glBindProgramPipeline.argtypes = [GLuint]
glDeleteProgramPipelines = _libraries['libGL.so.1'].glDeleteProgramPipelines
glDeleteProgramPipelines.restype = None
glDeleteProgramPipelines.argtypes = [GLsizei, POINTER(GLuint)]
glGenProgramPipelines = _libraries['libGL.so.1'].glGenProgramPipelines
glGenProgramPipelines.restype = None
glGenProgramPipelines.argtypes = [GLsizei, POINTER(GLuint)]
glIsProgramPipeline = _libraries['libGL.so.1'].glIsProgramPipeline
glIsProgramPipeline.restype = GLboolean
glIsProgramPipeline.argtypes = [GLuint]
glGetProgramPipelineiv = _libraries['libGL.so.1'].glGetProgramPipelineiv
glGetProgramPipelineiv.restype = None
glGetProgramPipelineiv.argtypes = [GLuint, GLenum, POINTER(GLint)]
glProgramUniform1i = _libraries['libGL.so.1'].glProgramUniform1i
glProgramUniform1i.restype = None
glProgramUniform1i.argtypes = [GLuint, GLint, GLint]
glProgramUniform1iv = _libraries['libGL.so.1'].glProgramUniform1iv
glProgramUniform1iv.restype = None
glProgramUniform1iv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLint)]
glProgramUniform1f = _libraries['libGL.so.1'].glProgramUniform1f
glProgramUniform1f.restype = None
glProgramUniform1f.argtypes = [GLuint, GLint, GLfloat]
glProgramUniform1fv = _libraries['libGL.so.1'].glProgramUniform1fv
glProgramUniform1fv.restype = None
glProgramUniform1fv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLfloat)]
glProgramUniform1d = _libraries['libGL.so.1'].glProgramUniform1d
glProgramUniform1d.restype = None
glProgramUniform1d.argtypes = [GLuint, GLint, GLdouble]
glProgramUniform1dv = _libraries['libGL.so.1'].glProgramUniform1dv
glProgramUniform1dv.restype = None
glProgramUniform1dv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLdouble)]
glProgramUniform1ui = _libraries['libGL.so.1'].glProgramUniform1ui
glProgramUniform1ui.restype = None
glProgramUniform1ui.argtypes = [GLuint, GLint, GLuint]
glProgramUniform1uiv = _libraries['libGL.so.1'].glProgramUniform1uiv
glProgramUniform1uiv.restype = None
glProgramUniform1uiv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLuint)]
glProgramUniform2i = _libraries['libGL.so.1'].glProgramUniform2i
glProgramUniform2i.restype = None
glProgramUniform2i.argtypes = [GLuint, GLint, GLint, GLint]
glProgramUniform2iv = _libraries['libGL.so.1'].glProgramUniform2iv
glProgramUniform2iv.restype = None
glProgramUniform2iv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLint)]
glProgramUniform2f = _libraries['libGL.so.1'].glProgramUniform2f
glProgramUniform2f.restype = None
glProgramUniform2f.argtypes = [GLuint, GLint, GLfloat, GLfloat]
glProgramUniform2fv = _libraries['libGL.so.1'].glProgramUniform2fv
glProgramUniform2fv.restype = None
glProgramUniform2fv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLfloat)]
glProgramUniform2d = _libraries['libGL.so.1'].glProgramUniform2d
glProgramUniform2d.restype = None
glProgramUniform2d.argtypes = [GLuint, GLint, GLdouble, GLdouble]
glProgramUniform2dv = _libraries['libGL.so.1'].glProgramUniform2dv
glProgramUniform2dv.restype = None
glProgramUniform2dv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLdouble)]
glProgramUniform2ui = _libraries['libGL.so.1'].glProgramUniform2ui
glProgramUniform2ui.restype = None
glProgramUniform2ui.argtypes = [GLuint, GLint, GLuint, GLuint]
glProgramUniform2uiv = _libraries['libGL.so.1'].glProgramUniform2uiv
glProgramUniform2uiv.restype = None
glProgramUniform2uiv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLuint)]
glProgramUniform3i = _libraries['libGL.so.1'].glProgramUniform3i
glProgramUniform3i.restype = None
glProgramUniform3i.argtypes = [GLuint, GLint, GLint, GLint, GLint]
glProgramUniform3iv = _libraries['libGL.so.1'].glProgramUniform3iv
glProgramUniform3iv.restype = None
glProgramUniform3iv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLint)]
glProgramUniform3f = _libraries['libGL.so.1'].glProgramUniform3f
glProgramUniform3f.restype = None
glProgramUniform3f.argtypes = [GLuint, GLint, GLfloat, GLfloat, GLfloat]
glProgramUniform3fv = _libraries['libGL.so.1'].glProgramUniform3fv
glProgramUniform3fv.restype = None
glProgramUniform3fv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLfloat)]
glProgramUniform3d = _libraries['libGL.so.1'].glProgramUniform3d
glProgramUniform3d.restype = None
glProgramUniform3d.argtypes = [GLuint, GLint, GLdouble, GLdouble, GLdouble]
glProgramUniform3dv = _libraries['libGL.so.1'].glProgramUniform3dv
glProgramUniform3dv.restype = None
glProgramUniform3dv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLdouble)]
glProgramUniform3ui = _libraries['libGL.so.1'].glProgramUniform3ui
glProgramUniform3ui.restype = None
glProgramUniform3ui.argtypes = [GLuint, GLint, GLuint, GLuint, GLuint]
glProgramUniform3uiv = _libraries['libGL.so.1'].glProgramUniform3uiv
glProgramUniform3uiv.restype = None
glProgramUniform3uiv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLuint)]
glProgramUniform4i = _libraries['libGL.so.1'].glProgramUniform4i
glProgramUniform4i.restype = None
glProgramUniform4i.argtypes = [GLuint, GLint, GLint, GLint, GLint, GLint]
glProgramUniform4iv = _libraries['libGL.so.1'].glProgramUniform4iv
glProgramUniform4iv.restype = None
glProgramUniform4iv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLint)]
glProgramUniform4f = _libraries['libGL.so.1'].glProgramUniform4f
glProgramUniform4f.restype = None
glProgramUniform4f.argtypes = [GLuint, GLint, GLfloat, GLfloat, GLfloat, GLfloat]
glProgramUniform4fv = _libraries['libGL.so.1'].glProgramUniform4fv
glProgramUniform4fv.restype = None
glProgramUniform4fv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLfloat)]
glProgramUniform4d = _libraries['libGL.so.1'].glProgramUniform4d
glProgramUniform4d.restype = None
glProgramUniform4d.argtypes = [GLuint, GLint, GLdouble, GLdouble, GLdouble, GLdouble]
glProgramUniform4dv = _libraries['libGL.so.1'].glProgramUniform4dv
glProgramUniform4dv.restype = None
glProgramUniform4dv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLdouble)]
glProgramUniform4ui = _libraries['libGL.so.1'].glProgramUniform4ui
glProgramUniform4ui.restype = None
glProgramUniform4ui.argtypes = [GLuint, GLint, GLuint, GLuint, GLuint, GLuint]
glProgramUniform4uiv = _libraries['libGL.so.1'].glProgramUniform4uiv
glProgramUniform4uiv.restype = None
glProgramUniform4uiv.argtypes = [GLuint, GLint, GLsizei, POINTER(GLuint)]
glProgramUniformMatrix2fv = _libraries['libGL.so.1'].glProgramUniformMatrix2fv
glProgramUniformMatrix2fv.restype = None
glProgramUniformMatrix2fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix3fv = _libraries['libGL.so.1'].glProgramUniformMatrix3fv
glProgramUniformMatrix3fv.restype = None
glProgramUniformMatrix3fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix4fv = _libraries['libGL.so.1'].glProgramUniformMatrix4fv
glProgramUniformMatrix4fv.restype = None
glProgramUniformMatrix4fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix2dv = _libraries['libGL.so.1'].glProgramUniformMatrix2dv
glProgramUniformMatrix2dv.restype = None
glProgramUniformMatrix2dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix3dv = _libraries['libGL.so.1'].glProgramUniformMatrix3dv
glProgramUniformMatrix3dv.restype = None
glProgramUniformMatrix3dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix4dv = _libraries['libGL.so.1'].glProgramUniformMatrix4dv
glProgramUniformMatrix4dv.restype = None
glProgramUniformMatrix4dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix2x3fv = _libraries['libGL.so.1'].glProgramUniformMatrix2x3fv
glProgramUniformMatrix2x3fv.restype = None
glProgramUniformMatrix2x3fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix3x2fv = _libraries['libGL.so.1'].glProgramUniformMatrix3x2fv
glProgramUniformMatrix3x2fv.restype = None
glProgramUniformMatrix3x2fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix2x4fv = _libraries['libGL.so.1'].glProgramUniformMatrix2x4fv
glProgramUniformMatrix2x4fv.restype = None
glProgramUniformMatrix2x4fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix4x2fv = _libraries['libGL.so.1'].glProgramUniformMatrix4x2fv
glProgramUniformMatrix4x2fv.restype = None
glProgramUniformMatrix4x2fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix3x4fv = _libraries['libGL.so.1'].glProgramUniformMatrix3x4fv
glProgramUniformMatrix3x4fv.restype = None
glProgramUniformMatrix3x4fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix4x3fv = _libraries['libGL.so.1'].glProgramUniformMatrix4x3fv
glProgramUniformMatrix4x3fv.restype = None
glProgramUniformMatrix4x3fv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLfloat)]
glProgramUniformMatrix2x3dv = _libraries['libGL.so.1'].glProgramUniformMatrix2x3dv
glProgramUniformMatrix2x3dv.restype = None
glProgramUniformMatrix2x3dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix3x2dv = _libraries['libGL.so.1'].glProgramUniformMatrix3x2dv
glProgramUniformMatrix3x2dv.restype = None
glProgramUniformMatrix3x2dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix2x4dv = _libraries['libGL.so.1'].glProgramUniformMatrix2x4dv
glProgramUniformMatrix2x4dv.restype = None
glProgramUniformMatrix2x4dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix4x2dv = _libraries['libGL.so.1'].glProgramUniformMatrix4x2dv
glProgramUniformMatrix4x2dv.restype = None
glProgramUniformMatrix4x2dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix3x4dv = _libraries['libGL.so.1'].glProgramUniformMatrix3x4dv
glProgramUniformMatrix3x4dv.restype = None
glProgramUniformMatrix3x4dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glProgramUniformMatrix4x3dv = _libraries['libGL.so.1'].glProgramUniformMatrix4x3dv
glProgramUniformMatrix4x3dv.restype = None
glProgramUniformMatrix4x3dv.argtypes = [GLuint, GLint, GLsizei, GLboolean, POINTER(GLdouble)]
glValidateProgramPipeline = _libraries['libGL.so.1'].glValidateProgramPipeline
glValidateProgramPipeline.restype = None
glValidateProgramPipeline.argtypes = [GLuint]
glGetProgramPipelineInfoLog = _libraries['libGL.so.1'].glGetProgramPipelineInfoLog
glGetProgramPipelineInfoLog.restype = None
glGetProgramPipelineInfoLog.argtypes = [GLuint, GLsizei, POINTER(GLsizei), STRING]
glVertexAttribL1d = _libraries['libGL.so.1'].glVertexAttribL1d
glVertexAttribL1d.restype = None
glVertexAttribL1d.argtypes = [GLuint, GLdouble]
glVertexAttribL2d = _libraries['libGL.so.1'].glVertexAttribL2d
glVertexAttribL2d.restype = None
glVertexAttribL2d.argtypes = [GLuint, GLdouble, GLdouble]
glVertexAttribL3d = _libraries['libGL.so.1'].glVertexAttribL3d
glVertexAttribL3d.restype = None
glVertexAttribL3d.argtypes = [GLuint, GLdouble, GLdouble, GLdouble]
glVertexAttribL4d = _libraries['libGL.so.1'].glVertexAttribL4d
glVertexAttribL4d.restype = None
glVertexAttribL4d.argtypes = [GLuint, GLdouble, GLdouble, GLdouble, GLdouble]
glVertexAttribL1dv = _libraries['libGL.so.1'].glVertexAttribL1dv
glVertexAttribL1dv.restype = None
glVertexAttribL1dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttribL2dv = _libraries['libGL.so.1'].glVertexAttribL2dv
glVertexAttribL2dv.restype = None
glVertexAttribL2dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttribL3dv = _libraries['libGL.so.1'].glVertexAttribL3dv
glVertexAttribL3dv.restype = None
glVertexAttribL3dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttribL4dv = _libraries['libGL.so.1'].glVertexAttribL4dv
glVertexAttribL4dv.restype = None
glVertexAttribL4dv.argtypes = [GLuint, POINTER(GLdouble)]
glVertexAttribLPointer = _libraries['libGL.so.1'].glVertexAttribLPointer
glVertexAttribLPointer.restype = None
glVertexAttribLPointer.argtypes = [GLuint, GLint, GLenum, GLsizei, POINTER(GLvoid)]
glGetVertexAttribLdv = _libraries['libGL.so.1'].glGetVertexAttribLdv
glGetVertexAttribLdv.restype = None
glGetVertexAttribLdv.argtypes = [GLuint, GLenum, POINTER(GLdouble)]
glViewportArrayv = _libraries['libGL.so.1'].glViewportArrayv
glViewportArrayv.restype = None
glViewportArrayv.argtypes = [GLuint, GLsizei, POINTER(GLfloat)]
glViewportIndexedf = _libraries['libGL.so.1'].glViewportIndexedf
glViewportIndexedf.restype = None
glViewportIndexedf.argtypes = [GLuint, GLfloat, GLfloat, GLfloat, GLfloat]
glViewportIndexedfv = _libraries['libGL.so.1'].glViewportIndexedfv
glViewportIndexedfv.restype = None
glViewportIndexedfv.argtypes = [GLuint, POINTER(GLfloat)]
glScissorArrayv = _libraries['libGL.so.1'].glScissorArrayv
glScissorArrayv.restype = None
glScissorArrayv.argtypes = [GLuint, GLsizei, POINTER(GLint)]
glScissorIndexed = _libraries['libGL.so.1'].glScissorIndexed
glScissorIndexed.restype = None
glScissorIndexed.argtypes = [GLuint, GLint, GLint, GLsizei, GLsizei]
glScissorIndexedv = _libraries['libGL.so.1'].glScissorIndexedv
glScissorIndexedv.restype = None
glScissorIndexedv.argtypes = [GLuint, POINTER(GLint)]
glDepthRangeArrayv = _libraries['libGL.so.1'].glDepthRangeArrayv
glDepthRangeArrayv.restype = None
glDepthRangeArrayv.argtypes = [GLuint, GLsizei, POINTER(GLclampd)]
glDepthRangeIndexed = _libraries['libGL.so.1'].glDepthRangeIndexed
glDepthRangeIndexed.restype = None
glDepthRangeIndexed.argtypes = [GLuint, GLclampd, GLclampd]
glGetFloati_v = _libraries['libGL.so.1'].glGetFloati_v
glGetFloati_v.restype = None
glGetFloati_v.argtypes = [GLenum, GLuint, POINTER(GLfloat)]
glGetDoublei_v = _libraries['libGL.so.1'].glGetDoublei_v
glGetDoublei_v.restype = None
glGetDoublei_v.argtypes = [GLenum, GLuint, POINTER(GLdouble)]
glDebugMessageControlARB = _libraries['libGL.so.1'].glDebugMessageControlARB
glDebugMessageControlARB.restype = None
glDebugMessageControlARB.argtypes = [GLenum, GLenum, GLenum, GLsizei, POINTER(GLuint), GLboolean]
glDebugMessageInsertARB = _libraries['libGL.so.1'].glDebugMessageInsertARB
glDebugMessageInsertARB.restype = None
glDebugMessageInsertARB.argtypes = [GLenum, GLenum, GLuint, GLenum, GLsizei, STRING]
GLDEBUGPROCARB = CFUNCTYPE(None, GLenum, GLenum, GLuint, GLenum, GLsizei, STRING, POINTER(GLvoid))
glDebugMessageCallbackARB = _libraries['libGL.so.1'].glDebugMessageCallbackARB
glDebugMessageCallbackARB.restype = None
glDebugMessageCallbackARB.argtypes = [GLDEBUGPROCARB, POINTER(GLvoid)]
glGetDebugMessageLogARB = _libraries['libGL.so.1'].glGetDebugMessageLogARB
glGetDebugMessageLogARB.restype = GLuint
glGetDebugMessageLogARB.argtypes = [GLuint, GLsizei, POINTER(GLenum), POINTER(GLenum), POINTER(GLuint), POINTER(GLenum), POINTER(GLsizei), STRING]
glGetGraphicsResetStatusARB = _libraries['libGL.so.1'].glGetGraphicsResetStatusARB
glGetGraphicsResetStatusARB.restype = GLenum
glGetGraphicsResetStatusARB.argtypes = []
glGetnMapdvARB = _libraries['libGL.so.1'].glGetnMapdvARB
glGetnMapdvARB.restype = None
glGetnMapdvARB.argtypes = [GLenum, GLenum, GLsizei, POINTER(GLdouble)]
glGetnMapfvARB = _libraries['libGL.so.1'].glGetnMapfvARB
glGetnMapfvARB.restype = None
glGetnMapfvARB.argtypes = [GLenum, GLenum, GLsizei, POINTER(GLfloat)]
glGetnMapivARB = _libraries['libGL.so.1'].glGetnMapivARB
glGetnMapivARB.restype = None
glGetnMapivARB.argtypes = [GLenum, GLenum, GLsizei, POINTER(GLint)]
glGetnPixelMapfvARB = _libraries['libGL.so.1'].glGetnPixelMapfvARB
glGetnPixelMapfvARB.restype = None
glGetnPixelMapfvARB.argtypes = [GLenum, GLsizei, POINTER(GLfloat)]
glGetnPixelMapuivARB = _libraries['libGL.so.1'].glGetnPixelMapuivARB
glGetnPixelMapuivARB.restype = None
glGetnPixelMapuivARB.argtypes = [GLenum, GLsizei, POINTER(GLuint)]
glGetnPixelMapusvARB = _libraries['libGL.so.1'].glGetnPixelMapusvARB
glGetnPixelMapusvARB.restype = None
glGetnPixelMapusvARB.argtypes = [GLenum, GLsizei, POINTER(GLushort)]
glGetnPolygonStippleARB = _libraries['libGL.so.1'].glGetnPolygonStippleARB
glGetnPolygonStippleARB.restype = None
glGetnPolygonStippleARB.argtypes = [GLsizei, POINTER(GLubyte)]
glGetnColorTableARB = _libraries['libGL.so.1'].glGetnColorTableARB
glGetnColorTableARB.restype = None
glGetnColorTableARB.argtypes = [GLenum, GLenum, GLenum, GLsizei, POINTER(GLvoid)]
glGetnConvolutionFilterARB = _libraries['libGL.so.1'].glGetnConvolutionFilterARB
glGetnConvolutionFilterARB.restype = None
glGetnConvolutionFilterARB.argtypes = [GLenum, GLenum, GLenum, GLsizei, POINTER(GLvoid)]
glGetnSeparableFilterARB = _libraries['libGL.so.1'].glGetnSeparableFilterARB
glGetnSeparableFilterARB.restype = None
glGetnSeparableFilterARB.argtypes = [GLenum, GLenum, GLenum, GLsizei, POINTER(GLvoid), GLsizei, POINTER(GLvoid), POINTER(GLvoid)]
glGetnHistogramARB = _libraries['libGL.so.1'].glGetnHistogramARB
glGetnHistogramARB.restype = None
glGetnHistogramARB.argtypes = [GLenum, GLboolean, GLenum, GLenum, GLsizei, POINTER(GLvoid)]
glGetnMinmaxARB = _libraries['libGL.so.1'].glGetnMinmaxARB
glGetnMinmaxARB.restype = None
glGetnMinmaxARB.argtypes = [GLenum, GLboolean, GLenum, GLenum, GLsizei, POINTER(GLvoid)]
glGetnTexImageARB = _libraries['libGL.so.1'].glGetnTexImageARB
glGetnTexImageARB.restype = None
glGetnTexImageARB.argtypes = [GLenum, GLint, GLenum, GLenum, GLsizei, POINTER(GLvoid)]
glReadnPixelsARB = _libraries['libGL.so.1'].glReadnPixelsARB
glReadnPixelsARB.restype = None
glReadnPixelsARB.argtypes = [GLint, GLint, GLsizei, GLsizei, GLenum, GLenum, GLsizei, POINTER(GLvoid)]
glGetnCompressedTexImageARB = _libraries['libGL.so.1'].glGetnCompressedTexImageARB
glGetnCompressedTexImageARB.restype = None
glGetnCompressedTexImageARB.argtypes = [GLenum, GLint, GLsizei, POINTER(GLvoid)]
glGetnUniformfvARB = _libraries['libGL.so.1'].glGetnUniformfvARB
glGetnUniformfvARB.restype = None
glGetnUniformfvARB.argtypes = [GLuint, GLint, GLsizei, POINTER(GLfloat)]
glGetnUniformivARB = _libraries['libGL.so.1'].glGetnUniformivARB
glGetnUniformivARB.restype = None
glGetnUniformivARB.argtypes = [GLuint, GLint, GLsizei, POINTER(GLint)]
glGetnUniformuivARB = _libraries['libGL.so.1'].glGetnUniformuivARB
glGetnUniformuivARB.restype = None
glGetnUniformuivARB.argtypes = [GLuint, GLint, GLsizei, POINTER(GLuint)]
glGetnUniformdvARB = _libraries['libGL.so.1'].glGetnUniformdvARB
glGetnUniformdvARB.restype = None
glGetnUniformdvARB.argtypes = [GLuint, GLint, GLsizei, POINTER(GLdouble)]
glDrawArraysInstancedBaseInstance = _libraries['libGL.so.1'].glDrawArraysInstancedBaseInstance
glDrawArraysInstancedBaseInstance.restype = None
glDrawArraysInstancedBaseInstance.argtypes = [GLenum, GLint, GLsizei, GLsizei, GLuint]
glDrawElementsInstancedBaseInstance = _libraries['libGL.so.1'].glDrawElementsInstancedBaseInstance
glDrawElementsInstancedBaseInstance.restype = None
glDrawElementsInstancedBaseInstance.argtypes = [GLenum, GLsizei, GLenum, c_void_p, GLsizei, GLuint]
glDrawElementsInstancedBaseVertexBaseInstance = _libraries['libGL.so.1'].glDrawElementsInstancedBaseVertexBaseInstance
glDrawElementsInstancedBaseVertexBaseInstance.restype = None
glDrawElementsInstancedBaseVertexBaseInstance.argtypes = [GLenum, GLsizei, GLenum, c_void_p, GLsizei, GLint, GLuint]
glDrawTransformFeedbackInstanced = _libraries['libGL.so.1'].glDrawTransformFeedbackInstanced
glDrawTransformFeedbackInstanced.restype = None
glDrawTransformFeedbackInstanced.argtypes = [GLenum, GLuint, GLsizei]
glDrawTransformFeedbackStreamInstanced = _libraries['libGL.so.1'].glDrawTransformFeedbackStreamInstanced
glDrawTransformFeedbackStreamInstanced.restype = None
glDrawTransformFeedbackStreamInstanced.argtypes = [GLenum, GLuint, GLuint, GLsizei]
glGetInternalformativ = _libraries['libGL.so.1'].glGetInternalformativ
glGetInternalformativ.restype = None
glGetInternalformativ.argtypes = [GLenum, GLenum, GLenum, GLsizei, POINTER(GLint)]
glGetActiveAtomicCounterBufferiv = _libraries['libGL.so.1'].glGetActiveAtomicCounterBufferiv
glGetActiveAtomicCounterBufferiv.restype = None
glGetActiveAtomicCounterBufferiv.argtypes = [GLuint, GLuint, GLenum, POINTER(GLint)]
glBindImageTexture = _libraries['libGL.so.1'].glBindImageTexture
glBindImageTexture.restype = None
glBindImageTexture.argtypes = [GLuint, GLuint, GLint, GLboolean, GLint, GLenum, GLenum]
glMemoryBarrier = _libraries['libGL.so.1'].glMemoryBarrier
glMemoryBarrier.restype = None
glMemoryBarrier.argtypes = [GLbitfield]
glTexStorage1D = _libraries['libGL.so.1'].glTexStorage1D
glTexStorage1D.restype = None
glTexStorage1D.argtypes = [GLenum, GLsizei, GLenum, GLsizei]
glTexStorage2D = _libraries['libGL.so.1'].glTexStorage2D
glTexStorage2D.restype = None
glTexStorage2D.argtypes = [GLenum, GLsizei, GLenum, GLsizei, GLsizei]
glTexStorage3D = _libraries['libGL.so.1'].glTexStorage3D
glTexStorage3D.restype = None
glTexStorage3D.argtypes = [GLenum, GLsizei, GLenum, GLsizei, GLsizei, GLsizei]
glTextureStorage1DEXT = _libraries['libGL.so.1'].glTextureStorage1DEXT
glTextureStorage1DEXT.restype = None
glTextureStorage1DEXT.argtypes = [GLuint, GLenum, GLsizei, GLenum, GLsizei]
glTextureStorage2DEXT = _libraries['libGL.so.1'].glTextureStorage2DEXT
glTextureStorage2DEXT.restype = None
glTextureStorage2DEXT.argtypes = [GLuint, GLenum, GLsizei, GLenum, GLsizei, GLsizei]
glTextureStorage3DEXT = _libraries['libGL.so.1'].glTextureStorage3DEXT
glTextureStorage3DEXT.restype = None
glTextureStorage3DEXT.argtypes = [GLuint, GLenum, GLsizei, GLenum, GLsizei, GLsizei, GLsizei]
GL_COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_ARB = 36495 # Variable c_int '36495'
GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER = 36059 # Variable c_int '36059'
GL_FRAMEBUFFER_ATTACHMENT_BLUE_SIZE = 33300 # Variable c_int '33300'
GL_UNSIGNED_INT_VEC2 = 36294 # Variable c_int '36294'
GL_UNSIGNED_INT_VEC3 = 36295 # Variable c_int '36295'
GL_UNSIGNED_INT_VEC4 = 36296 # Variable c_int '36296'
GL_UNSIGNED_SHORT_5_6_5 = 33635 # Variable c_int '33635'
GL_VERTEX_ATTRIB_ARRAY_SIZE = 34339 # Variable c_int '34339'
GL_DEPTH_ATTACHMENT = 36096 # Variable c_int '36096'
GL_MAX_GEOMETRY_IMAGE_UNIFORMS = 37069 # Variable c_int '37069'
GL_NEAREST_MIPMAP_LINEAR = 9986 # Variable c_int '9986'
GL_DITHER = 3024 # Variable c_int '3024'
GL_RGB16UI = 36215 # Variable c_int '36215'
GL_TEXTURE_RECTANGLE = 34037 # Variable c_int '34037'
GL_FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE = 33303 # Variable c_int '33303'
GL_FLOAT_VEC2 = 35664 # Variable c_int '35664'
GL_FLOAT_VEC3 = 35665 # Variable c_int '35665'
GL_R16_SNORM = 36760 # Variable c_int '36760'
GL_INT_IMAGE_2D_MULTISAMPLE = 36960 # Variable c_int '36960'
GL_FLOAT_VEC4 = 35666 # Variable c_int '35666'
GL_IMAGE_CUBE = 36944 # Variable c_int '36944'
GL_FLOAT = 5126 # Variable c_int '5126'
GL_INT_2_10_10_10_REV = 36255 # Variable c_int '36255'
GL_TEXTURE_COMPARE_MODE = 34892 # Variable c_int '34892'
GL_TEXTURE_MAX_LOD = 33083 # Variable c_int '33083'
GL_BUFFER_MAP_OFFSET = 37153 # Variable c_int '37153'
GL_MAX_TESS_EVALUATION_TEXTURE_IMAGE_UNITS = 36482 # Variable c_int '36482'
GL_IMAGE_2D = 36941 # Variable c_int '36941'
GL_PROXY_TEXTURE_RECTANGLE = 34039 # Variable c_int '34039'
GL_MAX_SUBROUTINES = 36327 # Variable c_int '36327'
GL_READ_BUFFER = 3074 # Variable c_int '3074'
GL_RGB16_SNORM = 36762 # Variable c_int '36762'
GL_STENCIL_BACK_PASS_DEPTH_PASS = 34819 # Variable c_int '34819'
GL_SAMPLER_2D_RECT = 35683 # Variable c_int '35683'
GL_UNSIGNED_INT_SAMPLER_BUFFER = 36312 # Variable c_int '36312'
GL_UNIFORM_BUFFER_START = 35369 # Variable c_int '35369'
GL_INT_IMAGE_2D_MULTISAMPLE_ARRAY = 36961 # Variable c_int '36961'
GL_ARB_shading_language_packing = 1 # Variable c_int '1'
GL_TEXTURE_COMPRESSED = 34465 # Variable c_int '34465'
GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS = 35979 # Variable c_int '35979'
GL_CONSTANT_COLOR = 32769 # Variable c_int '32769'
GL_RGBA32UI = 36208 # Variable c_int '36208'
GL_UNSIGNED_INT_SAMPLER_2D = 36306 # Variable c_int '36306'
GL_FRACTIONAL_EVEN = 36476 # Variable c_int '36476'
GL_MAX_TESS_CONTROL_UNIFORM_COMPONENTS = 36479 # Variable c_int '36479'
GL_TEXTURE8 = 33992 # Variable c_int '33992'
GL_TEXTURE9 = 33993 # Variable c_int '33993'
GL_MAX_VARYING_FLOATS = 35659 # Variable c_int '35659'
GL_DEBUG_CALLBACK_USER_PARAM_ARB = 33349 # Variable c_int '33349'
GL_TEXTURE4 = 33988 # Variable c_int '33988'
GL_TEXTURE5 = 33989 # Variable c_int '33989'
GL_TEXTURE6 = 33990 # Variable c_int '33990'
GL_TEXTURE7 = 33991 # Variable c_int '33991'
GL_TEXTURE0 = 33984 # Variable c_int '33984'
GL_CONTEXT_PROFILE_MASK = 37158 # Variable c_int '37158'
GL_TEXTURE2 = 33986 # Variable c_int '33986'
GL_TEXTURE3 = 33987 # Variable c_int '33987'
GL_TEXTURE_CUBE_MAP_POSITIVE_Y = 34071 # Variable c_int '34071'
GL_TEXTURE_CUBE_MAP_POSITIVE_X = 34069 # Variable c_int '34069'
GL_DOUBLE = 5130 # Variable c_int '5130'
GL_BLEND_EQUATION = 32777 # Variable c_int '32777'
GL_BYTE = 5120 # Variable c_int '5120'
GL_BOOL_VEC3 = 35672 # Variable c_int '35672'
GL_IMAGE_FORMAT_COMPATIBILITY_BY_SIZE = 37064 # Variable c_int '37064'
GL_TIMEOUT_IGNORED = 18446744073709551615L # Variable c_ulonglong '-1ull'
GL_MAX_TESS_CONTROL_TOTAL_OUTPUT_COMPONENTS = 36485 # Variable c_int '36485'
GL_TEXTURE_CUBE_MAP_NEGATIVE_X = 34070 # Variable c_int '34070'
GL_MAX_VARYING_VECTORS = 36348 # Variable c_int '36348'
GL_RENDERBUFFER_SAMPLES = 36011 # Variable c_int '36011'
GL_ARB_shader_atomic_counters = 1 # Variable c_int '1'
GL_RG = 33319 # Variable c_int '33319'
GL_DONT_CARE = 4352 # Variable c_int '4352'
GL_NAMED_STRING_TYPE_ARB = 36330 # Variable c_int '36330'
GL_MAX_COMBINED_TESS_EVALUATION_UNIFORM_COMPONENTS = 36383 # Variable c_int '36383'
GL_SRC_ALPHA_SATURATE = 776 # Variable c_int '776'
GL_PACK_COMPRESSED_BLOCK_DEPTH = 37165 # Variable c_int '37165'
GL_MAX_SAMPLES = 36183 # Variable c_int '36183'
GL_DEPTH_WRITEMASK = 2930 # Variable c_int '2930'
GL_FRAMEBUFFER_SRGB = 36281 # Variable c_int '36281'
GL_UNPACK_IMAGE_HEIGHT = 32878 # Variable c_int '32878'
GL_GREEN_INTEGER = 36245 # Variable c_int '36245'
GL_SAMPLER_2D_MULTISAMPLE = 37128 # Variable c_int '37128'
GL_TEXTURE_DEPTH_SIZE = 34890 # Variable c_int '34890'
GL_FLOAT_MAT3x2 = 35687 # Variable c_int '35687'
GL_TRIANGLE_STRIP = 5 # Variable c_int '5'
GL_NOOP = 5381 # Variable c_int '5381'
GL_PROGRAM_BINARY_RETRIEVABLE_HINT = 33367 # Variable c_int '33367'
GL_FLOAT_MAT3x4 = 35688 # Variable c_int '35688'
GL_ATOMIC_COUNTER_BUFFER_DATA_SIZE = 37572 # Variable c_int '37572'
GL_CONTEXT_FLAGS = 33310 # Variable c_int '33310'
GL_FRONT_LEFT = 1024 # Variable c_int '1024'
GL_INVALID_ENUM = 1280 # Variable c_int '1280'
GL_TEXTURE_BINDING_2D_MULTISAMPLE = 37124 # Variable c_int '37124'
GL_ALL_SHADER_BITS = 4294967295L # Variable c_uint '4294967295u'
GL_COMPRESSED_RGBA = 34030 # Variable c_int '34030'
GL_TRIANGLE_STRIP_ADJACENCY = 13 # Variable c_int '13'
GL_MAX_TESS_EVALUATION_ATOMIC_COUNTERS = 37588 # Variable c_int '37588'
GL_ARB_map_buffer_range = 1 # Variable c_int '1'
GL_TRANSFORM_FEEDBACK_BUFFER = 35982 # Variable c_int '35982'
GL_BLUE = 6405 # Variable c_int '6405'
GL_VERTEX_ARRAY_BINDING = 34229 # Variable c_int '34229'
GL_UNSIGNED_SHORT_5_5_5_1 = 32820 # Variable c_int '32820'
GL_TIMEOUT_EXPIRED = 37147 # Variable c_int '37147'
GL_QUERY_NO_WAIT = 36372 # Variable c_int '36372'
GL_PROVOKING_VERTEX = 36431 # Variable c_int '36431'
GL_DEBUG_SEVERITY_MEDIUM_ARB = 37191 # Variable c_int '37191'
GL_SIGNED_NORMALIZED = 36764 # Variable c_int '36764'
GL_STENCIL_FUNC = 2962 # Variable c_int '2962'
GL_RG16UI = 33338 # Variable c_int '33338'
GL_LINE_STRIP_ADJACENCY = 11 # Variable c_int '11'
GL_QUERY_RESULT = 34918 # Variable c_int '34918'
GL_ALIASED_LINE_WIDTH_RANGE = 33902 # Variable c_int '33902'
GL_POINT_SIZE = 2833 # Variable c_int '2833'
GL_DECR = 7683 # Variable c_int '7683'
GL_BACK = 1029 # Variable c_int '1029'
GL_RGBA_INTEGER = 36249 # Variable c_int '36249'
GL_TRANSFORM_FEEDBACK_BUFFER_MODE = 35967 # Variable c_int '35967'
GL_UNSIGNALED = 37144 # Variable c_int '37144'
GL_RGB12 = 32851 # Variable c_int '32851'
GL_INT = 5124 # Variable c_int '5124'
GL_RGB10 = 32850 # Variable c_int '32850'
GL_ATOMIC_COUNTER_BUFFER = 37568 # Variable c_int '37568'
GL_RGB16 = 32852 # Variable c_int '32852'
GL_PROXY_TEXTURE_CUBE_MAP = 34075 # Variable c_int '34075'
GL_CLIP_DISTANCE1 = 12289 # Variable c_int '12289'
GL_CLIP_DISTANCE0 = 12288 # Variable c_int '12288'
GL_CLIP_DISTANCE3 = 12291 # Variable c_int '12291'
GL_CLIP_DISTANCE2 = 12290 # Variable c_int '12290'
GL_CLIP_DISTANCE5 = 12293 # Variable c_int '12293'
GL_CLIP_DISTANCE4 = 12292 # Variable c_int '12292'
GL_MINOR_VERSION = 33308 # Variable c_int '33308'
GL_PROXY_TEXTURE_2D_ARRAY = 35867 # Variable c_int '35867'
GL_DOUBLEBUFFER = 3122 # Variable c_int '3122'
GL_VERSION_4_1 = 1 # Variable c_int '1'
GL_IMAGE_BINDING_LEVEL = 36667 # Variable c_int '36667'
GL_FRONT_AND_BACK = 1032 # Variable c_int '1032'
GL_R8 = 33321 # Variable c_int '33321'
GL_FRAGMENT_SHADER_BIT = 2 # Variable c_int '2'
GL_POINT = 6912 # Variable c_int '6912'
GL_MAX_COMBINED_TESS_CONTROL_UNIFORM_COMPONENTS = 36382 # Variable c_int '36382'
GL_COMPRESSED_RG_RGTC2 = 36285 # Variable c_int '36285'
GL_RESET_NOTIFICATION_STRATEGY_ARB = 33366 # Variable c_int '33366'
GL_DOUBLE_MAT4 = 36680 # Variable c_int '36680'
GL_MIN_PROGRAM_TEXEL_OFFSET = 35076 # Variable c_int '35076'
GL_DOUBLE_MAT2 = 36678 # Variable c_int '36678'
GL_DOUBLE_MAT3 = 36679 # Variable c_int '36679'
GL_SMOOTH_LINE_WIDTH_GRANULARITY = 2851 # Variable c_int '2851'
GL_PACK_COMPRESSED_BLOCK_WIDTH = 37163 # Variable c_int '37163'
GL_STENCIL = 6146 # Variable c_int '6146'
GL_SRGB = 35904 # Variable c_int '35904'
GL_SYNC_FENCE = 37142 # Variable c_int '37142'
GL_ONE_MINUS_CONSTANT_COLOR = 32770 # Variable c_int '32770'
GL_UNSIGNED_INT_8_8_8_8 = 32821 # Variable c_int '32821'
GL_MAX_TESS_CONTROL_INPUT_COMPONENTS = 34924 # Variable c_int '34924'
GL_SHADING_LANGUAGE_VERSION = 35724 # Variable c_int '35724'
GL_MIN_SAMPLE_SHADING_VALUE = 35895 # Variable c_int '35895'
GL_RGB16I = 36233 # Variable c_int '36233'
GL_RGB8_SNORM = 36758 # Variable c_int '36758'
GL_UNPACK_SKIP_PIXELS = 3316 # Variable c_int '3316'
GL_UNSIGNED_INT_SAMPLER_2D_RECT = 36309 # Variable c_int '36309'
GL_ARB_texture_rg = 1 # Variable c_int '1'
GL_ARB_vertex_type_2_10_10_10_rev = 1 # Variable c_int '1'
GL_FRAGMENT_SHADER = 35632 # Variable c_int '35632'
GL_SYNC_STATUS = 37140 # Variable c_int '37140'
GL_DOUBLE_VEC4 = 36862 # Variable c_int '36862'
GL_UNSIGNED_SHORT_4_4_4_4 = 32819 # Variable c_int '32819'
GL_DOUBLE_VEC2 = 36860 # Variable c_int '36860'
GL_DOUBLE_VEC3 = 36861 # Variable c_int '36861'
GL_FRAGMENT_SHADER_DERIVATIVE_HINT = 35723 # Variable c_int '35723'
GL_TEXTURE_DEPTH = 32881 # Variable c_int '32881'
GL_STENCIL_BACK_REF = 36003 # Variable c_int '36003'
GL_NO_ERROR = 0 # Variable c_int '0'
GL_MIN_PROGRAM_TEXTURE_GATHER_OFFSET_ARB = 36446 # Variable c_int '36446'
GL_PROGRAM_SEPARABLE = 33368 # Variable c_int '33368'
GL_VIEWPORT = 2978 # Variable c_int '2978'
GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME = 36049 # Variable c_int '36049'
GL_MAX_FRAGMENT_INTERPOLATION_OFFSET = 36444 # Variable c_int '36444'
GL_BLEND_SRC_ALPHA = 32971 # Variable c_int '32971'
GL_UNSIGNED_INT_IMAGE_2D = 36963 # Variable c_int '36963'
GL_UNPACK_COMPRESSED_BLOCK_HEIGHT = 37160 # Variable c_int '37160'
GL_ARB_framebuffer_object = 1 # Variable c_int '1'
GL_DRAW_BUFFER7 = 34860 # Variable c_int '34860'
GL_RGBA16UI = 36214 # Variable c_int '36214'
GL_DRAW_BUFFER5 = 34858 # Variable c_int '34858'
GL_DRAW_BUFFER2 = 34855 # Variable c_int '34855'
GL_DRAW_BUFFER3 = 34856 # Variable c_int '34856'
GL_DRAW_BUFFER0 = 34853 # Variable c_int '34853'
GL_DRAW_BUFFER1 = 34854 # Variable c_int '34854'
GL_MAX_DEPTH_TEXTURE_SAMPLES = 37135 # Variable c_int '37135'
GL_COPY = 5379 # Variable c_int '5379'
GL_TEXTURE_BINDING_2D_ARRAY = 35869 # Variable c_int '35869'
GL_DRAW_BUFFER8 = 34861 # Variable c_int '34861'
GL_ARB_shader_stencil_export = 1 # Variable c_int '1'
GL_MAX_DRAW_BUFFERS = 34852 # Variable c_int '34852'
GL_KEEP = 7680 # Variable c_int '7680'
GL_UNKNOWN_CONTEXT_RESET_ARB = 33365 # Variable c_int '33365'
GL_MAX_TEXTURE_BUFFER_SIZE = 35883 # Variable c_int '35883'
GL_MAX_DEBUG_MESSAGE_LENGTH_ARB = 37187 # Variable c_int '37187'
GL_TEXTURE_CUBE_MAP_SEAMLESS = 34895 # Variable c_int '34895'
GL_IMAGE_CUBE_MAP_ARRAY = 36948 # Variable c_int '36948'
GL_GEOMETRY_INPUT_TYPE = 35095 # Variable c_int '35095'
GL_R32UI = 33334 # Variable c_int '33334'
GL_RGBA8_SNORM = 36759 # Variable c_int '36759'
GL_FILL = 6914 # Variable c_int '6914'
GL_INT_SAMPLER_3D = 36299 # Variable c_int '36299'
GL_BACK_RIGHT = 1027 # Variable c_int '1027'
GL_INT_IMAGE_1D = 36951 # Variable c_int '36951'
GL_SRC_COLOR = 768 # Variable c_int '768'
GL_COLOR_LOGIC_OP = 3058 # Variable c_int '3058'
GL_SAMPLER_BINDING = 35097 # Variable c_int '35097'
GL_AND = 5377 # Variable c_int '5377'
GL_DEPTH24_STENCIL8 = 35056 # Variable c_int '35056'
GL_ATOMIC_COUNTER_BUFFER_ACTIVE_ATOMIC_COUNTER_INDICES = 37574 # Variable c_int '37574'
GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_FRAGMENT_SHADER = 37579 # Variable c_int '37579'
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE = 36051 # Variable c_int '36051'
GL_MAJOR_VERSION = 33307 # Variable c_int '33307'
GL_ARB_gpu_shader_fp64 = 1 # Variable c_int '1'
GL_STATIC_COPY = 35046 # Variable c_int '35046'
GL_ACTIVE_ATTRIBUTE_MAX_LENGTH = 35722 # Variable c_int '35722'
GL_EXTENSIONS = 7939 # Variable c_int '7939'
GL_BGR_INTEGER = 36250 # Variable c_int '36250'
GL_BUFFER_SIZE = 34660 # Variable c_int '34660'
GL_PROXY_TEXTURE_3D = 32880 # Variable c_int '32880'
GL_LAYER_PROVOKING_VERTEX = 33374 # Variable c_int '33374'
GL_RGBA4 = 32854 # Variable c_int '32854'
GL_UNIFORM_BUFFER_BINDING = 35368 # Variable c_int '35368'
GL_ARB_texture_compression_bptc = 1 # Variable c_int '1'
GL_UNIFORM_TYPE = 35383 # Variable c_int '35383'
GL_PROXY_TEXTURE_2D = 32868 # Variable c_int '32868'
GL_DELETE_STATUS = 35712 # Variable c_int '35712'
GL_ARB_vertex_array_bgra = 1 # Variable c_int '1'
GL_ANY_SAMPLES_PASSED = 35887 # Variable c_int '35887'
GL_LAST_VERTEX_CONVENTION = 36430 # Variable c_int '36430'
GL_FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE = 33301 # Variable c_int '33301'
GL_MIN_MAP_BUFFER_ALIGNMENT = 37052 # Variable c_int '37052'
GL_DEPTH_BUFFER_BIT = 256 # Variable c_int '256'
GL_STENCIL_BACK_PASS_DEPTH_FAIL = 34818 # Variable c_int '34818'
GL_INT_SAMPLER_CUBE_MAP_ARRAY = 36878 # Variable c_int '36878'
GL_TEXTURE_COMPRESSED_IMAGE_SIZE = 34464 # Variable c_int '34464'
GL_UNIFORM_BUFFER = 35345 # Variable c_int '35345'
GL_MAP_WRITE_BIT = 2 # Variable c_int '2'
GL_VERTEX_ATTRIB_ARRAY_POINTER = 34373 # Variable c_int '34373'
GL_SAMPLE_MASK = 36433 # Variable c_int '36433'
GL_UNIFORM_ATOMIC_COUNTER_BUFFER_INDEX = 37594 # Variable c_int '37594'
GL_TESS_GEN_SPACING = 36471 # Variable c_int '36471'
GL_CCW = 2305 # Variable c_int '2305'
GL_FRONT_RIGHT = 1025 # Variable c_int '1025'
GL_RGB32I = 36227 # Variable c_int '36227'
GL_MAP_INVALIDATE_BUFFER_BIT = 8 # Variable c_int '8'
GL_STENCIL_BACK_FUNC = 34816 # Variable c_int '34816'
GL_FRACTIONAL_ODD = 36475 # Variable c_int '36475'
GL_ARB_texture_compression_rgtc = 1 # Variable c_int '1'
GL_SYNC_GPU_COMMANDS_COMPLETE = 37143 # Variable c_int '37143'
GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE_ARRAY = 36972 # Variable c_int '36972'
GL_RGB9_E5 = 35901 # Variable c_int '35901'
GL_VERTEX_ATTRIB_ARRAY_INTEGER = 35069 # Variable c_int '35069'
GL_SMOOTH_POINT_SIZE_RANGE = 2834 # Variable c_int '2834'
GL_MAX_FRAGMENT_UNIFORM_BLOCKS = 35373 # Variable c_int '35373'
GL_IMAGE_2D_RECT = 36943 # Variable c_int '36943'
GL_MULTISAMPLE = 32925 # Variable c_int '32925'
GL_MAX_GEOMETRY_OUTPUT_VERTICES = 36320 # Variable c_int '36320'
GL_IMAGE_BINDING_ACCESS = 36670 # Variable c_int '36670'
GL_TEXTURE_RED_TYPE = 35856 # Variable c_int '35856'
GL_ONE_MINUS_SRC1_COLOR = 35066 # Variable c_int '35066'
GL_STREAM_READ = 35041 # Variable c_int '35041'
GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN = 35976 # Variable c_int '35976'
GL_TEXTURE23 = 34007 # Variable c_int '34007'
GL_FUNC_SUBTRACT = 32778 # Variable c_int '32778'
GL_R32F = 33326 # Variable c_int '33326'
GL_DRAW_INDIRECT_BUFFER = 36671 # Variable c_int '36671'
GL_ARB_draw_elements_base_vertex = 1 # Variable c_int '1'
GL_STENCIL_INDEX = 6401 # Variable c_int '6401'
GL_MAX_TESS_GEN_LEVEL = 36478 # Variable c_int '36478'
GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH = 35381 # Variable c_int '35381'
GL_IMPLEMENTATION_COLOR_READ_FORMAT = 35739 # Variable c_int '35739'
GL_READ_ONLY = 35000 # Variable c_int '35000'
GL_ATOMIC_COUNTER_BUFFER_START = 37570 # Variable c_int '37570'
GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING = 33296 # Variable c_int '33296'
GL_GEOMETRY_SHADER_INVOCATIONS = 34943 # Variable c_int '34943'
GL_MAX_COMBINED_ATOMIC_COUNTER_BUFFERS = 37585 # Variable c_int '37585'
GL_UNSIGNED_SHORT_5_6_5_REV = 33636 # Variable c_int '33636'
GL_COLOR_ATTACHMENT14 = 36078 # Variable c_int '36078'
GL_HIGH_FLOAT = 36338 # Variable c_int '36338'
GL_RGBA_SNORM = 36755 # Variable c_int '36755'
GL_COLOR_ATTACHMENT11 = 36075 # Variable c_int '36075'
GL_CLAMP_TO_EDGE = 33071 # Variable c_int '33071'
GL_COLOR_ATTACHMENT13 = 36077 # Variable c_int '36077'
GL_COLOR_ATTACHMENT12 = 36076 # Variable c_int '36076'
GL_NEAREST = 9728 # Variable c_int '9728'
GL_SYNC_FLAGS = 37141 # Variable c_int '37141'
GL_VERTEX_ATTRIB_ARRAY_ENABLED = 34338 # Variable c_int '34338'
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER = 36052 # Variable c_int '36052'
GL_MAX_TEXTURE_IMAGE_UNITS = 34930 # Variable c_int '34930'
GL_RGB32F = 34837 # Variable c_int '34837'
GL_FLOAT_MAT2 = 35674 # Variable c_int '35674'
GL_TESS_EVALUATION_SHADER_BIT = 16 # Variable c_int '16'
GL_DEBUG_SEVERITY_HIGH_ARB = 37190 # Variable c_int '37190'
GL_DEPTH = 6145 # Variable c_int '6145'
GL_FLOAT_MAT4 = 35676 # Variable c_int '35676'
GL_RENDERBUFFER_GREEN_SIZE = 36177 # Variable c_int '36177'
GL_MAX_DUAL_SOURCE_DRAW_BUFFERS = 35068 # Variable c_int '35068'
GL_MAX_FRAGMENT_IMAGE_UNIFORMS = 37070 # Variable c_int '37070'
GL_TESS_CONTROL_OUTPUT_VERTICES = 36469 # Variable c_int '36469'
GL_FRAMEBUFFER_ATTACHMENT_RED_SIZE = 33298 # Variable c_int '33298'
GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT = 36054 # Variable c_int '36054'
GL_POLYGON_MODE = 2880 # Variable c_int '2880'
GL_ONE_MINUS_SRC_ALPHA = 771 # Variable c_int '771'
GL_SAMPLER_2D_RECT_SHADOW = 35684 # Variable c_int '35684'
GL_ALL_BARRIER_BITS = 4294967295L # Variable c_uint '4294967295u'
GL_MAX_TESS_PATCH_COMPONENTS = 36484 # Variable c_int '36484'
GL_PROXY_TEXTURE_2D_MULTISAMPLE = 37121 # Variable c_int '37121'
GL_TEXTURE31 = 34015 # Variable c_int '34015'
GL_UNSIGNED_INT_SAMPLER_1D = 36305 # Variable c_int '36305'
GL_RGBA8I = 36238 # Variable c_int '36238'
GL_RG8UI = 33336 # Variable c_int '33336'
GL_DEPTH_CLEAR_VALUE = 2931 # Variable c_int '2931'
GL_ARB_cl_event = 1 # Variable c_int '1'
GL_MAX_TESS_CONTROL_IMAGE_UNIFORMS = 37067 # Variable c_int '37067'
GL_MAX_VERTEX_ATTRIBS = 34921 # Variable c_int '34921'
GL_BUFFER_MAP_POINTER = 35005 # Variable c_int '35005'
GL_LINE_SMOOTH = 2848 # Variable c_int '2848'
GL_R3_G3_B2 = 10768 # Variable c_int '10768'
GL_RENDERBUFFER_BINDING = 36007 # Variable c_int '36007'
GL_TESS_EVALUATION_SHADER = 36487 # Variable c_int '36487'
GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE = 36048 # Variable c_int '36048'
GL_STENCIL_REF = 2967 # Variable c_int '2967'
GL_DEPTH_TEST = 2929 # Variable c_int '2929'
GL_ACTIVE_SUBROUTINE_UNIFORMS = 36326 # Variable c_int '36326'
GL_ELEMENT_ARRAY_BUFFER_BINDING = 34965 # Variable c_int '34965'
GL_DOUBLE_MAT4x2 = 36685 # Variable c_int '36685'
GL_DOUBLE_MAT4x3 = 36686 # Variable c_int '36686'
GL_COPY_WRITE_BUFFER = 36663 # Variable c_int '36663'
GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_TESS_CONTROL_SHADER = 37576 # Variable c_int '37576'
GL_MIRRORED_REPEAT = 33648 # Variable c_int '33648'
GL_SAMPLER_CUBE_SHADOW = 36293 # Variable c_int '36293'
GL_TEXTURE_BINDING_3D = 32874 # Variable c_int '32874'
GL_UNSIGNED_SHORT = 5123 # Variable c_int '5123'
GL_MIN = 32775 # Variable c_int '32775'
GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER = 36060 # Variable c_int '36060'
GL_COMPRESSED_SRGB_ALPHA = 35913 # Variable c_int '35913'
GL_ONE_MINUS_DST_COLOR = 775 # Variable c_int '775'
GL_ONE_MINUS_SRC_COLOR = 769 # Variable c_int '769'
GL_FLOAT_MAT3 = 35675 # Variable c_int '35675'
GL_BLEND_EQUATION_RGB = 32777 # Variable c_int '32777'
GL_TEXTURE = 5890 # Variable c_int '5890'
GL_PROXY_TEXTURE_1D_ARRAY = 35865 # Variable c_int '35865'
GL_RGBA16 = 32859 # Variable c_int '32859'
GL_MAX_CLIP_DISTANCES = 3378 # Variable c_int '3378'
GL_PATCHES = 14 # Variable c_int '14'
GL_ARB_depth_buffer_float = 1 # Variable c_int '1'
GL_TIMESTAMP = 36392 # Variable c_int '36392'
GL_COLOR_BUFFER_BIT = 16384 # Variable c_int '16384'
GL_ATOMIC_COUNTER_BUFFER_ACTIVE_ATOMIC_COUNTERS = 37573 # Variable c_int '37573'
GL_ACTIVE_UNIFORMS = 35718 # Variable c_int '35718'
GL_ACTIVE_SUBROUTINE_UNIFORM_LOCATIONS = 36423 # Variable c_int '36423'
GL_VERTEX_PROGRAM_POINT_SIZE = 34370 # Variable c_int '34370'
GL_MAX_VERTEX_UNIFORM_VECTORS = 36347 # Variable c_int '36347'
GL_TEXTURE_BINDING_CUBE_MAP = 34068 # Variable c_int '34068'
GL_UNSIGNED_INT_ATOMIC_COUNTER = 37595 # Variable c_int '37595'
GL_IMAGE_BUFFER = 36945 # Variable c_int '36945'
GL_PRIMITIVE_RESTART = 36765 # Variable c_int '36765'
GL_SRGB_ALPHA = 35906 # Variable c_int '35906'
GL_DRAW_BUFFER12 = 34865 # Variable c_int '34865'
GL_NEAREST_MIPMAP_NEAREST = 9984 # Variable c_int '9984'
GL_NUM_COMPRESSED_TEXTURE_FORMATS = 34466 # Variable c_int '34466'
GL_RGBA16I = 36232 # Variable c_int '36232'
GL_ARB_map_buffer_alignment = 1 # Variable c_int '1'
GL_PACK_SKIP_ROWS = 3331 # Variable c_int '3331'
GL_IMAGE_BINDING_LAYERED = 36668 # Variable c_int '36668'
GL_TEXTURE_MAG_FILTER = 10240 # Variable c_int '10240'
GL_R8I = 33329 # Variable c_int '33329'
GL_LINEAR_MIPMAP_LINEAR = 9987 # Variable c_int '9987'
GL_UPPER_LEFT = 36002 # Variable c_int '36002'
GL_TRANSFORM_FEEDBACK_BUFFER_ACTIVE = 36388 # Variable c_int '36388'
GL_CONTEXT_COMPATIBILITY_PROFILE_BIT = 2 # Variable c_int '2'
GL_LINK_STATUS = 35714 # Variable c_int '35714'
GL_VERTEX_ATTRIB_ARRAY_DIVISOR = 35070 # Variable c_int '35070'
GL_COMPRESSED_SRGB_ALPHA_BPTC_UNORM_ARB = 36493 # Variable c_int '36493'
GL_CONSTANT_ALPHA = 32771 # Variable c_int '32771'
GL_SYNC_CL_EVENT_ARB = 33344 # Variable c_int '33344'
GL_VERSION = 7938 # Variable c_int '7938'
GL_MAX_TESS_EVALUATION_INPUT_COMPONENTS = 34925 # Variable c_int '34925'
GL_R32I = 33333 # Variable c_int '33333'
GL_TEXTURE_BINDING_2D_MULTISAMPLE_ARRAY = 37125 # Variable c_int '37125'
GL_BLEND_COLOR = 32773 # Variable c_int '32773'
GL_BOOL_VEC4 = 35673 # Variable c_int '35673'
GL_TEXTURE_SWIZZLE_B = 36420 # Variable c_int '36420'
GL_MAX_IMAGE_UNITS = 36664 # Variable c_int '36664'
GL_ONE_MINUS_CONSTANT_ALPHA = 32772 # Variable c_int '32772'
GL_FLOAT_32_UNSIGNED_INT_24_8_REV = 36269 # Variable c_int '36269'
GL_UNSIGNED_INT_IMAGE_1D_ARRAY = 36968 # Variable c_int '36968'
GL_TEXTURE_CUBE_MAP_POSITIVE_Z = 34073 # Variable c_int '34073'
GL_LEFT = 1030 # Variable c_int '1030'
GL_INT_IMAGE_BUFFER = 36956 # Variable c_int '36956'
GL_AND_INVERTED = 5380 # Variable c_int '5380'
GL_BLEND = 3042 # Variable c_int '3042'
GL_MAX_GEOMETRY_OUTPUT_COMPONENTS = 37156 # Variable c_int '37156'
GL_WAIT_FAILED = 37149 # Variable c_int '37149'
GL_SAMPLES_PASSED = 35092 # Variable c_int '35092'
GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = 35379 # Variable c_int '35379'
GL_UNIFORM_BLOCK_NAME_LENGTH = 35393 # Variable c_int '35393'
GL_SAMPLE_ALPHA_TO_COVERAGE = 32926 # Variable c_int '32926'
GL_LOSE_CONTEXT_ON_RESET_ARB = 33362 # Variable c_int '33362'
GL_BOOL_VEC2 = 35671 # Variable c_int '35671'
GL_LINE = 6913 # Variable c_int '6913'
GL_PIXEL_BUFFER_BARRIER_BIT = 128 # Variable c_int '128'
GL_POLYGON_OFFSET_POINT = 10753 # Variable c_int '10753'
GL_BGR = 32992 # Variable c_int '32992'
GL_MAX_TEXTURE_SIZE = 3379 # Variable c_int '3379'
GL_CLAMP_TO_BORDER = 33069 # Variable c_int '33069'
GL_RG32F = 33328 # Variable c_int '33328'
GL_UNSIGNED_INT_SAMPLER_2D_ARRAY = 36311 # Variable c_int '36311'
GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE = 36971 # Variable c_int '36971'
GL_ARRAY_BUFFER = 34962 # Variable c_int '34962'
GL_OR_REVERSE = 5387 # Variable c_int '5387'
GL_DEPTH_COMPONENT16 = 33189 # Variable c_int '33189'
GL_RGBA12 = 32858 # Variable c_int '32858'
GL_DEPTH_COMPONENT24 = 33190 # Variable c_int '33190'
GL_PROXY_TEXTURE_2D_MULTISAMPLE_ARRAY = 37123 # Variable c_int '37123'
GL_BLUE_INTEGER = 36246 # Variable c_int '36246'
GL_TEXTURE_RED_SIZE = 32860 # Variable c_int '32860'
GL_TEXTURE_1D = 3552 # Variable c_int '3552'
GL_MAX_VARYING_COMPONENTS = 35659 # Variable c_int '35659'
GL_SEPARATE_ATTRIBS = 35981 # Variable c_int '35981'
GL_SAMPLER_BUFFER = 36290 # Variable c_int '36290'
GL_BGRA_INTEGER = 36251 # Variable c_int '36251'
GL_IMAGE_3D = 36942 # Variable c_int '36942'
GL_FALSE = 0 # Variable c_int '0'
GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = 35377 # Variable c_int '35377'
GL_PATCH_DEFAULT_OUTER_LEVEL = 36468 # Variable c_int '36468'
GL_RG32I = 33339 # Variable c_int '33339'
GL_UNSIGNED_BYTE_2_3_3_REV = 33634 # Variable c_int '33634'
GL_SAMPLE_ALPHA_TO_ONE = 32927 # Variable c_int '32927'
GL_RENDERBUFFER_INTERNAL_FORMAT = 36164 # Variable c_int '36164'
GL_NUM_SHADER_BINARY_FORMATS = 36345 # Variable c_int '36345'
GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS = 35394 # Variable c_int '35394'
GL_ARB_depth_clamp = 1 # Variable c_int '1'
GL_TEXTURE_HEIGHT = 4097 # Variable c_int '4097'
GL_DOUBLE_MAT2x3 = 36681 # Variable c_int '36681'
GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT = 36055 # Variable c_int '36055'
GL_PROGRAM_POINT_SIZE = 34370 # Variable c_int '34370'
GL_DEBUG_LOGGED_MESSAGES_ARB = 37189 # Variable c_int '37189'
GL_UNPACK_COMPRESSED_BLOCK_DEPTH = 37161 # Variable c_int '37161'
GL_RGBA16F = 34842 # Variable c_int '34842'
GL_DOUBLE_MAT3x4 = 36684 # Variable c_int '36684'
GL_UNIFORM_BLOCK_REFERENCED_BY_GEOMETRY_SHADER = 35397 # Variable c_int '35397'
GL_SAMPLER_1D = 35677 # Variable c_int '35677'
GL_INT_SAMPLER_2D = 36298 # Variable c_int '36298'
GL_UNSIGNED_INT_SAMPLER_1D_ARRAY = 36310 # Variable c_int '36310'
GL_ONE = 1 # Variable c_int '1'
GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR_ARB = 33358 # Variable c_int '33358'
GL_TEXTURE_FIXED_SAMPLE_LOCATIONS = 37127 # Variable c_int '37127'
GL_DOUBLE_MAT3x2 = 36683 # Variable c_int '36683'
GL_STENCIL_PASS_DEPTH_FAIL = 2965 # Variable c_int '2965'
GL_DRAW_INDIRECT_BUFFER_BINDING = 36675 # Variable c_int '36675'
GL_RED = 6403 # Variable c_int '6403'
GL_BLEND_SRC_RGB = 32969 # Variable c_int '32969'
GL_UNSIGNED_INT_IMAGE_CUBE_MAP_ARRAY = 36970 # Variable c_int '36970'
GL_ARB_tessellation_shader = 1 # Variable c_int '1'
GL_ARB_vertex_attrib_64bit = 1 # Variable c_int '1'
GL_MAX_VERTEX_UNIFORM_BLOCKS = 35371 # Variable c_int '35371'
GL_POLYGON_OFFSET_LINE = 10754 # Variable c_int '10754'
GL_FUNC_REVERSE_SUBTRACT = 32779 # Variable c_int '32779'
GL_INT_IMAGE_2D = 36952 # Variable c_int '36952'
GL_LINE_WIDTH = 2849 # Variable c_int '2849'
GL_COLOR_ATTACHMENT15 = 36079 # Variable c_int '36079'
GL_PROGRAM_PIPELINE_BINDING = 33370 # Variable c_int '33370'
GL_GREEN = 6404 # Variable c_int '6404'
GL_INVALID_OPERATION = 1282 # Variable c_int '1282'
GL_MAX_RECTANGLE_TEXTURE_SIZE = 34040 # Variable c_int '34040'
GL_DEBUG_NEXT_LOGGED_MESSAGE_LENGTH_ARB = 33347 # Variable c_int '33347'
GL_FIXED_ONLY = 35101 # Variable c_int '35101'
GL_CLAMP_READ_COLOR = 35100 # Variable c_int '35100'
GL_RED_INTEGER = 36244 # Variable c_int '36244'
GL_NONE = 0 # Variable c_int '0'
GL_FRAMEBUFFER_DEFAULT = 33304 # Variable c_int '33304'
GL_TEXTURE_BINDING_BUFFER = 35884 # Variable c_int '35884'
GL_COLOR_ATTACHMENT5 = 36069 # Variable c_int '36069'
GL_MAX_FRAGMENT_UNIFORM_COMPONENTS = 35657 # Variable c_int '35657'
GL_COLOR_ATTACHMENT7 = 36071 # Variable c_int '36071'
GL_COLOR_ATTACHMENT6 = 36070 # Variable c_int '36070'
GL_COLOR_ATTACHMENT0 = 36064 # Variable c_int '36064'
GL_ARB_shading_language_include = 1 # Variable c_int '1'
GL_COMPRESSED_SRGB = 35912 # Variable c_int '35912'
GL_COLOR_ATTACHMENT9 = 36073 # Variable c_int '36073'
GL_TEXTURE_BINDING_RECTANGLE = 34038 # Variable c_int '34038'
GL_LINE_SMOOTH_HINT = 3154 # Variable c_int '3154'
GL_COMMAND_BARRIER_BIT = 64 # Variable c_int '64'
GL_SHADER_COMPILER = 36346 # Variable c_int '36346'
GL_NAND = 5390 # Variable c_int '5390'
GL_UNIFORM_BLOCK_DATA_SIZE = 35392 # Variable c_int '35392'
GL_BUFFER_USAGE = 34661 # Variable c_int '34661'
GL_MAX_CUBE_MAP_TEXTURE_SIZE = 34076 # Variable c_int '34076'
GL_PATCH_VERTICES = 36466 # Variable c_int '36466'
GL_CULL_FACE_MODE = 2885 # Variable c_int '2885'
GL_MAX_FRAGMENT_UNIFORM_VECTORS = 36349 # Variable c_int '36349'
GL_TRANSFORM_FEEDBACK_BUFFER_BINDING = 35983 # Variable c_int '35983'
GL_MAX_DEBUG_LOGGED_MESSAGES_ARB = 37188 # Variable c_int '37188'
GL_NUM_EXTENSIONS = 33309 # Variable c_int '33309'
GL_IMAGE_BINDING_FORMAT = 36974 # Variable c_int '36974'
GL_UNIFORM_IS_ROW_MAJOR = 35390 # Variable c_int '35390'
GL_MAX_UNIFORM_BLOCK_SIZE = 35376 # Variable c_int '35376'
GL_BOOL = 35670 # Variable c_int '35670'
GL_MAX_COMBINED_UNIFORM_BLOCKS = 35374 # Variable c_int '35374'
GL_TIME_ELAPSED = 35007 # Variable c_int '35007'
GL_ARB_base_instance = 1 # Variable c_int '1'
GL_COMPRESSED_TEXTURE_FORMATS = 34467 # Variable c_int '34467'
GL_TRANSFORM_FEEDBACK_VARYING_MAX_LENGTH = 35958 # Variable c_int '35958'
GL_ALPHA = 6406 # Variable c_int '6406'
GL_SET = 5391 # Variable c_int '5391'
GL_INT_SAMPLER_CUBE_MAP_ARRAY_ARB = 36878 # Variable c_int '36878'
GL_COLOR_WRITEMASK = 3107 # Variable c_int '3107'
GL_COLOR_CLEAR_VALUE = 3106 # Variable c_int '3106'
GL_DST_COLOR = 774 # Variable c_int '774'
GL_ACTIVE_ATOMIC_COUNTER_BUFFERS = 37593 # Variable c_int '37593'
GL_RGB_SNORM = 36754 # Variable c_int '36754'
GL_UNSIGNED_INT = 5125 # Variable c_int '5125'
GL_DEPTH_FUNC = 2932 # Variable c_int '2932'
GL_TEXTURE_WRAP_R = 32882 # Variable c_int '32882'
GL_TEXTURE_WRAP_S = 10242 # Variable c_int '10242'
GL_TEXTURE_WRAP_T = 10243 # Variable c_int '10243'
GL_COMPRESSED_RGB_BPTC_SIGNED_FLOAT_ARB = 36494 # Variable c_int '36494'
GL_INT_SAMPLER_1D = 36297 # Variable c_int '36297'
GL_DST_ALPHA = 772 # Variable c_int '772'
GL_ARB_texture_multisample = 1 # Variable c_int '1'
GL_STENCIL_BACK_VALUE_MASK = 36004 # Variable c_int '36004'
GL_INT_SAMPLER_2D_ARRAY = 36303 # Variable c_int '36303'
GL_UNSIGNED_INT_SAMPLER_CUBE_MAP_ARRAY = 36879 # Variable c_int '36879'
GL_POINT_SPRITE_COORD_ORIGIN = 36000 # Variable c_int '36000'
GL_ATOMIC_COUNTER_BUFFER_SIZE = 37571 # Variable c_int '37571'
GL_POINT_SIZE_RANGE = 2834 # Variable c_int '2834'
GL_TEXTURE_BINDING_1D = 32872 # Variable c_int '32872'
GL_FRONT_FACE = 2886 # Variable c_int '2886'
GL_COMPRESSED_RGB = 34029 # Variable c_int '34029'
GL_DEBUG_SOURCE_APPLICATION_ARB = 33354 # Variable c_int '33354'
GL_DEPTH_COMPONENT = 6402 # Variable c_int '6402'
GL_SRC1_COLOR = 35065 # Variable c_int '35065'
GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES = 35395 # Variable c_int '35395'
GL_ARB_sampler_objects = 1 # Variable c_int '1'
GL_DEBUG_TYPE_ERROR_ARB = 33356 # Variable c_int '33356'
GL_SHADER_TYPE = 35663 # Variable c_int '35663'
GL_RG16_SNORM = 36761 # Variable c_int '36761'
GL_VERTEX_ATTRIB_ARRAY_STRIDE = 34340 # Variable c_int '34340'
GL_CONTEXT_CORE_PROFILE_BIT = 1 # Variable c_int '1'
GL_COMPARE_REF_TO_TEXTURE = 34894 # Variable c_int '34894'
GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE = 36182 # Variable c_int '36182'
GL_FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE = 33297 # Variable c_int '33297'
GL_TRUE = 1 # Variable c_int '1'
GL_TEXTURE_MIN_FILTER = 10241 # Variable c_int '10241'
GL_REPLACE = 7681 # Variable c_int '7681'
GL_SAMPLER_1D_ARRAY = 36288 # Variable c_int '36288'
GL_VERSION_1_2 = 1 # Variable c_int '1'
GL_QUERY_COUNTER_BITS = 34916 # Variable c_int '34916'
GL_RG_INTEGER = 33320 # Variable c_int '33320'
GL_TEXTURE_SWIZZLE_R = 36418 # Variable c_int '36418'
GL_MAX_VERTEX_ATOMIC_COUNTERS = 37586 # Variable c_int '37586'
GL_IMAGE_FORMAT_COMPATIBILITY_TYPE = 37063 # Variable c_int '37063'
GL_UNIFORM_BLOCK_REFERENCED_BY_TESS_CONTROL_SHADER = 34032 # Variable c_int '34032'
GL_PACK_SWAP_BYTES = 3328 # Variable c_int '3328'
GL_EQUAL = 514 # Variable c_int '514'
GL_DEBUG_SOURCE_THIRD_PARTY_ARB = 33353 # Variable c_int '33353'
GL_TEXTURE_SWIZZLE_G = 36419 # Variable c_int '36419'
GL_DEPTH_STENCIL_ATTACHMENT = 33306 # Variable c_int '33306'
GL_RENDERBUFFER_HEIGHT = 36163 # Variable c_int '36163'
GL_MIN_SAMPLE_SHADING_VALUE_ARB = 35895 # Variable c_int '35895'
GL_TEXTURE_BINDING_1D_ARRAY = 35868 # Variable c_int '35868'
GL_INTERLEAVED_ATTRIBS = 35980 # Variable c_int '35980'
GL_TEXTURE_ALPHA_TYPE = 35859 # Variable c_int '35859'
GL_POLYGON_OFFSET_UNITS = 10752 # Variable c_int '10752'
GL_LOW_FLOAT = 36336 # Variable c_int '36336'
GL_LINE_WIDTH_GRANULARITY = 2851 # Variable c_int '2851'
GL_DRAW_BUFFER13 = 34866 # Variable c_int '34866'
GL_COMPRESSED_RED_RGTC1 = 36283 # Variable c_int '36283'
GL_TEXTURE_INTERNAL_FORMAT = 4099 # Variable c_int '4099'
GL_UNSIGNED_INT_10_10_10_2 = 32822 # Variable c_int '32822'
GL_SHADER_SOURCE_LENGTH = 35720 # Variable c_int '35720'
GL_POLYGON_SMOOTH_HINT = 3155 # Variable c_int '3155'
GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS = 35968 # Variable c_int '35968'
GL_INT_SAMPLER_BUFFER = 36304 # Variable c_int '36304'
GL_ATOMIC_COUNTER_BARRIER_BIT = 4096 # Variable c_int '4096'
GL_IMAGE_1D_ARRAY = 36946 # Variable c_int '36946'
GL_TEXTURE_BLUE_TYPE = 35858 # Variable c_int '35858'
GL_UNSIGNED_INT_IMAGE_3D = 36964 # Variable c_int '36964'
GL_UNPACK_ALIGNMENT = 3317 # Variable c_int '3317'
GL_SAMPLER_CUBE_MAP_ARRAY_SHADOW = 36877 # Variable c_int '36877'
GL_ARB_uniform_buffer_object = 1 # Variable c_int '1'
GL_ARB_texture_swizzle = 1 # Variable c_int '1'
GL_STEREO = 3123 # Variable c_int '3123'
GL_ALREADY_SIGNALED = 37146 # Variable c_int '37146'
GL_LINE_STRIP = 3 # Variable c_int '3'
GL_COLOR_ATTACHMENT3 = 36067 # Variable c_int '36067'
GL_STREAM_COPY = 35042 # Variable c_int '35042'
GL_PACK_ROW_LENGTH = 3330 # Variable c_int '3330'
GL_ARB_explicit_attrib_location = 1 # Variable c_int '1'
GL_NUM_SAMPLE_COUNTS = 37760 # Variable c_int '37760'
GL_COLOR_ATTACHMENT2 = 36066 # Variable c_int '36066'
GL_MEDIUM_INT = 36340 # Variable c_int '36340'
GL_TEXTURE_CUBE_MAP = 34067 # Variable c_int '34067'
GL_UNSIGNED_INT_SAMPLER_CUBE_MAP_ARRAY_ARB = 36879 # Variable c_int '36879'
GL_TEXTURE_2D_MULTISAMPLE_ARRAY = 37122 # Variable c_int '37122'
GL_COLOR = 6144 # Variable c_int '6144'
GL_MAX_IMAGE_SAMPLES = 36973 # Variable c_int '36973'
GL_FRAMEBUFFER_COMPLETE = 36053 # Variable c_int '36053'
GL_COMPRESSED_RGBA_BPTC_UNORM_ARB = 36492 # Variable c_int '36492'
GL_R16UI = 33332 # Variable c_int '33332'
GL_DYNAMIC_READ = 35049 # Variable c_int '35049'
GL_TEXTURE_BUFFER = 35882 # Variable c_int '35882'
GL_COPY_READ_BUFFER = 36662 # Variable c_int '36662'
GL_PROGRAM_BINARY_FORMATS = 34815 # Variable c_int '34815'
GL_IMAGE_FORMAT_COMPATIBILITY_BY_CLASS = 37065 # Variable c_int '37065'
GL_LOW_INT = 36339 # Variable c_int '36339'
GL_COLOR_ATTACHMENT8 = 36072 # Variable c_int '36072'
GL_DEPTH_STENCIL = 34041 # Variable c_int '34041'
GL_TRANSFORM_FEEDBACK_BARRIER_BIT = 2048 # Variable c_int '2048'
GL_TEXTURE30 = 34014 # Variable c_int '34014'
GL_MAX_VERTEX_OUTPUT_COMPONENTS = 37154 # Variable c_int '37154'
GL_POINTS = 0 # Variable c_int '0'
GL_READ_WRITE = 35002 # Variable c_int '35002'
GL_RENDERBUFFER_BLUE_SIZE = 36178 # Variable c_int '36178'
GL_UNIFORM_NAME_LENGTH = 35385 # Variable c_int '35385'
GL_FASTEST = 4353 # Variable c_int '4353'
GL_SYNC_CONDITION = 37139 # Variable c_int '37139'
GL_FRONT = 1028 # Variable c_int '1028'
GL_HALF_FLOAT = 5131 # Variable c_int '5131'
GL_ACTIVE_UNIFORM_MAX_LENGTH = 35719 # Variable c_int '35719'
GL_TESS_CONTROL_SHADER_BIT = 8 # Variable c_int '8'
GL_SCISSOR_BOX = 3088 # Variable c_int '3088'
GL_OR = 5383 # Variable c_int '5383'
GL_MAP_INVALIDATE_RANGE_BIT = 4 # Variable c_int '4'
GL_TRANSFORM_FEEDBACK_BUFFER_PAUSED = 36387 # Variable c_int '36387'
GL_TEXTURE22 = 34006 # Variable c_int '34006'
GL_TEXTURE21 = 34005 # Variable c_int '34005'
GL_TEXTURE20 = 34004 # Variable c_int '34004'
GL_TEXTURE27 = 34011 # Variable c_int '34011'
GL_TEXTURE26 = 34010 # Variable c_int '34010'
GL_TEXTURE25 = 34009 # Variable c_int '34009'
GL_TEXTURE24 = 34008 # Variable c_int '34008'
GL_R8_SNORM = 36756 # Variable c_int '36756'
GL_TEXTURE29 = 34013 # Variable c_int '34013'
GL_TEXTURE28 = 34012 # Variable c_int '34012'
GL_ARB_provoking_vertex = 1 # Variable c_int '1'
GL_MAX_3D_TEXTURE_SIZE = 32883 # Variable c_int '32883'
GL_PRIMITIVE_RESTART_INDEX = 36766 # Variable c_int '36766'
GL_DEBUG_SOURCE_API_ARB = 33350 # Variable c_int '33350'
GL_TRIANGLES_ADJACENCY = 12 # Variable c_int '12'
GL_TEXTURE_CUBE_MAP_NEGATIVE_Z = 34074 # Variable c_int '34074'
GL_LINE_LOOP = 2 # Variable c_int '2'
GL_MAX_SUBROUTINE_UNIFORM_LOCATIONS = 36328 # Variable c_int '36328'
GL_QUERY_WAIT = 36371 # Variable c_int '36371'
GL_MAP_FLUSH_EXPLICIT_BIT = 16 # Variable c_int '16'
GL_PACK_SKIP_PIXELS = 3332 # Variable c_int '3332'
GL_RG8I = 33335 # Variable c_int '33335'
GL_UNSIGNED_SHORT_1_5_5_5_REV = 33638 # Variable c_int '33638'
GL_ARB_half_float_vertex = 1 # Variable c_int '1'
GL_UNIFORM_BLOCK_REFERENCED_BY_TESS_EVALUATION_SHADER = 34033 # Variable c_int '34033'
GL_SUBPIXEL_BITS = 3408 # Variable c_int '3408'
GL_TESS_CONTROL_SHADER = 36488 # Variable c_int '36488'
GL_RIGHT = 1031 # Variable c_int '1031'
GL_DEBUG_SOURCE_WINDOW_SYSTEM_ARB = 33351 # Variable c_int '33351'
GL_TEXTURE_MAX_LEVEL = 33085 # Variable c_int '33085'
GL_COMPRESSED_SIGNED_RED_RGTC1 = 36284 # Variable c_int '36284'
GL_TEXTURE_CUBE_MAP_ARRAY = 36873 # Variable c_int '36873'
GL_UNIFORM_BLOCK_BINDING = 35391 # Variable c_int '35391'
GL_MAX_SAMPLE_MASK_WORDS = 36441 # Variable c_int '36441'
GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT = 35380 # Variable c_int '35380'
GL_RGBA8UI = 36220 # Variable c_int '36220'
GL_UNIFORM_OFFSET = 35387 # Variable c_int '35387'
GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY = 37132 # Variable c_int '37132'
GL_UNSIGNED_INT_IMAGE_CUBE = 36966 # Variable c_int '36966'
GL_TEXTURE1 = 33985 # Variable c_int '33985'
GL_LEQUAL = 515 # Variable c_int '515'
GL_TRANSFORM_FEEDBACK = 36386 # Variable c_int '36386'
GL_TEXTURE_CUBE_MAP_ARRAY_ARB = 36873 # Variable c_int '36873'
GL_ARB_transform_feedback2 = 1 # Variable c_int '1'
GL_ARB_transform_feedback3 = 1 # Variable c_int '1'
GL_UNSIGNED_INT_SAMPLER_CUBE = 36308 # Variable c_int '36308'
GL_TEXTURE_WIDTH = 4096 # Variable c_int '4096'
GL_ONE_MINUS_SRC1_ALPHA = 35067 # Variable c_int '35067'
GL_COLOR_ATTACHMENT4 = 36068 # Variable c_int '36068'
GL_UNIFORM_SIZE = 35384 # Variable c_int '35384'
GL_FUNC_ADD = 32774 # Variable c_int '32774'
GL_FLOAT_MAT4x2 = 35689 # Variable c_int '35689'
GL_FLOAT_MAT4x3 = 35690 # Variable c_int '35690'
GL_ARB_conservative_depth = 1 # Variable c_int '1'
GL_BUFFER_ACCESS = 35003 # Variable c_int '35003'
GL_ARB_vertex_array_object = 1 # Variable c_int '1'
GL_COMPRESSED_RG = 33318 # Variable c_int '33318'
GL_UNPACK_SWAP_BYTES = 3312 # Variable c_int '3312'
GL_CURRENT_VERTEX_ATTRIB = 34342 # Variable c_int '34342'
GL_ARRAY_BUFFER_BINDING = 34964 # Variable c_int '34964'
GL_SCISSOR_TEST = 3089 # Variable c_int '3089'
GL_TEXTURE_2D = 3553 # Variable c_int '3553'
GL_MAX_COLOR_TEXTURE_SAMPLES = 37134 # Variable c_int '37134'
GL_BACK_LEFT = 1026 # Variable c_int '1026'
GL_RG_SNORM = 36753 # Variable c_int '36753'
GL_DYNAMIC_DRAW = 35048 # Variable c_int '35048'
GL_MAX_GEOMETRY_ATOMIC_COUNTER_BUFFERS = 37583 # Variable c_int '37583'
GL_OUT_OF_MEMORY = 1285 # Variable c_int '1285'
GL_PATCH_DEFAULT_INNER_LEVEL = 36467 # Variable c_int '36467'
GL_INT_SAMPLER_CUBE = 36300 # Variable c_int '36300'
GL_LINES_ADJACENCY = 10 # Variable c_int '10'
GL_MAX_TESS_CONTROL_ATOMIC_COUNTER_BUFFERS = 37581 # Variable c_int '37581'
GL_VENDOR = 7936 # Variable c_int '7936'
GL_IMPLEMENTATION_COLOR_READ_TYPE = 35738 # Variable c_int '35738'
GL_MAX_GEOMETRY_TOTAL_OUTPUT_COMPONENTS = 36321 # Variable c_int '36321'
GL_UNSIGNED_SHORT_4_4_4_4_REV = 33637 # Variable c_int '33637'
GL_UNPACK_ROW_LENGTH = 3314 # Variable c_int '3314'
GL_UNPACK_COMPRESSED_BLOCK_SIZE = 37162 # Variable c_int '37162'
GL_CURRENT_PROGRAM = 35725 # Variable c_int '35725'
GL_ARB_transform_feedback_instanced = 1 # Variable c_int '1'
GL_BUFFER_MAPPED = 35004 # Variable c_int '35004'
GL_MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS = 35978 # Variable c_int '35978'
GL_UNSIGNED_INT_8_8_8_8_REV = 33639 # Variable c_int '33639'
GL_GEOMETRY_OUTPUT_TYPE = 35096 # Variable c_int '35096'
GL_RASTERIZER_DISCARD = 35977 # Variable c_int '35977'
GL_NUM_PROGRAM_BINARY_FORMATS = 34814 # Variable c_int '34814'
GL_MAX_TEXTURE_LOD_BIAS = 34045 # Variable c_int '34045'
GL_MAX_COMBINED_IMAGE_UNITS_AND_FRAGMENT_OUTPUTS = 36665 # Variable c_int '36665'
GL_STREAM_DRAW = 35040 # Variable c_int '35040'
GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER = 35396 # Variable c_int '35396'
GL_ONE_MINUS_DST_ALPHA = 773 # Variable c_int '773'
GL_TEXTURE_FETCH_BARRIER_BIT = 8 # Variable c_int '8'
GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE = 37130 # Variable c_int '37130'
GL_BUFFER_UPDATE_BARRIER_BIT = 512 # Variable c_int '512'
GL_VERSION_2_1 = 1 # Variable c_int '1'
GL_SIGNALED = 37145 # Variable c_int '37145'
GL_FRAMEBUFFER = 36160 # Variable c_int '36160'
GL_MEDIUM_FLOAT = 36337 # Variable c_int '36337'
GL_INT_SAMPLER_2D_RECT = 36301 # Variable c_int '36301'
GL_STENCIL_TEST = 2960 # Variable c_int '2960'
GL_TEXTURE_BINDING_2D = 32873 # Variable c_int '32873'
GL_VIEWPORT_BOUNDS_RANGE = 33373 # Variable c_int '33373'
GL_QUADS_FOLLOW_PROVOKING_VERTEX_CONVENTION = 36428 # Variable c_int '36428'
GL_R11F_G11F_B10F = 35898 # Variable c_int '35898'
GL_TEXTURE_MIN_LOD = 33082 # Variable c_int '33082'
GL_INT_IMAGE_CUBE = 36955 # Variable c_int '36955'
GL_SRGB8 = 35905 # Variable c_int '35905'
GL_VERSION_4_0 = 1 # Variable c_int '1'
GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR_ARB = 33357 # Variable c_int '33357'
GL_PIXEL_UNPACK_BUFFER_BINDING = 35055 # Variable c_int '35055'
GL_INVERT = 5386 # Variable c_int '5386'
GL_IMAGE_2D_MULTISAMPLE = 36949 # Variable c_int '36949'
GL_RGB32UI = 36209 # Variable c_int '36209'
GL_PROXY_TEXTURE_1D = 32867 # Variable c_int '32867'
GL_STENCIL_BACK_FAIL = 34817 # Variable c_int '34817'
GL_POLYGON_OFFSET_FACTOR = 32824 # Variable c_int '32824'
GL_COLOR_ATTACHMENT1 = 36065 # Variable c_int '36065'
GL_QUERY_BY_REGION_NO_WAIT = 36374 # Variable c_int '36374'
GL_TRANSFORM_FEEDBACK_VARYINGS = 35971 # Variable c_int '35971'
GL_UNSIGNED_INT_IMAGE_BUFFER = 36967 # Variable c_int '36967'
GL_DEPTH_COMPONENT32F = 36012 # Variable c_int '36012'
GL_TRIANGLE_FAN = 6 # Variable c_int '6'
GL_SYNC_FLUSH_COMMANDS_BIT = 1 # Variable c_int '1'
GL_ALWAYS = 519 # Variable c_int '519'
GL_TEXTURE_COMPARE_FUNC = 34893 # Variable c_int '34893'
GL_MAX_GEOMETRY_SHADER_INVOCATIONS = 36442 # Variable c_int '36442'
GL_MAX_TESS_CONTROL_UNIFORM_BLOCKS = 36489 # Variable c_int '36489'
GL_STENCIL_BACK_WRITEMASK = 36005 # Variable c_int '36005'
GL_DEBUG_SOURCE_SHADER_COMPILER_ARB = 33352 # Variable c_int '33352'
GL_SHADER_IMAGE_ACCESS_BARRIER_BIT = 32 # Variable c_int '32'
GL_ARB_sync = 1 # Variable c_int '1'
GL_INVALID_FRAMEBUFFER_OPERATION = 1286 # Variable c_int '1286'
GL_ARB_texture_buffer_object_rgb32 = 1 # Variable c_int '1'
GL_BUFFER_ACCESS_FLAGS = 37151 # Variable c_int '37151'
GL_ARB_draw_buffers_blend = 1 # Variable c_int '1'
GL_UNIFORM_BUFFER_SIZE = 35370 # Variable c_int '35370'
GL_MAX_TRANSFORM_FEEDBACK_BUFFERS = 36464 # Variable c_int '36464'
GL_TRIANGLES = 4 # Variable c_int '4'
GL_SAMPLER_2D_ARRAY_SHADOW = 36292 # Variable c_int '36292'
GL_VERSION_1_3 = 1 # Variable c_int '1'
GL_DEPTH32F_STENCIL8 = 36013 # Variable c_int '36013'
GL_MAX_ARRAY_TEXTURE_LAYERS = 35071 # Variable c_int '35071'
GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING = 34975 # Variable c_int '34975'
GL_UNIFORM_MATRIX_STRIDE = 35389 # Variable c_int '35389'
GL_SAMPLER_CUBE_MAP_ARRAY_SHADOW_ARB = 36877 # Variable c_int '36877'
GL_ARB_shading_language_420pack = 1 # Variable c_int '1'
GL_MIN_FRAGMENT_INTERPOLATION_OFFSET = 36443 # Variable c_int '36443'
GL_MAX_SERVER_WAIT_TIMEOUT = 37137 # Variable c_int '37137'
GL_TEXTURE_BUFFER_FORMAT = 35886 # Variable c_int '35886'
GL_QUERY_BY_REGION_WAIT = 36373 # Variable c_int '36373'
GL_TESS_GEN_VERTEX_ORDER = 36472 # Variable c_int '36472'
GL_ATOMIC_COUNTER_BUFFER_BINDING = 37569 # Variable c_int '37569'
GL_NOR = 5384 # Variable c_int '5384'
GL_SRGB8_ALPHA8 = 35907 # Variable c_int '35907'
GL_TEXTURE_UPDATE_BARRIER_BIT = 256 # Variable c_int '256'
GL_PACK_ALIGNMENT = 3333 # Variable c_int '3333'
GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_GEOMETRY_SHADER = 37578 # Variable c_int '37578'
GL_SAMPLER_2D_ARRAY = 36289 # Variable c_int '36289'
GL_IMAGE_2D_ARRAY = 36947 # Variable c_int '36947'
GL_DEPTH_RANGE = 2928 # Variable c_int '2928'
GL_ARB_sample_shading = 1 # Variable c_int '1'
GL_RENDERER = 7937 # Variable c_int '7937'
GL_UNPACK_LSB_FIRST = 3313 # Variable c_int '3313'
GL_MAX_COLOR_ATTACHMENTS = 36063 # Variable c_int '36063'
GL_BGRA = 32993 # Variable c_int '32993'
GL_ACTIVE_UNIFORM_BLOCKS = 35382 # Variable c_int '35382'
GL_RGB8I = 36239 # Variable c_int '36239'
GL_FRAMEBUFFER_ATTACHMENT_GREEN_SIZE = 33299 # Variable c_int '33299'
GL_UNPACK_SKIP_IMAGES = 32877 # Variable c_int '32877'
GL_COMPATIBLE_SUBROUTINES = 36427 # Variable c_int '36427'
GL_PROXY_TEXTURE_CUBE_MAP_ARRAY_ARB = 36875 # Variable c_int '36875'
GL_ACTIVE_TEXTURE = 34016 # Variable c_int '34016'
GL_ARB_blend_func_extended = 1 # Variable c_int '1'
GL_TEXTURE_BASE_LEVEL = 33084 # Variable c_int '33084'
GL_RGB16F = 34843 # Variable c_int '34843'
GL_PACK_LSB_FIRST = 3329 # Variable c_int '3329'
GL_SMOOTH_LINE_WIDTH_RANGE = 2850 # Variable c_int '2850'
GL_FIRST_VERTEX_CONVENTION = 36429 # Variable c_int '36429'
GL_DRAW_BUFFER6 = 34859 # Variable c_int '34859'
GL_IMAGE_BINDING_LAYER = 36669 # Variable c_int '36669'
GL_CLIP_DISTANCE7 = 12295 # Variable c_int '12295'
GL_MAX_GEOMETRY_ATOMIC_COUNTERS = 37589 # Variable c_int '37589'
GL_ARB_internalformat_query = 1 # Variable c_int '1'
GL_UNSIGNED_INT_SAMPLER_3D = 36307 # Variable c_int '36307'
GL_ARB_ES2_compatibility = 1 # Variable c_int '1'
GL_UNIFORM_BLOCK_INDEX = 35386 # Variable c_int '35386'
GL_DEBUG_TYPE_PERFORMANCE_ARB = 33360 # Variable c_int '33360'
GL_RG16I = 33337 # Variable c_int '33337'
GL_INT_VEC4 = 35669 # Variable c_int '35669'
GL_INT_VEC3 = 35668 # Variable c_int '35668'
GL_INT_VEC2 = 35667 # Variable c_int '35667'
GL_STENCIL_FAIL = 2964 # Variable c_int '2964'
GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS = 35378 # Variable c_int '35378'
GL_VERSION_4_2 = 1 # Variable c_int '1'
GL_MAX_ATOMIC_COUNTER_BUFFER_SIZE = 37592 # Variable c_int '37592'
GL_MAX_TESS_CONTROL_OUTPUT_COMPONENTS = 36483 # Variable c_int '36483'
GL_MAX_UNIFORM_BUFFER_BINDINGS = 35375 # Variable c_int '35375'
GL_CONDITION_SATISFIED = 37148 # Variable c_int '37148'
GL_TEXTURE_IMMUTABLE_FORMAT = 37167 # Variable c_int '37167'
GL_CONTEXT_FLAG_FORWARD_COMPATIBLE_BIT = 1 # Variable c_int '1'
GL_LINE_WIDTH_RANGE = 2850 # Variable c_int '2850'
GL_IMAGE_2D_MULTISAMPLE_ARRAY = 36950 # Variable c_int '36950'
GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT = 1 # Variable c_int '1'
GL_FRAMEBUFFER_UNSUPPORTED = 36061 # Variable c_int '36061'
GL_MAX_ATOMIC_COUNTER_BUFFER_BINDINGS = 37596 # Variable c_int '37596'
GL_NO_RESET_NOTIFICATION_ARB = 33377 # Variable c_int '33377'
GL_MAX_TESS_EVALUATION_OUTPUT_COMPONENTS = 36486 # Variable c_int '36486'
GL_DRAW_BUFFER4 = 34857 # Variable c_int '34857'
GL_DYNAMIC_COPY = 35050 # Variable c_int '35050'
GL_LESS = 513 # Variable c_int '513'
GL_ARB_viewport_array = 1 # Variable c_int '1'
GL_ARB_separate_shader_objects = 1 # Variable c_int '1'
GL_PROGRAM_BINARY_LENGTH = 34625 # Variable c_int '34625'
GL_FRAMEBUFFER_UNDEFINED = 33305 # Variable c_int '33305'
GL_TRANSFORM_FEEDBACK_BINDING = 36389 # Variable c_int '36389'
GL_TEXTURE_1D_ARRAY = 35864 # Variable c_int '35864'
GL_TEXTURE_STENCIL_SIZE = 35057 # Variable c_int '35057'
GL_RENDERBUFFER_WIDTH = 36162 # Variable c_int '36162'
GL_READ_FRAMEBUFFER_BINDING = 36010 # Variable c_int '36010'
GL_FRAMEBUFFER_ATTACHMENT_LAYERED = 36263 # Variable c_int '36263'
GL_UNSIGNED_INT_5_9_9_9_REV = 35902 # Variable c_int '35902'
GL_TEXTURE_BLUE_SIZE = 32862 # Variable c_int '32862'
GL_TEXTURE_DEPTH_TYPE = 35862 # Variable c_int '35862'
GL_SAMPLER_3D = 35679 # Variable c_int '35679'
GL_INT_IMAGE_CUBE_MAP_ARRAY = 36959 # Variable c_int '36959'
GL_RGBA2 = 32853 # Variable c_int '32853'
GL_MAX_PROGRAM_TEXTURE_GATHER_OFFSET_ARB = 36447 # Variable c_int '36447'
GL_INT_SAMPLER_2D_MULTISAMPLE = 37129 # Variable c_int '37129'
GL_EQUIV = 5385 # Variable c_int '5385'
GL_DRAW_BUFFER10 = 34863 # Variable c_int '34863'
GL_DRAW_BUFFER11 = 34864 # Variable c_int '34864'
GL_RGBA8 = 32856 # Variable c_int '32856'
GL_MAX_PROGRAM_TEXTURE_GATHER_OFFSET = 36447 # Variable c_int '36447'
GL_DRAW_BUFFER14 = 34867 # Variable c_int '34867'
GL_DRAW_BUFFER15 = 34868 # Variable c_int '34868'
GL_INT_IMAGE_3D = 36953 # Variable c_int '36953'
GL_INFO_LOG_LENGTH = 35716 # Variable c_int '35716'
GL_RGB_INTEGER = 36248 # Variable c_int '36248'
GL_COLOR_ATTACHMENT10 = 36074 # Variable c_int '36074'
GL_ARB_shader_subroutine = 1 # Variable c_int '1'
GL_DEBUG_SEVERITY_LOW_ARB = 37192 # Variable c_int '37192'
GL_R16F = 33325 # Variable c_int '33325'
GL_RENDERBUFFER_STENCIL_SIZE = 36181 # Variable c_int '36181'
GL_REPEAT = 10497 # Variable c_int '10497'
GL_INT_IMAGE_2D_ARRAY = 36958 # Variable c_int '36958'
GL_R16I = 33331 # Variable c_int '33331'
GL_RG8_SNORM = 36757 # Variable c_int '36757'
GL_POINT_SIZE_GRANULARITY = 2835 # Variable c_int '2835'
GL_STATIC_READ = 35045 # Variable c_int '35045'
GL_VERSION_2_0 = 1 # Variable c_int '1'
GL_DEBUG_SOURCE_OTHER_ARB = 33355 # Variable c_int '33355'
GL_GEOMETRY_SHADER_BIT = 4 # Variable c_int '4'
GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER = 35398 # Variable c_int '35398'
GL_TEXTURE_GREEN_SIZE = 32861 # Variable c_int '32861'
GL_VALIDATE_STATUS = 35715 # Variable c_int '35715'
GL_MAP_READ_BIT = 1 # Variable c_int '1'
GL_RG16 = 33324 # Variable c_int '33324'
GL_ACTIVE_ATTRIBUTES = 35721 # Variable c_int '35721'
GL_MAX_COMBINED_IMAGE_UNIFORMS = 37071 # Variable c_int '37071'
GL_INVALID_INDEX = 4294967295L # Variable c_uint '4294967295u'
GL_INT_IMAGE_1D_ARRAY = 36957 # Variable c_int '36957'
GL_STENCIL_CLEAR_VALUE = 2961 # Variable c_int '2961'
GL_SAMPLE_MASK_VALUE = 36434 # Variable c_int '36434'
GL_STENCIL_BUFFER_BIT = 1024 # Variable c_int '1024'
GL_MAX_GEOMETRY_UNIFORM_COMPONENTS = 36319 # Variable c_int '36319'
GL_TEXTURE_2D_MULTISAMPLE = 37120 # Variable c_int '37120'
GL_SAMPLER_1D_ARRAY_SHADOW = 36291 # Variable c_int '36291'
GL_ARB_texture_query_lod = 1 # Variable c_int '1'
GL_DEBUG_TYPE_PORTABILITY_ARB = 33359 # Variable c_int '33359'
GL_ARB_copy_buffer = 1 # Variable c_int '1'
GL_DEBUG_TYPE_OTHER_ARB = 33361 # Variable c_int '33361'
GL_SAMPLER_2D_MULTISAMPLE_ARRAY = 37131 # Variable c_int '37131'
GL_UNSIGNED_INT_IMAGE_2D_RECT = 36965 # Variable c_int '36965'
GL_POLYGON_OFFSET_FILL = 32823 # Variable c_int '32823'
GL_BLEND_EQUATION_ALPHA = 34877 # Variable c_int '34877'
GL_ACTIVE_SUBROUTINES = 36325 # Variable c_int '36325'
GL_ARB_texture_cube_map_array = 1 # Variable c_int '1'
GL_STENCIL_INDEX1 = 36166 # Variable c_int '36166'
GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS = 36264 # Variable c_int '36264'
GL_QUERY_RESULT_AVAILABLE = 34919 # Variable c_int '34919'
GL_MAX_RENDERBUFFER_SIZE = 34024 # Variable c_int '34024'
GL_STENCIL_PASS_DEPTH_PASS = 2966 # Variable c_int '2966'
GL_INCR_WRAP = 34055 # Variable c_int '34055'
GL_RENDERBUFFER_ALPHA_SIZE = 36179 # Variable c_int '36179'
GL_SAMPLE_SHADING_ARB = 35894 # Variable c_int '35894'
GL_HIGH_INT = 36341 # Variable c_int '36341'
GL_GEQUAL = 518 # Variable c_int '518'
GL_SAMPLER_CUBE_MAP_ARRAY = 36876 # Variable c_int '36876'
GL_ARB_fragment_coord_conventions = 1 # Variable c_int '1'
GL_DECR_WRAP = 34056 # Variable c_int '34056'
GL_MAX_VIEWPORTS = 33371 # Variable c_int '33371'
GL_MAX_VERTEX_UNIFORM_COMPONENTS = 35658 # Variable c_int '35658'
GL_ATTACHED_SHADERS = 35717 # Variable c_int '35717'
GL_ARB_texture_storage = 1 # Variable c_int '1'
GL_SAMPLE_POSITION = 36432 # Variable c_int '36432'
GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY = 37133 # Variable c_int '37133'
GL_MAX_FRAGMENT_ATOMIC_COUNTERS = 37590 # Variable c_int '37590'
GL_MAX_FRAGMENT_INPUT_COMPONENTS = 37157 # Variable c_int '37157'
GL_ARB_shader_image_load_store = 1 # Variable c_int '1'
GL_GUILTY_CONTEXT_RESET_ARB = 33363 # Variable c_int '33363'
GL_VIEWPORT_INDEX_PROVOKING_VERTEX = 33375 # Variable c_int '33375'
GL_SAMPLE_COVERAGE_INVERT = 32939 # Variable c_int '32939'
GL_LINES = 1 # Variable c_int '1'
GL_TEXTURE18 = 34002 # Variable c_int '34002'
GL_TEXTURE19 = 34003 # Variable c_int '34003'
GL_TEXTURE16 = 34000 # Variable c_int '34000'
GL_TEXTURE17 = 34001 # Variable c_int '34001'
GL_TEXTURE14 = 33998 # Variable c_int '33998'
GL_ARB_shader_bit_encoding = 1 # Variable c_int '1'
GL_TEXTURE12 = 33996 # Variable c_int '33996'
GL_TEXTURE13 = 33997 # Variable c_int '33997'
GL_TEXTURE10 = 33994 # Variable c_int '33994'
GL_UNPACK_SKIP_ROWS = 3315 # Variable c_int '3315'
GL_TEXTURE_BINDING_CUBE_MAP_ARRAY_ARB = 36874 # Variable c_int '36874'
GL_SAMPLE_BUFFERS = 32936 # Variable c_int '32936'
GL_DEPTH_CLAMP = 34383 # Variable c_int '34383'
GL_BLEND_DST_ALPHA = 32970 # Variable c_int '32970'
GL_RGB = 6407 # Variable c_int '6407'
GL_TEXTURE_BUFFER_DATA_STORE_BINDING = 35885 # Variable c_int '35885'
GL_ARB_framebuffer_sRGB = 1 # Variable c_int '1'
GL_VERTEX_ATTRIB_ARRAY_NORMALIZED = 34922 # Variable c_int '34922'
GL_RGB5_A1 = 32855 # Variable c_int '32855'
GL_VERTEX_SHADER = 35633 # Variable c_int '35633'
GL_TEXTURE_ALPHA_SIZE = 32863 # Variable c_int '32863'
GL_TRANSFORM_FEEDBACK_BUFFER_START = 35972 # Variable c_int '35972'
GL_COPY_INVERTED = 5388 # Variable c_int '5388'
GL_MAX_PROGRAM_TEXEL_OFFSET = 35077 # Variable c_int '35077'
GL_MAX_GEOMETRY_INPUT_COMPONENTS = 37155 # Variable c_int '37155'
GL_LOWER_LEFT = 36001 # Variable c_int '36001'
GL_TEXTURE_COMPRESSION_HINT = 34031 # Variable c_int '34031'
GL_TEXTURE15 = 33999 # Variable c_int '33999'
GL_POLYGON_SMOOTH = 2881 # Variable c_int '2881'
GL_RGBA32F = 34836 # Variable c_int '34836'
GL_RGBA32I = 36226 # Variable c_int '36226'
GL_VERTEX_ATTRIB_ARRAY_TYPE = 34341 # Variable c_int '34341'
GL_PIXEL_UNPACK_BUFFER = 35052 # Variable c_int '35052'
GL_SAMPLER_2D = 35678 # Variable c_int '35678'
GL_MAX_COMBINED_ATOMIC_COUNTERS = 37591 # Variable c_int '37591'
GL_LINEAR_MIPMAP_NEAREST = 9985 # Variable c_int '9985'
GL_ARB_get_program_binary = 1 # Variable c_int '1'
GL_STENCIL_WRITEMASK = 2968 # Variable c_int '2968'
GL_RG8 = 33323 # Variable c_int '33323'
GL_NAMED_STRING_LENGTH_ARB = 36329 # Variable c_int '36329'
GL_ARB_timer_query = 1 # Variable c_int '1'
GL_PACK_IMAGE_HEIGHT = 32876 # Variable c_int '32876'
GL_DEBUG_CALLBACK_FUNCTION_ARB = 33348 # Variable c_int '33348'
GL_RGB10_A2 = 32857 # Variable c_int '32857'
GL_ACTIVE_SUBROUTINE_MAX_LENGTH = 36424 # Variable c_int '36424'
GL_UNSIGNED_INT_IMAGE_2D_ARRAY = 36969 # Variable c_int '36969'
GL_INVALID_VALUE = 1281 # Variable c_int '1281'
GL_MAX_VERTEX_IMAGE_UNIFORMS = 37066 # Variable c_int '37066'
GL_TEXTURE_CUBE_MAP_NEGATIVE_Y = 34072 # Variable c_int '34072'
GL_VERTEX_SHADER_BIT = 1 # Variable c_int '1'
GL_MAP_UNSYNCHRONIZED_BIT = 32 # Variable c_int '32'
GL_ZERO = 0 # Variable c_int '0'
GL_MAX_TESS_EVALUATION_UNIFORM_BLOCKS = 36490 # Variable c_int '36490'
GL_PIXEL_PACK_BUFFER = 35051 # Variable c_int '35051'
GL_ELEMENT_ARRAY_BUFFER = 34963 # Variable c_int '34963'
GL_UNSIGNED_INT_2_10_10_10_REV = 33640 # Variable c_int '33640'
GL_CLEAR = 5376 # Variable c_int '5376'
GL_BUFFER_MAP_LENGTH = 37152 # Variable c_int '37152'
GL_ARB_texture_rgb10_a2ui = 1 # Variable c_int '1'
GL_DOUBLE_MAT2x4 = 36682 # Variable c_int '36682'
GL_MAX_VERTEX_STREAMS = 36465 # Variable c_int '36465'
GL_INNOCENT_CONTEXT_RESET_ARB = 33364 # Variable c_int '33364'
GL_ARB_debug_output = 1 # Variable c_int '1'
GL_MAX_ELEMENTS_INDICES = 33001 # Variable c_int '33001'
GL_DEBUG_OUTPUT_SYNCHRONOUS_ARB = 33346 # Variable c_int '33346'
GL_UNSIGNED_NORMALIZED = 35863 # Variable c_int '35863'
GL_SMOOTH_POINT_SIZE_GRANULARITY = 2835 # Variable c_int '2835'
GL_SRC_ALPHA = 770 # Variable c_int '770'
GL_TEXTURE_3D = 32879 # Variable c_int '32879'
GL_FIXED = 5132 # Variable c_int '5132'
GL_GEOMETRY_VERTICES_OUT = 35094 # Variable c_int '35094'
GL_MAX_TESS_CONTROL_TEXTURE_IMAGE_UNITS = 36481 # Variable c_int '36481'
GL_RGB8 = 32849 # Variable c_int '32849'
GL_MAX_FRAGMENT_ATOMIC_COUNTER_BUFFERS = 37584 # Variable c_int '37584'
GL_MAX_TESS_EVALUATION_IMAGE_UNIFORMS = 37068 # Variable c_int '37068'
GL_ARB_robustness = 1 # Variable c_int '1'
GL_NOTEQUAL = 517 # Variable c_int '517'
GL_UNIFORM_ARRAY_STRIDE = 35388 # Variable c_int '35388'
GL_TEXTURE_SAMPLES = 37126 # Variable c_int '37126'
GL_RGB4 = 32847 # Variable c_int '32847'
GL_RGB5 = 32848 # Variable c_int '32848'
GL_INCR = 7682 # Variable c_int '7682'
GL_CULL_FACE = 2884 # Variable c_int '2884'
GL_COMPRESSED_RED = 33317 # Variable c_int '33317'
GL_INT_SAMPLER_1D_ARRAY = 36302 # Variable c_int '36302'
GL_SAMPLE_COVERAGE_VALUE = 32938 # Variable c_int '32938'
GL_ARB_compressed_texture_pixel_storage = 1 # Variable c_int '1'
GL_RGBA16_SNORM = 36763 # Variable c_int '36763'
GL_RENDERBUFFER_RED_SIZE = 36176 # Variable c_int '36176'
GL_MAX_VIEWPORT_DIMS = 3386 # Variable c_int '3386'
GL_ARB_texture_gather = 1 # Variable c_int '1'
GL_TEXTURE_SWIZZLE_A = 36421 # Variable c_int '36421'
GL_GREATER = 516 # Variable c_int '516'
GL_TEXTURE_BORDER_COLOR = 4100 # Variable c_int '4100'
GL_SAMPLE_SHADING = 35894 # Variable c_int '35894'
GL_COMPRESSED_SIGNED_RG_RGTC2 = 36286 # Variable c_int '36286'
GL_WRITE_ONLY = 35001 # Variable c_int '35001'
GL_TEXTURE11 = 33995 # Variable c_int '33995'
GL_RG32UI = 33340 # Variable c_int '33340'
GL_FRAGMENT_INTERPOLATION_OFFSET_BITS = 36445 # Variable c_int '36445'
GL_TEXTURE_BINDING_CUBE_MAP_ARRAY = 36874 # Variable c_int '36874'
GL_NEVER = 512 # Variable c_int '512'
GL_UNSIGNED_INT_IMAGE_1D = 36962 # Variable c_int '36962'
GL_STENCIL_VALUE_MASK = 2963 # Variable c_int '2963'
GL_BLEND_DST = 3040 # Variable c_int '3040'
GL_ELEMENT_ARRAY_BARRIER_BIT = 2 # Variable c_int '2'
GL_MAX_ELEMENTS_VERTICES = 33000 # Variable c_int '33000'
GL_CONTEXT_FLAG_ROBUST_ACCESS_BIT_ARB = 4 # Variable c_int '4'
GL_SAMPLER_CUBE_MAP_ARRAY_ARB = 36876 # Variable c_int '36876'
GL_SYNC_CL_EVENT_COMPLETE_ARB = 33345 # Variable c_int '33345'
GL_MAX_TESS_EVALUATION_UNIFORM_COMPONENTS = 36480 # Variable c_int '36480'
GL_DRAW_BUFFER9 = 34862 # Variable c_int '34862'
GL_TEXTURE_SHARED_SIZE = 35903 # Variable c_int '35903'
GL_COMPILE_STATUS = 35713 # Variable c_int '35713'
GL_LOGIC_OP_MODE = 3056 # Variable c_int '3056'
GL_ARB_seamless_cube_map = 1 # Variable c_int '1'
GL_RENDERBUFFER_DEPTH_SIZE = 36180 # Variable c_int '36180'
GL_FRAMEBUFFER_BARRIER_BIT = 1024 # Variable c_int '1024'
GL_PACK_COMPRESSED_BLOCK_SIZE = 37166 # Variable c_int '37166'
GL_STENCIL_ATTACHMENT = 36128 # Variable c_int '36128'
GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS = 35660 # Variable c_int '35660'
GL_PACK_COMPRESSED_BLOCK_HEIGHT = 37164 # Variable c_int '37164'
GL_ARB_occlusion_query2 = 1 # Variable c_int '1'
GL_TEXTURE_SWIZZLE_RGBA = 36422 # Variable c_int '36422'
GL_DEPTH_COMPONENT32 = 33191 # Variable c_int '33191'
GL_RGBA = 6408 # Variable c_int '6408'
GL_SHORT = 5122 # Variable c_int '5122'
GL_READ_FRAMEBUFFER = 36008 # Variable c_int '36008'
GL_CW = 2304 # Variable c_int '2304'
GL_UNSIGNED_INT_24_8 = 34042 # Variable c_int '34042'
GL_UNSIGNED_BYTE = 5121 # Variable c_int '5121'
GL_VIEWPORT_SUBPIXEL_BITS = 33372 # Variable c_int '33372'
GL_MAX_PATCH_VERTICES = 36477 # Variable c_int '36477'
GL_FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE = 33302 # Variable c_int '33302'
GL_IMAGE_1D = 36940 # Variable c_int '36940'
GL_NICEST = 4354 # Variable c_int '4354'
GL_UNIFORM_BARRIER_BIT = 4 # Variable c_int '4'
GL_ARB_draw_indirect = 1 # Variable c_int '1'
GL_VERSION_3_2 = 1 # Variable c_int '1'
GL_UNSIGNED_INT_10F_11F_11F_REV = 35899 # Variable c_int '35899'
GL_R16 = 33322 # Variable c_int '33322'
GL_OBJECT_TYPE = 37138 # Variable c_int '37138'
GL_ISOLINES = 36474 # Variable c_int '36474'
GL_GEOMETRY_SHADER = 36313 # Variable c_int '36313'
GL_ACTIVE_PROGRAM = 33369 # Variable c_int '33369'
GL_R8UI = 33330 # Variable c_int '33330'
GL_STATIC_DRAW = 35044 # Variable c_int '35044'
GL_VERSION_1_5 = 1 # Variable c_int '1'
GL_VERSION_1_4 = 1 # Variable c_int '1'
GL_PACK_SKIP_IMAGES = 32875 # Variable c_int '32875'
GL_RENDERBUFFER = 36161 # Variable c_int '36161'
GL_VERSION_1_1 = 1 # Variable c_int '1'
GL_VERSION_1_0 = 1 # Variable c_int '1'
GL_FLOAT_MAT2x3 = 35685 # Variable c_int '35685'
GL_UNSIGNED_BYTE_3_3_2 = 32818 # Variable c_int '32818'
GL_FLOAT_MAT2x4 = 35686 # Variable c_int '35686'
GL_TESS_GEN_POINT_MODE = 36473 # Variable c_int '36473'
GL_TESS_GEN_MODE = 36470 # Variable c_int '36470'
GL_TRANSFORM_FEEDBACK_BUFFER_SIZE = 35973 # Variable c_int '35973'
GL_DRAW_BUFFER = 3073 # Variable c_int '3073'
GL_VERSION_3_1 = 1 # Variable c_int '1'
GL_VERSION_3_0 = 1 # Variable c_int '1'
GL_VERSION_3_3 = 1 # Variable c_int '1'
GL_PRIMITIVES_GENERATED = 35975 # Variable c_int '35975'
GL_AND_REVERSE = 5378 # Variable c_int '5378'
GL_STENCIL_INDEX4 = 36167 # Variable c_int '36167'
GL_POINT_FADE_THRESHOLD_SIZE = 33064 # Variable c_int '33064'
GL_MAX = 32776 # Variable c_int '32776'
GL_TEXTURE_GREEN_TYPE = 35857 # Variable c_int '35857'
GL_STENCIL_INDEX8 = 36168 # Variable c_int '36168'
GL_MAX_INTEGER_SAMPLES = 37136 # Variable c_int '37136'
GL_MIN_PROGRAM_TEXTURE_GATHER_OFFSET = 36446 # Variable c_int '36446'
GL_PROXY_TEXTURE_CUBE_MAP_ARRAY = 36875 # Variable c_int '36875'
GL_OR_INVERTED = 5389 # Variable c_int '5389'
GL_RGB8UI = 36221 # Variable c_int '36221'
GL_RED_SNORM = 36752 # Variable c_int '36752'
GL_STENCIL_INDEX16 = 36169 # Variable c_int '36169'
GL_SHADER_INCLUDE_ARB = 36270 # Variable c_int '36270'
GL_NUM_COMPATIBLE_SUBROUTINES = 36426 # Variable c_int '36426'
GL_XOR = 5382 # Variable c_int '5382'
GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_TESS_EVALUATION_SHADER = 37577 # Variable c_int '37577'
GL_INT_IMAGE_2D_RECT = 36954 # Variable c_int '36954'
GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS = 35881 # Variable c_int '35881'
GL_UNPACK_COMPRESSED_BLOCK_WIDTH = 37159 # Variable c_int '37159'
GL_ARB_gpu_shader5 = 1 # Variable c_int '1'
GL_SAMPLER_1D_SHADOW = 35681 # Variable c_int '35681'
GL_BLEND_DST_RGB = 32968 # Variable c_int '32968'
GL_SAMPLER_2D_SHADOW = 35682 # Variable c_int '35682'
GL_CLIP_DISTANCE6 = 12294 # Variable c_int '12294'
GL_MAX_GEOMETRY_UNIFORM_BLOCKS = 35372 # Variable c_int '35372'
GL_RG16F = 33327 # Variable c_int '33327'
GL_SAMPLER_CUBE = 35680 # Variable c_int '35680'
GL_MAX_VERTEX_ATOMIC_COUNTER_BUFFERS = 37580 # Variable c_int '37580'
GL_BLEND_SRC = 3041 # Variable c_int '3041'
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL = 36050 # Variable c_int '36050'
GL_ACTIVE_SUBROUTINE_UNIFORM_MAX_LENGTH = 36425 # Variable c_int '36425'
GL_LINEAR = 9729 # Variable c_int '9729'
GL_PIXEL_PACK_BUFFER_BINDING = 35053 # Variable c_int '35053'
GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_VERTEX_SHADER = 37575 # Variable c_int '37575'
GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS = 35661 # Variable c_int '35661'
GL_MAX_TESS_EVALUATION_ATOMIC_COUNTER_BUFFERS = 37582 # Variable c_int '37582'
GL_TEXTURE_2D_ARRAY = 35866 # Variable c_int '35866'
GL_SAMPLE_COVERAGE = 32928 # Variable c_int '32928'
GL_UNDEFINED_VERTEX = 33376 # Variable c_int '33376'
GL_MAX_TESS_CONTROL_ATOMIC_COUNTERS = 37587 # Variable c_int '37587'
GL_DRAW_FRAMEBUFFER = 36009 # Variable c_int '36009'
GL_IMAGE_BINDING_NAME = 36666 # Variable c_int '36666'
GL_SAMPLES = 32937 # Variable c_int '32937'
GL_TEXTURE_LOD_BIAS = 34049 # Variable c_int '34049'
GL_CURRENT_QUERY = 34917 # Variable c_int '34917'
GL_RGB10_A2UI = 36975 # Variable c_int '36975'
__GLsync._fields_ = [
]
__all__ = ['glCopyTexImage1D', 'GLsizei', 'glStencilMaskSeparate',
           'GL_DITHER', 'GL_FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE',
           'glCompressedTexSubImage3D', 'GLboolean',
           'GL_INT_IMAGE_2D_MULTISAMPLE', 'glTextureStorage3DEXT',
           'GL_PROXY_TEXTURE_2D_MULTISAMPLE', 'GL_TEXTURE_MAX_LOD',
           'GLchar', 'GL_SAMPLER_2D_RECT', 'GL_RGB9_E5',
           'GL_TEXTURE_COMPRESSED', 'GL_ALL_BARRIER_BITS',
           'GL_RGBA32UI', 'GL_TEXTURE_MIN_LOD',
           'glDrawElementsInstancedBaseInstance',
           'GL_TEXTURE_CUBE_MAP_POSITIVE_Y',
           'GL_TEXTURE_CUBE_MAP_POSITIVE_X', 'GL_BLEND_EQUATION',
           'GL_BYTE', 'GL_IMAGE_FORMAT_COMPATIBILITY_BY_SIZE',
           'glVertexAttribP4ui', 'GL_TIMEOUT_IGNORED', 'glIsBuffer',
           'glGetMultisamplefv', 'glProgramUniformMatrix4fv',
           'GL_DEBUG_NEXT_LOGGED_MESSAGE_LENGTH_ARB',
           'GL_COLOR_CLEAR_VALUE', 'GL_BUFFER_USAGE',
           'GL_WAIT_FAILED', 'GL_TRANSFORM_FEEDBACK_BUFFER_BINDING',
           'GL_ATOMIC_COUNTER_BUFFER_DATA_SIZE',
           'GL_TEXTURE_BINDING_2D_MULTISAMPLE',
           'GL_TRIANGLE_STRIP_ADJACENCY',
           'GL_MAX_TESS_EVALUATION_ATOMIC_COUNTERS',
           'GL_TRANSFORM_FEEDBACK_BUFFER', 'glMinSampleShadingARB',
           'GL_PROVOKING_VERTEX', 'GL_SIGNED_NORMALIZED',
           'GL_RG_SNORM', 'glVertexAttrib4ubv',
           'glGetBufferParameteriv', 'GLhalfARB', 'GL_POINT_SIZE',
           'GL_TEXTURE_COMPARE_FUNC', 'GL_RGB12', 'GL_RGB10',
           'GL_RGB16', 'GL_POLYGON_OFFSET_FILL', 'glVertexAttribL4d',
           'GL_FIRST_VERTEX_CONVENTION', 'GLfloat',
           'GL_FRAGMENT_SHADER_BIT', 'glUniformMatrix3dv',
           'GL_DOUBLE_MAT4', 'GL_DOUBLE_MAT2', 'GL_DOUBLE_MAT3',
           'glResumeTransformFeedback', 'GL_SHADING_LANGUAGE_VERSION',
           'GL_MIN_SAMPLE_SHADING_VALUE',
           'GL_UNSIGNED_SHORT_1_5_5_5_REV', 'glVertexAttribI2i',
           'GL_CONTEXT_CORE_PROFILE_BIT',
           'GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS',
           'GL_FRAGMENT_SHADER_DERIVATIVE_HINT', 'GL_TEXTURE_DEPTH',
           'glIsEnabled', 'glStencilOp', 'glFramebufferTexture2D',
           'GL_DRAW_BUFFER6', 'GL_DRAW_BUFFER7', 'GL_DRAW_BUFFER4',
           'GL_DRAW_BUFFER5', 'GL_DRAW_BUFFER2', 'GL_DRAW_BUFFER3',
           'GL_DRAW_BUFFER0', 'GL_DRAW_BUFFER1', 'GL_COPY',
           'GL_DRAW_BUFFER8', 'GL_ARB_shader_stencil_export',
           'GL_TEXTURE_CUBE_MAP_SEAMLESS', 'GL_TEXTURE_RECTANGLE',
           'GL_FILL', 'GL_INT_IMAGE_1D', 'GL_SRC_COLOR',
           'GL_SAMPLER_BINDING', 'glGetAttachedShaders',
           'GL_ATOMIC_COUNTER_BUFFER_ACTIVE_ATOMIC_COUNTER_INDICES',
           'GL_SAMPLE_BUFFERS', 'glDeleteVertexArrays',
           'GL_RGBA_INTEGER', 'GL_ARB_gpu_shader_fp64',
           'glGetnMapdvARB', 'GL_ACTIVE_ATTRIBUTE_MAX_LENGTH',
           'GL_EXTENSIONS', 'glViewportArrayv', 'GL_UPPER_LEFT',
           'GL_DEPTH_BUFFER_BIT', 'GL_STENCIL_BACK_PASS_DEPTH_FAIL',
           'GL_INT_SAMPLER_CUBE_MAP_ARRAY', 'GL_UNIFORM_BUFFER',
           'GL_CCW', 'glDebugMessageInsertARB',
           'GL_DEPTH_COMPONENT24', 'glUniform2dv',
           'GL_VERTEX_ATTRIB_ARRAY_INTEGER',
           'GL_FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE', 'GL_R32I',
           'GL_R32F', 'GL_MAX_VIEWPORTS', 'glGetPointerv',
           'GL_MAX_VARYING_COMPONENTS', 'glGetUniformfv',
           'glGetUniformuiv',
           'GL_MAX_COMBINED_ATOMIC_COUNTER_BUFFERS',
           'glGetnUniformfvARB', 'GL_RGBA_SNORM',
           'glCompileShaderIncludeARB', 'glDrawElementsInstanced',
           'GL_FLOAT_MAT3', 'GL_DEPTH', 'GL_FLOAT_MAT4',
           'glGetRenderbufferParameteriv',
           'GL_MAX_TESS_PATCH_COMPONENTS', 'GL_RG8I', 'GL_RGBA8I',
           'glFenceSync', 'GL_ARB_cl_event', 'GL_RG32F',
           'GL_VERSION_4_2', 'glVertexAttrib3sv',
           'glValidateProgramPipeline',
           'GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_TESS_CONTROL_SHADER',
           'GL_SAMPLER_CUBE_SHADOW', 'GL_TEXTURE_BINDING_3D',
           'glGenSamplers', 'GL_TEXTURE',
           'glDrawTransformFeedbackInstanced',
           'GL_MAX_CLIP_DISTANCES', 'GLsizeiptr',
           'GL_ARB_depth_buffer_float', 'glDrawTransformFeedback',
           'GL_ACTIVE_UNIFORMS', 'glGetTexParameterIuiv',
           'glVertexAttrib4Nbv', 'GL_UNSIGNED_INT_ATOMIC_COUNTER',
           'glIsSync', 'GL_NUM_COMPRESSED_TEXTURE_FORMATS',
           'GL_BLEND_EQUATION_RGB', 'GL_TEXTURE_MAX_LEVEL',
           'GL_TRANSFORM_FEEDBACK_BARRIER_BIT', 'glVertexAttribL3d',
           'GL_MAX_IMAGE_UNITS', 'GL_TEXTURE_CUBE_MAP_POSITIVE_Z',
           'GL_INT_IMAGE_BUFFER', 'GL_MAX_GEOMETRY_OUTPUT_COMPONENTS',
           'glProgramUniform1ui', 'GL_LINE',
           'GL_PIXEL_BUFFER_BARRIER_BIT',
           'GL_MAX_COMBINED_TESS_CONTROL_UNIFORM_COMPONENTS',
           'GL_UNSIGNED_INT_SAMPLER_1D_ARRAY',
           'GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE', 'glUniform4uiv',
           'GL_BLUE_INTEGER', 'glVertexAttribL1dv', 'GL_SYNC_FLAGS',
           'GL_PATCH_DEFAULT_OUTER_LEVEL', 'GL_RG32I',
           'GL_UNSIGNED_BYTE_2_3_3_REV',
           'GL_RENDERBUFFER_INTERNAL_FORMAT', 'glScissorArrayv',
           'GL_DEBUG_LOGGED_MESSAGES_ARB', 'GLubyte',
           'GL_RENDERBUFFER_WIDTH',
           'GL_UNIFORM_BLOCK_REFERENCED_BY_GEOMETRY_SHADER',
           'GL_SAMPLE_ALPHA_TO_COVERAGE',
           'GL_DRAW_INDIRECT_BUFFER_BINDING',
           'GL_ARB_tessellation_shader', 'GL_INT_IMAGE_2D',
           'GL_ARB_vertex_attrib_64bit', 'glMapBuffer',
           'GL_INVALID_OPERATION', 'GL_CLAMP_READ_COLOR',
           'GL_RED_INTEGER', 'glDeleteSync',
           'GL_TEXTURE_BINDING_BUFFER', 'GL_COLOR_ATTACHMENT5',
           'GL_COLOR_ATTACHMENT4', 'GL_COLOR_ATTACHMENT7',
           'GL_COLOR_ATTACHMENT6', 'glUniformMatrix4x2dv',
           'GL_COLOR_ATTACHMENT0', 'GL_COLOR_ATTACHMENT3',
           'GL_COLOR_ATTACHMENT2', 'glUniform3iv',
           'GL_COLOR_ATTACHMENT9', 'GL_COLOR_ATTACHMENT8',
           'glPolygonMode', 'GL_DEPTH_WRITEMASK', 'GL_PATCH_VERTICES',
           'GL_CULL_FACE_MODE', 'GL_TEXTURE_1D_ARRAY',
           'glProgramUniform4iv', 'uint64_t',
           'GL_MIN_MAP_BUFFER_ALIGNMENT', 'glUseProgram',
           'glGetProgramInfoLog', 'GL_RGB_SNORM', 'GL_FLOAT_MAT3x2',
           'GL_ALWAYS', 'GL_COMPRESSED_RGB_BPTC_SIGNED_FLOAT_ARB',
           'GL_POINT_SPRITE_COORD_ORIGIN', 'GL_POINT_SIZE_RANGE',
           'GL_DEBUG_SOURCE_APPLICATION_ARB',
           'GL_DEBUG_TYPE_ERROR_ARB', 'GL_SHADER_TYPE',
           'glDeleteShader', 'GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE',
           'GL_UNIFORM_BLOCK_REFERENCED_BY_TESS_CONTROL_SHADER',
           'GL_MAX_VERTEX_STREAMS', 'glUniform2ui',
           'glVertexAttribI3i', 'GL_RG16UI', 'glVertexAttribI4usv',
           'glTexParameterf', 'glTexParameteri', 'glGetShaderSource',
           'GL_STENCIL_BACK_REF', 'GLclampf', 'GLbyte', 'GLclampd',
           'GL_STEREO', 'GL_ALREADY_SIGNALED',
           'GL_ARB_explicit_attrib_location', 'GL_MEDIUM_INT',
           'GL_TEXTURE_CUBE_MAP', 'glVertexAttribP1uiv',
           'glLinkProgram', 'GL_MAX_IMAGE_SAMPLES',
           'glDebugMessageCallbackARB', 'glGetString',
           'GL_TEXTURE_BUFFER', 'GL_PACK_COMPRESSED_BLOCK_WIDTH',
           'glEndQuery', 'GL_POINTS', 'glVertexAttribI2ui',
           'GL_MAP_UNSYNCHRONIZED_BIT', 'glDeleteTextures',
           'GL_RENDERBUFFER_BLUE_SIZE', 'GL_UNIFORM_NAME_LENGTH',
           'glVertexAttrib4f', 'glVertexAttrib4d', 'GL_SCISSOR_BOX',
           'GL_LINE_WIDTH_GRANULARITY', 'glBeginConditionalRender',
           'GL_MAX_3D_TEXTURE_SIZE', 'glSamplerParameteri',
           'GL_DONT_CARE', 'glSamplerParameterf', 'glUniform1f',
           'glUniform1d', 'glGetCompressedTexImage',
           'GL_UNSIGNED_SHORT_5_5_5_1', 'glUniform1i',
           'GL_UNIFORM_BLOCK_BINDING', 'GL_LINE_WIDTH', 'GLint64EXT',
           'GL_LEQUAL', 'GL_ARB_transform_feedback2',
           'GL_ARB_transform_feedback3', 'GL_ONE_MINUS_SRC1_ALPHA',
           'glCullFace', 'glProgramUniform4i', 'GL_ARB_timer_query',
           'glProgramUniform4f', 'glViewportIndexedf',
           'glProgramUniform4d', 'glVertexAttribI2uiv',
           'GL_CURRENT_VERTEX_ATTRIB', 'glAttachShader',
           'glQueryCounter', 'GL_LINES_ADJACENCY',
           'GL_IMPLEMENTATION_COLOR_READ_TYPE',
           'GL_UNSIGNED_SHORT_4_4_4_4_REV',
           'GL_UNPACK_COMPRESSED_BLOCK_SIZE', 'glVertexAttribI4sv',
           'glDrawTransformFeedbackStreamInstanced',
           'GL_LINE_STRIP_ADJACENCY', 'glTexParameterIuiv',
           'GL_INT_IMAGE_CUBE_MAP_ARRAY', 'GL_VIEWPORT_BOUNDS_RANGE',
           'GL_QUADS_FOLLOW_PROVOKING_VERTEX_CONVENTION',
           'GL_PIXEL_UNPACK_BUFFER_BINDING',
           'GL_TRANSFORM_FEEDBACK_VARYINGS',
           'GL_MAX_TESS_CONTROL_TEXTURE_IMAGE_UNITS',
           'glIsTransformFeedback',
           'GL_MAX_GEOMETRY_SHADER_INVOCATIONS',
           'GL_MAX_TESS_CONTROL_UNIFORM_BLOCKS',
           'glIsProgramPipeline', 'GL_STENCIL_BACK_WRITEMASK',
           'GL_INVALID_FRAMEBUFFER_OPERATION', 'GLintptr',
           'glUniformMatrix3fv', 'glGetnMapfvARB',
           'GL_DEPTH32F_STENCIL8', 'GL_MAX_ARRAY_TEXTURE_LAYERS',
           'GL_IMAGE_BINDING_NAME',
           'GL_INT_SAMPLER_CUBE_MAP_ARRAY_ARB',
           'GL_MAX_SERVER_WAIT_TIMEOUT',
           'GL_UNSIGNED_INT_2_10_10_10_REV', 'GL_NOR',
           'glGetNamedStringARB', 'GL_TEXTURE_UPDATE_BARRIER_BIT',
           'GL_PACK_ALIGNMENT', 'glVertexAttribL2d', 'glStencilFunc',
           'GL_UNPACK_LSB_FIRST', 'glGetProgramPipelineiv',
           'GL_ACTIVE_TEXTURE', 'GL_TEXTURE_BASE_LEVEL',
           'glGetShaderInfoLog', 'GL_UNSIGNED_INT_SAMPLER_3D',
           'glVertexAttribI4i', 'GL_INT_VEC4', 'GL_INT_VEC3',
           'GL_INT_VEC2', 'GL_STENCIL_FAIL', 'GL_DOUBLEBUFFER',
           'glBlendEquationSeparate', 'GL_VERSION_4_0',
           'GL_VERSION_4_1', 'glGetSubroutineIndex',
           'glVertexAttrib2sv', 'GL_IMAGE_2D_MULTISAMPLE_ARRAY',
           'GL_FRAMEBUFFER_UNSUPPORTED', 'GLushort',
           'GL_ARB_viewport_array', 'GL_ARB_separate_shader_objects',
           'GL_MAX_CUBE_MAP_TEXTURE_SIZE', 'glGetnUniformdvARB',
           'GL_TEXTURE_BLUE_SIZE', 'GLsizeiptrARB', 'glDeleteBuffers',
           'glBindProgramPipeline', 'glScissor', 'glGetBooleanv',
           'GL_DRAW_BUFFER10', 'GL_DRAW_BUFFER11', 'GL_DRAW_BUFFER12',
           'GL_DRAW_BUFFER13', 'GL_UNSIGNED_INT_10_10_10_2',
           'GL_DRAW_BUFFER15', 'GL_INT_IMAGE_3D',
           'GL_SRC_ALPHA_SATURATE', 'GL_CONSTANT_ALPHA', 'GL_R16I',
           'glGetStringi',
           'GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER',
           'GL_SCISSOR_TEST', 'glPointParameterfv', 'glUniform2fv',
           'GL_STENCIL_CLEAR_VALUE', 'GL_SAMPLE_MASK_VALUE',
           'glBindBufferRange', 'glVertexAttribL3dv',
           'glGetUniformdv', 'GL_ARB_texture_cube_map_array',
           'GL_MAX_RENDERBUFFER_SIZE', 'GL_INCR_WRAP',
           'GL_RENDERBUFFER_ALPHA_SIZE', 'GL_HIGH_INT',
           'GL_SAMPLE_SHADING_ARB', 'GL_SAMPLE_POSITION',
           'GL_MAX_FRAGMENT_ATOMIC_COUNTERS',
           'GL_ARB_shader_image_load_store',
           'GL_GUILTY_CONTEXT_RESET_ARB', 'GL_INCR',
           'glClientWaitSync', 'GL_MAX_RECTANGLE_TEXTURE_SIZE',
           'GL_UNPACK_SKIP_ROWS', 'GL_UNSIGNED_INT_IMAGE_3D',
           'glBlendFunciARB', 'glVertexAttrib4Nsv',
           'GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_GEOMETRY_SHADER',
           'GL_BLEND_DST_ALPHA', 'glGetUniformSubroutineuiv',
           'GL_INT_SAMPLER_CUBE', 'GL_TEXTURE14', 'GL_DECR_WRAP',
           'GL_CURRENT_QUERY', 'GL_COLOR_ATTACHMENT10',
           'GL_VERTEX_SHADER', 'GL_RGB16UI', 'GL_COPY_INVERTED',
           'glIsSampler', 'GL_MAX_GEOMETRY_INPUT_COMPONENTS',
           'GL_LOWER_LEFT', 'glCopyTexSubImage1D',
           'glCheckFramebufferStatus', 'GL_TEXTURE_BINDING_1D',
           'GL_PIXEL_UNPACK_BUFFER', 'glBindImageTexture',
           'GL_TEXTURE_BUFFER_DATA_STORE_BINDING',
           'glDrawRangeElements', 'glSamplerParameterIiv',
           'GL_VERTEX_SHADER_BIT', 'GL_ZERO',
           'GL_ELEMENT_ARRAY_BUFFER', 'GL_TESS_CONTROL_SHADER_BIT',
           'GL_BUFFER_MAP_LENGTH', 'glMultiDrawArrays',
           'GL_READ_ONLY', 'GL_MAX_FRAGMENT_IMAGE_UNIFORMS',
           'glDeleteNamedStringARB', 'GL_FIXED', 'glVertexAttribL1d',
           'glVertexAttribI3uiv', 'GL_COMPRESSED_RED', 'GL_BGR',
           'GL_RGBA16_SNORM', 'GL_MAX_VIEWPORT_DIMS', 'glBeginQuery',
           'glBindBuffer', 'GL_TEXTURE_BORDER_COLOR',
           'glUniformMatrix2x4fv', 'GL_ACTIVE_ATOMIC_COUNTER_BUFFERS',
           'GL_ELEMENT_ARRAY_BARRIER_BIT', 'GL_MAX_ELEMENTS_VERTICES',
           'glDepthRangeIndexed', 'glGetError', 'GL_COMPILE_STATUS',
           'GL_LOGIC_OP_MODE', 'glGetTexLevelParameterfv',
           'glGetnColorTableARB', 'GL_READ_WRITE', 'GL_UNSIGNED_BYTE',
           'GLuint64EXT', 'glProgramUniform2ui',
           'glProgramUniform4ui', 'GL_PIXEL_PACK_BUFFER',
           'glStencilMask', 'GL_PACK_LSB_FIRST', 'GL_VERSION_1_3',
           'GL_VERSION_1_2', 'GL_VERSION_1_1', 'GL_VERSION_1_0',
           'GL_UNSIGNED_BYTE_3_3_2',
           'GL_PROXY_TEXTURE_CUBE_MAP_ARRAY_ARB',
           'GL_TRANSFORM_FEEDBACK_BUFFER_SIZE', 'GL_DRAW_BUFFER',
           'GL_VERSION_3_1', 'GL_VERSION_3_0', 'GL_VERSION_3_3',
           'GL_STENCIL_INDEX1', 'GL_STENCIL_INDEX4',
           'GL_TEXTURE_GREEN_TYPE', 'GL_STENCIL_INDEX8',
           'GL_DEPTH_CLAMP', 'GL_RGB8UI', 'GL_STENCIL_INDEX16',
           'GL_INT_IMAGE_2D_RECT', 'GL_ARB_gpu_shader5',
           'GL_BLEND_DST_RGB', 'GL_CLEAR', 'glPixelStoref',
           'GL_DRAW_BUFFER9', 'glPatchParameterfv',
           'GL_PIXEL_PACK_BUFFER_BINDING',
           'GL_CONTEXT_FLAG_ROBUST_ACCESS_BIT_ARB',
           'GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS',
           'glVertexAttribI3ui', 'GL_RGB5_A1',
           'GL_VERTEX_ATTRIB_ARRAY_SIZE',
           'GL_MAX_GEOMETRY_IMAGE_UNIFORMS', 'GL_FLOAT_VEC2',
           'GL_FLOAT_VEC3', 'GL_FLOAT_VEC4', 'glProgramParameteri',
           'GL_BUFFER_MAP_OFFSET', 'GL_BUFFER_SIZE',
           'GL_UNSIGNED_INT_SAMPLER_BUFFER',
           'GL_UNIFORM_BUFFER_START',
           'GL_MAX_TESS_CONTROL_OUTPUT_COMPONENTS',
           'GL_UNSIGNED_INT_SAMPLER_2D',
           'GL_MAX_TESS_CONTROL_UNIFORM_COMPONENTS', 'GL_DOUBLE',
           'glCreateShader', 'glGenRenderbuffers',
           'glCopyTexSubImage2D', 'glBlendFuncSeparate',
           'GL_MAX_SAMPLES', 'GL_NOOP', 'GL_CONTEXT_FLAGS',
           'GL_ALL_SHADER_BITS', 'glPointSize',
           'glGetProgramPipelineInfoLog', 'GL_ARB_map_buffer_range',
           'glVertexAttrib4Nuiv', 'glRenderbufferStorage',
           'glWaitSync', 'GL_QUERY_WAIT', 'glUniform3i',
           'glBlendEquationSeparatei', 'glUniform3d', 'glUniform3f',
           'GL_MAX_TEXTURE_LOD_BIAS', 'GL_ALIASED_LINE_WIDTH_RANGE',
           'GLint', 'glGetFragDataIndex', 'GL_POINT',
           'GL_LINEAR_MIPMAP_NEAREST',
           'GL_RESET_NOTIFICATION_STRATEGY_ARB',
           'GL_SMOOTH_LINE_WIDTH_GRANULARITY', 'GL_SRGB',
           'GL_ARB_texture_storage', 'GL_ONE_MINUS_CONSTANT_COLOR',
           'GL_UNSIGNED_INT_8_8_8_8',
           'GL_MAX_TESS_CONTROL_INPUT_COMPONENTS',
           'glDeleteFramebuffers', 'glDrawArrays',
           'GL_UNSIGNED_INT_SAMPLER_2D_RECT', 'glGetnTexImageARB',
           'glClear', 'glBlendFuncSeparateiARB', 'glVertexAttribP2ui',
           'GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME',
           'GL_BLEND_SRC_ALPHA', 'GL_UNSIGNED_INT_IMAGE_2D',
           'glVertexAttrib4Nub', 'GL_AND_REVERSE', 'glBindBufferBase',
           'glTexImage1D', 'GL_QUERY_RESULT_AVAILABLE',
           'GL_RGBA8_SNORM', 'GL_INT_SAMPLER_3D',
           'glGetQueryObjecti64v', 'GL_AND', 'glIsRenderbuffer',
           'GL_STATIC_COPY', 'glIsVertexArray',
           'glDisableVertexAttribArray',
           'GL_ARB_texture_compression_bptc', 'glStencilOpSeparate',
           'GL_ONE_MINUS_DST_ALPHA', 'glVertexAttribI4ubv',
           'GL_SYNC_GPU_COMMANDS_COMPLETE',
           'GL_VERTEX_ATTRIB_ARRAY_POINTER',
           'GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE_ARRAY',
           'GL_MAX_GEOMETRY_OUTPUT_VERTICES',
           'GL_DRAW_INDIRECT_BUFFER',
           'GL_IMPLEMENTATION_COLOR_READ_FORMAT', 'glPolygonOffset',
           'glGetVertexAttribIiv', 'GL_COMPRESSED_TEXTURE_FORMATS',
           'GL_UNSIGNED_INT_SAMPLER_CUBE_MAP_ARRAY',
           'GL_DEBUG_SEVERITY_HIGH_ARB', 'glPatchParameteri',
           'GL_TESS_CONTROL_OUTPUT_VERTICES',
           'GL_SAMPLER_2D_RECT_SHADOW', 'GL_TEXTURE30',
           'GL_TEXTURE31', 'GL_UNSIGNED_INT_SAMPLER_1D',
           'GL_BACK_LEFT', 'GL_MAX_TESS_CONTROL_IMAGE_UNIFORMS',
           'GL_BUFFER_MAP_POINTER', 'glTextureStorage2DEXT',
           'GLbitfield', 'GL_ARB_provoking_vertex', 'GL_STENCIL_REF',
           'GL_ACTIVE_SUBROUTINE_UNIFORMS',
           'glBlendEquationSeparateiARB', 'GL_DOUBLE_MAT4x2',
           'GL_DOUBLE_MAT4x3', 'GL_COPY_WRITE_BUFFER',
           'glStencilFuncSeparate', 'GL_PROXY_TEXTURE_1D_ARRAY',
           'GLint64',
           'GL_ATOMIC_COUNTER_BUFFER_ACTIVE_ATOMIC_COUNTERS',
           'GL_ACTIVE_SUBROUTINE_UNIFORM_LOCATIONS',
           'GL_PROGRAM_SEPARABLE', 'GL_MAX_VERTEX_UNIFORM_VECTORS',
           'glVertexAttribI3iv', 'glUniform2i', 'glUniform2f',
           'glUniform2d', 'GL_TEXTURE_MAG_FILTER',
           'glFramebufferTextureLayer', 'GL_ONE_MINUS_SRC1_COLOR',
           'GL_STREAM_READ', 'glProgramUniform2fv', 'GL_SAMPLER_CUBE',
           'glProgramUniformMatrix2x4dv', 'GL_INT_2_10_10_10_REV',
           'GL_LEFT', 'GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS',
           'glGetInteger64i_v', 'glBlitFramebuffer', 'glIsEnabledi',
           'GL_MAX_TEXTURE_SIZE', 'GL_ARRAY_BUFFER', 'GLintptrARB',
           'GL_OR_REVERSE', 'GL_TEXTURE_COMPRESSED_IMAGE_SIZE',
           'GL_TEXTURE_1D', 'GL_BLEND_SRC_RGB',
           'glProgramUniformMatrix3fv',
           'GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS',
           'glBindFragDataLocation', 'GL_SAMPLE_ALPHA_TO_ONE',
           'GL_NUM_SHADER_BINARY_FORMATS', 'glGetnPolygonStippleARB',
           'GL_INT_SAMPLER_2D', 'GL_SAMPLER_2D_MULTISAMPLE',
           'GL_DOUBLE_MAT3x2', 'GL_STENCIL_PASS_DEPTH_FAIL',
           'GL_INT_IMAGE_2D_MULTISAMPLE_ARRAY', 'GL_DOUBLE_MAT3x4',
           'GL_IMAGE_2D_MULTISAMPLE',
           'GL_MAX_GEOMETRY_UNIFORM_BLOCKS',
           'GL_UNSIGNED_SHORT_5_6_5_REV', 'GL_FIXED_ONLY', 'GL_NONE',
           'glCopyTexSubImage3D', 'GL_POLYGON_MODE', 'GL_HALF_FLOAT',
           'GL_NAND', 'GL_UNIFORM_BLOCK_DATA_SIZE',
           'glGetActiveUniformBlockiv', 'GL_UNIFORM_IS_ROW_MAJOR',
           'GL_MAX_UNIFORM_BLOCK_SIZE',
           'GL_FRAGMENT_INTERPOLATION_OFFSET_BITS', 'GL_ALPHA',
           'GL_MIN_FRAGMENT_INTERPOLATION_OFFSET',
           'GL_COLOR_WRITEMASK', 'glBindVertexArray',
           'GL_UNSIGNED_INT_IMAGE_1D', 'GL_MAX_TEXTURE_IMAGE_UNITS',
           'GL_TEXTURE_WRAP_R', 'GL_TEXTURE_WRAP_S',
           'GL_TEXTURE_WRAP_T', 'GL_DST_ALPHA', 'GL_FLOAT_MAT2',
           'GL_ARB_texture_multisample', 'GL_INT_SAMPLER_2D_ARRAY',
           'GL_COMPRESSED_RGB', 'GL_SRC1_COLOR',
           'glUniformMatrix2x4dv', 'glViewport',
           'GL_TEXTURE_SWIZZLE_R', 'GL_PACK_SWAP_BYTES', 'GL_EQUAL',
           'GL_TEXTURE_SWIZZLE_G', 'GL_MIN_SAMPLE_SHADING_VALUE_ARB',
           'GL_TEXTURE_BINDING_1D_ARRAY', 'GL_TEXTURE_SWIZZLE_B',
           'GL_TEXTURE_SWIZZLE_A', 'GL_LOW_FLOAT',
           'glGetActiveSubroutineUniformiv',
           'GL_POINT_FADE_THRESHOLD_SIZE', 'GL_INT_SAMPLER_BUFFER',
           'glTexBuffer', 'glPixelStorei', 'glValidateProgram',
           'glActiveShaderProgram',
           'GL_SAMPLER_CUBE_MAP_ARRAY_SHADOW', 'GL_LINE_STRIP',
           'GL_PACK_ROW_LENGTH', 'glBindTexture', 'GL_COLOR',
           'GL_DYNAMIC_READ', 'glDetachShader',
           'glUniformMatrix3x4dv', 'GL_DEPTH_STENCIL',
           'GL_SYNC_CONDITION', 'GL_ACTIVE_UNIFORM_MAX_LENGTH',
           'glViewportIndexedfv', 'GL_MAP_INVALIDATE_RANGE_BIT',
           'GL_TEXTURE23', 'GL_TEXTURE22', 'GL_TEXTURE21',
           'GL_TEXTURE20', 'GL_TEXTURE27', 'GL_TEXTURE26',
           'GL_TEXTURE25', 'GL_TEXTURE24', 'GL_R8_SNORM',
           'GL_TEXTURE29', 'GL_TEXTURE28', 'glDrawElementsBaseVertex',
           'GL_ELEMENT_ARRAY_BUFFER_BINDING',
           'GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER',
           'GL_TRIANGLES_ADJACENCY', 'glSampleCoverage',
           'GL_IMAGE_2D_ARRAY', 'glTexStorage1D', 'GL_READ_BUFFER',
           'GL_PACK_SKIP_PIXELS', 'GL_ARB_half_float_vertex',
           'GL_TESS_CONTROL_SHADER', 'GL_GEQUAL', 'glGetUniformiv',
           'GL_RGBA8UI', 'GL_R16F', 'GL_TRANSFORM_FEEDBACK',
           'glUniform4ui', 'glBindFramebuffer',
           'GL_TEXTURE_COMPRESSION_HINT', 'GL_COMPRESSED_RED_RGTC1',
           'GL_UNSIGNED_INT_24_8', 'GL_ARB_conservative_depth',
           'GL_ARRAY_BUFFER_BINDING', 'GL_TEXTURE_2D',
           'glScissorIndexed', 'GL_DYNAMIC_DRAW',
           'GL_MAX_GEOMETRY_TOTAL_OUTPUT_COMPONENTS',
           'GL_UNPACK_ROW_LENGTH', 'GL_CURRENT_PROGRAM',
           'GL_BUFFER_MAPPED', 'glCreateShaderProgramv',
           'glGetQueryObjectiv', 'GL_STREAM_DRAW',
           'GL_ARB_ES2_compatibility',
           'GL_MAX_UNIFORM_BUFFER_BINDINGS', 'glGenerateMipmap',
           'GL_BUFFER_UPDATE_BARRIER_BIT', 'GL_SIGNALED',
           'GL_FRAMEBUFFER', 'glPointParameteri', 'GL_R16',
           'glUnmapBuffer', 'glPointParameterf',
           'GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR_ARB',
           'GL_ARB_shader_bit_encoding', 'GL_STENCIL_BACK_FAIL',
           'glVertexAttribP4uiv', 'GL_SYNC_FLUSH_COMMANDS_BIT',
           'glReleaseShaderCompiler', 'glReadPixels',
           'GL_SHADER_IMAGE_ACCESS_BARRIER_BIT', 'GL_VERSION_1_5',
           'GL_VERSION_1_4', 'GL_ATOMIC_COUNTER_BUFFER_SIZE',
           'GL_UNIFORM_MATRIX_STRIDE',
           'GL_MAX_TESS_CONTROL_ATOMIC_COUNTERS',
           'GL_MAX_DEPTH_TEXTURE_SAMPLES', 'GL_QUERY_BY_REGION_WAIT',
           'GL_TESS_GEN_VERTEX_ORDER', 'glReadnPixelsARB',
           'glUseProgramStages', 'glReadBuffer',
           'GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_TESS_EVALUATION_SHADER',
           'glBlendEquationiARB', 'GL_MAX_GEOMETRY_ATOMIC_COUNTERS',
           'GL_DEBUG_TYPE_PERFORMANCE_ARB', 'glGetBufferSubData',
           'GLDEBUGPROCARB',
           'GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS',
           'glTextureStorage1DEXT', 'GL_MAX_VERTEX_ATTRIBS',
           'glGenBuffers', 'glGetnConvolutionFilterARB',
           'GL_LINE_WIDTH_RANGE', 'GL_XOR', 'glTexImage3D',
           'glIsFramebuffer', 'glGenFramebuffers', 'GL_LESS',
           'GL_VERSION_3_2', 'GL_FRAMEBUFFER_UNDEFINED',
           'GL_TEXTURE_STENCIL_SIZE', 'glGetnPixelMapuivARB',
           'GL_INT_SAMPLER_1D',
           'GL_MAX_PROGRAM_TEXTURE_GATHER_OFFSET_ARB',
           'glGetBufferParameteri64v', 'glProgramUniform4dv',
           'GL_DEBUG_SEVERITY_LOW_ARB', 'GL_REPEAT', 'GL_OR_INVERTED',
           'glProgramUniform3uiv', 'GL_DEBUG_SOURCE_OTHER_ARB',
           'GL_VALIDATE_STATUS', 'GL_RG16', 'GL_UNPACK_SKIP_IMAGES',
           'GL_TEXTURE_2D_MULTISAMPLE', 'GL_SAMPLER_1D_ARRAY_SHADOW',
           'GL_BLEND_EQUATION_ALPHA', 'GL_ACTIVE_ATTRIBUTES',
           'glVertexAttrib4Nusv', 'glColorMask',
           'GL_ARB_fragment_coord_conventions', 'GL_ATTACHED_SHADERS',
           'glBlendFunci', 'GL_QUERY_BY_REGION_NO_WAIT',
           'GL_FLOAT_MAT2x3', 'GL_VIEWPORT_INDEX_PROVOKING_VERTEX',
           'GL_SAMPLE_COVERAGE_INVERT', 'GL_LINES', 'GL_TEXTURE18',
           'GL_TEXTURE19', 'GL_TEXTURE16', 'GL_TEXTURE17',
           'glGetFloati_v', 'GL_TEXTURE15', 'GL_TEXTURE12',
           'GL_TEXTURE13', 'GL_TEXTURE10', 'GL_TEXTURE11',
           'glGetUniformLocation', 'GL_RGB', 'glUniform4fv',
           'GL_ARB_framebuffer_sRGB',
           'GL_TRANSFORM_FEEDBACK_BUFFER_START',
           'GL_MAX_PROGRAM_TEXEL_OFFSET', 'GL_POLYGON_OFFSET_FACTOR',
           'GL_RGBA32F', 'GL_RGBA32I', 'GL_VERTEX_ATTRIB_ARRAY_TYPE',
           'glEndConditionalRender', 'GL_STENCIL_WRITEMASK', 'GL_RG8',
           'glProgramUniform2uiv', 'glGetQueryObjectuiv',
           'GL_UNSIGNED_INT_IMAGE_2D_ARRAY', 'glVertexAttrib4iv',
           'GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE',
           'glProgramUniform1uiv', 'glFramebufferTexture',
           'GL_PRIMITIVE_RESTART',
           'GL_UNIFORM_ATOMIC_COUNTER_BUFFER_INDEX',
           'GL_TRANSFORM_FEEDBACK_BUFFER_PAUSED', 'GL_TEXTURE_3D',
           'glDepthMask', 'glProgramUniformMatrix2x4fv',
           'GL_ARB_robustness', 'glGetnSeparableFilterARB',
           'glProgramUniform2dv',
           'GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_FRAGMENT_SHADER',
           'glActiveTexture', 'GL_SAMPLE_SHADING',
           'GL_CLIP_DISTANCE3', 'GL_RG32UI', 'glUniformMatrix2fv',
           'GL_TEXTURE_INTERNAL_FORMAT', 'glGetFloatv',
           'GL_FRAMEBUFFER_COMPLETE', 'GL_FRAMEBUFFER_BARRIER_BIT',
           'GL_COPY_READ_BUFFER', 'GL_PACK_COMPRESSED_BLOCK_HEIGHT',
           'GL_ARB_occlusion_query2', 'GL_SUBPIXEL_BITS',
           'glGetnCompressedTexImageARB', 'glGetIntegerv',
           'GL_TRANSFORM_FEEDBACK_BUFFER_ACTIVE',
           'GL_MAX_PATCH_VERTICES',
           'GL_MIN_PROGRAM_TEXTURE_GATHER_OFFSET_ARB',
           'glProgramUniformMatrix3dv', 'GL_NICEST',
           'GL_UNIFORM_BARRIER_BIT', 'GL_ARB_draw_indirect',
           'glIsQuery', 'GL_INT_IMAGE_CUBE', 'glTexImage2D',
           'GL_PACK_SKIP_IMAGES', 'glIsTexture',
           'glVertexAttrib4Nubv', 'GL_FLOAT_MAT2x4',
           'GL_PRIMITIVES_GENERATED', 'GL_RED_SNORM',
           'GL_SHADER_INCLUDE_ARB', 'glGetSubroutineUniformLocation',
           'glGetSamplerParameteriv', 'glCopyBufferSubData',
           'glVertexAttribI1uiv', 'GL_BLEND_COLOR',
           'glDeleteProgramPipelines',
           'GL_ACTIVE_SUBROUTINE_UNIFORM_MAX_LENGTH',
           'glGetActiveUniform', 'GL_TEXTURE_LOD_BIAS',
           'GL_COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_ARB',
           'GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER',
           'GL_FRAMEBUFFER_ATTACHMENT_BLUE_SIZE',
           'glMinSampleShading', 'glFramebufferRenderbuffer',
           'GL_QUERY_RESULT', 'GL_R16_SNORM', 'glGetDoublei_v',
           'glVertexAttrib1sv', 'glBindSampler', 'glLineWidth',
           'glGetIntegeri_v', 'glGetTransformFeedbackVarying',
           'GL_IMAGE_2D', 'GL_RGB16_SNORM',
           'GL_MAX_VERTEX_UNIFORM_BLOCKS', 'glDepthRangef',
           'glEnablei', 'GL_TEXTURE_BINDING_CUBE_MAP',
           'glProgramUniformMatrix2dv', 'GL_RENDERBUFFER_SAMPLES',
           'GL_RG', 'GL_UNSIGNED_INT_IMAGE_CUBE',
           'GL_MAX_COMBINED_TESS_EVALUATION_UNIFORM_COMPONENTS',
           'GL_PACK_COMPRESSED_BLOCK_DEPTH', 'GL_GREEN_INTEGER',
           'GL_TEXTURE_DEPTH_SIZE', 'glSampleMaski',
           'GL_FLOAT_MAT3x4', 'glUniformMatrix3x2fv',
           'glGetInternalformativ', 'GL_COMPRESSED_RGBA',
           'glVertexAttrib2dv', 'glUniformMatrix3x4fv',
           'GL_MAX_COLOR_ATTACHMENTS', 'GL_QUERY_NO_WAIT',
           'GL_UNPACK_SWAP_BYTES', 'glCopyTexImage2D', 'glColorMaski',
           'GL_TRANSFORM_FEEDBACK_BUFFER_MODE',
           'GL_MAX_GEOMETRY_UNIFORM_COMPONENTS', 'glTexStorage3D',
           'GL_IMAGE_BINDING_LEVEL', 'GL_R8',
           'GL_MAX_PROGRAM_TEXTURE_GATHER_OFFSET', 'GL_RGB_INTEGER',
           'GL_STENCIL', 'GLshort', 'GL_SYNC_CL_EVENT_COMPLETE_ARB',
           'glProgramUniformMatrix4x3fv', 'glVertexAttribI4iv',
           'GL_ARB_vertex_type_2_10_10_10_rev', 'GL_FRAGMENT_SHADER',
           'GL_SYNC_STATUS', 'glGetActiveUniformName', 'GL_VIEWPORT',
           'GL_MAX_FRAGMENT_INTERPOLATION_OFFSET',
           'GL_UNPACK_COMPRESSED_BLOCK_HEIGHT',
           'glGetFramebufferAttachmentParameteriv', 'GL_RGB8I',
           'GL_BLEND_SRC', 'GL_UNKNOWN_CONTEXT_RESET_ARB',
           'glTexParameteriv', 'glGetTexImage',
           'glGetNamedStringivARB', 'GL_INT_SAMPLER_2D_RECT',
           'GL_DEPTH24_STENCIL8', 'GL_GEOMETRY_SHADER_INVOCATIONS',
           'GL_PACK_IMAGE_HEIGHT', 'glProgramUniform2iv',
           'glGetQueryiv', 'glGetSamplerParameterfv', 'GL_RGBA16F',
           'GL_TEXTURE_COMPARE_MODE', 'GL_ANY_SAMPLES_PASSED',
           'GL_FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE',
           'glGetUniformIndices', 'glPointParameteriv',
           'GL_MAP_WRITE_BIT', 'GL_ARB_texture_compression_rgtc',
           'GLhalfNV', 'GL_IMAGE_BINDING_ACCESS',
           'glVertexAttribP3ui', 'GL_TESS_GEN_SPACING', 'GL_LINEAR',
           'glGetVertexAttribLdv', 'GL_ARB_draw_elements_base_vertex',
           'GL_STENCIL_INDEX', 'GL_ATOMIC_COUNTER_BUFFER_START',
           'GLhandleARB', 'glDepthRange', 'GL_HIGH_FLOAT',
           'GL_GREATER', 'glDrawBuffer',
           'GL_VERTEX_ATTRIB_ARRAY_ENABLED', 'glClearBufferuiv',
           'GL_TESS_EVALUATION_SHADER_BIT', 'GL_FRONT_FACE',
           'GL_REPLACE', 'GL_VERTEX_ATTRIB_ARRAY_STRIDE',
           'GL_FRAMEBUFFER_ATTACHMENT_RED_SIZE', 'glFlush',
           'glDrawElementsInstancedBaseVertexBaseInstance',
           'GL_RENDERBUFFER_BINDING', 'GL_TESS_EVALUATION_SHADER',
           'glGetTexLevelParameteriv', 'GL_BLEND', 'GL_R16UI',
           'GL_UNSIGNED_SHORT', 'GL_MIN', 'GL_COMPRESSED_SRGB_ALPHA',
           'GL_ONE_MINUS_SRC_COLOR', 'glClampColor', 'glClearStencil',
           'GL_PATCHES', 'GL_TIMESTAMP',
           'GL_VERTEX_PROGRAM_POINT_SIZE', 'GL_SRGB_ALPHA',
           'glBeginQueryIndexed', 'GL_DOUBLE_MAT2x4',
           'GL_ARB_map_buffer_alignment', 'GL_PACK_SKIP_ROWS',
           'glGetProgramiv', 'GL_LINEAR_MIPMAP_LINEAR',
           'glProgramUniform4fv', 'GL_GEOMETRY_SHADER', 'GL_R8I',
           'GL_SYNC_CL_EVENT_ARB',
           'GL_MAX_TESS_EVALUATION_INPUT_COMPONENTS',
           'glFlushMappedBufferRange', 'glTexStorage2D',
           'GL_ONE_MINUS_CONSTANT_ALPHA', 'GL_NEAREST_MIPMAP_LINEAR',
           'glGenQueries', 'GL_FRACTIONAL_EVEN', 'GL_DRAW_BUFFER14',
           'glGetnUniformivARB', 'glTexSubImage3D',
           'glDeleteSamplers', 'GL_SAMPLES_PASSED',
           'GL_RENDERBUFFER_RED_SIZE',
           'GL_PROXY_TEXTURE_2D_MULTISAMPLE_ARRAY',
           'GL_SEPARATE_ATTRIBS', 'GL_IMAGE_3D', 'GL_TEXTURE_HEIGHT',
           'GL_DOUBLE_MAT2x3', 'glGetDoublev', 'GL_RGBA16I',
           'GL_MAX_VARYING_VECTORS', 'glUniform4dv',
           'glProgramUniform3dv', 'GL_ARB_shader_atomic_counters',
           'GL_TEXTURE_FIXED_SAMPLE_LOCATIONS', 'GL_RED',
           'GL_UNSIGNED_INT_IMAGE_CUBE_MAP_ARRAY', 'glUniform3fv',
           'GL_POLYGON_OFFSET_LINE', 'GL_FUNC_REVERSE_SUBTRACT',
           'GL_NO_RESET_NOTIFICATION_ARB', 'GL_GREEN',
           'glGetnPixelMapusvARB', 'GL_STENCIL_BACK_PASS_DEPTH_PASS',
           'glUniformMatrix4dv', 'GL_ATOMIC_COUNTER_BARRIER_BIT',
           'glMultiDrawElements', 'GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS',
           'GL_UNSIGNED_INT_8_8_8_8_REV', 'GL_IMAGE_BINDING_FORMAT',
           'GL_MAX_COMBINED_UNIFORM_BLOCKS', 'GL_ONE',
           'GL_ARB_base_instance', 'glBindTransformFeedback',
           'GL_DST_COLOR', 'GL_UNSIGNED_INT',
           'GL_MAX_ATOMIC_COUNTER_BUFFER_BINDINGS', 'glUniform2uiv',
           'GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES', 'glFinish',
           'GL_RG16_SNORM', 'GL_QUERY_COUNTER_BITS', 'GL_RG_INTEGER',
           'glUniform1uiv', 'GL_MAX_VERTEX_ATOMIC_COUNTERS',
           'GL_IMAGE_FORMAT_COMPATIBILITY_TYPE',
           'GL_MAX_FRAGMENT_ATOMIC_COUNTER_BUFFERS',
           'GL_RENDERBUFFER_HEIGHT', 'GL_INTERLEAVED_ATTRIBS',
           'GL_TEXTURE_ALPHA_TYPE', 'glClearDepth', 'GL_BLUE',
           'GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS',
           'GL_TEXTURE_BLUE_TYPE', 'GL_COLOR_ATTACHMENT1',
           'GL_STREAM_COPY', 'GL_TEXTURE_FETCH_BARRIER_BIT',
           'glGetnPixelMapfvARB', 'GL_TEXTURE_2D_MULTISAMPLE_ARRAY',
           'glGetnUniformuivARB', 'GL_COMPRESSED_RGBA_BPTC_UNORM_ARB',
           'GL_IMAGE_FORMAT_COMPATIBILITY_BY_CLASS',
           'glUniformMatrix4x3dv', 'GL_LAYER_PROVOKING_VERTEX',
           'GL_FASTEST', 'glDeleteQueries', 'GL_TEXTURE_RED_TYPE',
           'GL_PRIMITIVE_RESTART_INDEX', 'GL_DEBUG_SOURCE_API_ARB',
           'GL_TEXTURE_CUBE_MAP_NEGATIVE_Z',
           'GL_MAX_SUBROUTINE_UNIFORM_LOCATIONS',
           'glGetVertexAttribfv', 'GL_RIGHT',
           'GL_DEBUG_SOURCE_WINDOW_SYSTEM_ARB', 'glGetActiveAttrib',
           'GL_COMPRESSED_SIGNED_RED_RGTC1',
           'GL_TEXTURE_CUBE_MAP_ARRAY', 'glTexSubImage2D',
           'GL_TIMEOUT_EXPIRED', 'glLogicOp',
           'glProgramUniformMatrix3x4fv', 'glProgramUniformMatrix4dv',
           'GL_TEXTURE_WIDTH', 'GL_UNIFORM_SIZE', 'GL_FLOAT_MAT4x2',
           'GL_FLOAT_MAT4x3', 'GL_ARB_vertex_array_object',
           'GL_COMPRESSED_RG', 'GL_POLYGON_OFFSET_UNITS',
           'glDrawTransformFeedbackStream',
           'GL_MAX_COLOR_TEXTURE_SAMPLES', '__GLsync',
           'GL_MAX_GEOMETRY_ATOMIC_COUNTER_BUFFERS',
           'GL_OUT_OF_MEMORY', 'GL_MAX_TEXTURE_BUFFER_SIZE',
           'glProvokingVertex', 'glShaderBinary', 'glDrawElements',
           'GL_ARB_transform_feedback_instanced',
           'GL_MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS',
           'GL_GEOMETRY_OUTPUT_TYPE', 'GL_RASTERIZER_DISCARD',
           'GL_BOOL', 'glUniform1iv',
           'GL_MAX_COMBINED_IMAGE_UNITS_AND_FRAGMENT_OUTPUTS',
           'GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER',
           'glDrawArraysInstanced',
           'GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE',
           'glProgramUniformMatrix2fv', 'glSamplerParameteriv',
           'GL_INT_SAMPLER_2D_MULTISAMPLE', 'GL_STENCIL_TEST',
           'glVertexAttrib4uiv', 'glEndQueryIndexed',
           'GL_R11F_G11F_B10F', 'glProgramUniform1iv', 'GL_INVERT',
           'glBindRenderbuffer', 'GL_PROXY_TEXTURE_1D', 'glIsProgram',
           'GL_DEPTH_COMPONENT32F', 'GL_TRIANGLE_FAN',
           'glUniformMatrix3x2dv', 'glVertexAttrib4fv',
           'glProgramUniformMatrix2x3dv',
           'GL_MAX_TESS_EVALUATION_OUTPUT_COMPONENTS',
           'GL_DEBUG_SOURCE_SHADER_COMPILER_ARB', 'glVertexAttrib2fv',
           'GL_BUFFER_ACCESS_FLAGS', 'GL_ARB_draw_buffers_blend',
           'GL_UNIFORM_BUFFER_SIZE', 'GL_TEXTURE_IMMUTABLE_FORMAT',
           'GL_ARB_shading_language_420pack',
           'GL_TEXTURE_BUFFER_FORMAT',
           'GL_ATOMIC_COUNTER_BUFFER_BINDING',
           'GL_MAX_TESS_EVALUATION_TEXTURE_IMAGE_UNITS',
           'GL_MAX_SUBROUTINES', 'GL_ARB_sample_shading',
           'glProgramUniform3i', 'GL_BGRA',
           'GL_ACTIVE_UNIFORM_BLOCKS', 'glProgramUniform3f',
           'GL_SAMPLER_1D', 'glProgramUniform3d', 'GL_RGB16I',
           'GL_ARB_blend_func_extended', 'GL_RGB16F',
           'GL_SMOOTH_LINE_WIDTH_RANGE', 'GL_IMAGE_BINDING_LAYER',
           'GL_CLIP_DISTANCE7', 'GL_LAST_VERTEX_CONVENTION',
           'GL_UNIFORM_BLOCK_NAME_LENGTH', 'GL_SAMPLE_MASK',
           'GL_SAMPLER_CUBE_MAP_ARRAY_SHADOW_ARB',
           'glVertexAttribI1ui', 'GL_CONDITION_SATISFIED',
           'GL_CONTEXT_FLAG_FORWARD_COMPATIBLE_BIT', 'GLuint64',
           'glIsNamedStringARB', 'GL_READ_FRAMEBUFFER_BINDING',
           'GL_FRAMEBUFFER_ATTACHMENT_LAYERED',
           'GL_UNIFORM_ARRAY_STRIDE', 'glGetInteger64v',
           'GL_ARB_sampler_objects', 'GL_RGBA2', 'GL_RGBA4',
           'GL_RGBA8', 'GL_INFO_LOG_LENGTH', 'GL_COMPRESSED_RG_RGTC2',
           'GL_ARB_shader_subroutine', 'glVertexAttrib4Niv',
           'glClearBufferiv', 'GL_SRGB8',
           'GL_RENDERBUFFER_STENCIL_SIZE', 'GL_INT_IMAGE_2D_ARRAY',
           'glNamedStringARB', 'GL_POINT_SIZE_GRANULARITY',
           'GL_STATIC_READ', 'GL_VERSION_2_0', 'GL_VERSION_2_1',
           'GL_GEOMETRY_SHADER_BIT', 'GL_MAP_READ_BIT',
           'glGetActiveSubroutineUniformName',
           'GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS', 'GLuint',
           'GL_MAX_COMBINED_IMAGE_UNIFORMS', 'glGetnHistogramARB',
           'glGetSamplerParameterIuiv',
           'GL_COMPRESSED_SIGNED_RG_RGTC2',
           'GL_ARB_texture_query_lod', 'GL_DEBUG_TYPE_OTHER_ARB',
           'GL_SAMPLER_2D_MULTISAMPLE_ARRAY', 'glClearDepthf',
           'GL_STENCIL_PASS_DEPTH_PASS',
           'glProgramUniformMatrix4x3dv', 'glGetnMinmaxARB',
           'GL_POLYGON_SMOOTH', 'glGetnMapivARB',
           'glVertexAttribI4ui', 'GL_LOSE_CONTEXT_ON_RESET_ARB',
           'GL_RGBA12', 'GL_ARB_texture_buffer_object_rgb32',
           'GL_RGBA16', 'glDepthFunc', 'glBlendEquation',
           'GL_NAMED_STRING_LENGTH_ARB', 'glBeginTransformFeedback',
           'GL_DEPTH_ATTACHMENT', 'GL_TEXTURE_ALPHA_SIZE',
           'glCompressedTexImage1D', 'glDeleteTransformFeedbacks',
           'glDrawRangeElementsBaseVertex', 'glBindAttribLocation',
           'glUniformMatrix2dv', 'GLdouble', 'glVertexAttrib1dv',
           'GL_DEBUG_CALLBACK_FUNCTION_ARB', 'GL_RGB10_A2',
           'GL_ACTIVE_SUBROUTINE_MAX_LENGTH', 'glBufferSubData',
           'GL_MAX_VERTEX_IMAGE_UNIFORMS', 'glBlendFuncSeparatei',
           'GL_ARB_vertex_array_bgra',
           'GL_MAX_TESS_EVALUATION_UNIFORM_BLOCKS', 'ptrdiff_t',
           'GL_DEBUG_OUTPUT_SYNCHRONOUS_ARB',
           'GL_UNSIGNED_NORMALIZED',
           'GL_SMOOTH_POINT_SIZE_GRANULARITY', 'glDisablei',
           'GL_NOTEQUAL', 'GL_FLOAT_32_UNSIGNED_INT_24_8_REV',
           'GL_INT_SAMPLER_1D_ARRAY', 'glGetSynciv',
           'GL_TEXTURE_RED_SIZE', 'glProgramUniform2i',
           'glProgramUniform2d', 'glProgramUniform2f',
           'glGetProgramBinary', 'GL_TEXTURE_BINDING_CUBE_MAP_ARRAY',
           'glPauseTransformFeedback', 'GL_TEXTURE_SHARED_SIZE',
           'GL_ARB_seamless_cube_map', 'glTexSubImage1D',
           'GL_RENDERBUFFER_DEPTH_SIZE',
           'GL_PACK_COMPRESSED_BLOCK_SIZE',
           'GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS', 'glVertexAttribP3uiv',
           'GL_SHORT', 'GL_CW', 'GL_MAX_VERTEX_UNIFORM_COMPONENTS',
           'GL_IMAGE_1D', 'GLcharARB', 'GLhalf',
           'GL_UNSIGNED_INT_10F_11F_11F_REV', 'glVertexAttrib4sv',
           'GL_STATIC_DRAW', 'GL_ARB_sync', 'GL_RENDERBUFFER',
           'GL_FRAMEBUFFER_ATTACHMENT_GREEN_SIZE',
           'GL_NUM_COMPATIBLE_SUBROUTINES', 'glTexParameterfv',
           'GL_SAMPLER_3D', 'glUniform3dv', 'GL_MAX_INTEGER_SAMPLES',
           'GL_MIN_PROGRAM_TEXTURE_GATHER_OFFSET',
           'glProgramUniform3fv', 'GL_TEXTURE_GREEN_SIZE',
           'GL_UNPACK_COMPRESSED_BLOCK_WIDTH',
           'glDrawElementsIndirect', 'GL_VERTEX_ATTRIB_ARRAY_DIVISOR',
           'glGetQueryObjectui64v',
           'GL_MAX_VERTEX_ATOMIC_COUNTER_BUFFERS',
           'glProgramUniform1fv', 'glUniformMatrix4fv',
           'GL_UNDEFINED_VERTEX', 'GL_IMAGE_2D_RECT', 'GL_SAMPLES',
           'glGenProgramPipelines', 'GL_UNSIGNED_INT_VEC2',
           'GL_UNSIGNED_INT_VEC3', 'GL_UNSIGNED_INT_VEC4',
           'GL_UNSIGNED_SHORT_5_6_5', 'glUniformSubroutinesuiv',
           'GL_RGB32UI', 'glCompileShader',
           'GL_PROXY_TEXTURE_RECTANGLE',
           'GL_ARB_shading_language_packing',
           'glVertexAttribIPointer', 'GL_CONSTANT_COLOR', 'GL_RG8UI',
           'GL_TEXTURE8', 'GL_TEXTURE9',
           'GL_DEBUG_CALLBACK_USER_PARAM_ARB', 'GL_TEXTURE4',
           'GL_TEXTURE5', 'GL_TEXTURE6', 'GL_TEXTURE7', 'GL_TEXTURE0',
           'GL_CONTEXT_PROFILE_MASK', 'GL_TEXTURE2', 'GL_TEXTURE3',
           'GL_BOOL_VEC4', 'GL_BOOL_VEC3', 'GL_BOOL_VEC2',
           'GL_MAX_TESS_CONTROL_TOTAL_OUTPUT_COMPONENTS',
           'glCompressedTexImage2D', 'glVertexAttrib1f',
           'GL_NAMED_STRING_TYPE_ARB', 'glDrawBuffers',
           'glVertexAttrib1s', 'GL_UNPACK_IMAGE_HEIGHT',
           'GL_TRIANGLE_STRIP', 'GL_PROGRAM_BINARY_RETRIEVABLE_HINT',
           'GL_FRONT_LEFT', 'GL_NUM_SAMPLE_COUNTS', 'glDeleteProgram',
           'GL_VERTEX_ARRAY_BINDING', 'glUniformMatrix4x3fv',
           'glClearBufferfv', 'GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY',
           'GL_STENCIL_FUNC', 'GL_DECR', 'GL_BACK', 'glClearBufferfi',
           'glDrawArraysIndirect', 'glGenVertexArrays', 'GL_INT',
           'GL_ATOMIC_COUNTER_BUFFER', 'glProgramUniformMatrix3x2dv',
           'GL_CLIP_DISTANCE1', 'GL_CLIP_DISTANCE0',
           'glGetSamplerParameterIiv', 'GL_CLIP_DISTANCE2',
           'GL_CLIP_DISTANCE5', 'GL_CLIP_DISTANCE4',
           'GL_MINOR_VERSION', 'GL_CLIP_DISTANCE6',
           'GL_FRONT_AND_BACK', 'glGetVertexAttribdv',
           'glProgramUniformMatrix3x4dv',
           'GL_SAMPLER_CUBE_MAP_ARRAY_ARB', 'GL_SYNC_FENCE',
           'GL_RGB8_SNORM', 'GL_UNPACK_SKIP_PIXELS', 'glUniform1ui',
           'GL_ARB_texture_rg', 'GL_DOUBLE_VEC4',
           'GL_UNSIGNED_SHORT_4_4_4_4', 'GL_DOUBLE_VEC2',
           'GL_DOUBLE_VEC3', 'glMemoryBarrier', 'GL_NO_ERROR',
           'GL_ARB_framebuffer_object', 'GL_RGBA16UI',
           'glGetFragDataLocation', 'GL_TEXTURE_BINDING_2D_ARRAY',
           'GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT',
           'GL_MAX_DRAW_BUFFERS', 'GL_DELETE_STATUS',
           'GL_IMAGE_CUBE_MAP_ARRAY', 'GL_R32UI',
           'GL_PATCH_DEFAULT_INNER_LEVEL', 'GL_MAJOR_VERSION',
           'glMapBufferRange', 'GL_BGR_INTEGER', 'GL_FALSE',
           'GL_PROXY_TEXTURE_3D', 'GL_UNIFORM_BUFFER_BINDING',
           'GL_UNIFORM_TYPE', 'GL_MAX_DEBUG_MESSAGE_LENGTH_ARB',
           'glProgramUniformMatrix4x2dv', 'glIsShader', 'glEnable',
           'glGetActiveUniformsiv', 'GL_FRONT_RIGHT',
           'GL_MAP_INVALIDATE_BUFFER_BIT', 'glBlendEquationi',
           'GL_FRACTIONAL_ODD', 'GL_DEPTH_TEST',
           'glGetAttribLocation', 'glVertexAttrib4dv',
           'GL_SMOOTH_POINT_SIZE_RANGE', 'GL_MULTISAMPLE',
           'GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN',
           'GL_FUNC_SUBTRACT', 'glProgramUniform3ui',
           'GL_MAX_TESS_GEN_LEVEL',
           'GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH',
           'glProgramUniformMatrix2x3fv', 'GL_CLAMP_TO_BORDER',
           'GL_COLOR_ATTACHMENT15', 'GL_COLOR_ATTACHMENT14',
           'GL_DEPTH_RANGE', 'GL_COLOR_ATTACHMENT11',
           'GL_CLAMP_TO_EDGE', 'GL_COLOR_ATTACHMENT13',
           'GL_COLOR_ATTACHMENT12', 'GL_NEAREST',
           'GL_MAX_TESS_EVALUATION_ATOMIC_COUNTER_BUFFERS',
           'glProgramUniform1i', 'glProgramUniform1d',
           'GL_MAX_DUAL_SOURCE_DRAW_BUFFERS', 'glProgramUniform1f',
           'GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT',
           'glProgramUniform3iv', 'glGetVertexAttribPointerv',
           'GL_DEPTH_CLEAR_VALUE', 'GL_GEOMETRY_INPUT_TYPE',
           'glVertexAttrib4s', 'GL_SRC_ALPHA',
           'GL_UNSIGNED_INT_5_9_9_9_REV',
           'GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE',
           'GL_MAX_VARYING_FLOATS', 'GL_TEXTURE_CUBE_MAP_NEGATIVE_Y',
           'GL_TEXTURE_CUBE_MAP_NEGATIVE_X', 'GL_ONE_MINUS_DST_COLOR',
           'glUniform4iv', 'GL_FLOAT', 'glGenTextures',
           'GL_COLOR_BUFFER_BIT', 'GL_SAMPLER_2D', 'GL_IMAGE_BUFFER',
           'GL_NEAREST_MIPMAP_NEAREST', 'glGetActiveUniformBlockName',
           'GL_IMAGE_BINDING_LAYERED', 'glVertexAttribPointer',
           'GL_CONTEXT_COMPATIBILITY_PROFILE_BIT', 'GL_LINK_STATUS',
           'GL_COMPRESSED_SRGB_ALPHA_BPTC_UNORM_ARB',
           'GL_TEXTURE_BINDING_2D_MULTISAMPLE_ARRAY',
           'GL_ARB_texture_rgb10_a2ui', 'GL_MAP_FLUSH_EXPLICIT_BIT',
           'GL_AND_INVERTED', 'glVertexAttribP1ui',
           'GL_FRAMEBUFFER_SRGB', 'GL_POLYGON_OFFSET_POINT',
           'glBindFragDataLocationIndexed', 'glUniform2iv',
           'GL_UNSIGNED_INT_SAMPLER_2D_ARRAY', 'GL_DEPTH_COMPONENT16',
           'GL_ARB_compressed_texture_pixel_storage',
           'GL_MAX_SAMPLE_MASK_WORDS', 'GL_UNSIGNALED', 'GL_RGB32I',
           'glFramebufferTexture1D', 'glGetShaderiv',
           'GL_SAMPLER_BUFFER', 'GL_BGRA_INTEGER', 'GL_RGB32F',
           'GL_ONE_MINUS_SRC_ALPHA', 'GL_UNSIGNED_INT_IMAGE_1D_ARRAY',
           'glUniform1dv', 'GL_PROGRAM_POINT_SIZE',
           'GL_UNPACK_COMPRESSED_BLOCK_DEPTH',
           'GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING',
           'glVertexAttrib1fv',
           'GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR_ARB',
           'glDebugMessageControlARB', 'GL_ARB_depth_clamp',
           'glUniformMatrix2x3dv',
           'GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT',
           'GL_PROGRAM_PIPELINE_BINDING', 'glCompressedTexImage3D',
           'GL_MAX_FRAGMENT_UNIFORM_COMPONENTS',
           'glGetVertexAttribiv', 'glVertexAttrib3fv',
           'GL_FRAMEBUFFER_DEFAULT', 'GL_TEXTURE_BINDING_RECTANGLE',
           'GL_LINE_SMOOTH_HINT', 'GL_COMMAND_BARRIER_BIT',
           'GL_FRONT', 'GL_MAX_FRAGMENT_UNIFORM_VECTORS',
           'GL_MAX_DEBUG_LOGGED_MESSAGES_ARB', 'GL_NUM_EXTENSIONS',
           'GL_FRAMEBUFFER_BINDING', 'GL_SET', 'GL_DEPTH_FUNC',
           'glMultiDrawElementsBaseVertex', 'GL_INVALID_ENUM',
           'GL_STENCIL_BACK_VALUE_MASK',
           'GL_MAX_TESS_CONTROL_ATOMIC_COUNTER_BUFFERS',
           'GL_DEPTH_COMPONENT', 'glCompressedTexSubImage1D',
           'GL_COMPARE_REF_TO_TEXTURE',
           'GL_FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE', 'GL_TRUE',
           'GL_TEXTURE_MIN_FILTER', 'GL_COMPATIBLE_SUBROUTINES',
           'glTransformFeedbackVaryings',
           'GL_RENDERBUFFER_GREEN_SIZE',
           'GL_DEBUG_SOURCE_THIRD_PARTY_ARB',
           'GL_DEPTH_STENCIL_ATTACHMENT', 'GL_SHADER_SOURCE_LENGTH',
           'GL_DYNAMIC_COPY', 'GL_IMAGE_1D_ARRAY',
           'GL_UNPACK_ALIGNMENT', 'GL_ARB_uniform_buffer_object',
           'glGetBooleani_v', 'GL_ARB_texture_swizzle',
           'GL_RG8_SNORM',
           'GL_UNSIGNED_INT_SAMPLER_CUBE_MAP_ARRAY_ARB', 'glHint',
           'GL_DEBUG_SEVERITY_MEDIUM_ARB', 'glVertexAttribP2uiv',
           'GL_DEBUG_TYPE_PORTABILITY_ARB',
           'GL_PROGRAM_BINARY_FORMATS', 'GL_LOW_INT',
           'glDepthRangeArrayv', 'GL_MAX_VERTEX_OUTPUT_COMPONENTS',
           'GL_KEEP', 'glGetActiveAtomicCounterBufferiv',
           'GL_PROXY_TEXTURE_2D', 'GL_OR',
           'GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER',
           'glVertexAttribL4dv', 'glGetTexParameteriv',
           'glProgramUniform1dv', 'GL_SAMPLER_1D_ARRAY',
           'GL_ACTIVE_SUBROUTINES', 'GL_LINE_LOOP', 'GL_BACK_RIGHT',
           'GL_UNIFORM_BLOCK_REFERENCED_BY_TESS_EVALUATION_SHADER',
           'GL_R3_G3_B2', 'glDisable', 'GL_UNIFORM_OFFSET',
           'GL_TEXTURE1', 'glProgramUniform4uiv',
           'GL_UNSIGNED_INT_SAMPLER_CUBE', 'GL_TIME_ELAPSED',
           'GL_FUNC_ADD', 'GL_BUFFER_ACCESS', 'GLsync',
           'GL_VIEWPORT_SUBPIXEL_BITS', 'GL_SHADER_COMPILER',
           'GLenum', 'GL_LINE_SMOOTH',
           'GL_NUM_PROGRAM_BINARY_FORMATS', 'GL_STENCIL_BACK_FUNC',
           'GL_POLYGON_SMOOTH_HINT', 'GL_MEDIUM_FLOAT',
           'glVertexAttrib3f', 'glVertexAttrib3d', 'glBlendColor',
           'glSamplerParameterIuiv', 'GL_OBJECT_TYPE',
           'glVertexAttrib3s', 'glGetProgramStageiv',
           'GL_UNSIGNED_INT_IMAGE_BUFFER', 'GL_R8UI',
           'glGetGraphicsResetStatusARB', 'glUniform4i',
           'GL_DRAW_FRAMEBUFFER_BINDING', 'glEnableVertexAttribArray',
           'glUniform4d', 'glUniform4f',
           'glRenderbufferStorageMultisample', 'GL_TRIANGLES',
           'GL_SAMPLER_2D_ARRAY_SHADOW', 'glVertexAttribLPointer',
           'GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING',
           'glDrawElementsInstancedBaseVertex', 'GL_SRGB8_ALPHA8',
           'glGetActiveSubroutineName', 'GL_SAMPLER_2D_ARRAY',
           'glUniformBlockBinding', 'GL_RENDERER',
           'GL_MIRRORED_REPEAT', 'glProgramUniformMatrix3x2fv',
           'GL_PROGRAM_BINARY_LENGTH', 'glGetQueryIndexediv',
           'GL_COLOR_LOGIC_OP', 'GL_ARB_internalformat_query',
           'GL_TRANSFORM_FEEDBACK_VARYING_MAX_LENGTH',
           'GL_UNIFORM_BLOCK_INDEX', 'GL_IMAGE_CUBE',
           'GL_MAX_ATOMIC_COUNTER_BUFFER_SIZE',
           'GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT', 'glBlendFunc',
           'glCreateProgram', 'glPrimitiveRestartIndex',
           'GL_TRANSFORM_FEEDBACK_BINDING', 'GL_COMPRESSED_SRGB',
           'GL_TEXTURE_DEPTH_TYPE', 'GL_EQUIV', 'glUniform3uiv',
           'glClearColor', 'glUniform3ui', 'glVertexAttribI4uiv',
           'glVertexAttrib4bv', 'GL_INVALID_INDEX',
           'GL_INT_IMAGE_1D_ARRAY', 'GL_STENCIL_BUFFER_BIT',
           'glVertexAttrib1d', 'GL_ARB_copy_buffer',
           'glUniformMatrix2x3fv', 'glGenTransformFeedbacks',
           'glGetVertexAttribIuiv', 'GL_SAMPLER_CUBE_MAP_ARRAY',
           'glCompressedTexSubImage2D', 'glProgramBinary',
           'glVertexAttribI4bv', 'glGetTexParameterfv',
           'GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY',
           'GL_MAX_FRAGMENT_INPUT_COMPONENTS',
           'GL_MAX_FRAGMENT_UNIFORM_BLOCKS',
           'GL_TEXTURE_BINDING_CUBE_MAP_ARRAY_ARB',
           'glTexParameterIiv', 'glEndTransformFeedback',
           'glVertexAttrib4usv', 'glTexImage2DMultisample',
           'GL_VERTEX_ATTRIB_ARRAY_NORMALIZED',
           'GL_SAMPLER_2D_SHADOW', 'glVertexAttribI1iv',
           'glVertexAttribDivisor', 'GLvdpauSurfaceNV',
           'glUniformMatrix4x2fv', 'GL_MAX_COMBINED_ATOMIC_COUNTERS',
           'GL_ARB_get_program_binary', 'GL_INVALID_VALUE',
           'GL_VERSION', 'glProgramUniformMatrix4x2fv',
           'GL_INNOCENT_CONTEXT_RESET_ARB', 'GL_ARB_debug_output',
           'GL_MAX_ELEMENTS_INDICES', 'glVertexAttribI2iv',
           'glGetShaderPrecisionFormat', 'GL_GEOMETRY_VERTICES_OUT',
           'GL_RGB8', 'GL_MAX_TESS_EVALUATION_IMAGE_UNIFORMS',
           'glShaderSource', 'glDeleteRenderbuffers',
           'GL_TEXTURE_SAMPLES', 'GL_RGB4', 'GL_RGB5', 'GL_CULL_FACE',
           'GL_SAMPLE_COVERAGE_VALUE', 'GL_PROXY_TEXTURE_CUBE_MAP',
           'GL_ARB_texture_gather', 'GL_ARB_shading_language_include',
           'GL_NEVER', 'GL_STENCIL_VALUE_MASK', 'GL_BLEND_DST',
           'glBufferData', 'glGetTexParameterIiv',
           'GL_MAX_TESS_EVALUATION_UNIFORM_COMPONENTS',
           'glVertexAttribI1i', 'GL_TEXTURE_SWIZZLE_RGBA',
           'GL_DEPTH_COMPONENT32', 'GL_RGBA', 'GL_READ_FRAMEBUFFER',
           'glGetDebugMessageLogARB', 'GL_MIN_PROGRAM_TEXEL_OFFSET',
           'GL_TEXTURE_CUBE_MAP_ARRAY_ARB', 'glGetBufferPointerv',
           'GL_VENDOR', 'glFramebufferTexture3D',
           'GL_TEXTURE_2D_ARRAY', 'GL_TEXTURE_BINDING_2D',
           'GL_ISOLINES', 'GL_ACTIVE_PROGRAM', 'GLvoid',
           'glSamplerParameterfv', 'glUniform1fv', 'int64_t',
           'GL_TESS_GEN_POINT_MODE', 'GL_TESS_GEN_MODE',
           'glScissorIndexedv', 'GL_MAX_TRANSFORM_FEEDBACK_BUFFERS',
           'GL_MAX', 'GL_PROXY_TEXTURE_2D_ARRAY',
           'GL_PROXY_TEXTURE_CUBE_MAP_ARRAY',
           'GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS',
           'GL_SAMPLER_1D_SHADOW', 'GL_UNSIGNED_INT_IMAGE_2D_RECT',
           'glVertexAttrib2d', 'glVertexAttrib2f',
           'glVertexAttrib3dv', 'GL_RG16F',
           'GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL',
           'glVertexAttrib2s', 'glTexImage3DMultisample', 'GL_RG16I',
           'glGetUniformBlockIndex', 'GL_WRITE_ONLY',
           'GL_ATOMIC_COUNTER_BUFFER_REFERENCED_BY_VERTEX_SHADER',
           'GL_STENCIL_ATTACHMENT', 'glFrontFace',
           'GL_SAMPLE_COVERAGE', 'glDrawArraysInstancedBaseInstance',
           'GL_DRAW_FRAMEBUFFER', 'GL_RGB10_A2UI',
           'glVertexAttribL2dv']
