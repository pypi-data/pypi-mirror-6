from ctypes import *

STRING = c_char_p
_libraries = {}
_libraries['libGL.so.1'] = CDLL('libGL.so.1')


GLX_FRONT_LEFT_EXT = 8414 # Variable c_int '8414'
GLX_FRONT_EXT = GLX_FRONT_LEFT_EXT # alias
GLX_BACK_LEFT_EXT = 8416 # Variable c_int '8416'
GLX_BACK_EXT = GLX_BACK_LEFT_EXT # alias
GLX_TRANSPARENT_INDEX = 32777 # Variable c_int '32777'
GLX_BIND_TO_TEXTURE_RGBA_EXT = 8401 # Variable c_int '8401'
GLX_BIND_TO_TEXTURE_TARGETS_EXT = 8403 # Variable c_int '8403'
GLX_EVENT_MASK_SGIX = 32799 # Variable c_int '32799'
GLX_Y_INVERTED_EXT = 8404 # Variable c_int '8404'
GLX_RED_SIZE = 8 # Variable c_int '8'
GLX_MESA_copy_sub_buffer = 1 # Variable c_int '1'
GLX_MAX_PBUFFER_PIXELS = 32792 # Variable c_int '32792'
GLX_VISUAL_CAVEAT_EXT = 32 # Variable c_int '32'
GLX_STENCIL_BUFFER_BIT_SGIX = 64 # Variable c_int '64'
GLX_TEXTURE_RECTANGLE_EXT = 8413 # Variable c_int '8413'
GLX_GPU_NUM_RB_AMD = 8615 # Variable c_int '8615'
GLX_LOSE_CONTEXT_ON_RESET_ARB = 33362 # Variable c_int '33362'
GLX_SGIX_video_source = 1 # Variable c_int '1'
GLX_BUFFER_CLOBBER_MASK_SGIX = 134217728 # Variable c_int '134217728'
GLX_COLOR_INDEX_BIT_SGIX = 2 # Variable c_int '2'
GLX_FRONT_LEFT_BUFFER_BIT_SGIX = 1 # Variable c_int '1'
GLX_TEXTURE_FORMAT_RGB_EXT = 8409 # Variable c_int '8409'
GLX_PBUFFER_HEIGHT = 32832 # Variable c_int '32832'
GLX_COLOR_SAMPLES_NV = 8371 # Variable c_int '8371'
GLX_BACK_RIGHT_EXT = 8417 # Variable c_int '8417'
GLX_CONTEXT_ALLOW_BUFFER_BYTE_ORDER_MISMATCH_ARB = 8341 # Variable c_int '8341'
GLX_RGBA_TYPE = 32788 # Variable c_int '32788'
GLX_FRAMEBUFFER_SRGB_CAPABLE_ARB = 8370 # Variable c_int '8370'
GLX_TEXTURE_FORMAT_RGBA_EXT = 8410 # Variable c_int '8410'
GLX_NONE = 32768 # Variable c_int '32768'
GLX_AUX0_EXT = 8418 # Variable c_int '8418'
GLX_FRONT_RIGHT_EXT = 8415 # Variable c_int '8415'
GLX_CONTEXT_PROFILE_MASK_ARB = 37158 # Variable c_int '37158'
GLX_NON_CONFORMANT_CONFIG = 32781 # Variable c_int '32781'
GLX_EXT_framebuffer_sRGB = 1 # Variable c_int '1'
GLX_MESA_pixmap_colormap = 1 # Variable c_int '1'
GLX_CONTEXT_FLAGS_ARB = 8340 # Variable c_int '8340'
GLX_NUM_VIDEO_CAPTURE_SLOTS_NV = 8399 # Variable c_int '8399'
GLX_CONTEXT_COMPATIBILITY_PROFILE_BIT_ARB = 2 # Variable c_int '2'
GLX_DOUBLEBUFFER = 5 # Variable c_int '5'
GLX_BAD_ATTRIBUTE = 2 # Variable c_int '2'
GLX_NV_swap_group = 1 # Variable c_int '1'
GLX_STATIC_GRAY = 32775 # Variable c_int '32775'
GLX_TRANSPARENT_BLUE_VALUE = 39 # Variable c_int '39'
GLX_SAMPLES_ARB = 100001 # Variable c_int '100001'
GLX_BUFFER_SWAP_COMPLETE_INTEL_MASK = 67108864 # Variable c_int '67108864'
GLX_TRANSPARENT_TYPE = 35 # Variable c_int '35'
GLX_RGBA_BIT_SGIX = 1 # Variable c_int '1'
GLX_NO_EXTENSION = 3 # Variable c_int '3'
GLX_INTEL_swap_event = 1 # Variable c_int '1'
GLX_UNIQUE_ID_NV = 8398 # Variable c_int '8398'
GLX_OPTIMAL_PBUFFER_HEIGHT_SGIX = 32794 # Variable c_int '32794'
GLX_EXT_visual_rating = 1 # Variable c_int '1'
GLX_NV_float_buffer = 1 # Variable c_int '1'
GLX_GRAY_SCALE_EXT = 32774 # Variable c_int '32774'
GLX_SGIS_multisample = 1 # Variable c_int '1'
GLX_AUX_BUFFERS_BIT_SGIX = 16 # Variable c_int '16'
GLX_BAD_HYPERPIPE_CONFIG_SGIX = 91 # Variable c_int '91'
GLX_SLOW_CONFIG = 32769 # Variable c_int '32769'
GLX_MESA_set_3dfx_mode = 1 # Variable c_int '1'
GLX_RGBA_FLOAT_TYPE_ARB = 8377 # Variable c_int '8377'
GLX_AUX_BUFFERS_BIT = 16 # Variable c_int '16'
GLX_TRANSPARENT_RGB = 32776 # Variable c_int '32776'
GLX_VISUAL_ID = 32779 # Variable c_int '32779'
GLX_BLUE_SIZE = 10 # Variable c_int '10'
GLX_HYPERPIPE_STEREO_SGIX = 3 # Variable c_int '3'
GLX_WINDOW_BIT = 1 # Variable c_int '1'
GLX_SAMPLE_BUFFERS_BIT_SGIX = 256 # Variable c_int '256'
GLX_SYNC_SWAP_SGIX = 1 # Variable c_int '1'
GLX_SWAP_EXCHANGE_OML = 32865 # Variable c_int '32865'
GLX_MESA_swap_control = 1 # Variable c_int '1'
GLX_NV_video_output = 1 # Variable c_int '1'
GLX_LARGEST_PBUFFER_SGIX = 32796 # Variable c_int '32796'
GLX_BACK_RIGHT_BUFFER_BIT = 8 # Variable c_int '8'
GLX_RGBA = 4 # Variable c_int '4'
GLX_TRUE_COLOR_EXT = 32770 # Variable c_int '32770'
GLX_RENDER_TYPE = 32785 # Variable c_int '32785'
GLX_EXT_texture_from_pixmap = 1 # Variable c_int '1'
GLX_SGIX_fbconfig = 1 # Variable c_int '1'
GLX_EXT_swap_control = 1 # Variable c_int '1'
GLX_VISUAL_ID_EXT = 32779 # Variable c_int '32779'
GLX_STENCIL_BUFFER_BIT = 64 # Variable c_int '64'
GLX_SLOW_VISUAL_EXT = 32769 # Variable c_int '32769'
GLX_SWAP_INTERVAL_EXT = 8433 # Variable c_int '8433'
GLX_TRANSPARENT_INDEX_VALUE = 36 # Variable c_int '36'
GLX_TRANSPARENT_INDEX_EXT = 32777 # Variable c_int '32777'
GLX_DEPTH_BUFFER_BIT = 32 # Variable c_int '32'
GLX_BACK_LEFT_BUFFER_BIT = 4 # Variable c_int '4'
GLX_RGBA_FLOAT_BIT_ARB = 4 # Variable c_int '4'
GLX_MAX_PBUFFER_WIDTH_SGIX = 32790 # Variable c_int '32790'
GLX_TRANSPARENT_TYPE_EXT = 35 # Variable c_int '35'
GLX_MIPMAP_TEXTURE_EXT = 8407 # Variable c_int '8407'
GLX_PBUFFER = 32803 # Variable c_int '32803'
GLX_NV_video_capture = 1 # Variable c_int '1'
GLX_X_RENDERABLE = 32786 # Variable c_int '32786'
GLX_MAX_PBUFFER_HEIGHT = 32791 # Variable c_int '32791'
GLX_SGI_swap_control = 1 # Variable c_int '1'
GLX_SAVED_SGIX = 32801 # Variable c_int '32801'
GLX_BACK_RIGHT_BUFFER_BIT_SGIX = 8 # Variable c_int '8'
GLX_BLENDED_RGBA_SGIS = 32805 # Variable c_int '32805'
GLX_OPTIMAL_PBUFFER_WIDTH_SGIX = 32793 # Variable c_int '32793'
GLX_WIDTH_SGIX = 32797 # Variable c_int '32797'
GLX_STATIC_GRAY_EXT = 32775 # Variable c_int '32775'
GLX_ARB_framebuffer_sRGB = 1 # Variable c_int '1'
GLX_VENDOR = 1 # Variable c_int '1'
GLX_VIDEO_OUT_STACKED_FIELDS_1_2_NV = 8395 # Variable c_int '8395'
GLX_EXT_visual_info = 1 # Variable c_int '1'
GLX_NON_CONFORMANT_VISUAL_EXT = 32781 # Variable c_int '32781'
GLX_SGIX_video_resize = 1 # Variable c_int '1'
GLX_HYPERPIPE_PIPE_NAME_LENGTH_SGIX = 80 # Variable c_int '80'
GLX_COLOR_INDEX_TYPE = 32789 # Variable c_int '32789'
GLX_MAX_PBUFFER_HEIGHT_SGIX = 32791 # Variable c_int '32791'
GLX_HYPERPIPE_PIXEL_AVERAGE_SGIX = 4 # Variable c_int '4'
GLX_TEXTURE_2D_BIT_EXT = 2 # Variable c_int '2'
GLX_DONT_CARE = 4294967295L # Variable c_uint '4294967295u'
GLX_SGIX_swap_barrier = 1 # Variable c_int '1'
GLX_STATIC_COLOR_EXT = 32773 # Variable c_int '32773'
GLX_SWAP_METHOD_OML = 32864 # Variable c_int '32864'
GLX_SAMPLE_BUFFERS = 100000 # Variable c_int '100000'
GLX_SAVED = 32801 # Variable c_int '32801'
GLX_BUFFER_SIZE = 2 # Variable c_int '2'
GLX_ARB_create_context_robustness = 1 # Variable c_int '1'
GLX_ACCUM_GREEN_SIZE = 15 # Variable c_int '15'
GLX_GRAY_SCALE = 32774 # Variable c_int '32774'
GLX_MESA_swap_frame_usage = 1 # Variable c_int '1'
GLX_STEREO = 6 # Variable c_int '6'
GLX_ARB_create_context = 1 # Variable c_int '1'
GLX_CONTEXT_DEBUG_BIT_ARB = 1 # Variable c_int '1'
GLX_TRANSPARENT_RED_VALUE = 37 # Variable c_int '37'
GLX_SAMPLES_3DFX = 32849 # Variable c_int '32849'
GLX_DAMAGED = 32800 # Variable c_int '32800'
GLX_RENDER_TYPE_SGIX = 32785 # Variable c_int '32785'
GLX_NONE_EXT = 32768 # Variable c_int '32768'
GLX_CONTEXT_ROBUST_ACCESS_BIT_ARB = 4 # Variable c_int '4'
GLX_SAMPLE_BUFFERS_ARB = 100000 # Variable c_int '100000'
GLX_COLOR_INDEX_BIT = 2 # Variable c_int '2'
GLX_MULTISAMPLE_SUB_RECT_WIDTH_SGIS = 32806 # Variable c_int '32806'
GLX_FBCONFIG_ID_SGIX = 32787 # Variable c_int '32787'
GLX_DRAWABLE_TYPE = 32784 # Variable c_int '32784'
GLX_GLXEXT_VERSION = 33 # Variable c_int '33'
GLX_SWAP_COPY_OML = 32866 # Variable c_int '32866'
GLX_SAMPLE_BUFFERS_3DFX = 32848 # Variable c_int '32848'
GLX_STENCIL_SIZE = 13 # Variable c_int '13'
GLX_RGBA_UNSIGNED_FLOAT_TYPE_EXT = 8369 # Variable c_int '8369'
GLX_SGIX_visual_select_group = 1 # Variable c_int '1'
GLX_MESA_agp_offset = 1 # Variable c_int '1'
GLX_SGIX_swap_group = 1 # Variable c_int '1'
GLX_BIND_TO_MIPMAP_TEXTURE_EXT = 8402 # Variable c_int '8402'
GLX_ACCUM_BLUE_SIZE = 16 # Variable c_int '16'
GLX_PBUFFER_BIT_SGIX = 4 # Variable c_int '4'
GLX_SWAP_UNDEFINED_OML = 32867 # Variable c_int '32867'
GLX_PBUFFER_BIT = 4 # Variable c_int '4'
GLX_SCREEN_EXT = 32780 # Variable c_int '32780'
GLX_GPU_FASTEST_TARGET_GPUS_AMD = 8610 # Variable c_int '8610'
GLX_SCREEN = 32780 # Variable c_int '32780'
GLX_VIDEO_OUT_DEPTH_NV = 8389 # Variable c_int '8389'
GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB = 2 # Variable c_int '2'
GLX_HYPERPIPE_DISPLAY_PIPE_SGIX = 1 # Variable c_int '1'
GLX_DEPTH_BUFFER_BIT_SGIX = 32 # Variable c_int '32'
GLX_ARB_render_texture = 1 # Variable c_int '1'
GLX_PBUFFER_SGIX = 32803 # Variable c_int '32803'
GLX_WINDOW = 32802 # Variable c_int '32802'
GLX_MAX_PBUFFER_PIXELS_SGIX = 32792 # Variable c_int '32792'
GLX_VISUAL_SELECT_GROUP_SGIX = 32808 # Variable c_int '32808'
GLX_AUX_BUFFERS = 7 # Variable c_int '7'
GLX_VIDEO_OUT_FIELD_2_NV = 8394 # Variable c_int '8394'
GLX_WINDOW_SGIX = 32802 # Variable c_int '32802'
GLX_OML_sync_control = 1 # Variable c_int '1'
GLX_GPU_NUM_SPI_AMD = 8616 # Variable c_int '8616'
GLX_ACCUM_ALPHA_SIZE = 17 # Variable c_int '17'
GLX_X_VISUAL_TYPE = 34 # Variable c_int '34'
GLX_SAMPLES = 100001 # Variable c_int '100001'
GLX_EXT_swap_control_tear = 1 # Variable c_int '1'
GLX_PbufferClobber = 0 # Variable c_int '0'
GLX_VIDEO_OUT_FRAME_NV = 8392 # Variable c_int '8392'
GLX_VIDEO_OUT_COLOR_NV = 8387 # Variable c_int '8387'
GLX_USE_GL = 1 # Variable c_int '1'
GLX_BAD_ENUM = 7 # Variable c_int '7'
GLX_RGBA_BIT = 1 # Variable c_int '1'
GLX_ARB_fbconfig_float = 1 # Variable c_int '1'
GLX_X_VISUAL_TYPE_EXT = 34 # Variable c_int '34'
GLX_WIDTH = 32797 # Variable c_int '32797'
GLX_SGI_make_current_read = 1 # Variable c_int '1'
GLX_LATE_SWAPS_TEAR_EXT = 8435 # Variable c_int '8435'
GLX_CONTEXT_MAJOR_VERSION_ARB = 8337 # Variable c_int '8337'
GLX_WINDOW_BIT_SGIX = 1 # Variable c_int '1'
GLX_AUX6_EXT = 8424 # Variable c_int '8424'
GLX_NUM_VIDEO_SLOTS_NV = 8432 # Variable c_int '8432'
GLX_SGI_video_sync = 1 # Variable c_int '1'
GLX_TEXTURE_FORMAT_NONE_EXT = 8408 # Variable c_int '8408'
GLX_ACCUM_BUFFER_BIT = 128 # Variable c_int '128'
GLX_TRANSPARENT_ALPHA_VALUE = 40 # Variable c_int '40'
GLX_HEIGHT_SGIX = 32798 # Variable c_int '32798'
GLX_CONFIG_CAVEAT = 32 # Variable c_int '32'
GLX_AUX9_EXT = 8427 # Variable c_int '8427'
GLX_DRAWABLE_TYPE_SGIX = 32784 # Variable c_int '32784'
GLX_SGIX_hyperpipe = 1 # Variable c_int '1'
GLX_PIXMAP_BIT = 2 # Variable c_int '2'
GLX_TRANSPARENT_BLUE_VALUE_EXT = 39 # Variable c_int '39'
GLX_VIDEO_OUT_STACKED_FIELDS_2_1_NV = 8396 # Variable c_int '8396'
GLX_LEVEL = 3 # Variable c_int '3'
GLX_ARB_multisample = 1 # Variable c_int '1'
GLX_SHARE_CONTEXT_EXT = 32778 # Variable c_int '32778'
GLX_AUX8_EXT = 8426 # Variable c_int '8426'
GLX_HEIGHT = 32798 # Variable c_int '32798'
GLX_FRONT_RIGHT_BUFFER_BIT = 2 # Variable c_int '2'
GLX_HYPERPIPE_RENDER_PIPE_SGIX = 2 # Variable c_int '2'
GLX_PBUFFER_CLOBBER_MASK = 134217728 # Variable c_int '134217728'
GLX_TEXTURE_1D_EXT = 8411 # Variable c_int '8411'
GLX_AUX2_EXT = 8420 # Variable c_int '8420'
GLX_TRANSPARENT_GREEN_VALUE_EXT = 38 # Variable c_int '38'
GLX_MAX_SWAP_INTERVAL_EXT = 8434 # Variable c_int '8434'
GLX_EXT_fbconfig_packed_float = 1 # Variable c_int '1'
GLX_PIPE_RECT_LIMITS_SGIX = 2 # Variable c_int '2'
GLX_TRANSPARENT_RGB_EXT = 32776 # Variable c_int '32776'
GLX_NV_present_video = 1 # Variable c_int '1'
GLX_MULTISAMPLE_SUB_RECT_HEIGHT_SGIS = 32807 # Variable c_int '32807'
GLX_BAD_HYPERPIPE_SGIX = 92 # Variable c_int '92'
GLX_OML_swap_method = 1 # Variable c_int '1'
GLX_EXTENSION_NAME = 'GLX' # Variable STRING '(const char*)"GLX"'
GLX_GPU_NUM_SIMD_AMD = 8614 # Variable c_int '8614'
GLX_VERSION_1_4 = 1 # Variable c_int '1'
GLX_VERSION_1_1 = 1 # Variable c_int '1'
GLX_VERSION_1_2 = 1 # Variable c_int '1'
GLX_VERSION_1_3 = 1 # Variable c_int '1'
GLX_NO_RESET_NOTIFICATION_ARB = 33377 # Variable c_int '33377'
GLX_COLOR_INDEX_TYPE_SGIX = 32789 # Variable c_int '32789'
GLX_ACCUM_RED_SIZE = 14 # Variable c_int '14'
GLX_RGBA_UNSIGNED_FLOAT_BIT_EXT = 8 # Variable c_int '8'
GLX_TEXTURE_FORMAT_EXT = 8405 # Variable c_int '8405'
GLX_TRANSPARENT_ALPHA_VALUE_EXT = 40 # Variable c_int '40'
GLX_MESA_release_buffers = 1 # Variable c_int '1'
GLX_FLIP_COMPLETE_INTEL = 33154 # Variable c_int '33154'
GLX_SAMPLE_BUFFERS_SGIS = 100000 # Variable c_int '100000'
GLX_PRESERVED_CONTENTS_SGIX = 32795 # Variable c_int '32795'
GLX_STATIC_COLOR = 32773 # Variable c_int '32773'
GLX_VIDEO_OUT_COLOR_AND_DEPTH_NV = 8391 # Variable c_int '8391'
GLX_TRUE_COLOR = 32770 # Variable c_int '32770'
GLX_AUX3_EXT = 8421 # Variable c_int '8421'
GLX_TEXTURE_2D_EXT = 8412 # Variable c_int '8412'
GLX_SGI_cushion = 1 # Variable c_int '1'
GLX_EXTENSIONS = 3 # Variable c_int '3'
GLX_TEXTURE_1D_BIT_EXT = 1 # Variable c_int '1'
GLX_GPU_RENDERER_STRING_AMD = 7937 # Variable c_int '7937'
GLX_SYNC_FRAME_SGIX = 0 # Variable c_int '0'
GLX_EXCHANGE_COMPLETE_INTEL = 33152 # Variable c_int '33152'
GLX_VIDEO_OUT_COLOR_AND_ALPHA_NV = 8390 # Variable c_int '8390'
GLX_GREEN_SIZE = 9 # Variable c_int '9'
GLX_COVERAGE_SAMPLES_NV = 100001 # Variable c_int '100001'
GLX_SGIX_dmbuffer = 1 # Variable c_int '1'
GLX_PSEUDO_COLOR_EXT = 32772 # Variable c_int '32772'
GLX_COPY_COMPLETE_INTEL = 33153 # Variable c_int '33153'
GLX_GPU_NUM_PIPES_AMD = 8613 # Variable c_int '8613'
GLX_DIRECT_COLOR = 32771 # Variable c_int '32771'
GLX_BAD_VISUAL = 4 # Variable c_int '4'
GLX_PIPE_RECT_SGIX = 1 # Variable c_int '1'
GLX_TEXTURE_RECTANGLE_BIT_EXT = 4 # Variable c_int '4'
GLX_CONTEXT_RESET_NOTIFICATION_STRATEGY_ARB = 33366 # Variable c_int '33366'
GLX_DEVICE_ID_NV = 8397 # Variable c_int '8397'
GLX_ACCUM_BUFFER_BIT_SGIX = 128 # Variable c_int '128'
GLX_VIDEO_OUT_ALPHA_NV = 8388 # Variable c_int '8388'
GLX_TEXTURE_TARGET_EXT = 8406 # Variable c_int '8406'
GLX_BIND_TO_TEXTURE_RGB_EXT = 8400 # Variable c_int '8400'
GLX_ALPHA_SIZE = 11 # Variable c_int '11'
GLX_LARGEST_PBUFFER = 32796 # Variable c_int '32796'
GLX_NV_copy_image = 1 # Variable c_int '1'
GLX_PBUFFER_WIDTH = 32833 # Variable c_int '32833'
GLX_BAD_CONTEXT = 5 # Variable c_int '5'
GLX_FRONT_LEFT_BUFFER_BIT = 1 # Variable c_int '1'
GLX_PIXMAP_BIT_SGIX = 2 # Variable c_int '2'
GLX_SUN_get_transparent_index = 1 # Variable c_int '1'
GLX_X_RENDERABLE_SGIX = 32786 # Variable c_int '32786'
GLX_DIRECT_COLOR_EXT = 32771 # Variable c_int '32771'
GLX_EXT_import_context = 1 # Variable c_int '1'
GLX_DAMAGED_SGIX = 32800 # Variable c_int '32800'
GLX_SAMPLES_SGIS = 100001 # Variable c_int '100001'
GLX_CONTEXT_ES2_PROFILE_BIT_EXT = 4 # Variable c_int '4'
GLX_TRANSPARENT_GREEN_VALUE = 38 # Variable c_int '38'
GLX_AUX4_EXT = 8422 # Variable c_int '8422'
GLX_TRANSPARENT_INDEX_VALUE_EXT = 36 # Variable c_int '36'
GLX_TRANSPARENT_RED_VALUE_EXT = 37 # Variable c_int '37'
GLX_FRONT_RIGHT_BUFFER_BIT_SGIX = 2 # Variable c_int '2'
GLX_BACK_LEFT_BUFFER_BIT_SGIX = 4 # Variable c_int '4'
GLX_HYPERPIPE_ID_SGIX = 32816 # Variable c_int '32816'
GLX_AUX5_EXT = 8423 # Variable c_int '8423'
GLX_GPU_OPENGL_VERSION_STRING_AMD = 7938 # Variable c_int '7938'
GLX_FRAMEBUFFER_SRGB_CAPABLE_EXT = 8370 # Variable c_int '8370'
GLX_AUX7_EXT = 8425 # Variable c_int '8425'
GLX_GPU_CLOCK_AMD = 8612 # Variable c_int '8612'
GLX_AUX1_EXT = 8419 # Variable c_int '8419'
GLX_BAD_SCREEN = 1 # Variable c_int '1'
GLX_NV_multisample_coverage = 1 # Variable c_int '1'
GLX_DEPTH_SIZE = 12 # Variable c_int '12'
GLX_FLOAT_COMPONENTS_NV = 8368 # Variable c_int '8368'
GLX_DIGITAL_MEDIA_PBUFFER_SGIX = 32804 # Variable c_int '32804'
GLX_GPU_RAM_AMD = 8611 # Variable c_int '8611'
GLX_PRESERVED_CONTENTS = 32795 # Variable c_int '32795'
GLX_VERSION = 2 # Variable c_int '2'
GLX_PSEUDO_COLOR = 32772 # Variable c_int '32772'
GLX_RGBA_TYPE_SGIX = 32788 # Variable c_int '32788'
GLX_FBCONFIG_ID = 32787 # Variable c_int '32787'
GLX_GPU_VENDOR_AMD = 7936 # Variable c_int '7936'
GLX_BufferSwapComplete = 1 # Variable c_int '1'
GLX_EVENT_MASK = 32799 # Variable c_int '32799'
GLX_CONTEXT_CORE_PROFILE_BIT_ARB = 1 # Variable c_int '1'
GLX_BAD_VALUE = 6 # Variable c_int '6'
GLX_CONTEXT_MINOR_VERSION_ARB = 8338 # Variable c_int '8338'
GLX_MAX_PBUFFER_WIDTH = 32790 # Variable c_int '32790'
GLX_ARB_get_proc_address = 1 # Variable c_int '1'
GLX_VIDEO_OUT_FIELD_1_NV = 8393 # Variable c_int '8393'
GLX_SGIX_pbuffer = 1 # Variable c_int '1'
GLX_ARB_create_context_profile = 1 # Variable c_int '1'
class XVisualInfo(Structure):
    pass
class _XDisplay(Structure):
    pass
Display = _XDisplay
glXChooseVisual = _libraries['libGL.so.1'].glXChooseVisual
glXChooseVisual.restype = POINTER(XVisualInfo)
glXChooseVisual.argtypes = [POINTER(Display), c_int, POINTER(c_int)]
class __GLXcontextRec(Structure):
    pass
GLXContext = POINTER(__GLXcontextRec)
glXCreateContext = _libraries['libGL.so.1'].glXCreateContext
glXCreateContext.restype = GLXContext
glXCreateContext.argtypes = [POINTER(Display), POINTER(XVisualInfo), GLXContext, c_int]
glXDestroyContext = _libraries['libGL.so.1'].glXDestroyContext
glXDestroyContext.restype = None
glXDestroyContext.argtypes = [POINTER(Display), GLXContext]
XID = c_ulong
GLXDrawable = XID
glXMakeCurrent = _libraries['libGL.so.1'].glXMakeCurrent
glXMakeCurrent.restype = c_int
glXMakeCurrent.argtypes = [POINTER(Display), GLXDrawable, GLXContext]
glXCopyContext = _libraries['libGL.so.1'].glXCopyContext
glXCopyContext.restype = None
glXCopyContext.argtypes = [POINTER(Display), GLXContext, GLXContext, c_ulong]
glXSwapBuffers = _libraries['libGL.so.1'].glXSwapBuffers
glXSwapBuffers.restype = None
glXSwapBuffers.argtypes = [POINTER(Display), GLXDrawable]
GLXPixmap = XID
Pixmap = XID
glXCreateGLXPixmap = _libraries['libGL.so.1'].glXCreateGLXPixmap
glXCreateGLXPixmap.restype = GLXPixmap
glXCreateGLXPixmap.argtypes = [POINTER(Display), POINTER(XVisualInfo), Pixmap]
glXDestroyGLXPixmap = _libraries['libGL.so.1'].glXDestroyGLXPixmap
glXDestroyGLXPixmap.restype = None
glXDestroyGLXPixmap.argtypes = [POINTER(Display), GLXPixmap]
glXQueryExtension = _libraries['libGL.so.1'].glXQueryExtension
glXQueryExtension.restype = c_int
glXQueryExtension.argtypes = [POINTER(Display), POINTER(c_int), POINTER(c_int)]
glXQueryVersion = _libraries['libGL.so.1'].glXQueryVersion
glXQueryVersion.restype = c_int
glXQueryVersion.argtypes = [POINTER(Display), POINTER(c_int), POINTER(c_int)]
glXIsDirect = _libraries['libGL.so.1'].glXIsDirect
glXIsDirect.restype = c_int
glXIsDirect.argtypes = [POINTER(Display), GLXContext]
glXGetConfig = _libraries['libGL.so.1'].glXGetConfig
glXGetConfig.restype = c_int
glXGetConfig.argtypes = [POINTER(Display), POINTER(XVisualInfo), c_int, POINTER(c_int)]
glXGetCurrentContext = _libraries['libGL.so.1'].glXGetCurrentContext
glXGetCurrentContext.restype = GLXContext
glXGetCurrentContext.argtypes = []
glXGetCurrentDrawable = _libraries['libGL.so.1'].glXGetCurrentDrawable
glXGetCurrentDrawable.restype = GLXDrawable
glXGetCurrentDrawable.argtypes = []
glXWaitGL = _libraries['libGL.so.1'].glXWaitGL
glXWaitGL.restype = None
glXWaitGL.argtypes = []
glXWaitX = _libraries['libGL.so.1'].glXWaitX
glXWaitX.restype = None
glXWaitX.argtypes = []
Font = XID
glXUseXFont = _libraries['libGL.so.1'].glXUseXFont
glXUseXFont.restype = None
glXUseXFont.argtypes = [Font, c_int, c_int, c_int]
glXQueryExtensionsString = _libraries['libGL.so.1'].glXQueryExtensionsString
glXQueryExtensionsString.restype = STRING
glXQueryExtensionsString.argtypes = [POINTER(Display), c_int]
glXQueryServerString = _libraries['libGL.so.1'].glXQueryServerString
glXQueryServerString.restype = STRING
glXQueryServerString.argtypes = [POINTER(Display), c_int, c_int]
glXGetClientString = _libraries['libGL.so.1'].glXGetClientString
glXGetClientString.restype = STRING
glXGetClientString.argtypes = [POINTER(Display), c_int]
glXGetCurrentDisplay = _libraries['libGL.so.1'].glXGetCurrentDisplay
glXGetCurrentDisplay.restype = POINTER(Display)
glXGetCurrentDisplay.argtypes = []
class __GLXFBConfigRec(Structure):
    pass
GLXFBConfig = POINTER(__GLXFBConfigRec)
glXChooseFBConfig = _libraries['libGL.so.1'].glXChooseFBConfig
glXChooseFBConfig.restype = POINTER(GLXFBConfig)
glXChooseFBConfig.argtypes = [POINTER(Display), c_int, POINTER(c_int), POINTER(c_int)]
glXGetFBConfigAttrib = _libraries['libGL.so.1'].glXGetFBConfigAttrib
glXGetFBConfigAttrib.restype = c_int
glXGetFBConfigAttrib.argtypes = [POINTER(Display), GLXFBConfig, c_int, POINTER(c_int)]
glXGetFBConfigs = _libraries['libGL.so.1'].glXGetFBConfigs
glXGetFBConfigs.restype = POINTER(GLXFBConfig)
glXGetFBConfigs.argtypes = [POINTER(Display), c_int, POINTER(c_int)]
glXGetVisualFromFBConfig = _libraries['libGL.so.1'].glXGetVisualFromFBConfig
glXGetVisualFromFBConfig.restype = POINTER(XVisualInfo)
glXGetVisualFromFBConfig.argtypes = [POINTER(Display), GLXFBConfig]
GLXWindow = XID
Window = XID
glXCreateWindow = _libraries['libGL.so.1'].glXCreateWindow
glXCreateWindow.restype = GLXWindow
glXCreateWindow.argtypes = [POINTER(Display), GLXFBConfig, Window, POINTER(c_int)]
glXDestroyWindow = _libraries['libGL.so.1'].glXDestroyWindow
glXDestroyWindow.restype = None
glXDestroyWindow.argtypes = [POINTER(Display), GLXWindow]
glXCreatePixmap = _libraries['libGL.so.1'].glXCreatePixmap
glXCreatePixmap.restype = GLXPixmap
glXCreatePixmap.argtypes = [POINTER(Display), GLXFBConfig, Pixmap, POINTER(c_int)]
glXDestroyPixmap = _libraries['libGL.so.1'].glXDestroyPixmap
glXDestroyPixmap.restype = None
glXDestroyPixmap.argtypes = [POINTER(Display), GLXPixmap]
GLXPbuffer = XID
glXCreatePbuffer = _libraries['libGL.so.1'].glXCreatePbuffer
glXCreatePbuffer.restype = GLXPbuffer
glXCreatePbuffer.argtypes = [POINTER(Display), GLXFBConfig, POINTER(c_int)]
glXDestroyPbuffer = _libraries['libGL.so.1'].glXDestroyPbuffer
glXDestroyPbuffer.restype = None
glXDestroyPbuffer.argtypes = [POINTER(Display), GLXPbuffer]
glXQueryDrawable = _libraries['libGL.so.1'].glXQueryDrawable
glXQueryDrawable.restype = None
glXQueryDrawable.argtypes = [POINTER(Display), GLXDrawable, c_int, POINTER(c_uint)]
glXCreateNewContext = _libraries['libGL.so.1'].glXCreateNewContext
glXCreateNewContext.restype = GLXContext
glXCreateNewContext.argtypes = [POINTER(Display), GLXFBConfig, c_int, GLXContext, c_int]
glXMakeContextCurrent = _libraries['libGL.so.1'].glXMakeContextCurrent
glXMakeContextCurrent.restype = c_int
glXMakeContextCurrent.argtypes = [POINTER(Display), GLXDrawable, GLXDrawable, GLXContext]
glXGetCurrentReadDrawable = _libraries['libGL.so.1'].glXGetCurrentReadDrawable
glXGetCurrentReadDrawable.restype = GLXDrawable
glXGetCurrentReadDrawable.argtypes = []
glXQueryContext = _libraries['libGL.so.1'].glXQueryContext
glXQueryContext.restype = c_int
glXQueryContext.argtypes = [POINTER(Display), GLXContext, c_int, POINTER(c_int)]
glXSelectEvent = _libraries['libGL.so.1'].glXSelectEvent
glXSelectEvent.restype = None
glXSelectEvent.argtypes = [POINTER(Display), GLXDrawable, c_ulong]
glXGetSelectedEvent = _libraries['libGL.so.1'].glXGetSelectedEvent
glXGetSelectedEvent.restype = None
glXGetSelectedEvent.argtypes = [POINTER(Display), GLXDrawable, POINTER(c_ulong)]
__GLXextFuncPtr = CFUNCTYPE(None)
GLubyte = c_ubyte
glXGetProcAddressARB = _libraries['libGL.so.1'].glXGetProcAddressARB
glXGetProcAddressARB.restype = __GLXextFuncPtr
glXGetProcAddressARB.argtypes = [POINTER(GLubyte)]
glXGetProcAddress = _libraries['libGL.so.1'].glXGetProcAddress
glXGetProcAddress.restype = CFUNCTYPE(None)
glXGetProcAddress.argtypes = [POINTER(GLubyte)]
GLsizei = c_int
GLfloat = c_float
glXAllocateMemoryNV = _libraries['libGL.so.1'].glXAllocateMemoryNV
glXAllocateMemoryNV.restype = c_void_p
glXAllocateMemoryNV.argtypes = [GLsizei, GLfloat, GLfloat, GLfloat]
GLvoid = None
glXFreeMemoryNV = _libraries['libGL.so.1'].glXFreeMemoryNV
glXFreeMemoryNV.restype = None
glXFreeMemoryNV.argtypes = [POINTER(GLvoid)]
__GLXcontextRec._fields_ = [
]
__GLXFBConfigRec._fields_ = [
]
_XDisplay._fields_ = [
]
class Visual(Structure):
    pass
VisualID = c_ulong
XVisualInfo._fields_ = [
    ('visual', POINTER(Visual)),
    ('visualid', VisualID),
    ('screen', c_int),
    ('depth', c_int),
    ('c_class', c_int),
    ('red_mask', c_ulong),
    ('green_mask', c_ulong),
    ('blue_mask', c_ulong),
    ('colormap_size', c_int),
    ('bits_per_rgb', c_int),
]
class _XExtData(Structure):
    pass
XExtData = _XExtData
Visual._fields_ = [
    ('ext_data', POINTER(XExtData)),
    ('visualid', VisualID),
    ('c_class', c_int),
    ('red_mask', c_ulong),
    ('green_mask', c_ulong),
    ('blue_mask', c_ulong),
    ('bits_per_rgb', c_int),
    ('map_entries', c_int),
]
XPointer = STRING
_XExtData._fields_ = [
    ('number', c_int),
    ('next', POINTER(_XExtData)),
    ('free_private', CFUNCTYPE(c_int, POINTER(_XExtData))),
    ('private_data', XPointer),
]
__all__ = ['GLX_CONTEXT_PROFILE_MASK_ARB', 'GLsizei',
           'GLX_EXT_import_context', 'GLX_PIPE_RECT_LIMITS_SGIX',
           'glXCreateContext', 'GLX_STATIC_COLOR_EXT',
           'GLX_SWAP_METHOD_OML', 'GLX_SGIS_multisample',
           'GLX_NON_CONFORMANT_CONFIG', 'glXDestroyWindow',
           'GLX_CONTEXT_FLAGS_ARB', 'glXQueryDrawable',
           'GLX_ARB_multisample', 'GLX_ACCUM_RED_SIZE',
           'GLX_BACK_LEFT_EXT', 'GLX_X_VISUAL_TYPE_EXT',
           'XVisualInfo', 'GLX_BIND_TO_TEXTURE_RGB_EXT',
           'GLX_MESA_swap_frame_usage', 'GLX_NV_present_video',
           'GLX_VIDEO_OUT_STACKED_FIELDS_2_1_NV',
           'GLX_AUX_BUFFERS_BIT_SGIX', 'GLX_EXT_framebuffer_sRGB',
           'GLX_TRANSPARENT_INDEX_VALUE', 'GLX_LEVEL', 'GLX_AUX1_EXT',
           'GLX_SAMPLE_BUFFERS_3DFX', 'GLX_MESA_agp_offset',
           'GLX_BACK_EXT', 'GLX_DOUBLEBUFFER', 'Visual',
           'GLX_COLOR_INDEX_BIT_SGIX', 'GLX_SAVED_SGIX',
           'GLX_AUX6_EXT', 'GLX_STENCIL_SIZE',
           'GLX_RGBA_UNSIGNED_FLOAT_TYPE_EXT', 'GLX_WIDTH',
           'GLX_MAX_PBUFFER_WIDTH', 'GLfloat', 'GLX_WINDOW',
           'GLX_SAMPLE_BUFFERS', 'GLX_VERSION',
           'GLX_SGI_make_current_read', 'GLX_TRANSPARENT_RGB_EXT',
           'GLX_SAVED', 'GLX_DAMAGED_SGIX',
           'GLX_MULTISAMPLE_SUB_RECT_HEIGHT_SGIS',
           'GLX_PIPE_RECT_SGIX', 'GLX_BAD_SCREEN',
           'GLX_SWAP_COPY_OML', 'GLX_MESA_pixmap_colormap',
           'GLX_BAD_HYPERPIPE_CONFIG_SGIX',
           'GLX_NV_multisample_coverage',
           'GLX_SGIX_visual_select_group', 'GLX_DEPTH_SIZE',
           'GLX_BIND_TO_TEXTURE_RGBA_EXT', 'glXChooseFBConfig',
           'GLX_CONTEXT_RESET_NOTIFICATION_STRATEGY_ARB',
           'GLX_TEXTURE_FORMAT_RGB_EXT', 'GLX_DEVICE_ID_NV',
           'glXGetClientString', 'Pixmap', 'GLX_BAD_HYPERPIPE_SGIX',
           'GLX_BUFFER_SIZE', 'GLX_SLOW_CONFIG', '__GLXFBConfigRec',
           'GLX_EXTENSIONS', 'GLX_TEXTURE_1D_BIT_EXT',
           'GLX_DONT_CARE', 'GLX_ARB_create_context_robustness',
           'GLX_OML_swap_method', 'GLX_VIDEO_OUT_ALPHA_NV',
           'GLX_BLENDED_RGBA_SGIS', 'GLX_EXTENSION_NAME', '_XExtData',
           'GLX_BIND_TO_TEXTURE_TARGETS_EXT', 'GLX_SAMPLES_SGIS',
           'GLX_LATE_SWAPS_TEAR_EXT', 'GLX_ACCUM_BUFFER_BIT_SGIX',
           'GLXWindow', 'GLX_NUM_VIDEO_CAPTURE_SLOTS_NV',
           'GLX_CONTEXT_ES2_PROFILE_BIT_EXT',
           'GLX_CONTEXT_MAJOR_VERSION_ARB',
           'GLX_GPU_RENDERER_STRING_AMD', 'glXMakeContextCurrent',
           'GLX_MAX_PBUFFER_PIXELS_SGIX',
           'GLX_VISUAL_SELECT_GROUP_SGIX', 'GLX_GPU_NUM_SIMD_AMD',
           'GLX_PBUFFER_HEIGHT', 'GLX_EXT_swap_control',
           'GLX_VERSION_1_4', 'GLX_SHARE_CONTEXT_EXT',
           'GLX_VERSION_1_1', 'GLX_VERSION_1_2', 'GLX_VERSION_1_3',
           'GLX_SGIX_swap_group', '__GLXextFuncPtr',
           'GLX_BACK_RIGHT_BUFFER_BIT_SGIX', 'GLX_ACCUM_GREEN_SIZE',
           'GLX_NO_RESET_NOTIFICATION_ARB', 'GLX_VISUAL_ID_EXT',
           'GLX_WINDOW_BIT_SGIX', 'GLX_MESA_set_3dfx_mode',
           'GLX_BAD_ATTRIBUTE', 'GLX_RGBA_FLOAT_TYPE_ARB',
           'GLX_AUX_BUFFERS_BIT', 'GLX_STENCIL_BUFFER_BIT',
           'GLX_FLOAT_COMPONENTS_NV', 'GLXFBConfig',
           'glXGetSelectedEvent', 'glXMakeCurrent',
           'GLX_FRONT_RIGHT_EXT', 'GLX_DIGITAL_MEDIA_PBUFFER_SGIX',
           'GLX_RENDER_TYPE', 'GLX_FRONT_LEFT_EXT', 'GLX_SCREEN',
           'GLX_BIND_TO_MIPMAP_TEXTURE_EXT', 'GLX_EVENT_MASK_SGIX',
           'GLX_TRANSPARENT_RGB', 'GLX_VIDEO_OUT_FIELD_2_NV',
           'GLX_CONTEXT_COMPATIBILITY_PROFILE_BIT_ARB',
           'GLX_VISUAL_ID', 'GLX_COLOR_INDEX_TYPE_SGIX',
           'GLX_OPTIMAL_PBUFFER_WIDTH_SGIX', 'GLX_GPU_RAM_AMD',
           'GLX_SYNC_FRAME_SGIX', 'GLX_EXCHANGE_COMPLETE_INTEL',
           'GLX_GRAY_SCALE', 'GLX_VIDEO_OUT_COLOR_AND_ALPHA_NV',
           'GLX_WINDOW_SGIX', 'glXDestroyGLXPixmap',
           'GLX_FRAMEBUFFER_SRGB_CAPABLE_EXT', 'GLX_STATIC_GRAY_EXT',
           'GLX_ACCUM_BLUE_SIZE', 'GLX_TRANSPARENT_GREEN_VALUE',
           'GLX_NUM_VIDEO_SLOTS_NV', 'GLX_PBUFFER_BIT_SGIX',
           'GLX_SLOW_VISUAL_EXT', 'glXQueryVersion', 'GLubyte',
           'GLX_SWAP_INTERVAL_EXT', 'GLX_GREEN_SIZE',
           'GLX_COVERAGE_SAMPLES_NV', 'GLX_OML_sync_control',
           'GLXPixmap', 'GLX_BLUE_SIZE', 'GLX_AUX4_EXT',
           'glXGetCurrentDrawable', 'GLX_SGI_video_sync',
           'glXIsDirect', 'glXQueryExtension',
           'GLX_TRANSPARENT_INDEX_VALUE_EXT',
           'GLX_HYPERPIPE_STEREO_SGIX', 'GLX_SGIX_video_source',
           'GLX_PRESERVED_CONTENTS', 'GLX_CONTEXT_DEBUG_BIT_ARB',
           'glXDestroyContext', '_XDisplay', 'GLX_PBUFFER_BIT',
           'GLX_WIDTH_SGIX', 'GLX_COLOR_SAMPLES_NV', 'GLX_WINDOW_BIT',
           'GLX_RGBA_FLOAT_BIT_ARB', 'GLXDrawable',
           'GLX_PSEUDO_COLOR', 'GLX_NV_swap_group', 'Window',
           'GLX_AUX8_EXT', 'GLXPbuffer',
           'GLX_TRANSPARENT_RED_VALUE_EXT', 'GLX_GPU_NUM_SPI_AMD',
           'GLX_STEREO', 'GLX_ACCUM_ALPHA_SIZE', 'glXCopyContext',
           'GLX_Y_INVERTED_EXT', 'GLX_X_VISUAL_TYPE',
           'GLX_TRANSPARENT_BLUE_VALUE', 'GLX_RED_SIZE',
           'GLX_ARB_create_context', 'GLX_SAMPLES_ARB',
           'GLX_ALPHA_SIZE', 'GLX_TRANSPARENT_INDEX_EXT',
           'GLX_HEIGHT', 'GLX_SGIX_dmbuffer', 'GLX_SGI_swap_control',
           'GLX_MESA_copy_sub_buffer',
           'GLX_BUFFER_SWAP_COMPLETE_INTEL_MASK',
           'GLX_TRANSPARENT_TYPE', 'GLX_TEXTURE_FORMAT_NONE_EXT',
           'glXCreateGLXPixmap', 'GLX_SCREEN_EXT',
           'GLX_GPU_FASTEST_TARGET_GPUS_AMD', '__GLXcontextRec',
           'GLX_TRANSPARENT_RED_VALUE', 'GLX_SAMPLES_3DFX',
           'glXGetProcAddress', 'GLX_FRONT_RIGHT_BUFFER_BIT',
           'GLX_SAMPLES', 'GLX_DAMAGED', 'XID',
           'GLX_RGBA_UNSIGNED_FLOAT_BIT_EXT',
           'GLX_FRONT_RIGHT_BUFFER_BIT_SGIX', 'glXChooseVisual',
           'GLX_DEPTH_BUFFER_BIT', 'GLXContext', 'Display',
           'GLX_LARGEST_PBUFFER', 'GLX_SAMPLE_BUFFERS_BIT_SGIX',
           'GLX_PSEUDO_COLOR_EXT', 'glXCreatePixmap',
           'GLX_VIDEO_OUT_DEPTH_NV', 'GLX_SYNC_SWAP_SGIX',
           'GLX_EXT_visual_rating', 'GLX_ARB_framebuffer_sRGB',
           'GLX_HYPERPIPE_DISPLAY_PIPE_SGIX',
           'GLX_SWAP_UNDEFINED_OML', 'GLX_TEXTURE_FORMAT_EXT',
           'GLX_TRANSPARENT_ALPHA_VALUE_EXT', 'GLX_RGBA_BIT_SGIX',
           'GLX_BACK_LEFT_BUFFER_BIT', 'GLX_ACCUM_BUFFER_BIT',
           'GLX_NV_copy_image', 'GLX_RGBA_TYPE_SGIX',
           'GLX_COPY_COMPLETE_INTEL', 'GLX_MAX_PBUFFER_PIXELS',
           'GLX_GPU_VENDOR_AMD', 'GLX_RENDER_TYPE_SGIX',
           'GLX_TRANSPARENT_ALPHA_VALUE', 'GLX_MESA_release_buffers',
           'GLX_CONTEXT_ALLOW_BUFFER_BYTE_ORDER_MISMATCH_ARB',
           'glXGetFBConfigs', 'GLX_FBCONFIG_ID', 'glXWaitX',
           'GLX_VISUAL_CAVEAT_EXT', 'GLX_HEIGHT_SGIX', 'GLX_VENDOR',
           'GLX_VIDEO_OUT_STACKED_FIELDS_1_2_NV', 'GLX_DRAWABLE_TYPE',
           'GLX_PbufferClobber', 'GLX_PBUFFER_WIDTH',
           'glXDestroyPixmap', 'GLX_SWAP_EXCHANGE_OML', 'glXWaitGL',
           'GLX_EXT_visual_info', 'GLX_RGBA_TYPE', 'GLX_NO_EXTENSION',
           'GLX_MESA_swap_control', 'glXGetProcAddressARB',
           'GLX_TEXTURE_2D_EXT', 'XExtData', 'glXQueryContext',
           'GLX_VIDEO_OUT_COLOR_NV', 'GLX_NV_video_output',
           'GLX_GPU_NUM_PIPES_AMD', 'glXCreateNewContext',
           'GLX_FLIP_COMPLETE_INTEL', 'GLX_NON_CONFORMANT_VISUAL_EXT',
           'VisualID', 'XPointer', 'GLX_BAD_CONTEXT',
           'GLX_STENCIL_BUFFER_BIT_SGIX', 'GLX_TRANSPARENT_INDEX',
           'GLX_LARGEST_PBUFFER_SGIX', 'GLX_PIXMAP_BIT_SGIX',
           'GLX_SAMPLE_BUFFERS_SGIS', 'GLX_INTEL_swap_event',
           'GLX_SGIX_video_resize', 'GLX_BACK_LEFT_BUFFER_BIT_SGIX',
           'GLX_BufferSwapComplete', 'GLX_TEXTURE_TARGET_EXT',
           'glXSwapBuffers', 'glXGetCurrentDisplay',
           'GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB', 'GLX_AUX9_EXT',
           'GLX_HYPERPIPE_ID_SGIX', 'GLX_BACK_RIGHT_EXT',
           'glXGetFBConfigAttrib', 'GLX_HYPERPIPE_RENDER_PIPE_SGIX',
           'GLX_STATIC_COLOR', 'GLX_EVENT_MASK',
           'GLX_CONTEXT_CORE_PROFILE_BIT_ARB',
           'GLX_EXT_fbconfig_packed_float', 'GLX_USE_GL',
           'GLX_EXT_swap_control_tear', 'GLX_FRONT_EXT',
           'GLX_VIDEO_OUT_COLOR_AND_DEPTH_NV',
           'GLX_HYPERPIPE_PIPE_NAME_LENGTH_SGIX',
           'glXAllocateMemoryNV', 'GLX_DRAWABLE_TYPE_SGIX',
           'glXGetCurrentContext', 'GLX_PBUFFER_CLOBBER_MASK',
           'GLX_STATIC_GRAY', 'glXGetCurrentReadDrawable',
           'GLX_DIRECT_COLOR', 'GLX_FRONT_LEFT_BUFFER_BIT',
           'GLX_FRONT_LEFT_BUFFER_BIT_SGIX', 'GLX_UNIQUE_ID_NV',
           'GLX_TEXTURE_RECTANGLE_EXT', 'GLX_BACK_RIGHT_BUFFER_BIT',
           'GLX_MAX_PBUFFER_WIDTH_SGIX', 'GLX_BAD_VALUE',
           'GLX_AUX5_EXT', 'GLX_TEXTURE_1D_EXT', 'glXDestroyPbuffer',
           'GLX_TRUE_COLOR', 'GLX_NONE_EXT', 'glXSelectEvent',
           'GLX_GPU_OPENGL_VERSION_STRING_AMD', 'GLX_GPU_NUM_RB_AMD',
           'GLX_COLOR_INDEX_TYPE', 'GLX_MAX_PBUFFER_HEIGHT_SGIX',
           'GLX_MULTISAMPLE_SUB_RECT_WIDTH_SGIS',
           'GLX_FRAMEBUFFER_SRGB_CAPABLE_ARB',
           'GLX_CONTEXT_MINOR_VERSION_ARB',
           'GLX_CONTEXT_ROBUST_ACCESS_BIT_ARB',
           'GLX_LOSE_CONTEXT_ON_RESET_ARB',
           'GLX_HYPERPIPE_PIXEL_AVERAGE_SGIX', 'GLX_AUX3_EXT',
           'GLX_AUX2_EXT', 'Font', 'GLX_TEXTURE_FORMAT_RGBA_EXT',
           'GLX_TEXTURE_2D_BIT_EXT', 'glXGetConfig', 'GLX_NONE',
           'GLX_ARB_get_proc_address', 'GLX_AUX7_EXT',
           'GLX_VIDEO_OUT_FIELD_1_NV', 'GLX_TRANSPARENT_TYPE_EXT',
           'GLX_SGIX_pbuffer', 'GLX_SAMPLE_BUFFERS_ARB',
           'GLX_TRANSPARENT_GREEN_VALUE_EXT', 'GLX_COLOR_INDEX_BIT',
           'GLX_SGIX_hyperpipe', 'GLX_MIPMAP_TEXTURE_EXT',
           'GLX_SUN_get_transparent_index', 'GLX_BAD_VISUAL',
           'GLX_X_RENDERABLE_SGIX', 'GLX_FBCONFIG_ID_SGIX',
           'GLX_PBUFFER', 'GLX_VIDEO_OUT_FRAME_NV',
           'GLX_OPTIMAL_PBUFFER_HEIGHT_SGIX', 'GLX_BAD_ENUM',
           'GLX_BUFFER_CLOBBER_MASK_SGIX', 'GLX_RGBA',
           'GLX_DEPTH_BUFFER_BIT_SGIX',
           'GLX_ARB_create_context_profile', 'GLX_NV_float_buffer',
           'GLX_CONFIG_CAVEAT', 'GLvoid', 'GLX_RGBA_BIT',
           'GLX_ARB_fbconfig_float', 'GLX_PIXMAP_BIT',
           'GLX_MAX_SWAP_INTERVAL_EXT', 'GLX_AUX0_EXT',
           'GLX_GPU_CLOCK_AMD', 'GLX_AUX_BUFFERS',
           'GLX_PRESERVED_CONTENTS_SGIX', 'GLX_TRUE_COLOR_EXT',
           'glXFreeMemoryNV', 'GLX_NV_video_capture',
           'GLX_GRAY_SCALE_EXT', 'GLX_TEXTURE_RECTANGLE_BIT_EXT',
           'glXCreateWindow', 'GLX_EXT_texture_from_pixmap',
           'GLX_ARB_render_texture', 'glXCreatePbuffer',
           'GLX_GLXEXT_VERSION', 'GLX_X_RENDERABLE',
           'glXQueryServerString', 'GLX_SGIX_fbconfig',
           'GLX_TRANSPARENT_BLUE_VALUE_EXT', 'glXUseXFont',
           'GLX_PBUFFER_SGIX', 'GLX_SGIX_swap_barrier',
           'GLX_DIRECT_COLOR_EXT', 'GLX_MAX_PBUFFER_HEIGHT',
           'GLX_SGI_cushion', 'glXGetVisualFromFBConfig',
           'glXQueryExtensionsString']
